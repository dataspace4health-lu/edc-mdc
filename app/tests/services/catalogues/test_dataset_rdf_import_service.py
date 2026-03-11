from datetime import date
from unittest.mock import Mock

from models.dataset import DatasetType, Keyword, Theme
from models.organisation import Organisation
from models.spatial_coverage import SpatialCoverage
from models.user import User
from models.applicable_legislation import ApplicableLegislation
from repositories.keyword import KeywordRepository
from repositories.applicable_legislation import ApplicableLegislationRepository
from repositories.organisation import OrganisationRepository
from schemas.contact import ResourceContact
from schemas.dataset import DatasetDto
from services.catalogues.importers.dataset_rdf_import_service import (
    DatasetRDFImportService,
)
from services.catalogues.importers.dataset_rdf_mapper import DatasetRDFMapper
from services.catalogues.importers.distribution_rdf_mapper import DistributionRDFMapper
from models.identity_context import IdentityContext

SAMPLE_RDF = """
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix r5r: <http://data.europa.eu/r5r/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix adms: <http://www.w3.org/ns/adms#> .
@prefix dpv: <http://www.w3.org/ns/dpv#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix healthdcatap: <http://healthdataportal.eu/ns/health#> .

<http://example.org/datasets/1>
    a dcat:Dataset ;
    dct:title "Environmental Statistics"@eng ;
    dct:description "Dataset about environment"@eng ;
    dct:identifier "dataset-001" ;
    dct:accrualPeriodicity <http://publications.europa.eu/resource/authority/frequency/ANNUAL> ;
    dct:accessRights <http://publications.europa.eu/resource/authority/access-right/PUBLIC> ;
    dct:temporal [
        a dct:PeriodOfTime ;
        dcat:startDate "2023-01-01"^^xsd:date ;
        dcat:endDate "2023-12-31"^^xsd:date
    ] ;
    dct:modified "2024-01-15T00:00:00"^^xsd:dateTime ;
    dct:issued "2024-02-01T00:00:00"^^xsd:dateTime ;
    dct:type <https://example.org/dataset-type/REPORT> ;
    dcat:theme <https://example.org/theme/ENV> ;
    dcat:keyword "Environment"@eng ;
    dct:language <http://publications.europa.eu/resource/authority/language/ENG> ;
    dct:spatial <https://example.org/places/LU> ;
    r5r:applicableLegislation <http://example.org/legal/basis> ;
    dct:conformsTo <https://example.org/standard/1> ;
    dct:conformsTo <https://example.org/standard/2> ;
    dcat:landingPage <https://example.org/datasets/1> ;
    dcat:landingPage <https://example.org/datasets/1/about> ;
    dcat:version "1.0.0" ;
    adms:versionNotes "Initial release of environmental statistics" ;
    dpv:dataProtectionType "Personal Data"@eng ;
    dpv:dataProtectionType "Sensitive Data"@eng ;
    healthdcatap:minTypicalAge "18"^^xsd:nonNegativeInteger ;
    healthdcatap:maxTypicalAge "65"^^xsd:nonNegativeInteger ;
    healthdcatap:numberOfRecords "100"^^xsd:nonNegativeInteger ;
    healthdcatap:numberOfUniqueIndividuals "50"^^xsd:nonNegativeInteger ;
    healthdcatap:populationCoverage "Adults aged 18-65 in Luxembourg"@eng ;
    healthdcatap:hasCodeValues "ICD-10 Codes"@eng ;
    dpv:hasPurpose [
        a dpv:Purpose ;
        dct:description "Research and public health monitoring"@eng
    ];
    healthdcatap:hasCodingSystem <https://www.wikidata.org/entity/Q9006342>;
    dct:publisher [
        a foaf:Organization ;
        foaf:name "Environment Agency"@eng
    ] ;
    dct:creator [
        a foaf:Organization ;
        foaf:name "Research Department"@eng
    ] ;
    foaf:page <https://example.org/doc-1> ;
    foaf:page <https://example.org/doc-2> ;
    foaf:page <https://example.org/doc-3> ;
    foaf:page "doc-literal" ;
    foaf:page <file:///tmp/document2> ;
    prov:wasGeneratedBy [
        a prov:Activity ;
        rdfs:label "Generated Automatically"@eng
    ] ;
    dpv:hasLegalBasis [
        a dpv:LegalBasis ;
        dct:description "CSI Deliberation no. 21/028"@eng
    ] .
""".strip()


