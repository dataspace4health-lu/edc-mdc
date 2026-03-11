import os
import pytest
import uuid
from datetime import date, datetime
from unittest.mock import patch, MagicMock
import re
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import DCAT, DCTERMS, RDF, SKOS, FOAF
from services.catalogues.mappers.namespace_constants import HEALTHDCATAP, VCARD

from models.identity_context import IdentityContext
from models.dataset import Dataset, DatasetLandingPage, SeriesMembership
from models.organisation import Organisation
from models.data_service import DataService, DataServiceEndpoint
from models.distribution import Distribution, DistributionAccessService
from services.catalogue import CatalogueService
from services.config import ConfigService
from services.dataset_permissions_service import DatasetPermissionsService
from repositories.dataset import DatasetRepository
from repositories.applicable_legislation import ApplicableLegislationRepository
from repositories.data_service import DataServiceRepository
from repositories.data_dictionary import DataDictionaryRepository
from test_factory import sample_dataset


@pytest.fixture
def setup_environment():
    """Set up environment variables needed for the catalogue service."""
    os.environ["APP_URL"] = "https://test.example.com"
    yield
    if "APP_URL" in os.environ:
        del os.environ["APP_URL"]


@pytest.fixture
def config_service():
    mock_config = MagicMock(spec=ConfigService)
    mock_config.get_catalogue.return_value = {
        "url": "https://test.example.com",
        "uri_templates": {
            "datasets": "/datasets/{identifier}",
            "data_services": "/data-services/{id}",
            "sample_distribution_download": "/datasets/{identifier}/data-dictionaries/download",
        },
        "name": "Test Catalogue",
        "description": "Test catalogue description",
        "publisher_name": "Test Publisher",
    }
    mock_config.get_health_data_access_body.return_value = {
        "identifier": "https://health.data.lu/hdab/luxembourg",
        "name": "Health Data Access Body Luxembourg",
        "contact_name": "HDAB Contact Point",
        "contact_email": "hdab@health.lu",
    }
    return mock_config


@pytest.fixture
def mock_dataset_permissions_service():
    return MagicMock(spec=DatasetPermissionsService)


@pytest.fixture
def mock_data_dictionary_repository():
    repo = MagicMock(spec=DataDictionaryRepository)
    repo.get_data_dictionaries_by_dataset_id.return_value = []
    return repo


@pytest.fixture
def mock_identity():
    return MagicMock(spec=IdentityContext)


