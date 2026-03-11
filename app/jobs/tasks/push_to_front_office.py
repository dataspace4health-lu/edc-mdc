import logging
from celery import Task

from jobs import celery_app
from dependencies.database import get_script_db_session
from models.identity_context import IdentityContext
from services.front_office_publishing_factory import (
    create_front_office_publishing_service,
)

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="jobs.tasks.push_dataset_to_front_office",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    max_retries=3,
    acks_late=True,
)
def push_dataset_to_front_office_task(self: Task, dataset_id: int) -> dict:
    db_session = get_script_db_session()

    try:
        publishing_service = create_front_office_publishing_service(db_session)
        dataset = publishing_service._dataset_repository.get_dataset_by_id(dataset_id)

        identity = IdentityContext(
            user_id=1,
            permissions=["datasets:read:all-after-complete"],
            current_organisation_id=dataset.publisher_id,
        )

        result = publishing_service.generate_and_publish_dataset_catalogues(
            dataset_id=dataset_id,
            identity=identity,
        )

        return {
            "status": "success",
            "dataset_id": dataset_id,
            "files_count": len(result.files),
        }

    except Exception as e:
        logger.error(
            f"Pushing dataset {dataset_id} to front office failed: {str(e)}",
            exc_info=True,
        )
        raise

    finally:
        db_session.close()
