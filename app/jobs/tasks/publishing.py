import logging
import os
from celery import Task
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from jobs import celery_app
from dependencies.database import get_script_db_session
from models.identity_context import IdentityContext
from repositories.dataset import DatasetRepository
from repositories.applicable_legislation import ApplicableLegislationRepository
from repositories.data_service import DataServiceRepository
from repositories.data_dictionary import DataDictionaryRepository
from repositories.activity_log import ActivityLogRepository
from services.front_office import FrontOfficeDatasetPublishingService
from services.config import ConfigService
from services.dataset_permissions_service import DatasetPermissionsService
from services.catalogue import CatalogueService
from services.data_dictionary import DataDictionaryService
from services.database_session_manager import DatabaseSessionManager
from services.activity_logs.dataset_activity_log import DatasetActivityLogService
from services.activity_logs.data_dictionary_activity_log import (
    DataDictionaryActivityLogService,
)

logger = logging.getLogger(__name__)


def _create_publishing_service(
    db_session: Session,
) -> FrontOfficeDatasetPublishingService:
    dataset_repo = DatasetRepository(db_session)
    applicable_legislation_repo = ApplicableLegislationRepository(db_session)
    data_service_repo = DataServiceRepository(db_session)
    data_dict_repo = DataDictionaryRepository(db_session)
    activity_log_repo = ActivityLogRepository(db_session)

    dataset_permissions_service = DatasetPermissionsService(dataset_repo)
    config_path = os.getenv("CONFIG_PATH", "./config.json")
    config_service = ConfigService(config_path)
    session_mgr = DatabaseSessionManager(db_session)
    activity_log_service = DatasetActivityLogService(activity_log_repo)
    data_dictionary_activity_log_service = DataDictionaryActivityLogService(
        activity_log_repo
    )

    catalogue_service = CatalogueService(
        dataset_repository=dataset_repo,
        applicable_legislation_repository=applicable_legislation_repo,
        data_service_repository=data_service_repo,
        dataset_permissions_service=dataset_permissions_service,
        config_service=config_service,
    )

    data_dictionary_service = DataDictionaryService(
        repository=data_dict_repo,
        database_session_manager=session_mgr,
        activity_log_service=activity_log_service,
        dataset_permissions_service=dataset_permissions_service,
        data_dictionary_activity_log_service=data_dictionary_activity_log_service,
    )

    return FrontOfficeDatasetPublishingService(
        catalogue_service=catalogue_service,
        data_dictionary_service=data_dictionary_service,
        dataset_repository=dataset_repo,
    )


@celery_app.task(
    bind=True,
    name="jobs.tasks.publish_dataset_to_front_office",
    autoretry_for=(Exception,),
    retry_backoff=True,  # Exponential backoff: 2s, 4s, 8s, etc.
    retry_backoff_max=300,  # Max 5 minutes between retries
    max_retries=3,
    acks_late=True,  # Don't acknowledge until task completes
)
def publish_dataset_to_front_office_task(self: Task, dataset_id: int) -> dict:
    db_session = get_script_db_session()

    logger.info(f"[TASK_START] Publishing dataset {dataset_id} to front office")

    try:
        # Get dataset to retrieve its publisher_id for proper permission context
        dataset_repo = DatasetRepository(db_session)
        dataset = dataset_repo.get_dataset_by_id(dataset_id)

        if not dataset:
            raise HTTPException(
                status_code=404, detail=f"Dataset {dataset_id} not found"
            )

        # Use dataset's publisher_id as the organisation context for permission checks
        identity = IdentityContext(
            user_id=1,
            permissions=[
                "datasets:status-change:publish",
                "datasets:read:all-after-complete",
            ],
            current_organisation_id=dataset.publisher_id,
        )

        publishing_service = _create_publishing_service(db_session)
        result = publishing_service.generate_and_publish_dataset_catalogues(
            dataset_id=dataset_id,
            identity=identity,
        )

        files_count = len(result.files)
        logger.info(f"Dataset {dataset_id} published successfully: {files_count} files")

        # Log any failed file uploads
        failed_files = [f for f in result.files if f.publishing_status != "success"]
        for failed in failed_files:
            logger.warning(
                f"Dataset {dataset_id}: Failed to upload {failed.filename} - {failed.error}"
            )

        logger.info(f"[TASK_SUCCESS] Dataset {dataset_id} published to front office")

        return {
            "status": "success",
            "dataset_id": dataset_id,
            "files_count": files_count,
        }

    except Exception as e:
        # Check if it's a validation error (400-499) that won't be fixed by retrying
        if isinstance(e, HTTPException) and 400 <= e.status_code < 500:
            logger.info(
                f"Dataset {dataset_id} validation error - not retrying: {e.detail}"
            )
            return {
                "status": "failed_validation",
                "dataset_id": dataset_id,
                "error": str(e.detail),
            }

        # For other exceptions (5xx, connection errors, etc.), let Celery retry
        logger.error(f"Publishing dataset {dataset_id} failed: {str(e)}", exc_info=True)
        raise

    finally:
        db_session.close()
