import uuid
from datetime import UTC, date, datetime
from unittest.mock import patch

import pytest
from dependencies.database import Base
from fastapi import Request
from fastapi.testclient import TestClient
from main import app
from models.dataset import (
    Dataset,
    DatasetAreaOfCompetence,
    DatasetAreaOfWork,
    DatasetCodeValue,
    DatasetCodingSystem,
    DatasetConformsTo,
    DatasetContact,
    DatasetConvention,
    DatasetCreator,
    DatasetDataProtectionType,
    DatasetDocumentation,
    DatasetGroupManagers,
    DatasetHealthCategory,
    DatasetHealthTheme,
    DatasetKeyword,
    DatasetLandingPage,
    DatasetLanguage,
    DatasetApplicableLegislation,
    DatasetPersonalData,
    DatasetProvenanceEntry,
    DatasetPurpose,
    DatasetSpatialCoverage,
    DatasetStatus,
    DatasetTheme,
    DatasetType,
    DatasetTypes,
    DatasetVersionNote,
    HealthCategory,
    HealthTheme,
    Keyword,
    SpatialCoverage,
    Theme,
    WasGeneratedBy,
    OtherIdentifier,
    DatasetSpatialResolution,
)
from models.applicable_legislation import ApplicableLegislation
from models.dataset_comment import DatasetComment
from models.dataset_relation import DatasetRelation
from models.qualified_attribution import DatasetQualifiedAttribution
from models.distribution import (
    Distribution,
    DistributionAccessUrl,
    DistributionDownloadUrl,
    DistributionLanguage,
    DistributionApplicableLegislation,
    DistributionDocumentation,
    Language,
    LinkedSchema,
    DistributionPolicyAction,
)
from models.organisation import Contact, Organisation
from models.user import User
from models.keyword_assignment import KeywordAssignment
from models.applicable_legislation_assignment import ApplicableLegislationAssignment
from pydantic_core import Url
from schemas.dataset import DatasetDto, ResourceDataset
from schemas.distribution import DistributionDto, PolicyActionDto, ResourceDistribution
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from services.config import ConfigService
from services.user import UserService
from unittest.mock import MagicMock
from models.identity_context import IdentityContext


@pytest.fixture(scope="function")
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client_with_logged_in_user():
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.iam_roles = ["DATA_MANAGER"]

    with patch.object(
        Request,
        "session",
        {"user_id": 1},
    ) as mock_session:
        client = TestClient(app)
        config_service = ConfigService("./config.json")
        config_service.get_enable_multi_tenants = MagicMock(return_value=False)
        config_service.get_roles_path_in_access_token = MagicMock(
            return_value="resource_access.test.roles"
        )
        app.state.config_service = config_service
        with patch("services.user.UserService.find_by_id", return_value=mock_user):
            yield client


@pytest.fixture
def client_with_logged_in_catalogue_manager_user(db_session):
    cm = db_session.query(User).filter_by(iam_roles="CATALOGUE_MANAGER").first()

    if not cm:
        cm = User(
            name="Catalogue Manager",
            email="cm@example.com",
            iam_roles="CATALOGUE_MANAGER",
            external_id="cm-123",
        )
        db_session.add(cm)
        db_session.commit()

    session_prop = property(lambda self: {"user_id": cm.id})
    with patch.object(Request, "session", session_prop):
        with patch("services.user.UserService.find_by_id", return_value=cm):
            config_service = ConfigService("./config.json")
            config_service.get_enable_multi_tenants = lambda: False
            config_service.get_roles_path_in_access_token = (
                lambda: "resource_access.test.roles"
            )
            app.state.config_service = config_service

            client = TestClient(app)
            yield client


def get_or_create(session, model, **kwargs):
    """Helper function to get or create a database record."""
    instance = session.query(model).filter_by(**kwargs).first()
    if not instance:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
    return instance


def get_sample_organisation(db_session: Session) -> Organisation:
    if db_session.query(Organisation).count() > 0:
        return db_session.query(Organisation).first()

    contact1 = Contact(
        name="John Doe",
        email="john.doe@example.com",
        role="Manager",
        is_deprecated=False,
    )
    contact2 = Contact(
        name="Jane Smith",
        email="jane.smith@example.com",
        role="Director",
        is_deprecated=False,
    )

    organisation = Organisation(
        id=1,
        name="Sample Organisation",
        email="contact@organisation.com",
        type="Company",
        is_deprecated=False,
        contacts=[contact1, contact2],
    )
    db_session.add(organisation)
    db_session.commit()
    return organisation


def get_sample_contact(db_session: Session, organisation_id=None) -> Contact:
    if organisation_id is None:
        organisation = get_sample_organisation(db_session)
        organisation_id = organisation.id

    contact = (
        db_session.query(Contact).filter_by(organisation_id=organisation_id).first()
    )
    if contact:
        return contact

    contact = Contact(
        name="John Doe",
        email=f"john.doe.{uuid.uuid4()}@example.com",
        role="Manager",
        organisation_id=organisation_id,
    )
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)
    return contact


@pytest.fixture
def sample_organisation(db_session: Session) -> Organisation:
    return get_sample_organisation(db_session)


@pytest.fixture
def sample_contact(db_session: Session) -> Contact:
    return get_sample_contact(db_session)


@pytest.fixture
def sample_contributor(db_session: Session) -> User:
    user = User(
        name="contributor",
        email="contributor@lnds.lu",
        iam_roles="CONTRIBUTOR",
        external_id=str(uuid.uuid4()),
    )
    db_session.add(user)
    return user


