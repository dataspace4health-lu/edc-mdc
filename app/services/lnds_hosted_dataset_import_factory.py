import os
from typing import Optional

from sqlalchemy.orm import Session

from repositories.dataset import DatasetRepository
from repositories.distribution import DistributionRepository
from repositories.keyword import KeywordRepository
from repositories.keyword_assignment import KeywordAssignmentRepository
from repositories.applicable_legislation import ApplicableLegislationRepository
from repositories.applicable_legislation_assignment import (
    ApplicableLegislationAssignmentRepository,
)
from repositories.user_assignment import UserAssignmentRepository
from repositories.organisation import OrganisationRepository
from repositories.contact import ContactRepository
from repositories.qualified_attribution import QualifiedAttributionRepository
from repositories.dataset_relation import DatasetRelationRepository
from repositories.activity_log import ActivityLogRepository
from repositories.data_dictionary import DataDictionaryRepository
from services.catalogues.importers.distribution_rdf_mapper import (
    DistributionRDFMapper,
)
from services.catalogues.importers.dataset_rdf_mapper import DatasetRDFMapper
from services.catalogues.importers.qualified_attribution_rdf_mapper import (
    QualifiedAttributionRDFMapper,
)
from services.catalogues.importers.dataset_relation_rdf_mapper import (
    DatasetRelationRDFMapper,
)
from services.catalogues.importers.data_dictionary_rdf_mapper import (
    DataDictionaryRDFMapper,
)
from services.catalogues.importers.dataset_rdf_import_service import (
    DatasetRDFImportService,
)
from services.catalogues.importers.contact_import_service import ContactImportService
from services.contact import ContactService
from services.permissions.contact_permissions import ContactPermissionsService
from services.activity_logs.organisation_activity_log import (
    OrganisationActivityLogService,
)
from services.organisation_cache import OrganisationCache
from services.enun_values import EnumValuesService
from services.distribution import DistributionService
from services.data_dictionary import DataDictionaryService
from services.qualified_attribution import QualifiedAttributionService
from services.dataset_relation import DatasetRelationService
from services.activity_logs.dataset_activity_log import DatasetActivityLogService
from services.activity_logs.data_dictionary_activity_log import (
    DataDictionaryActivityLogService,
)
from services.activity_logs.distribution_activity_log import (
    DistributionActivityLogService,
)
from services.activity_logs.qualifiedAttributionActivityLogService import (
    QualifiedAttributionActivityLogService,
)
from services.dataset_permissions_service import DatasetPermissionsService
from services.dataset import DatasetService
from services.database_session_manager import DatabaseSessionManager
from services.lnds_hosted_dataset_import_service import LNDSHostedDatasetImportService
from services.config import ConfigService
from services.policy_action_manager import PolicyActionManager
from services.form_fields.form_fields_import_service import FormFieldsImportService
from services.form_fields_permission import FormFieldsPermissionsService
from services.activity_log import ActivityLogService
from services.emails.organisation_specific_email import (
    OrganisationSpecificEmailsService,
)
from services.front_office import FrontOfficeDatasetPublishingService
from services.catalogue import CatalogueService
from services.user import UserService
from repositories.user import UserRepository
from services.user_assignment_permissions import UserAssignmentPermissionsService
from services.activity_logs.user_assignment_activity_log import (
    UserAssignmentActivityLogService,
)


