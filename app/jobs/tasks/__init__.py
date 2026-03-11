# Import all tasks to ensure they're registered with Celery
from .lnds_dataset_import import import_lnds_datasets_task
from .push_to_front_office import push_dataset_to_front_office_task
from .push_catalogue_to_front_office import push_catalogue_to_front_office_task

__all__ = [
    "import_lnds_datasets_task",
    "push_dataset_to_front_office_task",
    "push_catalogue_to_front_office_task",
]
