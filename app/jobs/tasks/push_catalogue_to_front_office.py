import logging
import os
from celery import Task
from redis import Redis
from redis.exceptions import LockError

from jobs import celery_app
from dependencies.database import get_script_db_session
from repositories.dataset import DatasetRepository
from repositories.applicable_legislation import ApplicableLegislationRepository
from repositories.data_service import DataServiceRepository
from repositories.data_dictionary import DataDictionaryRepository
from services.catalogue import CatalogueService
from services.dataset_permissions_service import DatasetPermissionsService
from services.config import ConfigService
from services.front_office.base import BaseFrontOfficeService
from schemas.catalogue import CatalogueFormat

logger = logging.getLogger(__name__)

redis_client = Redis.from_url(
    os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    decode_responses=True,
)


@celery_app.task(
    bind=True,
    name="jobs.tasks.push_catalogue_to_front_office",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    max_retries=3,
    acks_late=True,
)
def push_catalogue_to_front_office_task(self: Task) -> dict:
    lock_key = "catalogue_push_lock"
    lock_timeout = 10 * 60

    lock = redis_client.lock(lock_key, timeout=lock_timeout, blocking=False)

    if not lock.acquire(blocking=False):
        logger.warning("Catalogue push task already running (lock held), skipping")
        return {"skipped": True, "reason": "already_running"}

    db_session = get_script_db_session()

    try:
        # Initialize repositories
        dataset_repository = DatasetRepository(db_session)
        applicable_legislation_repository = ApplicableLegislationRepository(db_session)
        data_service_repository = DataServiceRepository(db_session)
        data_dictionary_repository = DataDictionaryRepository(db_session)
        config_path = os.getenv("CONFIG_PATH", "./config.json")
        config_service = ConfigService(config_path)

        dataset_permissions_service = DatasetPermissionsService(
            dataset_repository=dataset_repository
        )

        # Initialize CatalogueService
        catalogue_service = CatalogueService(
            dataset_repository=dataset_repository,
            applicable_legislation_repository=applicable_legislation_repository,
            data_service_repository=data_service_repository,
            data_dictionary_repository=data_dictionary_repository,
            dataset_permissions_service=dataset_permissions_service,
            config_service=config_service,
        )

        # Generate catalogue RDF
        logger.info("Generating catalogue RDF (only non-public access datasets)")
        _, rdf_content = catalogue_service.get_catalogue(
            CatalogueFormat.RDF, only_non_public_access=True
        )

        # Initialize FrontOfficeService and publish
        front_office_service = BaseFrontOfficeService()
        logger.info("Pushing catalogue.rdf to front office")

        result = front_office_service.publish_files(
            files_data={CatalogueFormat.RDF: rdf_content},
            base_filename="catalogue",
        )

        logger.info(f"Catalogue push completed: {len(result.files)} file(s) published")

        return {
            "status": "success",
            "timestamp": result.timestamp,
            "files_count": len(result.files),
        }

    except Exception as e:
        logger.error(f"Catalogue push failed: {str(e)}", exc_info=True)
        raise

    finally:
        try:
            lock.release()
            logger.debug("Released catalogue push lock")
        except LockError:
            logger.warning("Lock was already released or expired")

        db_session.close()