@pytest.fixture
def mock_dataset_series():
    unique_id = lambda: str(uuid.uuid4())

    organisation = MagicMock(spec=Organisation)
    organisation.id = 1
    organisation.name = "Test Organisation"
    organisation.email = "test@example.com"
    organisation.type = "national_authority"

    def setup_base_properties(dataset):
        dataset.themes = []
        dataset.qualified_attributions = []
        dataset.spatial_coverages = []
        dataset.applicable_legislations = []
        dataset.dataset_types = []
        dataset.languages = []
        dataset.distributions = []
        dataset.source_relations = []
        dataset.keywords = []
        dataset.data_protection_types = []
        dataset.conforms_to = []
        dataset.creators = set()
        dataset.provenance = None
        dataset.release_date = None
        dataset.modified_at = None
        dataset.version = "1.0"
        dataset.contacts = []
        dataset.user_id = 1
        dataset.submitted_at = datetime(2023, 1, 1, 0, 0, 0)
        dataset.publisher = organisation
        dataset.landing_pages = []
        dataset.documentation_entries = []
        dataset.member_datasets = []

    member1 = MagicMock(spec=Dataset)
    member1.id = 101
    member1.title = "Member Dataset 2022"
    member1.description = "Dataset for year 2022"
    member1.identifier = unique_id()
    member1.periodicity = (
        "http://publications.europa.eu/resource/authority/frequency/ANNUAL"
    )
    member1.time_period_start = date(2022, 1, 1)
    member1.time_period_end = date(2022, 12, 31)
    member1.is_dataset_series = False
    member1.series_memberships = []
    member1.rights_statement = (
        "http://publications.europa.eu/resource/authority/access-right/PUBLIC"
    )
    landing_page1 = MagicMock(spec=DatasetLandingPage)
    landing_page1.url = "https://example.com/dataset/2022"
    member1.landing_pages = [landing_page1]
    doc1 = MagicMock()
    doc1.value = "https://example.com/docs/2022"
    member1.documentation_entries = [doc1]
    setup_base_properties(member1)

    member2 = MagicMock(spec=Dataset)
    member2.id = 102
    member2.title = "Member Dataset 2023"
    member2.description = "Dataset for year 2023"
    member2.identifier = unique_id()
    member2.periodicity = (
        "http://publications.europa.eu/resource/authority/frequency/ANNUAL"
    )
    member2.time_period_start = date(2023, 1, 1)
    member2.time_period_end = date(2023, 12, 31)
    member2.is_dataset_series = False
    member2.series_memberships = []
    member2.rights_statement = (
        "http://publications.europa.eu/resource/authority/access-right/PUBLIC"
    )
    landing_page2 = MagicMock(spec=DatasetLandingPage)
    landing_page2.url = "https://example.com/dataset/2023"
    member2.landing_pages = [landing_page2]
    doc2 = MagicMock()
    doc2.value = "https://example.com/docs/2023"
    member2.documentation_entries = [doc2]
    setup_base_properties(member2)

    member3 = MagicMock(spec=Dataset)
    member3.id = 103
    member3.title = "Member Dataset 2024"
    member3.description = "Dataset for year 2024"
    member3.identifier = unique_id()
    member3.periodicity = (
        "http://publications.europa.eu/resource/authority/frequency/ANNUAL"
    )
    member3.time_period_start = date(2024, 1, 1)
    member3.time_period_end = date(2024, 12, 31)
    member3.is_dataset_series = False
    member3.series_memberships = []
    member3.rights_statement = (
        "http://publications.europa.eu/resource/authority/access-right/PUBLIC"
    )
    landing_page3 = MagicMock(spec=DatasetLandingPage)
    landing_page3.url = "https://example.com/dataset/2024"
    member3.landing_pages = [landing_page3]
    doc3 = MagicMock()
    doc3.value = "https://example.com/docs/2024"
    member3.documentation_entries = [doc3]
    setup_base_properties(member3)

    series = MagicMock(spec=Dataset)
    series.id = 100
    series.title = "Annual Dataset Series"
    series.description = "A collection of annual datasets"
    series.identifier = unique_id()
    series.periodicity = (
        "http://publications.europa.eu/resource/authority/frequency/ANNUAL"
    )
    series.time_period_start = date(2022, 1, 1)
    series.time_period_end = date(2024, 12, 31)
    series.is_dataset_series = True
    series.series_memberships = []
    series.rights_statement = (
        "http://publications.europa.eu/resource/authority/access-right/PUBLIC"
    )
    landing_page_series = MagicMock(spec=DatasetLandingPage)
    landing_page_series.url = "https://example.com/dataset/series"
    series.landing_pages = [landing_page_series]
    doc_series = MagicMock()
    doc_series.value = "https://example.com/docs/series"
    series.documentation_entries = [doc_series]
    setup_base_properties(series)

    membership1 = MagicMock(spec=SeriesMembership)
    membership1.series_id = 100  # Use actual ID to avoid MagicMock in URI
    membership1.dataset_id = 101  # Use actual ID
    membership1.position = 0
    membership1.is_first = True
    membership1.is_last = False
    membership1.dataset = member1  # Add dataset relationship
    membership1.series = series  # Add series relationship

    membership2 = MagicMock(spec=SeriesMembership)
    membership2.series_id = 100
    membership2.dataset_id = 102
    membership2.position = 1
    membership2.is_first = False
    membership2.is_last = False
    membership2.dataset = member2  # Add dataset relationship
    membership2.series = series  # Add series relationship

    membership3 = MagicMock(spec=SeriesMembership)
    membership3.series_id = 100
    membership3.dataset_id = 103
    membership3.position = 2
    membership3.is_first = False
    membership3.is_last = True
    membership3.dataset = member3  # Add dataset relationship
    membership3.series = series  # Add series relationship

    series.member_datasets = [membership1, membership2, membership3]

    member_membership1 = MagicMock(spec=SeriesMembership)
    member_membership1.series_id = 100
    member_membership1.series = series  # Add series relationship
    member1.series_memberships = [member_membership1]

    member_membership2 = MagicMock(spec=SeriesMembership)
    member_membership2.series_id = 100
    member_membership2.series = series  # Add series relationship
    member2.series_memberships = [member_membership2]

    member_membership3 = MagicMock(spec=SeriesMembership)
    member_membership3.series_id = 100
    member_membership3.series = series  # Add series relationship
    member3.series_memberships = [member_membership3]

    return {
        "series": series,
        "member1": member1,
        "member2": member2,
        "member3": member3,
    }