@pytest.fixture
def sample_comment(db_session: Session) -> DatasetComment:
    comment = DatasetComment(
        user_id=1,
        dataset_id=1,
        content="Great data!",
    )
    db_session.add(comment)
    return comment


@pytest.fixture
def sample_dataset(db_session: Session) -> Dataset:
    sample_org = get_sample_organisation(db_session)
    sample_contact = get_sample_contact(db_session)
    theme1 = get_or_create(db_session, Theme, key="ENV", eng_label="Environment")
    keyword1 = get_or_create(
        db_session,
        Keyword,
        key="security",
        eng_label="Security",
        parent_key="People",
    )
    applicable_legislation1 = get_or_create(
        db_session,
        ApplicableLegislation,
        key="GDPR",
        eng_label="GDPR",
        description="General Data Protection Regulation",
        link="https://eur-lex.europa.eu/eli/reg",
    )
    existing_kw_assignment = (
        db_session.query(KeywordAssignment)
        .filter_by(keyword_key=keyword1.key, organisation_id=sample_org.id)
        .first()
    )

    if not existing_kw_assignment:
        db_session.add(
            KeywordAssignment(
                keyword_key=keyword1.key,
                organisation_id=sample_org.id,
            )
        )
    existing_lb_assignment = (
        db_session.query(ApplicableLegislationAssignment)
        .filter_by(
            applicable_legislation_key=applicable_legislation1.key,
            organisation_id=sample_org.id,
        )
        .first()
    )

    if not existing_lb_assignment:
        db_session.add(
            ApplicableLegislationAssignment(
                applicable_legislation_key=applicable_legislation1.key,
                organisation_id=sample_org.id,
            )
        )
    spatial_coverage1 = get_or_create(
        db_session, SpatialCoverage, key="LUX", eng_label="Luxembourg"
    )
    language1 = get_or_create(db_session, Language, key="SAN", eng_label="Sanskrit")
    dataset_type1 = get_or_create(
        db_session, DatasetType, key="REPORTING", eng_label="REPORTING_OBLIGATION"
    )
    health_category1 = get_or_create(
        db_session, HealthCategory, key="EHRS", eng_label="EHRS"
    )
    health_theme1 = get_or_create(
        db_session, HealthTheme, key="CLIMATE_HEALTH", eng_label="Climate Health"
    )
    dataset_theme = DatasetTheme(key=theme1.key, value=theme1)
    dataset_keyword = DatasetKeyword(key=keyword1.key, value=keyword1)
    dataset_health_category = DatasetHealthCategory(
        key=health_category1.key, value=health_category1
    )
    dataset_health_theme = DatasetHealthTheme(
        key=health_theme1.key, value=health_theme1
    )
    dataset_spatial_coverage = DatasetSpatialCoverage(
        key=spatial_coverage1.key, value=spatial_coverage1
    )
    dataset_conventions = DatasetConvention(key="banana")
    dataset_data_protection_types = DatasetDataProtectionType(
        key="commercial_confidentiality"
    )
    dataset_areas_of_work = DatasetAreaOfWork(key="monitoring")
    dataset_areas_of_competence = DatasetAreaOfCompetence(key="bruit")
    distribution_language = DistributionLanguage(key=language1.key, value=language1)
    dataset_types = DatasetTypes(key=dataset_type1.key, value=dataset_type1)
    dataset_applicable_legislation = DatasetApplicableLegislation(
        key=applicable_legislation1.key
    )
    distribution_applicable_legislation1 = DistributionApplicableLegislation(key="GDPR")
    distribution_applicable_legislation2 = DistributionApplicableLegislation(key="GDPR")
    group_manager1 = get_or_create(
        db_session,
        User,
        name="group_manager_1",
        email="group_manager1@email.com",
        iam_roles="GROUP_MANAGER",
        external_id=str(uuid.uuid4()),
    )
    dataset_group_manager1 = DatasetGroupManagers(user=group_manager1)
    dataset_language = DatasetLanguage(key=language1.key, value=language1)
    landing_page_url = "https://example.com/landing_page"
    dataset_doc_url = "https://example.com/dataset_document"
    dataset_purpose = "Research and public health monitoring"
    distribution_doc_url = "https://example.com/distribution_document"
    conforms_to = DatasetConformsTo(key="https://example.com/conforms_to")
    was_generated_by = WasGeneratedBy(key="id-1")
    linked_schemas = LinkedSchema(key="dcat")
    other_identifiers = OtherIdentifier(key="id-1")
    temporal_resolution = "P10D"
    dataset_coding_systems = DatasetCodingSystem(
        value="https://www.wikidata.org/entity/Q9006342"
    )
    dataset_code_values = DatasetCodeValue(value="ICD-10 Codes")
    personal_data = DatasetPersonalData(key="Age")

    distribution1 = Distribution(
        title="Sample Distribution 1",
        description="Sample Description 1",
        download_urls=[DistributionDownloadUrl(url="https://example.com")],
        access_urls=[DistributionAccessUrl(url="https://example.com")],
        file_type="CSV",
        rights_statement="NO_LIMITATIONS_TO_PUBLIC_ACCESS",
        license="no_license",
        languages={distribution_language},
        internal_only=True,
        applicable_legislations={distribution_applicable_legislation1},
        distribution_path="INSIPRE",
        availability="Stable",
        documentation_entries=[DistributionDocumentation(value=distribution_doc_url)],
        release_date=date(2023, 12, 31),
        modification_date=date(2023, 12, 31),
        linked_schemas=[linked_schemas],
        byte_size=10,
        checksum="test",
        policy_type="odrl:Set",
        media_type="application/elm+xml",
        compression_format="text/turtle",
        packaging_format="text/csv",
        created_at=datetime(2024, 2, 29, 12, 0),
        distribution_dcat_status="Completed",
        spatial_resolution=1,
        temporal_resolution="PT1H",
        access_services=set(),
    )

    policy_action1 = DistributionPolicyAction(
        policy_action_type="permission",
        policy_constraint_type="purpose",
        policy_constraint_value="DUO:0000006",
        temporal_restriction_start=None,
        temporal_restriction_end=None,
        spatial_restrictions=set(),
    )
    distribution1.policy_actions = {policy_action1}

    distribution2 = Distribution(
        title="Sample Distribution 2",
        description="Sample Description 2",
        download_urls=[DistributionDownloadUrl(url="https://example.com")],
        access_urls=[DistributionAccessUrl(url="https://example.com")],
        file_type="JSON",
        rights_statement="NO_LIMITATIONS_TO_PUBLIC_ACCESS",
        license="no_license",
        languages={distribution_language},
        internal_only=False,
        applicable_legislations={distribution_applicable_legislation2},
        distribution_path="INSIPRE",
        availability="Stable",
        documentation_entries=[DistributionDocumentation(value=distribution_doc_url)],
        release_date=date(2023, 12, 31),
        modification_date=date(2023, 12, 31),
        linked_schemas=[linked_schemas],
        byte_size=10,
        checksum="test",
        policy_type="odrl:Set",
        media_type="application/elm+xml",
        compression_format="text/turtle",
        packaging_format="text/csv",
        created_at=datetime(2024, 2, 29, 12, 0),
        distribution_dcat_status="Completed",
        spatial_resolution=1,
        temporal_resolution="PT1H",
        access_services=set(),
    )

    policy_action2 = DistributionPolicyAction(
        policy_action_type="permission",
        policy_constraint_type="temporal",
        policy_constraint_value=None,
        temporal_restriction_start=date(2023, 1, 1),
        temporal_restriction_end=date(2023, 12, 31),
        spatial_restrictions=set(),
    )
    distribution2.policy_actions = {policy_action2}

    dataset_contact = DatasetContact(contact_id=sample_contact.id)

    dataset = Dataset(
        title="Sample Dataset",
        description="Sample dataset description",
        publisher_id=sample_org.id,
        submitted_at=datetime(2024, 2, 29, 12, 0),
        release_date=date(2022, 12, 31),
        modified_at=date(2022, 12, 31),
        deprecated_at=date(2022, 12, 31),
        time_period_start=date(2024, 3, 1),
        time_period_end=date(2025, 2, 28),
        rights_statement="PUBLIC",
        periodicity="ANNUALLY",
        dataset_types={dataset_types},
        themes={dataset_theme},
        keywords={dataset_keyword},
        health_categories={dataset_health_category},
        health_themes={dataset_health_theme},
        spatial_coverages={dataset_spatial_coverage},
        conventions={dataset_conventions},
        areas_of_work={dataset_areas_of_work},
        areas_of_competence={dataset_areas_of_competence},
        applicable_legislations={dataset_applicable_legislation},
        notes="",
        version="0.0.0",
        duration_of_administrative_utility=0,
        max_typical_age=0,
        min_typical_age=0,
        number_of_records=0,
        number_of_unique_individuals=0,
        final_disposition="Archive",
        identifier=str(uuid.uuid1()),
        distributions={distribution1, distribution2},
        user_id=1,
        status=DatasetStatus.DRAFT.value,
        group_managers={dataset_group_manager1},
        data_protection_types={dataset_data_protection_types},
        monitoring_location="Luxembourg",
        population_coverage="Adults aged 18-65 in Luxembourg",
        coding_systems=[dataset_coding_systems],
        code_values=[dataset_code_values],
        languages={dataset_language},
        conforms_to_values=[],
        was_generated_by={was_generated_by},
        other_identifiers={other_identifiers},
        temporal_resolution=temporal_resolution,
        contacts={dataset_contact},
        personal_data=[personal_data],
    )

    # Add creators using the junction table
    dataset_creator = DatasetCreator(dataset=dataset, organisation_id=sample_org.id)
    dataset.creators = {dataset_creator}

    dataset_purpose_entry = DatasetPurpose(dataset=dataset, value=dataset_purpose)
    dataset.purpose_entries = {dataset_purpose_entry}

    # Add provenance entries using the junction table
    provenance_entry = DatasetProvenanceEntry(dataset=dataset, value="Official records")
    dataset.provenance_entries = [provenance_entry]

    # Add version notes using the junction table
    version_note = DatasetVersionNote(dataset=dataset, value="note-1")
    dataset.version_notes = [version_note]

    db_session.add(dataset)
    db_session.commit()

    # Ensure deterministic single entries for ordered list relations
    dataset.code_values.clear()
    dataset.landing_pages.clear()
    dataset.documentation_entries.clear()
    dataset.conforms_to_values.clear()
    dataset.code_values.append(
        DatasetCodeValue(dataset_id=dataset.id, value="ICD-10 Codes")
    )
    dataset.landing_pages.append(
        DatasetLandingPage(dataset_id=dataset.id, url=landing_page_url)
    )
    dataset.documentation_entries.append(
        DatasetDocumentation(dataset_id=dataset.id, value=dataset_doc_url)
    )
    dataset.conforms_to_values.append(
        DatasetConformsTo(dataset_id=dataset.id, key="https://example.com/conforms_to")
    )
    db_session.commit()

    # Add spatial resolutions after dataset has an ID
    dataset_spatial_resolution = DatasetSpatialResolution(
        dataset_id=dataset.id, value=1
    )
    db_session.add(dataset_spatial_resolution)
    dataset.spatial_resolutions = [dataset_spatial_resolution]
    db_session.commit()

    return dataset


