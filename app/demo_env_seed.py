from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from schemas.organisation import OrganisationDto, ContactDto
from schemas.form_field import ApplicableLegislationFormFieldDto
from models.identity_context import IdentityContext
from services.organisation import OrganisationService
from repositories.organisation import OrganisationRepository
from repositories.activity_log import ActivityLogRepository
from services.activity_log import ActivityLogService
from dependencies.database import get_script_db_session

from repositories.dataset import DatasetRepository
from repositories.distribution import DistributionRepository
from repositories.dataset_relation import DatasetRelationRepository
from repositories.organisation import OrganisationRepository
from repositories.contact import ContactRepository
from repositories.user import UserRepository
from repositories.theme import ThemeRepository
from repositories.keyword import KeywordRepository
from repositories.dataset import DatasetRepository
from repositories.applicable_legislation import ApplicableLegislationRepository
from repositories.keyword_assignment import KeywordAssignmentRepository
from repositories.applicable_legislation_assignment import (
    ApplicableLegislationAssignmentRepository,
)
from services.dataset import DatasetService
from services.dataset_status import DatasetStatusService
from services.distribution import DistributionService
from services.enun_values import EnumValuesService
from services.dataset_permissions_service import DatasetPermissionsService
from services.database_session_manager import DatabaseSessionManager
from services.dataset_status import DatasetStatusService
from services.email_service import EmailService
from services.user import UserService
from services.form_fields_service import FormFieldsService
from services.organisation_cache import OrganisationCache, get_organisation_cache
from services.form_fields_permission import FormFieldsPermissionsService
from schemas.dataset import DatasetDto
from schemas.distribution import DistributionDto
from services.config import ConfigService
from services.user_assignment_permissions import UserAssignmentPermissionsService
from repositories.user_assignment import UserAssignmentRepository
from repositories.data_dictionary import DataDictionaryRepository
from services.data_dictionary import DataDictionaryService
from services.dataset_relation import DatasetRelationService
from services.user_assignment import UserAssignmentService
from services.activity_logs.user_assignment_activity_log import (
    UserAssignmentActivityLogService,
)
from services.activity_logs.data_dictionary_activity_log import (
    DataDictionaryActivityLogService,
)


def initialize_user_service(db_session):
    user_repository = UserRepository(db_session=db_session)
    user_assignment_repository = UserAssignmentRepository(db_session=db_session)
    organisation_repository = OrganisationRepository(db_session=db_session)
    config_service = ConfigService("./config.json")
    user_assignment_permissions_service = UserAssignmentPermissionsService(
        user_assignment_repository=user_assignment_repository,
        user_repository=user_repository,
        organisation_repository=organisation_repository,
    )
    dataset_repository = DatasetRepository(db_session=db_session)
    applicable_legislation_repository = ApplicableLegislationRepository(
        db_session=db_session
    )
    keyword_repository = KeywordRepository(db_session=db_session)
    activity_log_repository = ActivityLogRepository(db_session=db_session)

    user_assignment_activity_log_service = UserAssignmentActivityLogService(
        repository=activity_log_repository
    )

    user_service = UserService(
        db_session=db_session,
        user_repository=user_repository,
        user_assignment_permissions_service=user_assignment_permissions_service,
        user_assignment_repository=user_assignment_repository,
        dataset_repository=dataset_repository,
        applicable_legislation_repository=applicable_legislation_repository,
        keyword_repository=keyword_repository,
        activity_log_repository=activity_log_repository,
        user_assignment_activity_log_service=user_assignment_activity_log_service,
        config_service=config_service,
    )
    return user_service


def add_user(db_session):
    user_service = initialize_user_service(db_session)

    user_service.create_or_find(
        email="carolina.cisterna@lnds.lu",
        name="Carolina Cisterna",
        external_id="66f125f6-a560-4422-b542-776fc63c0b08",
        iam_roles="DATA_MANAGER",
    )