def test_dataset_series_rdf_comprehensive(
    db_session,
    mock_dataset_series,
    setup_environment,
    config_service,
    mock_dataset_permissions_service,
    mock_data_dictionary_repository,
):
    repository = DatasetRepository(db_session)
    applicable_legislation_repository = ApplicableLegislationRepository(db_session)
    data_service_repository = DataServiceRepository(db_session)

    series = mock_dataset_series["series"]
    member1 = mock_dataset_series["member1"]
    member2 = mock_dataset_series["member2"]
    member3 = mock_dataset_series["member3"]

    DCAT_FULL = Namespace("http://www.w3.org/ns/dcat#")  # NOSONAR

    all_datasets = [series, member1, member2, member3]
    with patch.object(repository, "get_public_datasets", return_value=all_datasets):
        catalogue_service = CatalogueService(
            dataset_repository=repository,
            applicable_legislation_repository=applicable_legislation_repository,
            data_service_repository=data_service_repository,
            data_dictionary_repository=mock_data_dictionary_repository,
            dataset_permissions_service=mock_dataset_permissions_service,
            config_service=config_service,
        )

        mime_type, rdf_text = catalogue_service.get_catalogue("ttl")

        g = Graph()
        g.parse(data=rdf_text, format="turtle")

        assert mime_type == "text/turtle"
        assert len(rdf_text) > 0

        base_url = "https://test.example.com"

        for dataset in [series, member1, member2, member3]:
            dataset_uri = URIRef(f"{base_url}/datasets/{dataset.identifier}")

            assert (
                dataset_uri,
                RDF.type,
                DCAT.DatasetSeries if dataset.is_dataset_series else DCAT.Dataset,
            ) in g

        # Specific tests only for the series members
        series_uri = URIRef(f"{base_url}/datasets/{series.identifier}")
        member1_uri = URIRef(f"{base_url}/datasets/{member1.identifier}")
        member2_uri = URIRef(f"{base_url}/datasets/{member2.identifier}")
        member3_uri = URIRef(f"{base_url}/datasets/{member3.identifier}")

        assert (series_uri, RDF.type, DCAT_FULL.DatasetSeries) in g
        assert (member1_uri, RDF.type, DCAT.Dataset) in g
        assert (member2_uri, RDF.type, DCAT.Dataset) in g
        assert (member3_uri, RDF.type, DCAT.Dataset) in g

        assert (series_uri, DCAT_FULL.first, member1_uri) in g
        assert (series_uri, DCAT_FULL.last, member3_uri) in g

        assert (member1_uri, DCAT_FULL.inSeries, series_uri) in g
        assert (member2_uri, DCAT_FULL.inSeries, series_uri) in g
        assert (member3_uri, DCAT_FULL.inSeries, series_uri) in g

        assert (member1_uri, DCAT_FULL.next, member2_uri) in g
        assert (member2_uri, DCAT_FULL.prev, member1_uri) in g
        assert (member2_uri, DCAT_FULL.next, member3_uri) in g
        assert (member3_uri, DCAT_FULL.prev, member2_uri) in g

        assert (series_uri, DCTERMS.title, Literal(series.title, lang="eng")) in g
        assert (member1_uri, DCTERMS.title, Literal(member1.title, lang="eng")) in g

        graph_text = g.serialize(format="turtle")

        assert (
            "http://publications.europa.eu/resource/authority/frequency/ANNUAL"
            in graph_text
        ), "Annual periodicity should be present in the graph"


def test_dataset_series_string_patterns(
    db_session,
    mock_dataset_series,
    setup_environment,
    config_service,
    mock_dataset_permissions_service,
    mock_data_dictionary_repository,
):
    repository = DatasetRepository(db_session)
    applicable_legislation_repository = ApplicableLegislationRepository(db_session)
    data_service_repository = DataServiceRepository(db_session)

    series = mock_dataset_series["series"]
    member1 = mock_dataset_series["member1"]
    member2 = mock_dataset_series["member2"]
    member3 = mock_dataset_series["member3"]

    all_datasets = [series, member1, member2, member3]
    with patch.object(repository, "get_public_datasets", return_value=all_datasets):
        catalogue_service = CatalogueService(
            dataset_repository=repository,
            applicable_legislation_repository=applicable_legislation_repository,
            data_service_repository=data_service_repository,
            data_dictionary_repository=mock_data_dictionary_repository,
            dataset_permissions_service=mock_dataset_permissions_service,
            config_service=config_service,
        )
        _, rdf_text = catalogue_service.get_catalogue("ttl")

        assert re.search(
            rf"<.*/datasets/{series.identifier}> a dcat:DatasetSeries", rdf_text
        )
        assert re.search(
            rf"<.*/datasets/{member1.identifier}> a dcat:Dataset", rdf_text
        )

        assert re.search(rf"dcat:first <.*/datasets/{member1.identifier}>", rdf_text)
        assert re.search(rf"dcat:last <.*/datasets/{member3.identifier}>", rdf_text)
        assert re.search(rf"dcat:inSeries <.*/datasets/{series.identifier}>", rdf_text)

        assert re.search(rf"dcat:next <.*/datasets/{member2.identifier}>", rdf_text)
        assert re.search(rf"dcat:prev <.*/datasets/{member1.identifier}>", rdf_text)


@pytest.fixture
def mock_data_service():
    data_service = MagicMock(spec=DataService)
    data_service.id = 1
    data_service.title = "Test Data Service"
    data_service.license = "http://spdx.org/licenses/MIT"  # NOSONAR
    data_service.distribution_dcat_status = MagicMock()
    data_service.distribution_dcat_status.value = "COMPLETED"

    endpoint1 = MagicMock(spec=DataServiceEndpoint)
    endpoint1.endpoint_url = "https://api.example.com/data1"
    endpoint1.endpoint_description = "https://api.example.com/docs/openapi1.json"

    endpoint2 = MagicMock(spec=DataServiceEndpoint)
    endpoint2.endpoint_url = "https://api.example.com/data2"
    endpoint2.endpoint_description = None

    data_service.endpoints = [endpoint1, endpoint2]
    return data_service


@pytest.fixture
def mock_distribution_with_service(mock_data_service):
    distribution = MagicMock(spec=Distribution)
    distribution.id = 1
    distribution.title = "Test Distribution"
    distribution.description = "Test Description"
    distribution.internal_only = False
    distribution.rights_statement = (
        "http://publications.europa.eu/resource/authority/access-right/PUBLIC"
    )
    distribution.format = None
    distribution.media_type = None
    distribution.byte_size = None
    distribution.download_urls = []
    distribution.access_urls = []
    distribution.license = "http://spdx.org/licenses/MIT"  # NOSONAR
    distribution.distribution_dcat_status = MagicMock()
    distribution.distribution_dcat_status.value = "COMPLETED"
    distribution.compression_format = None
    distribution.packaging_format = None
    distribution.spatial_resolution = None
    distribution.temporal_resolution = None
    distribution.documentation_entries = []
    distribution.created_at = None
    distribution.has_policy = None
    distribution.checksum = None
    distribution.availability = None
    distribution.file_type = None

    access_service = MagicMock(spec=DistributionAccessService)
    access_service.data_service = mock_data_service
    distribution.access_services = [access_service]

    return distribution