@pytest.fixture
def sample_dataset_with_relation(
    db_session: Session, sample_dataset: Dataset
) -> Dataset:
    related_contacts = {
        DatasetContact(contact_id=dc.contact_id) for dc in sample_dataset.contacts
    }

    # Create a related dataset
    related_dataset = Dataset(
        title="Related Dataset",
        status=DatasetStatus.INTERNAL_ONLY.value,
        description="A dataset related to the sample dataset",
        contacts=related_contacts,
        publisher_id=sample_dataset.publisher_id,
        submitted_at=datetime(2024, 3, 1, 12, 0),
        release_date=date(2022, 12, 31),
        modified_at=date(2022, 12, 31),
        deprecated_at=date(2022, 12, 31),
        time_period_start=date(2024, 4, 1),
        time_period_end=date(2025, 3, 31),
        rights_statement="PUBLIC",
        periodicity="ANNUALLY",
        dataset_types=sample_dataset.dataset_types,
        themes=sample_dataset.themes,
        keywords=sample_dataset.keywords,
        spatial_coverages=sample_dataset.spatial_coverages,
        conventions=sample_dataset.conventions,
        areas_of_work=sample_dataset.areas_of_work,
        areas_of_competence=sample_dataset.areas_of_competence,
        applicable_legislations=sample_dataset.applicable_legislations,
        notes="",
        version="0.0.0",
        duration_of_administrative_utility=0,
        max_typical_age=0,
        min_typical_age=0,
        number_of_records=0,
        number_of_unique_individuals=0,
        final_disposition="Archive",
        distributions=set(),
        group_managers=sample_dataset.group_managers,
        identifier=str(uuid.uuid1()),
        data_protection_types=sample_dataset.data_protection_types,
        monitoring_location="Luxembourg",
        population_coverage="Adults aged 18-65 in Luxembourg",
        languages=sample_dataset.languages,
        coding_systems=sample_dataset.coding_systems,
    )

    # Copy creators from sample_dataset
    related_dataset.creators = {
        DatasetCreator(dataset=related_dataset, organisation_id=creator.organisation_id)
        for creator in sample_dataset.creators
    }

    # Copy landing pages from sample_dataset
    related_dataset.landing_pages = [
        DatasetLandingPage(url=landing_page.url)
        for landing_page in sample_dataset.landing_pages
    ]

    # Copy documentation from sample_dataset
    related_dataset.documentation_entries = [
        DatasetDocumentation(value=doc.value)
        for doc in sample_dataset.documentation_entries
    ]
    related_dataset.purpose_entries = {
        DatasetPurpose(dataset=related_dataset, value=purpose.value)
        for purpose in sample_dataset.purpose_entries
    }

    # Add provenance entries
    related_dataset.provenance_entries = [
        DatasetProvenanceEntry(dataset=related_dataset, value="Official records")
    ]

    # Add version notes
    related_dataset.version_notes = [
        DatasetVersionNote(dataset=related_dataset, value="note-1")
    ]

    db_session.add(related_dataset)
    db_session.flush()

    relation = DatasetRelation(
        source_dataset=sample_dataset.id,
        target_dataset=related_dataset.id,
        relation_type="dct:isPartOf",
    )
    db_session.add(relation)
    db_session.commit()

    return sample_dataset