def add_applicable_legislations(db_session):
    keyword_repository = KeywordRepository(db_session=db_session)
    dataset_repository = DatasetRepository(db_session=db_session)
    applicable_legislation_repository = ApplicableLegislationRepository(
        db_session=db_session
    )
    user_assignment_repository = UserAssignmentRepository(db_session=db_session)
    keyword_assignment_repository = KeywordAssignmentRepository(db_session=db_session)
    applicable_legislation_assignment_repository = (
        ApplicableLegislationAssignmentRepository(db_session=db_session)
    )

    form_fields_permissions_service = FormFieldsPermissionsService(
        keyword_repository=keyword_repository,
        applicable_legislation_repository=applicable_legislation_repository,
        user_assignment_repository=user_assignment_repository,
        keyword_assignment_repository=keyword_assignment_repository,
        applicable_legislation_assignment_repository=applicable_legislation_assignment_repository,
    )

    activity_log_repository = ActivityLogRepository(db_session=db_session)
    activity_log_service = ActivityLogService(repository=activity_log_repository)

    form_fields_service = FormFieldsService(
        keyword_repository=keyword_repository,
        dataset_repository=dataset_repository,
        applicable_legislation_repository=applicable_legislation_repository,
        form_fields_permissions_service=form_fields_permissions_service,
        activity_log_service=activity_log_service,
        applicable_legislation_assignment_repository=applicable_legislation_assignment_repository,
    )

    dto = ApplicableLegislationFormFieldDto(
        key="iIétablissements iihospitaliersl",
        eng_label="Article 3 de la loi modifiée du 08 mars 2018",
        description="Les établissements hospitaliers sont tenus de communiquer les données relatives aux infections nosocomiales à la Direction de la santé.",
        link="https://legilux.public.lu/eli/etat/leg/loi/2018/03/08/a222/jo",
        organisation_ids=[],
    )

    identity = IdentityContext(user_id=2, permissions=["form-fields:edit"])

    form_fields_service.create("applicable_legislation", dto, identity)


def initialize_dataset_service(db_session):
    dataset_repository = DatasetRepository(db_session=db_session)
    distribution_repository = DistributionRepository(db_session=db_session)
    dataset_relation_repository = DatasetRelationRepository(db_session=db_session)
    organisation_repository = OrganisationRepository(db_session=db_session)
    contact_repository = ContactRepository(db_session=db_session)

    # Instantiate services
    activity_log_repository = ActivityLogRepository(db_session=db_session)
    activity_log_service = ActivityLogService(repository=activity_log_repository)
    vocabulary_service = EnumValuesService(db_session=db_session)
    distribution_service = DistributionService(
        vocabulary_service=vocabulary_service,
        dataset_repository=dataset_repository,
        distribution_repository=distribution_repository,
    )
    dataset_permissions_service = DatasetPermissionsService(
        dataset_repository=dataset_repository
    )  # Add necessary parameters

    # Manage database sessions
    database_session_manager = DatabaseSessionManager(db_session=db_session)

    data_dictionary_repository = DataDictionaryRepository(db_session=db_session)
    data_dictionary_activity_log_service = DataDictionaryActivityLogService(
        activity_log_repository
    )

    data_dictionary_service = DataDictionaryService(
        repository=data_dictionary_repository,
        database_session_manager=database_session_manager,
        activity_log_service=activity_log_service,
        dataset_permissions_service=dataset_permissions_service,
        data_dictionary_activity_log_service=data_dictionary_activity_log_service,
    )
    dataset_relation_service = DatasetRelationService(
        repository=dataset_relation_repository,
        database_session_manager=database_session_manager,
        activity_log_service=activity_log_service,
        dataset_permissions_service=dataset_permissions_service,
    )

    # Create the DatasetService
    dataset_service = DatasetService(
        vocabulary_service=vocabulary_service,
        distribution_service=distribution_service,
        dataset_repository=dataset_repository,
        dataset_relation_service=dataset_relation_service,
        activity_log_service=activity_log_service,
        database_session_manager=database_session_manager,
        organisation_repository=organisation_repository,
        dataset_permissions_service=dataset_permissions_service,
        contact_repository=contact_repository,
        data_dictionary_service=data_dictionary_service,
    )

    return dataset_service