def test_data_service_in_catalogue(
    db_session,
    setup_environment,
    mock_data_service,
    config_service,
    mock_dataset_permissions_service,
    mock_data_dictionary_repository,
):
    repository = DatasetRepository(db_session)
    applicable_legislation_repository = ApplicableLegislationRepository(db_session)
    data_service_repository = DataServiceRepository(db_session)

    with patch.object(repository, "get_public_datasets", return_value=[]), patch.object(
        data_service_repository, "get_data_services", return_value=[mock_data_service]
    ):

        catalogue_service = CatalogueService(
            dataset_repository=repository,
            applicable_legislation_repository=applicable_legislation_repository,
            data_service_repository=data_service_repository,
            data_dictionary_repository=mock_data_dictionary_repository,
            dataset_permissions_service=mock_dataset_permissions_service,
            config_service=config_service,
        )

        _, rdf_text = catalogue_service.get_catalogue("ttl")
        g = Graph()
        g.parse(data=rdf_text, format="turtle")

        base_url = "https://test.example.com"
        service_uri = URIRef(f"{base_url}/data-services/{mock_data_service.id}")
        catalog_uri = URIRef(base_url)

        # Test DataService is properly defined
        assert (service_uri, RDF.type, DCAT.DataService) in g
        assert (
            service_uri,
            DCTERMS.title,
            Literal(mock_data_service.title, lang="eng"),
        ) in g

        # Test endpoints are properly defined
        assert (
            service_uri,
            DCAT.endpointURL,
            URIRef(mock_data_service.endpoints[0].endpoint_url),
        ) in g
        assert (
            service_uri,
            DCAT.endpointDescription,
            URIRef(mock_data_service.endpoints[0].endpoint_description),
        ) in g
        assert (
            service_uri,
            DCAT.endpointURL,
            URIRef(mock_data_service.endpoints[1].endpoint_url),
        ) in g

        # Test catalog links to the service
        assert (catalog_uri, DCAT.service, service_uri) in g


def test_distribution_service_linking(
    db_session,
    setup_environment,
    mock_data_service,
    mock_distribution_with_service,
    config_service,
    mock_dataset_permissions_service,
    mock_data_dictionary_repository,
):
    repository = DatasetRepository(db_session)
    applicable_legislation_repository = ApplicableLegislationRepository(db_session)
    data_service_repository = DataServiceRepository(db_session)

    dataset = MagicMock(spec=Dataset)
    dataset.id = 1
    dataset.title = "Test Dataset"
    dataset.description = "Test Dataset Description"
    dataset.identifier = str(uuid.uuid4())
    dataset.periodicity = (
        "http://publications.europa.eu/resource/authority/frequency/ANNUAL"
    )
    dataset.time_period_start = date(2023, 1, 1)
    dataset.is_dataset_series = False
    dataset.distributions = [mock_distribution_with_service]
    dataset.publisher = MagicMock(spec=Organisation)
    dataset.publisher.name = "Test Organisation"
    dataset.publisher.type = "national_authority"
    dataset.publisher.email = "test@example.com"
    dataset.submitted_at = datetime(2023, 1, 1, 0, 0, 0)
    dataset.themes = []
    dataset.spatial_coverages = []
    dataset.applicable_legislations = []
    dataset.languages = []
    dataset.keywords = []
    dataset.source_relations = []
    dataset.dataset_types = []
    dataset.data_protection_types = []
    dataset.conforms_to = []
    dataset.creators = set()
    dataset.provenance = None
    dataset.modified_at = None
    dataset.release_date = None
    dataset.version = "1.0"
    dataset.contacts = []
    dataset.user_id = 1
    dataset.landing_pages = []
    dataset.documentation_entries = []
    dataset.rights_statement = (
        "http://publications.europa.eu/resource/authority/access-right/PUBLIC"
    )

    with patch.object(
        repository, "get_public_datasets", return_value=[dataset]
    ), patch.object(
        data_service_repository, "get_data_services", return_value=[mock_data_service]
    ):

        catalogue_service = CatalogueService(
            dataset_repository=repository,
            applicable_legislation_repository=applicable_legislation_repository,
            data_service_repository=data_service_repository,
            data_dictionary_repository=mock_data_dictionary_repository,
            dataset_permissions_service=mock_dataset_permissions_service,
            config_service=config_service,
        )

        _, rdf_text = catalogue_service.get_catalogue("ttl")
        g = Graph()
        g.parse(data=rdf_text, format="turtle")

        base_url = "https://test.example.com"
        service_uri = URIRef(f"{base_url}/data-services/{mock_data_service.id}")

        # Find distribution by querying for Distribution type with correct identifier
        distribution_uri = None
        for s, p, o in g.triples((None, RDF.type, DCAT.Distribution)):
            identifier = g.value(s, DCTERMS.identifier)
            if identifier and int(identifier) == mock_distribution_with_service.id:
                distribution_uri = s
                break

        assert distribution_uri is not None, "Distribution should exist in graph"

        # Test distribution links to the service
        assert (distribution_uri, DCAT.accessService, service_uri) in g