def create_lnds_hosted_dataset_import_service(
    db_session: Session,
    source_url: Optional[str] = None,
    source_instance_name: Optional[str] = None,
    page_size: int = 50,
) -> LNDSHostedDatasetImportService:
    # Initialize session manager
    session_mgr = DatabaseSessionManager(db_session)

    # Initialize repositories
    dataset_repo = DatasetRepository(db_session)
    distribution_repo = DistributionRepository(db_session)
    keyword_repo = KeywordRepository(db_session)
    keyword_assignment_repo = KeywordAssignmentRepository(db_session)
    applicable_legislation_repo = ApplicableLegislationRepository(db_session)
    applicable_legislation_assignment_repo = ApplicableLegislationAssignmentRepository(
        db_session
    )
    user_assignment_repo = UserAssignmentRepository(db_session)
    org_repo = OrganisationRepository(db_session)
    contact_repo = ContactRepository(db_session)
    qa_repo = QualifiedAttributionRepository(db_session)
    dr_repo = DatasetRelationRepository(db_session)
    activity_log_repo = ActivityLogRepository(db_session)
    data_dictionary_repo = DataDictionaryRepository(db_session)
    user_repo = UserRepository(db_session)
    qualified_attribution_activity_log_service = QualifiedAttributionActivityLogService(
        activity_log_repo
    )

    distribution_activity_log_service = DistributionActivityLogService(
        activity_log_repo
    )
    # Initialize RDF mappers
    dist_rdf_mapper = DistributionRDFMapper(applicable_legislation_repo)
    dataset_rdf_mapper = DatasetRDFMapper(
        keyword_repo, applicable_legislation_repo, org_repo, dist_rdf_mapper
    )
    qa_rdf_mapper = QualifiedAttributionRDFMapper(org_repo)
    dr_rdf_mapper = DatasetRelationRDFMapper(dataset_repo)
    dd_rdf_mapper = DataDictionaryRDFMapper()

    # Initialize config and permissions
    config_path = os.getenv("CONFIG_PATH", "./config.json")
    config_service = ConfigService(config_path)
    permissions_service = DatasetPermissionsService(dataset_repo)

    # Initialize core services
    enum_service = EnumValuesService(db_session)
    policy_action_manager = PolicyActionManager(distribution_repo)
    dist_service = DistributionService(
        enum_service,
        dataset_repo,
        distribution_repo,
        policy_action_manager,
        permissions_service,
        distribution_activity_log_service,
    )
    activity_log_service = DatasetActivityLogService(activity_log_repo)
    qa_service = QualifiedAttributionService(
        qa_repo,
        session_mgr,
        permissions_service,
        org_repo,
        dataset_repo,
        qualified_attribution_activity_log_service,
    )
    dr_service = DatasetRelationService(
        dr_repo, session_mgr, activity_log_service, permissions_service
    )
    dd_activity_log_service = DataDictionaryActivityLogService(activity_log_repo)
    dd_service = DataDictionaryService(
        data_dictionary_repo,
        session_mgr,
        activity_log_service,
        permissions_service,
        dd_activity_log_service,
    )

    # Initialize dataset service
    dataset_service = DatasetService(
        enum_service,
        dist_service,
        dataset_repo,
        activity_log_service,
        session_mgr,
        org_repo,
        permissions_service,
        contact_repo,
        dd_service,
        qa_service,
        dr_service,
        config_service,
    )

    # Initialize form fields services
    form_fields_permissions_service = FormFieldsPermissionsService(
        keyword_repo,
        keyword_assignment_repo,
        applicable_legislation_repo,
        applicable_legislation_assignment_repo,
        user_assignment_repo,
    )
    form_fields_activity_log_service = ActivityLogService(activity_log_repo)
    email_service = OrganisationSpecificEmailsService(org_repo, contact_repo)
    form_fields_import_service = FormFieldsImportService(
        keyword_repository=keyword_repo,
        keyword_assignment_repository=keyword_assignment_repo,
        dataset_repository=dataset_repo,
        applicable_legislation_repository=applicable_legislation_repo,
        applicable_legislation_assignment_repository=applicable_legislation_assignment_repo,
        distribution_repository=distribution_repo,
        organisation_repository=org_repo,
        form_fields_permissions_service=form_fields_permissions_service,
        activity_log_service=form_fields_activity_log_service,
        email_service=email_service,
    )

    # Initialize contact services
    org_activity_log_service = OrganisationActivityLogService(activity_log_repo)
    contact_permissions_service = ContactPermissionsService(user_assignment_repo)
    org_cache = OrganisationCache(org_repo)
    contact_service = ContactService(
        contact_repo,
        org_activity_log_service,
        org_repo,
        org_cache,
        contact_permissions_service,
    )
    contact_import_service = ContactImportService(contact_service, contact_repo)

    # Initialize RDF import service
    rdf_import_service = DatasetRDFImportService(
        dataset_service,
        dataset_rdf_mapper,
        qa_service,
        qa_rdf_mapper,
        dr_service,
        dr_rdf_mapper,
        form_fields_import_service,
        contact_import_service,
        dd_service,
        dd_rdf_mapper,
        dist_service,
        activity_log_service,
    )

    # Initialize user service for service account management
    user_assignment_permissions_service = UserAssignmentPermissionsService(
        user_assignment_repo,
        org_repo,
        user_repo,
        config_service,
    )
    user_assignment_activity_log_service = UserAssignmentActivityLogService(
        activity_log_repo
    )
    user_service = UserService(
        db_session,
        user_repo,
        user_assignment_repo,
        user_assignment_permissions_service,
        activity_log_repo,
        user_assignment_activity_log_service,
        dataset_repo,
        applicable_legislation_repo,
        keyword_repo,
        config_service,
    )

    # Create and return import service
    return LNDSHostedDatasetImportService(
        dataset_repo,
        rdf_import_service,
        session_mgr,
        activity_log_service,
        user_service,
        config_service,
        source_url,
        source_instance_name,
        page_size,
    )


