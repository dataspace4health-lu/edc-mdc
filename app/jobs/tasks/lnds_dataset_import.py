import logging
import os
from celery import Task
import httpx
from redis import Redis
from redis.exceptions import LockError

from jobs import celery_app
from dependencies.database import get_script_db_session
from services.lnds_hosted_dataset_import_factory import (
    create_lnds_hosted_dataset_import_service,
)

logger = logging.getLogger(__name__)

# Redis client for distributed locking
redis_client = Redis.from_url(
    os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    decode_responses=True,
)


@celery_app.task(
    bind=True,
    name="jobs.tasks.import_lnds_datasets",
    autoretry_for=(httpx.TimeoutException, httpx.ConnectError),
    retry_backoff=True,  # Exponential backoff: 2s, 4s, 8s, etc.
    retry_backoff_max=300,  # Max 5 minutes between retries
    max_retries=3,
    acks_late=True,  # Don't acknowledge until task completes
)
def import_lnds_datasets_task(self: Task, max_pages: int = None) -> dict:
    # P0-1: Distributed lock to prevent concurrent execution
    lock_key = "lnds_dataset_import_lock"
    lock_timeout = 10 * 60  # 10 minutes (matches task_time_limit)

    # Try to acquire lock (atomic operation in Redis)
    lock = redis_client.lock(lock_key, timeout=lock_timeout, blocking=False)

    if not lock.acquire(blocking=False):
        logger.warning("Import task already running (lock held), skipping")
        return {"skipped": True, "reason": "already_running"}

    db_session = get_script_db_session()
    import_service = None

    try:
        # Create import service with dependencies
        import_service = create_lnds_hosted_dataset_import_service(
            db_session=db_session,
        )

        logger.info(
            "Starting LNDS dataset import from %s (source name: %s)",
            import_service.source_instance_url,
            import_service.source_instance_name,
        )

        # Run import
        stats = import_service.import_released_datasets(max_pages=max_pages)

        logger.info(
            f"Import completed: {stats['processed']} processed, "
            f"{stats['created']} created, {stats['updated']} updated, "
            f"{stats['failed']} failed"
        )

        return stats

    except Exception as e:
        logger.error(f"Import failed: {str(e)}", exc_info=True)
        raise  # Let Celery handle retry

    finally:
        # P0-2: Release lock first (before other cleanup)
        try:
            lock.release()
            logger.debug("Released import lock")
        except LockError:
            logger.warning("Lock was already released or expired")

        # Cleanup resources
        if import_service:
            import_service.close()
        db_session.close()