def test_data_service_string_patterns(
    db_session,
    setup_environment,
    mock_data_service,
    config_service,
    mock_dataset_permissions_service,
    mock_data_dictionary_repository,
):
    repository = DatasetRepository(db_session)
    applicable_legislation_repository = ApplicableLegislationRepository(db_session)
    data_service_repository = DataServiceRepository(db_session)

    with patch.object(repository, "get_public_datasets", return_value=[]), patch.object(
        data_service_repository, "get_data_services", return_value=[mock_data_service]
    ):

        catalogue_service = CatalogueService(
            dataset_repository=repository,
            applicable_legislation_repository=applicable_legislation_repository,
            data_service_repository=data_service_repository,
            data_dictionary_repository=mock_data_dictionary_repository,
            dataset_permissions_service=mock_dataset_permissions_service,
            config_service=config_service,
        )

        _, rdf_text = catalogue_service.get_catalogue("ttl")

        # Test basic structure patterns
        assert re.search(
            rf"<.*/data-services/{mock_data_service.id}> a dcat:DataService",
            rdf_text,
        )
        assert re.search(rf'dct:title "Test Data Service"@eng', rdf_text)
        assert re.search(
            rf"dcat:endpointURL <{mock_data_service.endpoints[0].endpoint_url}>",
            rdf_text,
        )
        assert re.search(
            rf"dcat:endpointDescription <{mock_data_service.endpoints[0].endpoint_description}>",
            rdf_text,
        )


def test_data_dictionary_sample_distribution(
    db_session,
    setup_environment,
    config_service,
    mock_dataset_permissions_service,
    mock_data_dictionary_repository,
    mock_identity,
):
    repository = DatasetRepository(db_session)
    applicable_legislation_repository = ApplicableLegislationRepository(db_session)
    data_service_repository = DataServiceRepository(db_session)

    dataset = MagicMock(spec=Dataset)
    dataset.id = 200
    dataset.title = "Dataset With Dictionary"
    dataset.description = "A dataset that has a data dictionary"
    dataset.identifier = str(uuid.uuid4())
    dataset.periodicity = (
        "http://publications.europa.eu/resource/authority/frequency/ANNUAL"
    )
    dataset.time_period_start = date(2023, 1, 1)
    dataset.is_dataset_series = False
    dataset.distributions = []
    dataset.publisher = MagicMock(spec=Organisation)
    dataset.publisher.name = "Test Organisation"
    dataset.publisher.type = "national_authority"
    dataset.publisher.email = "test@example.com"
    dataset.submitted_at = datetime(2023, 1, 1, 0, 0, 0)
    dataset.themes = []
    dataset.spatial_coverages = []
    dataset.applicable_legislations = []
    dataset.languages = []
    dataset.keywords = []
    dataset.source_relations = []
    dataset.dataset_types = []
    dataset.data_protection_types = []
    dataset.contact = None
    dataset.landing_pages = []
    dataset.documentation_entries = []
    dataset.rights_statement = (
        "http://publications.europa.eu/resource/authority/access-right/PUBLIC"
    )
    dataset.conforms_to = []
    dataset.creators = set()
    dataset.provenance = None
    dataset.modified_at = None
    dataset.release_date = None
    dataset.version = "1.0"
    dataset.version_notes = None
    dataset.user_id = 1

    data_dict_entry1 = MagicMock()
    data_dict_entry1.field_name = "field1"
    data_dict_entry1.description = "Description of field 1"
    data_dict_entry1.data_type = "string"
    data_dict_entry1.personally_identifiable_variable = False
    data_dict_entry1.required = False
    data_dict_entry1.max_allowed_value = None
    data_dict_entry1.min_allowed_value = None
    data_dict_entry1.variable_unit = None
    data_dict_entry1.allowed_values = None
    data_dict_entry1.allowed_values_description = None
    data_dict_entry1.privacy_risk_type = None
    data_dict_entry1.is_authentic_source = False
    data_dict_entry1.authentic_source_assignments = []

    data_dict_entry2 = MagicMock()
    data_dict_entry2.field_name = "field2"
    data_dict_entry2.description = "Description of field 2"
    data_dict_entry2.data_type = "integer"
    data_dict_entry2.personally_identifiable_variable = False
    data_dict_entry2.required = False
    data_dict_entry2.max_allowed_value = None
    data_dict_entry2.min_allowed_value = None
    data_dict_entry2.variable_unit = None
    data_dict_entry2.allowed_values = None
    data_dict_entry2.allowed_values_description = None
    data_dict_entry2.privacy_risk_type = None
    data_dict_entry2.is_authentic_source = False
    data_dict_entry2.authentic_source_assignments = []

    dataset.data_dictionaries = [data_dict_entry1, data_dict_entry2]

    with patch.object(
        repository, "get_dataset_by_id", return_value=dataset
    ), patch.object(data_service_repository, "get_data_services", return_value=[]):

        catalogue_service = CatalogueService(
            dataset_repository=repository,
            applicable_legislation_repository=applicable_legislation_repository,
            data_service_repository=data_service_repository,
            data_dictionary_repository=mock_data_dictionary_repository,
            dataset_permissions_service=mock_dataset_permissions_service,
            config_service=config_service,
        )

        _, rdf_text = catalogue_service.get_individual_dataset_catalogue(
            "ttl", dataset.id, mock_identity
        )

        g = Graph()
        g.parse(data=rdf_text, format="turtle")

        base_url = "https://test.example.com"
        dataset_uri = URIRef(f"{base_url}/datasets/{dataset.identifier}")

        adms = Namespace("http://www.w3.org/ns/adms#")

        # Sample distributions are linked via adms:sample
        sample_nodes = list(g.objects(dataset_uri, adms.sample))

        assert (
            sample_nodes
        ), "Dataset should have at least one sample distribution linked via adms:sample"

        dd_distribution_uri = sample_nodes[0]

        # Sample must also appear under dcat:distribution for completeness
        assert dd_distribution_uri in list(
            g.objects(dataset_uri, DCAT.distribution)
        ), "Sample distribution should also be listed under dcat:distribution"

        assert (
            dd_distribution_uri,
            RDF.type,
            DCAT.Distribution,
        ) in g, "Sample should be a dcat:Distribution"

        assert (
            dd_distribution_uri,
            DCTERMS.title,
            Literal(f"Data Dictionary for {dataset.title}", lang="eng"),
        ) in g, "Title should match expected format"

        assert (
            dd_distribution_uri,
            DCTERMS.description,
            Literal(
                "Machine-readable data dictionary describing the structure and contents of the dataset.",
                lang="eng",
            ),
        ) in g, "Description should match expected text"

        graph_text = g.serialize(format="turtle")

        assert "text/csv" in graph_text, "CSV format should be present"
        assert (
            "http://publications.europa.eu/resource/authority/file-type/CSV"  # NOSONAR
            in graph_text
        ), "CSV format URI should be present"

        assert "MediaType" in graph_text, "MediaType should be present"
        assert (
            "http://www.iana.org/assignments/media-types/text/csv" in graph_text
        ), "CSV media type URI should be present"

        expected_url = (
            f"{base_url}/datasets/{dataset.identifier}/data-dictionaries/download"
        )
        graph_text = g.serialize(format="turtle")

        required_elements = ["dcat:accessURL", "dcat:downloadURL", expected_url]

        for element in required_elements:
            assert (
                element in graph_text
            ), f"Required element '{element}' should be present in graph"