class StubDataset:
    def __init__(self, id: int):
        self.id = id


class StubDatasetService:
    def __init__(self):
        self.called_with = None
        self.response = StubDataset(123)

    def insert_dataset(
        self, dataset_dto: DatasetDto, identity: IdentityContext, **kwargs
    ):
        self.called_with = {
            "dto": dataset_dto,
            "identity": identity,
            "kwargs": kwargs,
        }
        return self.response


class StubQualifiedAttributionService:
    def __init__(self):
        self.called_with = []

    def add_qualified_attribution(self, dataset_id: int, data, identity):
        self.called_with.append(
            {"dataset_id": dataset_id, "data": data, "identity": identity}
        )


class StubQualifiedAttributionRDFMapper:
    def map_qualified_attributions(self, graph, dataset_uri):
        return []


class StubDatasetRelationService:
    def __init__(self):
        self.called_with = []

    def add_relation(self, source_dataset_id: int, add_relation, identity):
        self.called_with.append(
            {
                "source_dataset_id": source_dataset_id,
                "add_relation": add_relation,
                "identity": identity,
            }
        )


class StubDatasetRelationRDFMapper:
    def map_dataset_relations(self, graph, dataset_uri):
        return []


class StubFormFieldsImportService:
    def __init__(self):
        self.keyword_calls = []
        self.applicable_legislation_calls = []

    def ensure_keywords_exist(
        self,
        keyword_values,
        organisation_id: int | None = None,
        created_by_id: int | None = None,
        source_instance: str | None = None,
    ):
        self.keyword_calls.append(
            {
                "keyword_values": set(keyword_values),
                "organisation_id": organisation_id,
                "created_by_id": created_by_id,
                "source_instance": source_instance,
            }
        )
        return set(keyword_values)

    def ensure_applicable_legislations_exist(
        self,
        applicable_legislation_keys,
        organisation_id: int | None = None,
        created_by_id: int | None = None,
        source_instance: str | None = None,
    ):
        self.applicable_legislation_calls.append(
            {
                "applicable_legislation_keys": set(applicable_legislation_keys),
                "organisation_id": organisation_id,
                "created_by_id": created_by_id,
                "source_instance": source_instance,
            }
        )
        return set(applicable_legislation_keys)

    def ensure_applicable_legislations_with_titles_exist(
        self,
        applicable_legislation_data: dict[str, str],
        organisation_id: int | None = None,
        created_by_id: int | None = None,
        source_instance: str | None = None,
    ):
        self.applicable_legislation_calls.append(
            {
                "applicable_legislation_data": applicable_legislation_data,
                "organisation_id": organisation_id,
                "created_by_id": created_by_id,
                "source_instance": source_instance,
            }
        )
        return set(applicable_legislation_data.keys())


class StubContactImportService:
    def __init__(self):
        self.called_with = None
        self.contacts_to_return = None

    def ensure_contacts_from_graph(
        self,
        graph,
        dataset_uri,
        organisation_id,
        identity,
        skip_permission_validation=False,
    ):
        self.called_with = {
            "graph": graph,
            "dataset_uri": dataset_uri,
            "organisation_id": organisation_id,
            "identity": identity,
            "skip_permission_validation": skip_permission_validation,
        }
        return self.contacts_to_return if self.contacts_to_return is not None else []


class StubDataDictionaryService:
    def __init__(self):
        self.called_with = []

    def add_data_dictionary(self, dataset_id: int, data, identity):
        self.called_with.append(
            {"dataset_id": dataset_id, "data": data, "identity": identity}
        )


