import os
from celery.schedules import crontab

# Redis for both broker and results (simple, lightweight)
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

# Reliability settings
task_acks_late = True  # Don't ack until task finishes
task_reject_on_worker_lost = True  # Requeue on worker crash
broker_connection_retry_on_startup = True

# Timeouts
task_time_limit = 10 * 60  # 10 minutes hard limit
task_soft_time_limit = 8 * 60  # 8 minutes warning

# Serialization
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]

# Timezone
timezone = "UTC"
enable_utc = True

# Worker settings
worker_prefetch_multiplier = 1  # Fair distribution for long tasks
worker_max_tasks_per_child = (
    100  # Restart worker after 100 tasks (prevents memory leaks)
)

# Monitoring
task_track_started = True

# Result expiration (prevent Redis bloat)
result_expires = 3600  # Results expire after 1 hour

# ============================================================================
# CELERY BEAT SCHEDULE (Cron-like scheduler)
# ============================================================================

# Get cron schedule from environment variable (default: every 5 minutes)
import_datasets_cron = os.getenv("IMPORT_DATASETS_CRON_SCHEDULE", "*/1")
push_catalogue_cron = os.getenv(
    "PUSH_CATALOGUE_CRON_SCHEDULE", "0 9 * * 1"
)  # Default: every Monday at 09:00


def parse_cron_schedule(schedule: str):
    cron_parts = schedule.split()
    if len(cron_parts) == 1:
        return crontab(minute=cron_parts[0])
    if len(cron_parts) == 5:
        minute, hour, day_of_month, month_of_year, day_of_week = cron_parts
        return crontab(
            minute=minute,
            hour=hour,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
            day_of_week=day_of_week,
        )
    raise ValueError(
        "Invalid cron schedule format. Use minute-only ('*/5') or full cron ('0 9 * * 1')."
    )


beat_schedule = {
    # Import LNDS datasets based on cron schedule
    "import-lnds-datasets": {
        "task": "jobs.tasks.import_lnds_datasets",
        "schedule": parse_cron_schedule(import_datasets_cron),
    },
    # Push catalogue to front office every Monday at 9 AM
    "push-catalogue-to-front-office": {
        "task": "jobs.tasks.push_catalogue_to_front_office",
        "schedule": parse_cron_schedule(push_catalogue_cron),
    },
}