def test_distribution_temporal_constraint_date(
    db_session,
    setup_environment,
    config_service,
    sample_dataset,
    mock_dataset_permissions_service,
    mock_data_dictionary_repository,
    mock_identity,
):
    temporal_dist = None
    temporal_action = None

    for d in sample_dataset.distributions:
        for action in getattr(d, "policy_actions", []):
            if action.policy_constraint_type == "temporal":
                temporal_dist = d
                temporal_action = action
                break
        if temporal_dist:
            break

    assert (
        temporal_dist is not None
    ), "No distribution with temporal policy action found"
    assert temporal_action.temporal_restriction_start is not None
    assert temporal_action.temporal_restriction_end is not None

    repo = DatasetRepository(db_session)
    with patch.object(repo, "get_dataset_by_id", return_value=sample_dataset):
        svc = CatalogueService(
            dataset_repository=repo,
            applicable_legislation_repository=ApplicableLegislationRepository(
                db_session
            ),
            data_service_repository=DataServiceRepository(db_session),
            data_dictionary_repository=mock_data_dictionary_repository,
            dataset_permissions_service=mock_dataset_permissions_service,
            config_service=config_service,
        )

        mime, ttl = svc.get_individual_dataset_catalogue(
            "ttl", sample_dataset.id, mock_identity
        )
        assert mime == "text/turtle"

        g = Graph().parse(data=ttl, format="turtle")
        ODRL = Namespace("http://www.w3.org/ns/odrl/2/")  # NOSONAR

        constraints = list(g.triples((None, ODRL.leftOperand, ODRL.dateTime)))
        assert len(constraints) == 2

        right_values = [
            str(o)
            for (_, _, o) in g.triples((None, ODRL.rightOperand, None))
            if isinstance(o, Literal)
        ]
        assert any(
            v.startswith(temporal_action.temporal_restriction_start.isoformat())
            for v in right_values
        )
        assert any(
            v.startswith(temporal_action.temporal_restriction_end.isoformat())
            for v in right_values
        )