def create_sample_organisation_with_contacts(db_session):
    # Create repository and service instances
    organisation_repository = OrganisationRepository(db_session=db_session)
    activity_log_repository = ActivityLogRepository(db_session=db_session)
    activity_log_service = ActivityLogService(repository=activity_log_repository)

    # Simulate an identity context (mock user ID for the script)
    identity = IdentityContext(user_id=2, permissions=["organisations:edit"])

    # Initialize the organisation service
    org_service = OrganisationService(
        organisation_repository=organisation_repository,
        organisation_cache=get_organisation_cache(repository=organisation_repository),
        activity_log_service=activity_log_service,
    )

    contacts = [
        ContactDto(
            name="Carolina Cisterna",
            email="carolina.cisterna@lnds.lu",
            role="Contributor",
        ),
        ContactDto(
            name="Danielle Welter", email="danielle.welter@lnds.lu", role="Data Manager"
        ),
    ]

    # Define organisation DTO
    organisation_dto = OrganisationDto(
        name="LNDS", type="Company", email="info@lnds.lu", contacts=contacts
    )

    existing_orgs = org_service.get_organisations()

    if any(org.name == organisation_dto.name for org in existing_orgs):
        print(
            f"Organisation '{organisation_dto.name}' already exists. Skipping creation."
        )
        return next(org for org in existing_orgs if org.name == organisation_dto.name)

    resource_organisation = org_service.create_organisation(organisation_dto, identity)
    return resource_organisation


def create_sample_datasets(db_session, dataset_list):
    dataset_service = initialize_dataset_service(db_session)
    identity = IdentityContext(user_id=2, permissions=["datasets:edit:draft"])

    for dataset_info in dataset_list:
        distribution_dto = DistributionDto(
            title=dataset_info["distribution_title"],
            description=dataset_info["distribution_description"],
            download_urls=[dataset_info["download_urls"]],
            access_urls=[dataset_info["access_url"]],
            file_type=dataset_info["file_type"],
            rights_statement="http://publications.europa.eu/resource/authority/access-right/PUBLIC",
            license=dataset_info["license"],
            languages=frozenset(dataset_info["languages"]),
            internal_only=dataset_info["internal_only"],
            notes="",
            distribution_path="",
            policy_action_type=None,
            policy_constraint_type=None,
            policy_constraint_value=None,
            applicable_legislations=frozenset(),
            availability="",
            documentation="",
            modification_date=None,  # You may need to provide an actual date
            release_date=None,  # You may need to provide an actual date
            linked_schemas=[],
            byte_size=None,
            checksum="",
            media_type="",
            compression_format=None,
            packaging_format=None,
            distribution_dcat_status=None,
            spatial_resolutions=set(),
            temporal_resolution=None,
            access_service_ids=frozenset(),
            spatial_restrictions=frozenset(),
            temporal_restriction_start=None,
            temporal_restriction_end=None,
        )

        dataset_dto = DatasetDto(
            title=dataset_info["title"],
            description=dataset_info["description"],
            contact_ids=dataset_info["contact_ids"],
            publisher_id=dataset_info["publisher_id"],
            time_period_start=date.fromisoformat(dataset_info["time_period_start"]),
            time_period_end=date.fromisoformat(dataset_info["time_period_end"]),
            rights_statement="http://publications.europa.eu/resource/authority/access-right/PUBLIC",
            periodicity="http://publications.europa.eu/resource/authority/frequency/ANNUAL",
            themes=set(dataset_info["themes"]),
            qualified_attributions=set(),
            keywords=set(dataset_info["keywords"]),
            provenance="",
            health_legal_basis=[],
            applicable_legislations=set(),
            spatial_coverages=set(),
            conventions=set(),
            areas_of_work=set(),
            areas_of_competence=set(),
            dataset_types=set(dataset_info["dataset_types"]),
            distributions={distribution_dto},
            creator_ids={dataset_info["creator_id"]},
            status="DRAFT",
            release_date=None,
            modified_at=None,
            deprecated_at=None,
            version=None,
            duration_of_administrative_utility=None,
            max_typical_age=None,
            min_typical_age=None,
            number_of_records=None,
            number_of_unique_individuals=None,
            final_disposition=None,
            notes=None,
            group_managers=set(),
            data_protection_types=set(),
            monitoring_location=None,
            languages=frozenset(dataset_info["languages"]),
            landing_page="",
            documentation="",
            conforms_to=["https://www.w3.org/TR/vocab-dcat/"],
            is_dataset_series=False,
            member_datasets=set(),
            was_generated_by="",
            other_identifiers=set(),
            version_notes="",
            temporal_resolution=None,
        )

        resource_dataset = dataset_service.insert_dataset(dataset_dto, identity)
        print(
            f"Created dataset with ID: {resource_dataset.id}, title: {resource_dataset.title}"
        )