class StubDataDictionaryRDFMapper:
    def __init__(self, return_data_dicts=False):
        self.called_with = None
        self.return_data_dicts = return_data_dicts

    def map_data_dictionaries(self, graph, dataset_uri):
        self.called_with = {"graph": graph, "dataset_uri": dataset_uri}

        if not self.return_data_dicts:
            # Default: return None (no data dictionaries)
            return None

        # Return mock data dictionary entries when explicitly requested
        from schemas.data_dictionary import AddDataDictionaryEntry

        return [
            AddDataDictionaryEntry(
                field_name="temperature",
                description="Temperature in Celsius",
                data_type="Float",
                variable_unit="celsius",
                personally_identifiable_variable=None,
                required=None,
                max_allowed_value=None,
                min_allowed_value=None,
                allowed_values=None,
                allowed_values_description=None,
                privacy_risk_type=None,
                table_name=None,
            ),
            AddDataDictionaryEntry(
                field_name="location",
                description="Measurement location",
                data_type="String",
                personally_identifiable_variable=True,
                required=None,
                max_allowed_value=None,
                min_allowed_value=None,
                variable_unit=None,
                allowed_values=None,
                allowed_values_description=None,
                privacy_risk_type=None,
                table_name=None,
            ),
        ]


class StubDistributionService:
    def __init__(self):
        self.called_with = []

    def add_distribution(self, dataset_id: int, distribution_dto, identity):
        self.called_with.append(
            {
                "dataset_id": dataset_id,
                "distribution_dto": distribution_dto,
                "identity": identity,
            }
        )


def _prepare_dependencies(db_session):
    dataset_type = db_session.get(
        DatasetType, "https://example.org/dataset-type/REPORT"
    )
    if dataset_type is None:
        dataset_type = DatasetType(
            key="https://example.org/dataset-type/REPORT", eng_label="Report"
        )
        db_session.add(dataset_type)

    theme = db_session.get(Theme, "https://example.org/theme/ENV")
    if theme is None:
        theme = Theme(key="https://example.org/theme/ENV", eng_label="Environment")
        db_session.add(theme)

    keyword = db_session.get(Keyword, "ENVIRONMENT")
    if keyword is None:
        keyword = Keyword(key="ENVIRONMENT", eng_label="Environment")
        db_session.add(keyword)

    spatial = db_session.get(SpatialCoverage, "https://example.org/places/LU")
    if spatial is None:
        spatial = SpatialCoverage(
            key="https://example.org/places/LU", eng_label="Luxembourg"
        )
        db_session.add(spatial)

    applicable_legislation = db_session.get(
        ApplicableLegislation, "http://example.org/legal/basis"
    )
    if applicable_legislation is None:
        applicable_legislation = ApplicableLegislation(
            key="http://example.org/legal/basis",
            eng_label="Basis",
            description="Legal basis description",
            link="https://example.org/legal/basis",
        )
        db_session.add(applicable_legislation)

    organisation = (
        db_session.query(Organisation)
        .filter(Organisation.name == "Environment Agency")
        .first()
    )
    if organisation is None:
        organisation = Organisation(
            name="Environment Agency",
            type="agency",
            email="agency@example.org",
        )
        db_session.add(organisation)

    creator_organisation = (
        db_session.query(Organisation)
        .filter(Organisation.name == "Research Department")
        .first()
    )
    if creator_organisation is None:
        creator_organisation = Organisation(
            name="Research Department",
            type="department",
            email="research@example.org",
        )
        db_session.add(creator_organisation)

    user = db_session.query(User).filter(User.external_id == "importer-test").first()
    if user is None:
        user = User(
            name="Importer",
            email="importer@example.org",
            external_id="importer-test",
        )
        db_session.add(user)

    db_session.commit()

    keyword_repo = KeywordRepository(db_session)
    applicable_legislation_repo = ApplicableLegislationRepository(db_session)
    organisation_repo = OrganisationRepository(db_session)
    distribution_mapper = DistributionRDFMapper(
        applicable_legislation_repository=applicable_legislation_repo,
    )
    return (
        organisation,
        creator_organisation,
        user,
        keyword_repo,
        applicable_legislation_repo,
        organisation_repo,
        distribution_mapper,
    )