def test_dataset_version_uri_fragments(
    db_session,
    setup_environment,
    config_service,
    mock_dataset_permissions_service,
    mock_data_dictionary_repository,
):
    """Test that dataset versions get unique URIs using fragments for past versions"""
    repository = DatasetRepository(db_session)
    applicable_legislation_repository = ApplicableLegislationRepository(db_session)
    data_service_repository = DataServiceRepository(db_session)

    base_identifier = str(uuid.uuid4())

    # Create mock organisation for publisher
    organisation = MagicMock(spec=Organisation)
    organisation.name = "Test Organisation"
    organisation.type = "national_authority"
    organisation.email = "test@example.com"

    # Create version 1 (oldest) - has next_versions
    version1 = MagicMock(spec=Dataset)
    version1.id = 1
    version1.identifier = base_identifier
    version1.title = "Dataset v1"
    version1.description = "Version 1"
    version1.is_dataset_series = False
    version1.publisher = organisation
    version1.submitted_at = datetime(2023, 1, 1, 0, 0, 0)
    version1.periodicity = (
        "http://publications.europa.eu/resource/authority/frequency/ANNUAL"
    )
    version1.themes = []
    version1.spatial_coverages = []
    version1.applicable_legislations = []
    version1.languages = []
    version1.keywords = []
    version1.source_relations = []
    version1.dataset_types = []
    version1.data_protection_types = []
    version1.distributions = []
    version1.data_dictionaries = []
    version1.qualified_attributions = []
    version1.conforms_to = []
    version1.creators = set()
    version1.provenance = None
    version1.release_date = None
    version1.modified_at = None
    version1.version = "1.0"
    version1.contact = None
    version1.landing_pages = []
    version1.documentation_entries = []
    version1.rights_statement = (
        "http://publications.europa.eu/resource/authority/access-right/PUBLIC"
    )
    version1.series_memberships = []
    version1.member_datasets = []
    version1.previous_version = None

    # Create version 2 (middle) - has next_versions
    version2 = MagicMock(spec=Dataset)
    version2.id = 2
    version2.identifier = base_identifier
    version2.title = "Dataset v2"
    version2.description = "Version 2"
    version2.is_dataset_series = False
    version2.publisher = organisation
    version2.submitted_at = datetime(2023, 6, 1, 0, 0, 0)
    version2.periodicity = (
        "http://publications.europa.eu/resource/authority/frequency/ANNUAL"
    )
    version2.themes = []
    version2.spatial_coverages = []
    version2.applicable_legislations = []
    version2.languages = []
    version2.keywords = []
    version2.source_relations = []
    version2.dataset_types = []
    version2.data_protection_types = []
    version2.distributions = []
    version2.data_dictionaries = []
    version2.qualified_attributions = []
    version2.conforms_to = []
    version2.creators = set()
    version2.provenance = None
    version2.release_date = None
    version2.modified_at = None
    version2.version = "2.0"
    version2.contact = None
    version2.landing_pages = []
    version2.documentation_entries = []
    version2.rights_statement = (
        "http://publications.europa.eu/resource/authority/access-right/PUBLIC"
    )
    version2.series_memberships = []
    version2.member_datasets = []
    version2.previous_version = version1

    # Create version 3 (latest) - no next_versions
    version3 = MagicMock(spec=Dataset)
    version3.id = 3
    version3.identifier = base_identifier
    version3.title = "Dataset v3"
    version3.description = "Version 3"
    version3.is_dataset_series = False
    version3.publisher = organisation
    version3.submitted_at = datetime(2024, 1, 1, 0, 0, 0)
    version3.periodicity = (
        "http://publications.europa.eu/resource/authority/frequency/ANNUAL"
    )
    version3.themes = []
    version3.spatial_coverages = []
    version3.applicable_legislations = []
    version3.languages = []
    version3.keywords = []
    version3.source_relations = []
    version3.dataset_types = []
    version3.data_protection_types = []
    version3.distributions = []
    version3.data_dictionaries = []
    version3.qualified_attributions = []
    version3.conforms_to = []
    version3.creators = set()
    version3.provenance = None
    version3.release_date = None
    version3.modified_at = None
    version3.version = "3.0"
    version3.contact = None
    version3.landing_pages = []
    version3.documentation_entries = []
    version3.rights_statement = (
        "http://publications.europa.eu/resource/authority/access-right/PUBLIC"
    )
    version3.series_memberships = []
    version3.member_datasets = []
    version3.previous_version = version2

    # Set next_versions (past versions have next_versions)
    version1.next_versions = [version2]
    version2.next_versions = [version3]
    version3.next_versions = []  # Latest has no next versions

    all_versions = [version1, version2, version3]

    with patch.object(repository, "get_public_datasets", return_value=all_versions):
        catalogue_service = CatalogueService(
            dataset_repository=repository,
            applicable_legislation_repository=applicable_legislation_repository,
            data_service_repository=data_service_repository,
            data_dictionary_repository=mock_data_dictionary_repository,
            dataset_permissions_service=mock_dataset_permissions_service,
            config_service=config_service,
        )

        mime_type, rdf_text = catalogue_service.get_catalogue("ttl")

        g = Graph()
        g.parse(data=rdf_text, format="turtle")

        base_url = "https://test.example.com"

        # Version 1 (oldest, has next_versions) should have #version-1 fragment
        version1_uri = URIRef(f"{base_url}/datasets/{base_identifier}#version-1")

        # Version 2 (middle, has next_versions) should have #version-2 fragment
        version2_uri = URIRef(f"{base_url}/datasets/{base_identifier}#version-2")

        # Version 3 (latest, no next_versions) should have NO fragment
        version3_uri = URIRef(f"{base_url}/datasets/{base_identifier}")

        # Check that all three versions exist as separate dataset nodes
        assert (
            version1_uri,
            RDF.type,
            DCAT.Dataset,
        ) in g, "Version 1 should exist with #version-1 fragment"
        assert (
            version2_uri,
            RDF.type,
            DCAT.Dataset,
        ) in g, "Version 2 should exist with #version-2 fragment"
        assert (
            version3_uri,
            RDF.type,
            DCAT.Dataset,
        ) in g, "Version 3 (latest) should exist without fragment"

        # Check that each version has its own title
        v1_titles = list(g.objects(version1_uri, DCTERMS.title))
        v2_titles = list(g.objects(version2_uri, DCTERMS.title))
        v3_titles = list(g.objects(version3_uri, DCTERMS.title))

        assert len(v1_titles) == 1, "Version 1 should have exactly one title"
        assert len(v2_titles) == 1, "Version 2 should have exactly one title"
        assert len(v3_titles) == 1, "Version 3 should have exactly one title"

        assert str(v1_titles[0]) == "Dataset v1"
        assert str(v2_titles[0]) == "Dataset v2"
        assert str(v3_titles[0]) == "Dataset v3"