def update_dataset_status(db_session, dataset_id, status_trigger):
    identity = IdentityContext(
        user_id=2,
        permissions=[
            "datasets:status-change:draft",
            "datasets:status-change:complete",
            "datasets:status-change:validate",
            "datasets:status-change:approve",
            "datasets:status-change:publish",
            "datasets:status-change:deprecate",
        ],
    )

    dataset_repository = DatasetRepository(db_session=db_session)
    database_session_manager = DatabaseSessionManager(db_session=db_session)

    activity_log_repository = ActivityLogRepository(db_session=db_session)
    activity_log_service = ActivityLogService(repository=activity_log_repository)

    user_service = initialize_user_service(db_session)
    config_service = ConfigService("./config.json")
    email_service = EmailService(user_service, config_service)
    dataset_permissions_service = DatasetPermissionsService(
        dataset_repository=dataset_repository
    )

    dataset_status_service = DatasetStatusService(
        dataset_id=dataset_id,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        identity=identity,
        email_service=email_service,
        activity_log_service=activity_log_service,
        dataset_permissions_service=dataset_permissions_service,
    )

    dataset_status_service.update_status(status_trigger)


# Example usage:
dataset_list = [
    {
        "title": "Waste shipment inspections",
        "description": """The national and international shipment of waste is subject to specific authorisations and notification procedures.

Regulation (EC) 660/2014 has just strengthened the enforcement and inspection provisions contained in Article 50 of Regulation (EC) 1013/2006. According to paragraph 2a of this article, Member States shall ensure that, by January 1, 2017 at the latest, one or more plans are drawn up for their entire geographical territory, either separately or as a distinct part of other plans, concerning inspections carried out under paragraph 2.

A single plan covering the entire territory of the Grand Duchy of Luxembourg has been drawn up. This plan covers the period from January 1, 2017 to December 31, 2019.

The plan must be reviewed every 3 years. It must also be reviewed:
    - in the event of changes or revisions to waste shipment legislation;
    - during its period of validity, if the need for modification is identified on the basis of the results obtained.

Inspections of waste shipments will be carried out by the Environment Administration in collaboration with the Customs and Excise Administration and, where necessary, the Police Grand-Ducale:
    - at origin, with the producer, holder or notifier;
    - at the point of destination, particularly for intermediate or non-intermediate recovery or disposal operations, with the consignee or facility;
    - during transfer on the various traffic routes or near Luxembourg's entry or exit points.""",
        "contact_ids": [1],
        "publisher_id": 1,
        "dataset_types": {
            "http://publications.europa.eu/resource/authority/dataset-type/STRUCTURED_DATA"
        },
        "time_period_start": "2017-01-01",
        "time_period_end": "2019-12-31",
        "distribution_title": "Results of waste shipment inspections",
        "distribution_description": "Indications on vehicles transporting waste, non-compliant vehicles, nature of offence, and action taken. ",
        "download_urls": "https://environnement.public.lu/fr/emweltprozeduren/Autorisations/Gestion_des_dechets_et_ressources/Transferts_de_dechets/Inspections_en_matiere_de_transferts_de_dechets.html",
        "access_url": "https://environnement.public.lu/fr/emweltprozeduren/Autorisations/Gestion_des_dechets_et_ressources/Transferts_de_dechets/Inspections_en_matiere_de_transferts_de_dechets.html",
        "license": "no_license",
        "languages": {"http://publications.europa.eu/resource/authority/language/FRA"},
        "internal_only": False,
        "file_type": "http://publications.europa.eu/resource/authority/file-type/HTML",
        "themes": {"http://publications.europa.eu/resource/authority/data-theme/ENVI"},
        "qualified_attribution": {1},
        "keywords": {"waste shipment", "inspections", "environment"},
        "creator_id": 1,
    },
    {
        "title": "Synthetic dataset of the Luxembourgish population",
        "description": """The dataset was created from scratch using the open-source code on GitLab [https://gitlab.com/lnds-lu/tooling/synthetic-data-factory] released by LNDS and the real statistics from the STATEC, the statistics portal of Luxembourg . It is meant to be an example of the dataset structure anyone can generate by customizing some parameters, including the sample size. The data are organized by individual profiles on the rows and their personal features on the columns. The age-structure distribution, the number of populations over municipalities, the number of different nationalities present in Luxembourg, the salary statistics per municipality are some of real information we have ingested into our synthetic generation model to generate the dataset. Some other features (Date_of_birth, Social_matricule, First_name and Surname of foreign nationalities) have been obtained by a logical relationship between the variables without exploiting any additional real information.  We are in compliance with the law in reducing and putting close to zero, the reisk of identifying a real person completely by chance.
""",
        "contact_ids": [1],
        "publisher_id": 1,
        "dataset_types": {
            "http://publications.europa.eu/resource/authority/dataset-type/STRUCTURED_DATA"
        },
        "time_period_start": "2023-11-27",
        "time_period_end": "2023-12-31",
        "distribution_title": "Primary distribution of Luxembourg population synthetic dataset with 100000 entries",
        "distribution_description": "CSV file with variables: Gender,  Age,  Date_of_birth, Nationality, Municipality, Canton, Salary, Social_matricule, Ethnicity, Hair_color, Hair_length, First_name and Surname ",
        "download_urls": "https://data.public.lu/fr/datasets/r/ce8f07e5-cba8-4958-a4eb-bc60b41b9c1b",
        "access_url": "https://data.public.lu/fr/datasets/r/ce8f07e5-cba8-4958-a4eb-bc60b41b9c1b",
        "license": "no_license",
        "languages": {"http://publications.europa.eu/resource/authority/language/ENG"},
        "file_type": "http://publications.europa.eu/resource/authority/file-type/CSV",
        "internal_only": False,
        "themes": {"http://publications.europa.eu/resource/authority/data-theme/SOCI"},
        "keywords": {
            "synthetic data",
            "Luxembourgish population structure",
            "Luxembourgish cohort",
            "locations",
        },
        "creator_id": 1,
    },
    {
        "title": "Luxembourg Microdata Platform on Labour and Social Protection Data Dictionary",
        "description": "The IGSS microdata platform dataset can provide a range of data elements that have been transformed and aggregated for statistical purposes. It includes data from CCSS, ADEM, STATEC, CNS, CNAP, FNS, CAE and public pension schemes. Data are sub-divided into a number of thematic areas.",
        "contact_ids": [1],
        "publisher_id": 1,
        "dataset_types": {
            "http://publications.europa.eu/resource/authority/dataset-type/STRUCTURED_DATA"
        },
        "time_period_start": "2023-11-01",
        "time_period_end": "2023-12-31",
        "distribution_title": "Data available via the Luxembourg Microdata Platform on Labour and Social Protection",
        "distribution_description": "Distributions are generated per project with variables selected for that specific project",
        "download_urls": "https://igss.gouvernement.lu/dam-assets/microdata-platform/data-dictionary.pdf",
        "access_url": "https://igss.gouvernement.lu/dam-assets/microdata-platform/data-dictionary.pdf",
        "license": "no_license",
        "languages": {"http://publications.europa.eu/resource/authority/language/ENG"},
        "file_type": "http://publications.europa.eu/resource/authority/file-type/PDF",
        "internal_only": False,
        "themes": {
            "http://publications.europa.eu/resource/authority/data-theme/SOCI",
            "http://publications.europa.eu/resource/authority/data-theme/ECON",
        },
        "keywords": {"salary", "health", "population", "employment"},
        "creator_id": 1,
    },
]


def main():
    db_session = get_script_db_session()  # Establish a database session

    try:
        add_user(db_session)
        resource_organisation = create_sample_organisation_with_contacts(db_session)
        add_applicable_legislations(db_session)
        print(
            f"Organisation '{resource_organisation.name}' with ID {resource_organisation.id} has been created successfully."
        )
        create_sample_datasets(db_session, dataset_list)
        update_dataset_status(db_session, 1, "complete")
        update_dataset_status(db_session, 1, "validate")
        update_dataset_status(db_session, 1, "approve")
        update_dataset_status(db_session, 1, "publish")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db_session.close()


if __name__ == "__main__":
    main()