def create_dataset_rdf_import_service_from_dependencies(
    db_session: Session,
) -> DatasetRDFImportService:
    """
    Factory function for creating DatasetRDFImportService with a database session.
    This mirrors the Celery factory logic and is used by the API routes.
    """
    # Initialize session manager
    session_mgr = DatabaseSessionManager(db_session)

    # Initialize repositories
    dataset_repo = DatasetRepository(db_session)
    distribution_repo = DistributionRepository(db_session)
    keyword_repo = KeywordRepository(db_session)
    keyword_assignment_repo = KeywordAssignmentRepository(db_session)
    applicable_legislation_repo = ApplicableLegislationRepository(db_session)
    applicable_legislation_assignment_repo = ApplicableLegislationAssignmentRepository(
        db_session
    )
    user_assignment_repo = UserAssignmentRepository(db_session)
    org_repo = OrganisationRepository(db_session)
    contact_repo = ContactRepository(db_session)
    qa_repo = QualifiedAttributionRepository(db_session)
    dr_repo = DatasetRelationRepository(db_session)
    activity_log_repo = ActivityLogRepository(db_session)
    data_dictionary_repo = DataDictionaryRepository(db_session)
    user_repo = UserRepository(db_session)
    qualified_attribution_activity_log_service = QualifiedAttributionActivityLogService(
        activity_log_repo
    )
    distribution_activity_log_service = DistributionActivityLogService(
        activity_log_repo
    )

    # Initialize RDF mappers
    dist_rdf_mapper = DistributionRDFMapper(applicable_legislation_repo)
    dataset_rdf_mapper = DatasetRDFMapper(
        keyword_repo, applicable_legislation_repo, org_repo, dist_rdf_mapper
    )
    qa_rdf_mapper = QualifiedAttributionRDFMapper(org_repo)
    dr_rdf_mapper = DatasetRelationRDFMapper(dataset_repo)
    dd_rdf_mapper = DataDictionaryRDFMapper()

    # Initialize config and permissions
    config_path = os.getenv("CONFIG_PATH", "./config.json")
    config_service = ConfigService(config_path)
    permissions_service = DatasetPermissionsService(dataset_repo)

    # Initialize core services
    enum_service = EnumValuesService(db_session)
    policy_action_manager = PolicyActionManager(distribution_repo)
    dist_service = DistributionService(
        enum_service,
        dataset_repo,
        distribution_repo,
        policy_action_manager,
        permissions_service,
        distribution_activity_log_service,
    )
    activity_log_service = DatasetActivityLogService(activity_log_repo)
    qa_service = QualifiedAttributionService(
        qa_repo,
        session_mgr,
        permissions_service,
        org_repo,
        dataset_repo,
        qualified_attribution_activity_log_service,
    )
    dr_service = DatasetRelationService(
        dr_repo, session_mgr, activity_log_service, permissions_service
    )
    dd_activity_log_service = DataDictionaryActivityLogService(activity_log_repo)
    dd_service = DataDictionaryService(
        data_dictionary_repo,
        session_mgr,
        activity_log_service,
        permissions_service,
        dd_activity_log_service,
    )

    # Initialize dataset service
    dataset_service = DatasetService(
        enum_service,
        dist_service,
        dataset_repo,
        activity_log_service,
        session_mgr,
        org_repo,
        permissions_service,
        contact_repo,
        dd_service,
        qa_service,
        dr_service,
        config_service,
    )

    # Initialize form fields services
    form_fields_permissions_service = FormFieldsPermissionsService(
        keyword_repo,
        keyword_assignment_repo,
        applicable_legislation_repo,
        applicable_legislation_assignment_repo,
        user_assignment_repo,
    )
    form_fields_activity_log_service = ActivityLogService(activity_log_repo)
    email_service = OrganisationSpecificEmailsService(org_repo, contact_repo)
    form_fields_import_service = FormFieldsImportService(
        keyword_repository=keyword_repo,
        keyword_assignment_repository=keyword_assignment_repo,
        dataset_repository=dataset_repo,
        applicable_legislation_repository=applicable_legislation_repo,
        applicable_legislation_assignment_repository=applicable_legislation_assignment_repo,
        distribution_repository=distribution_repo,
        organisation_repository=org_repo,
        form_fields_permissions_service=form_fields_permissions_service,
        activity_log_service=form_fields_activity_log_service,
        email_service=email_service,
    )

    # Initialize contact services
    org_activity_log_service = OrganisationActivityLogService(activity_log_repo)
    contact_permissions_service = ContactPermissionsService(user_assignment_repo)
    org_cache = OrganisationCache(org_repo)
    contact_service = ContactService(
        contact_repo,
        org_activity_log_service,
        org_repo,
        org_cache,
        contact_permissions_service,
    )
    contact_import_service = ContactImportService(contact_service, contact_repo)

    # Create and return RDF import service
    return DatasetRDFImportService(
        dataset_service,
        dataset_rdf_mapper,
        qa_service,
        qa_rdf_mapper,
        dr_service,
        dr_rdf_mapper,
        form_fields_import_service,
        contact_import_service,
        dd_service,
        dd_rdf_mapper,
        dist_service,
        activity_log_service,
    )