def _create_service(
    keyword_repo,
    applicable_legislation_repo,
    organisation_repo,
    distribution_mapper,
    dataset_service,
    qualified_attribution_service=None,
    qualified_attribution_rdf_mapper=None,
    dataset_relation_service=None,
    dataset_relation_rdf_mapper=None,
    form_fields_import_service=None,
    contact_import_service=None,
    data_dictionary_service=None,
    data_dictionary_rdf_mapper=None,
    distribution_service=None,
    dataset_activity_log_service=None,
):
    mapper = DatasetRDFMapper(
        keyword_repository=keyword_repo,
        applicable_legislation_repository=applicable_legislation_repo,
        organisation_repository=organisation_repo,
        distribution_rdf_mapper=distribution_mapper,
    )
    return DatasetRDFImportService(
        dataset_service=dataset_service,
        dataset_rdf_mapper=mapper,
        qualified_attribution_service=qualified_attribution_service
        or StubQualifiedAttributionService(),
        qualified_attribution_rdf_mapper=qualified_attribution_rdf_mapper
        or StubQualifiedAttributionRDFMapper(),
        dataset_relation_service=dataset_relation_service
        or StubDatasetRelationService(),
        dataset_relation_rdf_mapper=dataset_relation_rdf_mapper
        or StubDatasetRelationRDFMapper(),
        form_fields_import_service=form_fields_import_service
        or StubFormFieldsImportService(),
        contact_import_service=contact_import_service or StubContactImportService(),
        data_dictionary_service=data_dictionary_service or StubDataDictionaryService(),
        data_dictionary_rdf_mapper=data_dictionary_rdf_mapper
        or StubDataDictionaryRDFMapper(),
        distribution_service=distribution_service or StubDistributionService(),
        dataset_activity_log_service=dataset_activity_log_service or Mock(),
    )


def test_parse_dataset_dto_maps_core_fields(db_session):
    (
        organisation,
        creator_organisation,
        user,
        keyword_repo,
        applicable_legislation_repo,
        organisation_repo,
        distribution_mapper,
    ) = _prepare_dependencies(db_session)
    service = _create_service(
        keyword_repo,
        applicable_legislation_repo,
        organisation_repo,
        distribution_mapper,
        StubDatasetService(),
    )

    dto, identifier = service.parse_dataset_dto(SAMPLE_RDF, "turtle")

    assert identifier == "dataset-001"
    assert dto.title == "Environmental Statistics"
    assert dto.description == "Dataset about environment"
    assert dto.publisher_id == organisation.id
    assert creator_organisation.id in dto.creator_ids
    assert dto.time_period_start == date(2023, 1, 1)
    assert dto.time_period_end == date(2023, 12, 31)
    assert (
        dto.rights_statement
        == "http://publications.europa.eu/resource/authority/access-right/PUBLIC"
    )
    assert (
        dto.periodicity
        == "http://publications.europa.eu/resource/authority/frequency/ANNUAL"
    )
    assert dto.dataset_types == {"https://example.org/dataset-type/REPORT"}
    assert dto.themes == {"https://example.org/theme/ENV"}
    assert dto.keywords == {"ENVIRONMENT"}
    assert dto.applicable_legislations == {
        "http://example.org/legal/basis",
    }
    assert dto.languages == frozenset(
        {"http://publications.europa.eu/resource/authority/language/ENG"}
    )
    assert dto.was_generated_by == frozenset({"Generated Automatically"})
    assert {str(url) for url in dto.landing_pages} == {
        "https://example.org/datasets/1",
        "https://example.org/datasets/1/about",
    }
    assert set(dto.documentation) == {
        "https://example.org/doc-1",
        "https://example.org/doc-2",
        "https://example.org/doc-3",
        "doc-literal",
        "document2",
    }
    assert [str(url) for url in dto.conforms_to] == [
        "https://example.org/standard/1",
        "https://example.org/standard/2",
    ]
    assert dto.spatial_coverages == {"https://example.org/places/LU"}
    assert dto.release_date == date(2024, 2, 1)
    assert dto.modified_at == date(2024, 1, 15)
    assert dto.version == "1.0.0"
    assert dto.version_notes == ["Initial release of environmental statistics"]
    assert dto.data_protection_types == {"PersonalData", "SensitiveData"}
    assert dto.min_typical_age == 18
    assert dto.max_typical_age == 65
    assert dto.number_of_records == 100
    assert dto.number_of_unique_individuals == 50
    assert dto.population_coverage == "Adults aged 18-65 in Luxembourg"
    assert dto.code_values == {"ICD-10 Codes"}
    assert dto.purpose == {"Research and public health monitoring"}
    assert dto.health_legal_basis == ["CSI Deliberation no. 21/028"]
    assert dto.coding_systems == {"https://www.wikidata.org/entity/Q9006342"}