@pytest.fixture
def sample_dataset_with_external_relation(
    db_session: Session, sample_dataset: Dataset
) -> Dataset:
    external_relation = DatasetRelation(
        source_dataset=sample_dataset.id,
        external_url="https://example.com/documentation",
        external_role="describedby",
        external_description="Official documentation for this dataset",
    )
    db_session.add(external_relation)
    db_session.commit()

    return sample_dataset


@pytest.fixture
def dataset_dto(sample_dataset) -> DatasetDto:
    """Fixture to create a sample dataset DTO."""
    return DatasetDto(
        status=DatasetStatus.DRAFT.value,
        title="title",
        description="description",
        contact_ids=(
            {dc.contact_id for dc in sample_dataset.contacts}
            if sample_dataset.contacts
            else None
        ),
        publisher_id=sample_dataset.publisher_id,
        time_period_start=date(2024, 3, 1),
        time_period_end=date(2025, 2, 28),
        retention_period_start=date(2023, 1, 1),
        retention_period_end=date(2025, 12, 31),
        rights_statement="PUBLIC",
        periodicity="ANNUAL",
        dataset_types={"http://purl.obolibrary.org/obo/T4FS_0000109"},  # NOSONAR
        release_date=date(2022, 12, 31),
        modified_at=date(2022, 12, 31),
        deprecated_at=date(2022, 12, 31),
        released_at=None,
        themes={"ENVIRONMENT"},
        keywords={"WASTE_MANAGEMENT"},
        health_categories={"EHRS"},
        health_themes={"CLIMATE_HEALTH"},
        spatial_coverages={"LUXEMBOURG"},
        conventions={"banana"},
        areas_of_work={"monitoring"},
        areas_of_competence={"bruit"},
        applicable_legislations={"GDPR"},
        notes="notes",
        duration_of_administrative_utility=0,
        max_typical_age=0,
        min_typical_age=0,
        number_of_records=0,
        number_of_unique_individuals=0,
        final_disposition="Archive",
        version="0.0.0",
        version_change_type=None,
        creator_ids={creator.organisation_id for creator in sample_dataset.creators},
        group_managers={gm.user.id for gm in sample_dataset.group_managers},
        data_protection_types={"commercial_confidentiality"},
        monitoring_location="Luxembourg",
        provenance=["Official records"],
        health_legal_basis=[],
        population_coverage="Adults aged 18-65 in Luxembourg",
        languages=frozenset(["ENG"]),
        conforms_to=["https://example.com/conforms_to"],
        landing_pages=["https://example.com/landing_page"],
        documentation=["https://example.com/dataset_document"],
        purpose={"Research and public health monitoring"},
        is_dataset_series=False,
        member_datasets=[],
        was_generated_by=[],
        other_identifiers=[],
        version_notes=["note-1"],
        spatial_resolutions=[1],
        temporal_resolution="P1D",
        code_values={"ICD-10 Codes"},
        coding_systems={"https://www.wikidata.org/entity/Q9006342"},
        source=None,
        source_dataset_id=None,
        personal_data=["Age"],
        distributions=[
            DistributionDto(
                title="distribution_title",
                description="distribution_description",
                download_urls=["https://example.com/download_urls"],
                access_urls=["https://example.com/access_url"],
                file_type="OTHER",
                rights_statement="PUBLIC",
                license="no_license",
                languages=frozenset(["ENG"]),
                internal_only=True,
                applicable_legislations=["GDPR"],
                notes="notes",
                distribution_path="INSIPRE",
                availability="Stable",
                documentation=["https://example.com/distribution_document"],
                release_date=date(2023, 12, 31),
                modification_date=date(2023, 12, 31),
                linked_schemas=["DCAT-AP"],
                byte_size=10,
                checksum="test",
                policy_actions=[
                    PolicyActionDto(
                        policy_action_type="permission",
                        policy_constraint_type="purpose",
                        policy_constraint_value="DUO:0000006",
                        temporal_restriction_start=None,
                        temporal_restriction_end=None,
                        spatial_restrictions=[],
                    )
                ],
                media_type="application/elm+xml",
                compression_format="application/merge-patch+json",
                packaging_format="text/plain",
                distribution_dcat_status="Completed",
                spatial_resolution=1,
                temporal_resolution="PT1H",
                access_service_ids=frozenset(),
            )
        ],
    )