def test_health_categories_and_themes_in_rdf(
    db_session,
    sample_dataset,
    setup_environment,
    config_service,
    mock_dataset_permissions_service,
    mock_data_dictionary_repository,
):
    repository = DatasetRepository(db_session)
    applicable_legislation_repository = ApplicableLegislationRepository(db_session)
    data_service_repository = DataServiceRepository(db_session)

    with patch.object(repository, "get_public_datasets", return_value=[sample_dataset]):
        catalogue_service = CatalogueService(
            dataset_repository=repository,
            applicable_legislation_repository=applicable_legislation_repository,
            data_service_repository=data_service_repository,
            data_dictionary_repository=mock_data_dictionary_repository,
            dataset_permissions_service=mock_dataset_permissions_service,
            config_service=config_service,
        )

        mime_type, rdf_text = catalogue_service.get_catalogue("ttl")

        g = Graph()
        g.parse(data=rdf_text, format="turtle")

        assert mime_type == "text/turtle"
        assert len(rdf_text) > 0

        base_url = "https://test.example.com"
        dataset_uri = URIRef(f"{base_url}/datasets/{sample_dataset.identifier}")

        # Check that the dataset has health categories
        health_categories = list(g.objects(dataset_uri, HEALTHDCATAP.healthCategory))
        assert (
            len(health_categories) > 0
        ), "Dataset should have at least one health category"

        for category_uri in health_categories:
            assert (
                category_uri,
                RDF.type,
                SKOS.Concept,
            ) in g, f"Health category {category_uri} should be a SKOS Concept"

            labels = list(g.objects(category_uri, SKOS.prefLabel))
            assert (
                len(labels) > 0
            ), f"Health category {category_uri} should have a prefLabel"

        health_themes = list(g.objects(dataset_uri, HEALTHDCATAP.healthTheme))
        assert len(health_themes) > 0, "Dataset should have at least one health theme"

        for theme_uri in health_themes:
            assert (
                theme_uri,
                RDF.type,
                SKOS.Concept,
            ) in g, f"Health theme {theme_uri} should be a SKOS Concept"

            labels = list(g.objects(theme_uri, SKOS.prefLabel))
            assert len(labels) > 0, f"Health theme {theme_uri} should have a prefLabel"

        assert (
            "healthdcatap:" in rdf_text
            or "http://healthdataportal.eu/ns/health#" in rdf_text
        ), "RDF should contain Health DCAT-AP namespace"


def test_health_data_access_body_in_rdf(
    db_session,
    sample_dataset,
    setup_environment,
    config_service,
    mock_dataset_permissions_service,
    mock_data_dictionary_repository,
):
    repository = DatasetRepository(db_session)
    applicable_legislation_repository = ApplicableLegislationRepository(db_session)
    data_service_repository = DataServiceRepository(db_session)

    with patch.object(repository, "get_public_datasets", return_value=[sample_dataset]):
        catalogue_service = CatalogueService(
            dataset_repository=repository,
            applicable_legislation_repository=applicable_legislation_repository,
            data_service_repository=data_service_repository,
            data_dictionary_repository=mock_data_dictionary_repository,
            dataset_permissions_service=mock_dataset_permissions_service,
            config_service=config_service,
        )

        mime_type, rdf_text = catalogue_service.get_catalogue("ttl")

        g = Graph()
        g.parse(data=rdf_text, format="turtle")

        assert mime_type == "text/turtle"
        assert len(rdf_text) > 0

        base_url = "https://test.example.com"
        dataset_uri = URIRef(f"{base_url}/datasets/{sample_dataset.identifier}")

        hdabs = list(g.objects(dataset_uri, HEALTHDCATAP.hdab))
        assert len(hdabs) == 1, "Health dataset should have exactly one HDAB"

        hdab_uri = hdabs[0]

        assert isinstance(hdab_uri, URIRef), "HDAB should be a URI reference"
        assert str(hdab_uri) == "https://health.data.lu/hdab/luxembourg"

        assert (
            hdab_uri,
            RDF.type,
            FOAF.Organization,
        ) in g, "HDAB should be a FOAF Organization"

        hdab_names = list(g.objects(hdab_uri, FOAF.name))
        assert len(hdab_names) > 0, "HDAB should have a name"
        assert str(hdab_names[0]) == "Health Data Access Body Luxembourg"

        contact_points = list(g.objects(hdab_uri, DCAT.contactPoint))
        assert len(contact_points) == 1, "HDAB should have a contact point"

        contact_node = contact_points[0]

        assert (
            contact_node,
            RDF.type,
            VCARD.Kind,
        ) in g, "HDAB contact point should be a vcard:Kind"

        contact_names = list(g.objects(contact_node, VCARD.fn))
        assert len(contact_names) > 0, "HDAB contact should have a name"

        contact_emails = list(g.objects(contact_node, VCARD.hasEmail))
        assert len(contact_emails) > 0, "HDAB contact should have an email"