def test_import_dataset_calls_dataset_service(db_session):
    (
        organisation,
        creator_organisation,
        user,
        keyword_repo,
        applicable_legislation_repo,
        organisation_repo,
        distribution_mapper,
    ) = _prepare_dependencies(db_session)
    stub_service = StubDatasetService()
    service = _create_service(
        keyword_repo,
        applicable_legislation_repo,
        organisation_repo,
        distribution_mapper,
        stub_service,
    )

    identity = IdentityContext(
        user_id=user.id,
        permissions=["datasets:edit:draft"],
        current_organisation_id=organisation.id,
    )

    response = service.import_dataset(SAMPLE_RDF, "turtle", identity)

    assert response == stub_service.response
    assert stub_service.called_with is not None
    captured = stub_service.called_with
    assert captured["dto"].title == "Environmental Statistics"
    assert captured["kwargs"]["identifier"] == "dataset-001"
    assert captured["kwargs"].get("suppress_create_logging", False) == False


def test_import_dataset_applies_target_status(db_session):
    (
        organisation,
        creator_organisation,
        user,
        keyword_repo,
        applicable_legislation_repo,
        organisation_repo,
        distribution_mapper,
    ) = _prepare_dependencies(db_session)
    stub_service = StubDatasetService()
    service = _create_service(
        keyword_repo,
        applicable_legislation_repo,
        organisation_repo,
        distribution_mapper,
        stub_service,
    )

    identity = IdentityContext(
        user_id=user.id,
        permissions=["datasets:edit:draft"],
        current_organisation_id=organisation.id,
    )

    service.import_dataset(
        SAMPLE_RDF,
        "turtle",
        identity,
        target_status="PUBLISHED",
    )

    captured = stub_service.called_with
    assert captured is not None
    assert captured["dto"].status == "PUBLISHED"


def test_import_dataset_applies_target_version_change_type(db_session):
    (
        organisation,
        creator_organisation,
        user,
        keyword_repo,
        applicable_legislation_repo,
        organisation_repo,
        distribution_mapper,
    ) = _prepare_dependencies(db_session)
    stub_service = StubDatasetService()
    service = _create_service(
        keyword_repo,
        applicable_legislation_repo,
        organisation_repo,
        distribution_mapper,
        stub_service,
    )

    identity = IdentityContext(
        user_id=user.id,
        permissions=["datasets:edit:draft"],
        current_organisation_id=organisation.id,
    )

    service.import_dataset(
        SAMPLE_RDF,
        "turtle",
        identity,
        target_version_change_type="UNDERLYING_DATA",
    )

    captured = stub_service.called_with
    assert captured is not None
    assert captured["dto"].version_change_type == "UNDERLYING_DATA"


