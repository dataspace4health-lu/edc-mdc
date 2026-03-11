import logging
import os
import signal
import urllib.parse
from typing import Annotated, Optional

import httpx
from fastapi import Depends
from models.identity_context import IdentityContext
from repositories.dataset import DatasetRepository
from services.activity_logs.dataset_activity_log import DatasetActivityLogService
from services.catalogues.importers.dataset_rdf_import_service import (
    DatasetRDFImportService,
)
from services.database_session_manager import DatabaseSessionManager
from services.user import UserService
from services.config import ConfigService, get_config_service
from auth.service_account_user import create_or_find_service_account_user

logger = logging.getLogger(__name__)


class LNDSHostedDatasetImportService:
    def __init__(
        self,
        dataset_repository: Annotated[DatasetRepository, Depends(DatasetRepository)],
        dataset_rdf_import_service: Annotated[
            DatasetRDFImportService, Depends(DatasetRDFImportService)
        ],
        database_session_manager: Annotated[
            DatabaseSessionManager, Depends(DatabaseSessionManager)
        ],
        dataset_activity_log_service: Annotated[
            DatasetActivityLogService, Depends(DatasetActivityLogService)
        ],
        user_service: Annotated[UserService, Depends(UserService)],
        config_service: Annotated[ConfigService, Depends(get_config_service)],
        source_instance_url: Optional[str] = None,
        source_instance_name: Optional[str] = None,
        page_size: int = 50,
    ):
        self._dataset_repository = dataset_repository
        self._dataset_rdf_import_service = dataset_rdf_import_service
        self._database_session_manager = database_session_manager
        self._dataset_activity_log_service = dataset_activity_log_service
        self._user_service = user_service
        self._config_service = config_service
        self._source_instance_url = (
            source_instance_url or os.getenv("SOURCE_INSTANCE_URL", "")
        ).rstrip("/")
        self._source_instance_name = source_instance_name or os.getenv(
            "SOURCE_INSTANCE_NAME", "lnds-mdc"
        )
        self._page_size = page_size

        # Service account configuration for authenticating with source instance
        self._oidc_issuer_url = os.getenv("SOURCE_OIDC_ISSUER_URL", "")
        self._service_account_client_id = os.getenv(
            "SOURCE_SERVICE_ACCOUNT_CLIENT_ID", ""
        )
        self._service_account_client_secret = os.getenv(
            "SOURCE_SERVICE_ACCOUNT_CLIENT_SECRET", ""
        )

        # Cache for access token and service account user
        self._access_token: Optional[str] = None
        self._service_account_user_id: Optional[int] = None

        # P0-2: Connection pooling - reuse HTTP client across all requests
        # Disable SSL verification for non-production environments (self-signed certs)
        environment = os.getenv("ENVIRONMENT", "development").lower()
        verify_ssl = environment == "production"
        self._http_client = httpx.Client(
            timeout=httpx.Timeout(30.0, read=60.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            verify=verify_ssl,
        )

        # Graceful shutdown support
        self._shutdown_requested = False
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)  # Also handle Ctrl+C

    @property
    def source_instance_url(self) -> str:
        return self._source_instance_url

    @property
    def source_instance_name(self) -> str:
        return self._source_instance_name

    @property
    def page_size(self) -> int:
        return self._page_size

    @property
    def service_account_user_id(self) -> int:
        if self._service_account_user_id is None:
            raise RuntimeError(
                "Service account user not initialized. "
                "Ensure access token is obtained before accessing user_id"
            )
        return self._service_account_user_id

    def _handle_shutdown(self, signum, frame):
        logger.info(
            "Shutdown signal received, will finish current dataset and exit gracefully"
        )
        self._shutdown_requested = True

    def _obtain_access_token(self) -> str:
        if not all(
            [
                self._oidc_issuer_url,
                self._service_account_client_id,
                self._service_account_client_secret,
            ]
        ):
            raise RuntimeError(
                "Service account credentials not configured. "
                "Set SOURCE_OIDC_ISSUER_URL, "
                "SOURCE_SERVICE_ACCOUNT_CLIENT_ID, and SOURCE_SERVICE_ACCOUNT_CLIENT_SECRET "
                "environment variables to authenticate with source instance."
            )

        token_endpoint = (
            f"{self._oidc_issuer_url.rstrip('/')}/protocol/openid-connect/token"
        )

        data = {
            "grant_type": "client_credentials",
            "client_id": self._service_account_client_id,
            "client_secret": self._service_account_client_secret,
        }

        try:
            response = self._http_client.post(
                token_endpoint,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data["access_token"]

            # Decode token to get service account identity and create/find user
            self._create_service_account_user(access_token)

            return access_token
        except Exception as e:
            logger.error(f"Failed to obtain access token: {str(e)}", exc_info=True)
            raise

    def _create_service_account_user(self, access_token: str) -> None:
        self._service_account_user_id = create_or_find_service_account_user(
            self._user_service,
            access_token,
            self._service_account_client_id,
            self._config_service,
            display_name="LNDS Datasets Import",
        )
        logger.info(f"Using service account user ID {self._service_account_user_id}")

    def _get_auth_headers(self) -> dict:
        if not self._access_token:
            self._access_token = self._obtain_access_token()

        if self._access_token:
            return {"Authorization": f"Bearer {self._access_token}"}
        return {}

    def import_released_datasets(
        self, max_pages: Optional[int] = None
    ) -> dict[str, int]:
        stats = {"processed": 0, "created": 0, "updated": 0, "failed": 0}

        page = 1
        while True:
            if max_pages and page > max_pages:
                break

            try:
                datasets = self._fetch_released_datasets_page(page)

                if not datasets:
                    break

                for dataset_item in datasets:
                    # Check for graceful shutdown request
                    if self._shutdown_requested:
                        logger.info(
                            "Graceful shutdown: stopping after completing current page"
                        )
                        return stats

                    try:
                        imported_dataset_id = self._import_single_dataset(
                            dataset_item, stats
                        )
                        if imported_dataset_id:
                            try:
                                self._queue_push_to_front_office(imported_dataset_id)
                            except Exception as e:
                                logger.error(
                                    f"Failed to queue push to front office for dataset {dataset_item['identifier']}: {str(e)}",
                                    exc_info=True,
                                )
                        stats["processed"] += 1
                    except Exception as e:
                        logger.error(
                            f"Failed to sync dataset {dataset_item['identifier']}: {str(e)}",
                            exc_info=True,
                        )
                        self._database_session_manager.rollback()
                        stats["failed"] += 1

                # If we got fewer items than page_size, we're on the last page
                if len(datasets) < self._page_size:
                    break

                page += 1

            except Exception as e:
                logger.error(f"Failed to fetch page {page}: {str(e)}", exc_info=True)
                self._database_session_manager.rollback()
                break

        logger.info(
            f"Sync completed: {stats['processed']} processed, "
            f"{stats['created']} created, {stats['updated']} updated, "
            f"{stats['failed']} failed"
        )

        # Ensure all changes are committed to database before next scheduled run
        self._database_session_manager.commit()

        return stats

    def _fetch_released_datasets_page(self, page: int) -> list[dict]:
        url = f"{self._source_instance_url}/api/v1/released-datasets"
        params = {"page": page, "page_size": self._page_size}

        logger.info(f"Fetching page {page} from {url}")

        # P0-2: Use pooled HTTP client (connection reuse)
        # Add authentication headers
        headers = self._get_auth_headers()

        try:
            response = self._http_client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                # Token might have expired, try to refresh
                logger.warning("Access token expired, obtaining new token")
                self._access_token = None
                headers = self._get_auth_headers()
                response = self._http_client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data.get("items", [])
            raise

    def _import_single_dataset(self, dataset_item: dict, stats: dict) -> Optional[int]:
        identifier = dataset_item["identifier"]
        source_status = dataset_item["status"]
        source_dataset_id = dataset_item["id"]
        source_previous_version_id = dataset_item.get("previous_version_dataset_id")
        source_released_at = dataset_item.get("released_at")
        source_version_change_type = dataset_item.get("version_change_type")

        # Check if dataset exists locally by source tracking
        existing_dataset = self._dataset_repository.get_dataset_by_source(
            self._source_instance_name, source_dataset_id
        )

        if existing_dataset:
            # Dataset exists - check if status needs update
            if existing_dataset.status != source_status:
                self._update_dataset_status(existing_dataset, source_status)
                stats["updated"] += 1
                return existing_dataset.id  # Return ID to trigger front office push
            return None
        else:
            # Dataset doesn't exist - download and import
            imported_dataset_id = self._import_dataset_from_source(
                source_dataset_id,
                identifier,
                source_status,
                source_previous_version_id,
                source_released_at,
                source_version_change_type,
            )
            stats["created"] += 1
            return imported_dataset_id

    def _queue_push_to_front_office(self, dataset_id: int) -> None:
        # if we import this at the top, it creates a circular dependency (modules depend on each other in a loop, so it's not possible to set up the program). So we imported this inside the function where it is actually used because by then, all modules are already fully loaded, so there's no circular problem
        from jobs.tasks.push_to_front_office import push_dataset_to_front_office_task

        push_dataset_to_front_office_task.delay(dataset_id)

    def _update_dataset_status(self, dataset, new_status: str) -> None:
        old_status = dataset.status
        dataset.status = new_status
        self._dataset_repository.merge(dataset)
        self._database_session_manager.commit()

        self._dataset_activity_log_service.log_external_status_sync(
            user_id=self.service_account_user_id,
            dataset_id=dataset.id,
            source_instance=self._source_instance_name,
            source_dataset_id=dataset.source_dataset_id,
            old_status=old_status,
            new_status=new_status,
        )

    def _import_dataset_from_source(
        self,
        dataset_id: int,
        identifier: str,
        source_status: str,
        source_previous_version_id: int | None = None,
        source_released_at: str | None = None,
        source_version_change_type: str | None = None,
    ) -> int:
        # Download RDF (TTL format)
        rdf_content = self._download_dataset_rdf(dataset_id)

        # Create identity context for import with system admin permissions
        # This allows importing datasets in any status and bypasses permission checks
        identity = IdentityContext(
            user_id=self.service_account_user_id,
            permissions=["system:admin"],
            current_organisation_id=None,
        )

        # Import dataset (skip duplicate check since we already checked by source)
        # Pass source tracking information so it's set during creation
        logger.info(
            f"Importing dataset {identifier} with source tracking: "
            f"source={self._source_instance_name}, source_dataset_id={dataset_id}"
        )
        imported_dataset_resource = self._dataset_rdf_import_service.import_dataset(
            rdf_content=rdf_content,
            rdf_format="turtle",  # TTL format
            identity=identity,
            duplicates_check=False,  # We already checked existence
            target_status=source_status,
            target_released_at=source_released_at,
            target_version_change_type=source_version_change_type,
            source=self._source_instance_name,
            source_dataset_id=dataset_id,
        )

        # Fetch the newly imported dataset
        imported_dataset = self._dataset_repository.get_dataset(
            imported_dataset_resource.id
        )

        logger.info(
            f"Imported dataset {identifier} (id={imported_dataset.id}): "
            f"source={imported_dataset.source}, source_dataset_id={imported_dataset.source_dataset_id}"
        )

        # Link to previous version if it exists in source
        if source_previous_version_id:
            local_previous_version = self._dataset_repository.get_dataset_by_source(
                self._source_instance_name, source_previous_version_id
            )
            if local_previous_version:
                imported_dataset.previous_version_dataset_id = local_previous_version.id
                logger.info(
                    f"Linked dataset {identifier} to previous version "
                    f"(local ID: {local_previous_version.id})"
                )
            else:
                logger.warning(
                    f"Previous version (source ID: {source_previous_version_id}) "
                    f"not found locally for dataset {identifier}"
                )

        self._database_session_manager.commit()

        logger.info(f"Successfully imported dataset {identifier} with source tracking")

        return imported_dataset.id

    def _download_dataset_rdf(self, dataset_id: int) -> str:
        url = f"{self._source_instance_url}/api/v1/released-datasets/{dataset_id}/download"
        params = {"format": "ttl"}

        logger.debug(f"Downloading RDF for dataset {dataset_id}")

        # No authentication needed - public endpoint for released datasets only
        # P0-2: Use pooled HTTP client (connection reuse)
        response = self._http_client.get(url, params=params)
        response.raise_for_status()
        return response.text

    def close(self):
        if hasattr(self, "_http_client"):
            self._http_client.close()