@pytest.fixture
def default_dataset_json(sample_dataset):
    return {
        "title": "Test Title",
        "description": "Test Description",
        "contact_ids": (
            [dc.contact_id for dc in sample_dataset.contacts]
            if sample_dataset.contacts
            else []
        ),
        "publisher_id": sample_dataset.publisher_id,
        "time_period_start": "2024-02-27",
        "time_period_end": "2024-02-27",
        "retention_period_start": "2023-01-01",
        "retention_period_end": "2025-12-31",
        "dataset_types": ["REPORTING"],
        "rights_statement": "http://publications.europa.eu/resource/authority/access-right/PUBLIC",
        "periodicity": "http://publications.europa.eu/resource/authority/frequency/UNKNOWN",
        "themes": ["http://publications.europa.eu/resource/authority/data-theme/ENVI"],
        "keywords": ["security"],
        "health_categories": ["EHRS"],
        "health_themes": ["CLIMATE_HEALTH"],
        "spatial_coverages": [
            "http://publications.europa.eu/resource/authority/country/LUX"
        ],
        "conventions": ["banana"],
        "areas_of_work": ["monitoring"],
        "areas_of_competence": ["bruit"],
        "applicable_legislations": ["GDPR"],
        "notes": None,
        "version": "0.0.0",
        "version_change_type": None,
        "duration_of_administrative_utility": 0,
        "max_typical_age": 0,
        "min_typical_age": 0,
        "number_of_records": 0,
        "number_of_unique_individuals": 0,
        "final_disposition": "Archive",
        "creator_ids": [creator.organisation_id for creator in sample_dataset.creators],
        "modified_at": "2022-12-31",
        "deprecated_at": "2022-12-31T00:00:00",
        "release_date": "2022-12-31",
        "identifier": sample_dataset.identifier,
        "group_managers_ids": [gm.user.id for gm in sample_dataset.group_managers],
        "group_manager_names": [gm.user.name for gm in sample_dataset.group_managers],
        "data_protection_types": ["commercial_confidentiality"],
        "monitoring_location": "Luxembourg",
        "provenance": ["Official records"],
        "health_legal_basis": [],
        "population_coverage": "Adults aged 18-65 in Luxembourg",
        "code_values": [],
        "coding_systems": ["https://www.wikidata.org/entity/Q9006342"],
        "languages": ["http://publications.europa.eu/resource/authority/language/ENG"],
        "landing_pages": ["https://example.com/landing_page"],
        "documentation": ["https://example.com/dataset_document"],
        "purpose": ["Research and public health monitoring"],
        "conforms_to": ["https://example.com/conforms_to"],
        "is_dataset_series": False,
        "member_datasets": [],
        "was_generated_by": [],
        "other_identifiers": [],
        "version_notes": ["note-1"],
        "spatial_resolutions": [1],
        "temporal_resolution": "P1D",
        "personal_data": ["Age"],
        "distributions": [
            {
                "languages": [
                    "http://publications.europa.eu/resource/authority/language/ENG"
                ],
                "title": "Test Distribution Title",
                "description": "Test Distribution Description",
                "download_urls": ["https://example.com/"],
                "access_urls": ["https://example.com/"],
                "file_type": "http://publications.europa.eu/resource/authority/file-type/PDF",
                "rights_statement": "http://publications.europa.eu/resource/authority/access-right/PUBLIC",
                "internal_only": True,
                "applicable_legislations": ["GDPR"],
                "notes": None,
                "license": "no_license",
                "distribution_path": "INSIPRE",
                "availability": "Stable",
                "documentation": ["https://example.com/distribution_document"],
                "release_date": "2023-12-31",
                "modification_date": "2023-12-31",
                "byte_size": 10,
                "checksum": "test",
                "policy_actions": [
                    {
                        "policy_action_type": "permission",
                        "policy_constraint_type": "purpose",
                        "policy_constraint_value": "DUO:0000006",
                        "temporal_restriction_start": None,
                        "temporal_restriction_end": None,
                        "spatial_restrictions": [],
                    }
                ],
                "linked_schemas": ["DCAT-AP"],
                "media_type": "application/elm+xml",
                "compression_format": "application/zip",
                "packaging_format": "text/csv",
                "distribution_dcat_status": "Completed",
                "spatial_resolution": 1,
                "temporal_resolution": "PT1H",
                "access_service_ids": [],
            }
        ],
    }


