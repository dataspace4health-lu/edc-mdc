import os
from sqlalchemy.orm import Session

from repositories.dataset import DatasetRepository
from repositories.applicable_legislation import ApplicableLegislationRepository
from repositories.data_service import DataServiceRepository
from repositories.data_dictionary import DataDictionaryRepository
from repositories.activity_log import ActivityLogRepository
from services.catalogue import CatalogueService
from services.data_dictionary import DataDictionaryService
from services.front_office import FrontOfficeDatasetPublishingService
from services.config import ConfigService
from services.dataset_permissions_service import DatasetPermissionsService
from services.database_session_manager import DatabaseSessionManager
from services.activity_logs.dataset_activity_log import DatasetActivityLogService
from services.activity_logs.data_dictionary_activity_log import (
    DataDictionaryActivityLogService,
)


def create_front_office_publishing_service(
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
        data_dictionary_repository=data_dict_repo,
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
