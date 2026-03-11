import logging
import os
from dotenv import load_dotenv
from celery import Celery
from celery.signals import setup_logging

# Load environment variables
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
if ENVIRONMENT == "development":
    load_dotenv()

# Create Celery app
celery_app = Celery("metadata_capture")

# Load config from jobs/config.py
celery_app.config_from_object("jobs.config")

# Import tasks explicitly to register them
from .tasks import lnds_dataset_import  # noqa
from .tasks import push_to_front_office  # noqa
from .tasks import push_catalogue_to_front_office  # noqa


@setup_logging.connect
def configure_logging(*args, **kwargs):
    log_level = os.getenv("LOG_LEVEL", "INFO")

    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