@pytest.fixture
def default_expected_json(sample_dataset):
    return {
        "status": DatasetStatus.DRAFT.value,
        "comments_count": 0,
        "author_name": "group_manager_1",
        "status_triggers": [],
        "title": "Test Title",
        "description": "Test Description",
        "contact_ids": (
            [dc.contact_id for dc in sample_dataset.contacts]
            if sample_dataset.contacts
            else []
        ),
        "contact_names": (
            [dc.contact.name for dc in sample_dataset.contacts if dc.contact]
            if sample_dataset.contacts
            else []
        ),
        "contact_emails": (
            [dc.contact.email for dc in sample_dataset.contacts if dc.contact]
            if sample_dataset.contacts
            else []
        ),
        "publisher_id": sample_dataset.publisher_id,
        "publisher_name": "Sample Organisation",
        "time_period_start": "2024-02-27",
        "time_period_end": "2024-02-27",
        "retention_period_start": "2023-01-01",
        "retention_period_end": "2025-12-31",
        "modified_at": "2022-12-31",
        "deprecated_at": "2022-12-31T00:00:00",
        "release_date": "2022-12-31",
        "authentic_source_reviewed_at": None,
        "dataset_types": [
            {
                "value": "REPORTING",
                "eng_label": "REPORTING_OBLIGATION",
            }
        ],
        "rights_statement": "http://publications.europa.eu/resource/authority/access-right/PUBLIC",
        "periodicity": {
            "value": "http://publications.europa.eu/resource/authority/frequency/UNKNOWN",
            "eng_label": "unknown",
        },
        "themes": [
            {
                "value": "http://publications.europa.eu/resource/authority/data-theme/ENVI",
                "eng_label": "Environment",
            }
        ],
        "keywords": [
            {"value": "security", "eng_label": "Security", "parent_value": "People"}
        ],
        "health_categories": [{"value": "EHRS", "eng_label": "EHRS"}],
        "health_themes": [{"value": "CLIMATE_HEALTH", "eng_label": "Climate Health"}],
        "spatial_coverages": [
            {
                "value": "http://publications.europa.eu/resource/authority/country/LUX",
                "eng_label": "Luxembourg",
            }
        ],
        "applicable_legislations": ["GDPR"],
        "conventions": ["banana"],
        "areas_of_work": ["monitoring"],
        "areas_of_competence": ["bruit"],
        "notes": None,
        "version": "0.0.0",
        "version_change_type": None,
        "duration_of_administrative_utility": 0,
        "max_typical_age": 0,
        "min_typical_age": 0,
        "number_of_records": 0,
        "number_of_unique_individuals": 0,
        "is_any_dictionary_authentic_source": False,
        "total_dictionaries": 0,
        "final_disposition": "Archive",
        "creator_ids": [creator.organisation_id for creator in sample_dataset.creators],
        "creator_names": ["Sample Organisation"],
        "identifier": str(uuid.uuid1()),
        "source": None,
        "source_dataset_id": None,
        "group_managers_ids": [gm.user.id for gm in sample_dataset.group_managers],
        "group_manager_names": [gm.user.name for gm in sample_dataset.group_managers],
        "data_protection_types": ["commercial_confidentiality"],
        "monitoring_location": "Luxembourg",
        "provenance": ["Official records"],
        "health_legal_basis": [],
        "population_coverage": "Adults aged 18-65 in Luxembourg",
        "code_values": [],
        "coding_systems": ["https://www.wikidata.org/entity/Q9006342"],
        "languages": [
            {
                "value": "http://publications.europa.eu/resource/authority/language/ENG",
                "eng_label": "English",
            }
        ],
        "landing_pages": ["https://example.com/landing_page"],
        "documentation": ["https://example.com/dataset_document"],
        "purpose": ["Research and public health monitoring"],
        "conforms_to": ["https://example.com/conforms_to"],
        "is_dataset_series": False,
        "member_datasets": None,
        "series_memberships": None,
        "was_generated_by": [],
        "other_identifiers": [],
        "version_notes": ["note-1"],
        "spatial_resolutions": [1],
        "temporal_resolution": "P1D",
        "personal_data": ["Age"],
        "distributions": [
            {
                "title": "Test Distribution Title",
                "description": "Test Distribution Description",
                "download_urls": ["https://example.com/"],
                "access_urls": ["https://example.com/"],
                "file_type": {
                    "value": "http://publications.europa.eu/resource/authority/file-type/PDF",
                    "eng_label": "PDF",
                },
                "rights_statement": "http://publications.europa.eu/resource/authority/access-right/PUBLIC",
                "internal_only": True,
                "is_analytics": False,
                "applicable_legislations": ["GDPR"],
                "languages": [
                    {
                        "value": "http://publications.europa.eu/resource/authority/language/ENG",
                        "eng_label": "English",
                    }
                ],
                "notes": None,
                "license": {"value": "no_license", "eng_label": "No License"},
                "distribution_path": "INSIPRE",
                "availability": "Stable",
                "documentation": ["https://example.com/distribution_document"],
                "release_date": "2023-12-31",
                "modification_date": "2023-12-31",
                "byte_size": 10,
                "checksum": "test",
                "policy_actions": [
                    {
                        "policy_action_type": "permission",
                        "policy_constraint_type": "purpose",
                        "policy_constraint_value": "DUO:0000006",
                        "temporal_restriction_start": None,
                        "temporal_restriction_end": None,
                        "spatial_restrictions": [],
                    }
                ],
                "linked_schemas": ["DCAT-AP"],
                "media_type": "application/elm+xml",
                "compression_format": "application/zip",
                "packaging_format": "text/csv",
                "distribution_dcat_status": "Completed",
                "spatial_resolution": 1,
                "temporal_resolution": "PT1H",
                "access_service_ids": [],
            }
        ],
    }