def test_import_dataset_precreates_reference_data(db_session):
    (
        organisation,
        creator_organisation,
        user,
        keyword_repo,
        applicable_legislation_repo,
        organisation_repo,
        distribution_mapper,
    ) = _prepare_dependencies(db_session)
    stub_form_fields = StubFormFieldsImportService()
    service = _create_service(
        keyword_repo,
        applicable_legislation_repo,
        organisation_repo,
        distribution_mapper,
        StubDatasetService(),
        form_fields_import_service=stub_form_fields,
    )

    identity = IdentityContext(
        user_id=user.id,
        permissions=["datasets:edit:draft"],
        current_organisation_id=organisation.id,
    )

    service.import_dataset(SAMPLE_RDF, "turtle", identity)

    assert stub_form_fields.keyword_calls
    keyword_call = stub_form_fields.keyword_calls[0]
    assert keyword_call["keyword_values"] == {"Environment"}
    assert keyword_call["organisation_id"] == organisation.id
    assert keyword_call["created_by_id"] == user.id

    assert stub_form_fields.applicable_legislation_calls
    applicable_legislation_call = stub_form_fields.applicable_legislation_calls[0]
    assert set(applicable_legislation_call["applicable_legislation_data"].keys()) == {
        "http://example.org/legal/basis",
    }
    assert applicable_legislation_call["organisation_id"] == organisation.id
    assert applicable_legislation_call["created_by_id"] == user.id


def test_import_dataset_injects_contact_ids(db_session):
    (
        organisation,
        creator_organisation,
        user,
        keyword_repo,
        applicable_legislation_repo,
        organisation_repo,
        distribution_mapper,
    ) = _prepare_dependencies(db_session)

    stub_dataset_service = StubDatasetService()
    stub_contact_service = StubContactImportService()
    stub_contact_service.contacts_to_return = [
        ResourceContact(
            id=42,
            name="John Doe",
            email="john@example.com",
            role="Manager",
            is_deprecated=False,
        )
    ]

    service = _create_service(
        keyword_repo,
        applicable_legislation_repo,
        organisation_repo,
        distribution_mapper,
        stub_dataset_service,
        contact_import_service=stub_contact_service,
    )

    identity = IdentityContext(
        user_id=user.id,
        permissions=["datasets:edit:draft"],
        current_organisation_id=organisation.id,
    )

    service.import_dataset(SAMPLE_RDF, "turtle", identity)

    # Verify contact import service was called in _ensure_reference_data_exists
    assert stub_contact_service.called_with is not None
    assert stub_contact_service.called_with["organisation_id"] == organisation.id
    assert stub_contact_service.called_with["identity"] == identity
    assert stub_contact_service.called_with["skip_permission_validation"] is True

    # Verify contact_ids was passed to mapper and set in dataset_dto
    captured = stub_dataset_service.called_with
    assert captured is not None
    assert captured["dto"].contact_ids == {42}


def test_import_dataset_without_contact(db_session):
    (
        organisation,
        creator_organisation,
        user,
        keyword_repo,
        applicable_legislation_repo,
        organisation_repo,
        distribution_mapper,
    ) = _prepare_dependencies(db_session)

    stub_dataset_service = StubDatasetService()
    stub_contact_service = StubContactImportService()
    stub_contact_service.contacts_to_return = []  # No contact in RDF

    service = _create_service(
        keyword_repo,
        applicable_legislation_repo,
        organisation_repo,
        distribution_mapper,
        stub_dataset_service,
        contact_import_service=stub_contact_service,
    )

    identity = IdentityContext(
        user_id=user.id,
        permissions=["datasets:edit:draft"],
        current_organisation_id=organisation.id,
    )

    service.import_dataset(SAMPLE_RDF, "turtle", identity)

    # Verify contact_ids remains None when no contact is found
    captured = stub_dataset_service.called_with
    assert captured is not None
    assert captured["dto"].contact_ids is None