@pytest.fixture
def default_organisation_json():
    unique_id = uuid.uuid4().hex
    return {
        "name": f"Organisation-{unique_id}",
        "email": f"contact-{unique_id}@organisation.com",
        "type": "Company",
        "is_deprecated": False,
        "contacts": [
            {
                "name": "John Doe",
                "email": f"john.doe-{unique_id}@example.com",
                "role": "Manager",
            },
            {
                "name": "Jane Smith",
                "email": f"jane.smith-{unique_id}@example.com",
                "role": "Director",
            },
        ],
    }


@pytest.fixture
def default_organisation_expected_json(sample_organisation):
    return {
        "id": sample_organisation.id,
        "name": sample_organisation.name,
        "email": sample_organisation.email,
        "type": sample_organisation.type,
        "is_deprecated": sample_organisation.is_deprecated,
        "contacts": [
            {
                "name": sample_organisation.contacts[0].name,
                "email": sample_organisation.contacts[0].email,
                "role": sample_organisation.contacts[0].role,
            },
            {
                "name": sample_organisation.contacts[1].name,
                "email": sample_organisation.contacts[1].email,
                "role": sample_organisation.contacts[1].role,
            },
        ],
    }


@pytest.fixture
def sample_dataset_with_qualified_attributions(
    db_session: Session, sample_dataset: Dataset
) -> Dataset:
    qa1 = DatasetQualifiedAttribution(
        dataset_id=sample_dataset.id,
        organisation_id=sample_dataset.publisher_id,
        role="author",
    )
    # Get first creator's organisation_id
    first_creator_org_id = next(iter(sample_dataset.creators)).organisation_id
    qa2 = DatasetQualifiedAttribution(
        dataset_id=sample_dataset.id,
        organisation_id=first_creator_org_id,
        role="contributor",
    )

    sample_dataset.qualified_attributions = [qa1, qa2]
    db_session.add(qa1)
    db_session.add(qa2)
    db_session.commit()
    db_session.refresh(sample_dataset)

    return sample_dataset


@pytest.fixture
def expected_empty_dataset_resource() -> ResourceDataset:
    return ResourceDataset(
        contact_ids=[],
        contact_emails=[],
        contact_names=[],
        creator_ids=[],
        creator_names=[],
        author_name="Jia",
        dataset_types=frozenset(),
        description=None,
        distributions=[],
        duration_of_administrative_utility=None,
        max_typical_age=None,
        min_typical_age=None,
        number_of_records=None,
        number_of_unique_individuals=None,
        is_any_dictionary_authentic_source=False,
        final_disposition=None,
        id=1,
        identifier=None,
        keywords=frozenset(),
        applicable_legislations=[],
        release_date=None,
        modified_at=None,
        deprecated_at=None,
        released_at=None,
        notes=None,
        periodicity=None,
        publisher_id=None,
        publisher_name=None,
        rights_statement=None,
        source_relations=[],
        spatial_coverages=frozenset(),
        conventions=[],
        areas_of_work=[],
        areas_of_competence=[],
        status="DRAFT",
        status_triggers=[],
        submitted_at=None,
        themes=frozenset(),
        health_categories=frozenset(),
        health_themes=frozenset(),
        qualified_attributions=[],
        time_period_end=None,
        time_period_start=None,
        retention_period_start=None,
        retention_period_end=None,
        title=None,
        user_id=None,
        version=None,
        version_change_type=None,
        group_manager_ids=[],
        group_manager_names=[],
        data_protection_types=[],
        monitoring_location=None,
        provenance=[],
        health_legal_basis=[],
        population_coverage=None,
        code_values=[],
        languages=frozenset(),
        landing_pages=[],
        documentation=[],
        purpose=[],
        conforms_to=[],
        was_generated_by=[],
        other_identifiers=[],
        version_notes=[],
        coding_systems=[],
        spatial_resolutions=[],
        temporal_resolution=None,
        is_dataset_series=False,
        personal_data=[],
    )