def test_import_dataset_with_data_dictionaries(db_session):
    """Test that data dictionaries are properly extracted and saved during dataset import"""
    (
        organisation,
        creator_organisation,
        user,
        keyword_repo,
        applicable_legislation_repo,
        organisation_repo,
        distribution_mapper,
    ) = _prepare_dependencies(db_session)

    rdf_with_data_dict = """
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix csvw: <http://www.w3.org/ns/csvw#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix dpv: <http://www.w3.org/ns/dpv#> .

<http://example.org/datasets/1>
    a dcat:Dataset ;
    dct:title "Environmental Statistics"@eng ;
    dct:description "Dataset about environment"@eng ;
    dct:identifier "dataset-001" ;
    dct:accrualPeriodicity <http://publications.europa.eu/resource/authority/frequency/ANNUAL> ;
    dct:accessRights <http://publications.europa.eu/resource/authority/access-right/PUBLIC> ;
    dct:temporal [
        a dct:PeriodOfTime ;
        dcat:startDate "2023-01-01"^^xsd:date ;
        dcat:endDate "2023-12-31"^^xsd:date
    ] ;
    dct:type <https://example.org/dataset-type/REPORT> ;
    dcat:theme <https://example.org/theme/ENV> ;
    dcat:keyword "Environment"@eng ;
    dct:publisher [
        a foaf:Organization ;
        foaf:name "Environment Agency"@eng
    ] ;
    foaf:page [
        a foaf:Document, csvw:TableSchema ;
        csvw:column [
            a csvw:Column ;
            csvw:name "temperature" ;
            dct:description "Temperature in Celsius"@eng ;
            csvw:datatype xsd:float ;
            csvw:unit "celsius"
        ] ;
        csvw:column [
            a csvw:Column ;
            csvw:name "location" ;
            dct:description "Measurement location"@eng ;
            csvw:datatype xsd:string ;
            a dpv:PersonalData
        ]
    ] .
    """.strip()

    stub_dataset_service = StubDatasetService()
    stub_data_dictionary_service = StubDataDictionaryService()
    stub_data_dictionary_mapper = StubDataDictionaryRDFMapper(return_data_dicts=True)

    service = _create_service(
        keyword_repo,
        applicable_legislation_repo,
        organisation_repo,
        distribution_mapper,
        stub_dataset_service,
        data_dictionary_service=stub_data_dictionary_service,
        data_dictionary_rdf_mapper=stub_data_dictionary_mapper,
    )

    identity = IdentityContext(
        user_id=user.id,
        permissions=["datasets:edit:draft"],
        current_organisation_id=organisation.id,
    )

    service.import_dataset(rdf_with_data_dict, "turtle", identity)

    # Verify the data dictionary mapper was called with the correct graph
    assert stub_data_dictionary_mapper.called_with is not None
    assert stub_data_dictionary_mapper.called_with["graph"] is not None

    # Verify the data dictionary service was called for each entry
    assert len(stub_data_dictionary_service.called_with) == 2


def test_import_dataset_with_source_suppresses_create_logging(db_session):
    (
        organisation,
        creator_organisation,
        user,
        keyword_repo,
        applicable_legislation_repo,
        organisation_repo,
        distribution_mapper,
    ) = _prepare_dependencies(db_session)
    stub_service = StubDatasetService()
    service = _create_service(
        keyword_repo,
        applicable_legislation_repo,
        organisation_repo,
        distribution_mapper,
        stub_service,
    )

    identity = IdentityContext(
        user_id=user.id,
        permissions=["datasets:edit:draft"],
        current_organisation_id=organisation.id,
    )

    response = service.import_dataset(
        SAMPLE_RDF,
        "turtle",
        identity,
        duplicates_check=False,
        source="lnds-mdc",
        source_dataset_id=100,
    )

    assert response == stub_service.response
    assert stub_service.called_with is not None
    captured = stub_service.called_with

    assert captured["kwargs"]["suppress_create_logging"] == True
    assert captured["kwargs"]["identifier"] == "dataset-001"