@pytest.fixture
def expected_dataset_resource(sample_dataset) -> ResourceDataset:
    return ResourceDataset(
        id=1,
        author_name="Jia",
        status=DatasetStatus.DRAFT.value,
        status_triggers=[],
        title="title",
        description="description",
        contact_ids=(
            [dc.contact_id for dc in sample_dataset.contacts]
            if sample_dataset.contacts
            else []
        ),
        contact_names=[],
        contact_emails=[],
        user_id=1,
        publisher_name=None,
        publisher_id=sample_dataset.publisher_id,
        submitted_at=None,
        time_period_start=date(2024, 3, 1).isoformat(),
        time_period_end=date(2025, 2, 28).isoformat(),
        retention_period_start=date(2023, 1, 1).isoformat(),
        retention_period_end=date(2025, 12, 31).isoformat(),
        rights_statement="PUBLIC",
        periodicity=None,
        dataset_types=frozenset(),
        themes=frozenset(),
        health_categories=frozenset(),
        health_themes=frozenset(),
        qualified_attributions=[],
        keywords=frozenset(),
        release_date=date(2022, 12, 31).isoformat(),
        modified_at=date(2022, 12, 31).isoformat(),
        deprecated_at=date(2022, 12, 31).isoformat(),
        released_at=date(2022, 12, 31).isoformat(),
        spatial_coverages=frozenset(),
        conventions=[],
        areas_of_work=[],
        areas_of_competence=[],
        applicable_legislations=[],
        notes="notes",
        version="0.0.0",
        version_change_type=None,
        duration_of_administrative_utility=0,
        max_typical_age=0,
        min_typical_age=0,
        number_of_records=0,
        number_of_unique_individuals=0,
        is_any_dictionary_authentic_source=False,
        final_disposition="Archive",
        creator_names=[],
        creator_ids=[creator.organisation_id for creator in sample_dataset.creators],
        identifier="b7c08d13-d4b4-4bca-9157-d22870922a6f",
        group_manager_ids=[gm.user.id for gm in sample_dataset.group_managers],
        group_manager_names=[gm.user.name for gm in sample_dataset.group_managers],
        data_protection_types=[],
        monitoring_location="Luxembourg",
        provenance=["Official records"],
        health_legal_basis=[],
        population_coverage="Adults aged 18-65 in Luxembourg",
        code_values=["ICD-10 Codes"],
        coding_systems=["https://www.wikidata.org/entity/Q9006342"],
        languages=frozenset(),
        conforms_to=["https://example.com/conforms_to"],
        landing_pages=["https://example.com/landing_page"],
        documentation=["https://example.com/dataset_document"],
        purpose=["Research and public health monitoring"],
        was_generated_by=[],
        other_identifiers=[],
        version_notes=["note-1"],
        spatial_resolutions=[1],
        temporal_resolution="P1D",
        is_dataset_series=False,
        personal_data=["Age"],
        distributions=[
            ResourceDistribution(
                id=None,
                title="distribution_title",
                description="distribution_description",
                dataset_id=1,
                download_urls=(),
                access_urls=("https://example.com/access_url",),
                file_type=None,
                rights_statement=None,
                internal_only=None,
                is_analytics=None,
                applicable_legislations=frozenset(),
                languages=frozenset(),
                notes=None,
                license=None,
                distribution_path=None,
                availability=None,
                documentation=None,
                modification_date=None,
                release_date=None,
                policy_actions=[],
                linked_schemas=(),
                spatial_resolution=1,
                compression_format=None,
                packaging_format=None,
                distribution_dcat_status=None,
                temporal_resolution=None,
                access_services=frozenset(),
            )
        ],
    )


@pytest.fixture
def simple_dataset() -> Dataset:
    """Simple dataset fixture for basic tests (especially email service tests)."""
    return Dataset(
        id=1,
        title="Test Dataset",
        user_id=999,
        publisher_id=100,
    )


@pytest.fixture
def sample_distribution() -> Distribution:
    """Basic distribution fixture for distribution service tests."""
    return Distribution(
        id=1,
        dataset_id=1,
        dataset=Dataset(id=1),
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_distribution_dto() -> DistributionDto:
    """DistributionDto fixture for distribution service tests."""
    return DistributionDto(
        title="distribution_title",
        description="distribution_description",
        download_urls=["https://example.com/download"],
        access_urls=["https://example.com/access"],
        file_type="OTHER",
        rights_statement="PUBLIC",
        internal_only=True,
        applicable_legislations=["GDPR"],
        languages=frozenset(["ENG"]),
        notes="notes",
        license="no_license",
        distribution_path="INSIPRE",
        availability="Stable",
        documentation=["https://example.com/doc"],
        modification_date=None,
        release_date=None,
        linked_schemas=[],
        byte_size=10,
        checksum="test",
        policy_actions=[
            PolicyActionDto(
                policy_action_type="permission",
                policy_constraint_type="purpose",
                policy_constraint_value="DUO:0000006",
                temporal_restriction_start=None,
                temporal_restriction_end=None,
                spatial_restrictions=[],
            )
        ],
        media_type="application/json",
        compression_format="application/zip",
        packaging_format="text/csv",
        distribution_dcat_status="Completed",
        spatial_resolution=1,
        temporal_resolution="PT1H",
        access_service_ids=frozenset(),
    )


@pytest.fixture
def expected_resource_distribution() -> ResourceDistribution:
    """Expected ResourceDistribution for distribution service tests."""
    return ResourceDistribution(
        id=1,
        title="distribution_title",
        description="distribution_description",
        dataset_id=1,
        download_urls=("download_urls",),
        access_urls=("access_url",),
        file_type=None,
        rights_statement=None,
        internal_only=True,
        is_analytics=False,
        applicable_legislations=[],
        languages=frozenset(),
        notes="notes",
        license=None,
        distribution_path="INSIPRE",
        availability=None,
        documentation=None,
        modification_date=None,
        release_date=None,
        policy_actions=[
            PolicyActionDto(
                policy_action_type="permission",
                policy_constraint_type="purpose",
                policy_constraint_value="DUO:0000006",
                temporal_restriction_start=None,
                temporal_restriction_end=None,
                spatial_restrictions=[],
            )
        ],
        linked_schemas=(),
        media_type="application/json",
        compression_format="application/zip",
        packaging_format="text/csv",
        created_at=None,
        distribution_dcat_status="Completed",
        spatial_resolution=1,
        temporal_resolution="PT1H",
        access_services=frozenset(),
    )
