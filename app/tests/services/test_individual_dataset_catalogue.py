import os
import pytest
import uuid
from datetime import date, datetime
from unittest.mock import patch, MagicMock, Mock
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DCAT, DCTERMS, RDF, FOAF

from models.identity_context import IdentityContext
from models.dataset import Dataset, DatasetLandingPage, SeriesMembership
from models.organisation import Organisation
from models.contact import Contact
from models.data_service import DataService, DataServiceEndpoint
from models.distribution import (
    Distribution,
    DistributionAccessUrl,
    DistributionDownloadUrl,
)
from services.catalogues.mappers.namespace_constants import CDSP, VCARD
from services.catalogue import CatalogueService
from services.config import ConfigService
from services.dataset_permissions_service import DatasetPermissionsService
from repositories.dataset import DatasetRepository
from repositories.applicable_legislation import ApplicableLegislationRepository
from repositories.data_service import DataServiceRepository
from repositories.data_dictionary import DataDictionaryRepository
from test_factory import sample_dataset
from datetime import datetime, timezone


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
    mock_config.get_health_data_access_body.return_value = None
    return mock_config


@pytest.fixture
def mock_dataset_permissions_service():
    mock_service = MagicMock(spec=DatasetPermissionsService)
    mock_service.validate_read_permissions.return_value = None
    return mock_service


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
        dataset.spatial_resolutions = []
        dataset.temporal_resolution = None
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
    membership1.series_id = 100
    membership1.dataset_id = 101
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


def test_get_individual_dataset_catalogue(
    db_session,
    mock_dataset_series,
    setup_environment,
    config_service,
    mock_dataset_permissions_service,
    mock_data_dictionary_repository,
    mock_identity,
):
    repository = DatasetRepository(db_session)
    applicable_legislation_repository = ApplicableLegislationRepository(db_session)
    data_service_repository = DataServiceRepository(db_session)

    member1 = mock_dataset_series["member1"]
    dataset_id = member1.id

    data_service = MagicMock(spec=DataService)
    data_service.id = 201
    data_service.title = "Test Data Service"
    data_service.description = "A service providing access to test data"
    data_service.name = "test-service"
    data_service.endpoints = []
    data_service.endpoint_url = "https://api.example.com/service"

    endpoint = MagicMock(spec=DataServiceEndpoint)
    endpoint.id = 301
    endpoint.service_id = 201
    endpoint.url = "https://api.example.com/data"
    endpoint.name = "data-endpoint"
    endpoint.description = "API endpoint for data access"
    endpoint.endpoint_url = "https://api.example.com/data"
    endpoint.endpoint_description = None
    data_service.endpoints = [endpoint]

    with patch.object(
        repository, "get_dataset_by_id", return_value=member1
    ), patch.object(
        data_service_repository, "get_data_services", return_value=[data_service]
    ):

        catalogue_service = CatalogueService(
            dataset_repository=repository,
            applicable_legislation_repository=applicable_legislation_repository,
            data_service_repository=data_service_repository,
            data_dictionary_repository=mock_data_dictionary_repository,
            dataset_permissions_service=mock_dataset_permissions_service,
            config_service=config_service,
        )

        format_name = "ttl"
        expected_mime = "text/turtle"
        mime_type, rdf_text = catalogue_service.get_individual_dataset_catalogue(
            format_name, dataset_id, mock_identity
        )

        # Verify that validate_read_permissions was called with the correct parameters
        mock_dataset_permissions_service.validate_read_permissions.assert_called_once_with(
            dataset_id, mock_identity
        )

        g = Graph()
        try:
            g.parse(data=rdf_text, format="turtle")
        except Exception as e:
            print(f"Failed to parse RDF: {e}")
            print(f"RDF content: {rdf_text[:300]}...")
            raise

        assert mime_type == expected_mime
        assert len(rdf_text) > 0

        base_url = "https://test.example.com"
        dataset_uri = URIRef(f"{base_url}/datasets/{member1.identifier}")

        dataset_triples = list(g.triples((dataset_uri, None, None)))
        assert (
            len(dataset_triples) > 0
        ), f"No triples found for dataset URI {dataset_uri}"

        dataset_type_found = False
        for s, p, o in g.triples((dataset_uri, RDF.type, None)):
            if o in (DCAT.Dataset, DCAT.DatasetSeries):
                dataset_type_found = True
                break
        assert (
            dataset_type_found
        ), f"Dataset {dataset_uri} has no proper rdf:type triple"

        # Individual dataset RDF does not include catalogue wrapper
        # Dataset is the root resource

        data_service_uri = URIRef(f"{base_url}/data-services/{data_service.id}")
        data_service_found = False
        for s, p, o in g.triples((data_service_uri, RDF.type, DCAT.DataService)):
            data_service_found = True
            break
        assert (
            data_service_found
        ), f"Data service {data_service_uri} not found in the graph"


def test_get_individual_dataset_catalogue_with_versions(
    db_session,
    mock_dataset_series,
    setup_environment,
    config_service,
    mock_dataset_permissions_service,
    mock_data_dictionary_repository,
    mock_identity,
):
    """Test that get_individual_dataset_catalogue with include_versions=True returns all versions"""
    repository = DatasetRepository(db_session)
    applicable_legislation_repository = ApplicableLegislationRepository(db_session)
    data_service_repository = DataServiceRepository(db_session)

    # Use the member datasets (not series) as they are regular datasets
    # These are properly mocked and won't have SQLAlchemy session issues
    member1 = mock_dataset_series["member1"]
    member2 = mock_dataset_series["member2"]
    member3 = mock_dataset_series["member3"]

    # Rename them to represent versions
    member1.title = "Dataset v1"
    member1.version = "1.0"
    member2.title = "Dataset v2"
    member2.version = "2.0"
    member3.title = "Dataset v3"
    member3.version = "3.0"

    # Simulate version chain
    all_versions = [member1, member2, member3]

    # Attach richer metadata to historical versions
    sample_distribution = MagicMock(spec=Distribution)
    sample_distribution.internal_only = False
    sample_distribution.description = "Historical distribution description"
    sample_distribution.title = "Historical Distribution"
    sample_distribution.id = 999
    sample_distribution.access_services = []
    sample_distribution.file_type = None
    sample_distribution.media_type = None
    sample_distribution.compression_format = None
    sample_distribution.packaging_format = None
    sample_distribution.languages = []
    sample_distribution.applicable_legislations = []
    sample_distribution.policy_actions = []
    sample_distribution.linked_schemas = []
    sample_distribution.rights_statement = None
    sample_distribution.license = None
    sample_distribution.availability = None
    sample_distribution.documentation_entries = []
    sample_distribution.byte_size = None
    sample_distribution.checksum = None
    sample_distribution.modification_date = None
    sample_distribution.release_date = None
    sample_distribution.distribution_dcat_status = None
    sample_distribution.spatial_resolution = None
    sample_distribution.temporal_resolution = None
    sample_distribution.access_urls = [
        DistributionAccessUrl(url="https://example.com/historical-access")
    ]
    sample_distribution.download_urls = [
        DistributionDownloadUrl(url="https://example.com/historical-download")
    ]
    sample_distribution.notes = None

    member1.distributions = [sample_distribution]

    data_dict_entry = MagicMock()
    data_dict_entry.field_name = "historical_field"
    data_dict_entry.description = "Historical field description"
    data_dict_entry.data_type = "string"
    data_dict_entry.personally_identifiable_variable = False
    data_dict_entry.required = False
    data_dict_entry.max_allowed_value = None
    data_dict_entry.min_allowed_value = None
    data_dict_entry.variable_unit = None
    data_dict_entry.allowed_values = None
    data_dict_entry.allowed_values_description = None
    data_dict_entry.privacy_risk_type = None
    data_dict_entry.is_authentic_source = False
    data_dict_entry.authentic_source_assignments = []
    data_dict_entry.dataset_id = member1.id
    member1.data_dictionaries = [data_dict_entry]

    # Configure mock repository to return data dictionaries for member1
    # Use a lambda with default parameter to capture the value
    mock_data_dictionary_repository.get_data_dictionaries_by_dataset_id = Mock(
        side_effect=lambda dataset_id: [data_dict_entry] if dataset_id == 101 else []
    )

    with patch.object(
        repository, "get_all_versions_of_dataset", return_value=all_versions
    ), patch.object(data_service_repository, "get_data_services", return_value=[]):

        catalogue_service = CatalogueService(
            dataset_repository=repository,
            applicable_legislation_repository=applicable_legislation_repository,
            data_service_repository=data_service_repository,
            data_dictionary_repository=mock_data_dictionary_repository,
            dataset_permissions_service=mock_dataset_permissions_service,
            config_service=config_service,
        )

        format_name = "ttl"
        mime_type, rdf_text = catalogue_service.get_individual_dataset_catalogue(
            format_name, member2.id, mock_identity, include_versions=True
        )

        # Verify permissions check
        mock_dataset_permissions_service.validate_read_permissions.assert_called_once_with(
            member2.id, mock_identity
        )

        # Verify get_all_versions_of_dataset was called
        repository.get_all_versions_of_dataset.assert_called_once_with(member2.id)

        g = Graph()
        try:
            g.parse(data=rdf_text, format="turtle")
        except Exception as e:
            print(f"Failed to parse RDF: {e}")
            print(f"RDF content: {rdf_text[:300]}...")
            raise

        base_url = "https://test.example.com"

        dataset_nodes = list(g.subjects(RDF.type, DCAT.Dataset))
        root_nodes = [
            node
            for node in dataset_nodes
            if isinstance(node, URIRef)
            and str(node).startswith(f"{base_url}/datasets/{member2.identifier}")
        ]
        assert (
            len(root_nodes) == 1
        ), f"Expected a single root dataset resource, found {len(root_nodes)}"

        dataset_uri = root_nodes[0]

        history_entries = list(g.objects(dataset_uri, CDSP.history))
        assert (
            len(history_entries) == len(all_versions) - 1
        ), "History should contain all other versions"

        expected_versions = {
            version.version for version in all_versions if version != member2
        }

        found_versions = set()
        version_entry_map = {}
        for entry in history_entries:
            version_literal = g.value(entry, DCAT.version)
            if version_literal:
                version_value = str(version_literal)
                found_versions.add(version_value)
                version_entry_map[version_value] = entry
            title_literal = g.value(entry, DCTERMS.title)
            assert (
                title_literal is not None
            ), "History entry should include dataset title"
            identifier_literal = g.value(entry, DCTERMS.identifier)
            assert (
                identifier_literal is not None
            ), "History entry should include dataset identifier"
            assert (
                g.value(entry, DCTERMS.description) is not None
            ), "History entry should include dataset description"

        assert (
            expected_versions == found_versions
        ), f"Expected version numbers {expected_versions}, found {found_versions}"

        # Verify detailed metadata exists for historical versions
        assert (
            "1.0" in version_entry_map
        ), "Expected to capture version 1.0 in version history"
        entry_v1 = version_entry_map["1.0"]
        assert list(
            g.objects(entry_v1, DCAT.distribution)
        ), "Historical version should include distributions"
        assert list(
            g.objects(entry_v1, FOAF.page)
        ), "Historical version should include data dictionary information"


def test_get_individual_dataset_catalogue_with_status(
    db_session,
    mock_dataset_series,
    setup_environment,
    config_service,
    mock_dataset_permissions_service,
    mock_data_dictionary_repository,
    mock_identity,
):

    repository = DatasetRepository(db_session)
    applicable_legislation_repository = ApplicableLegislationRepository(db_session)
    data_service_repository = DataServiceRepository(db_session)

    member1 = mock_dataset_series["member1"]
    member1.status = "PUBLISHED"
    dataset_id = member1.id

    with patch.object(
        repository, "get_dataset_by_id", return_value=member1
    ), patch.object(data_service_repository, "get_data_services", return_value=[]):

        catalogue_service = CatalogueService(
            dataset_repository=repository,
            applicable_legislation_repository=applicable_legislation_repository,
            data_service_repository=data_service_repository,
            data_dictionary_repository=mock_data_dictionary_repository,
            dataset_permissions_service=mock_dataset_permissions_service,
            config_service=config_service,
        )

        # Test with include_status=True
        format_name = "ttl"
        mime_type, rdf_text = catalogue_service.get_individual_dataset_catalogue(
            format_name, dataset_id, mock_identity, include_status=True
        )

        g = Graph()
        g.parse(data=rdf_text, format="turtle")

        base_url = "https://test.example.com"
        dataset_uri = URIRef(f"{base_url}/datasets/{member1.identifier}")

        # Check that cdsp:status is present
        status_triples = list(g.triples((dataset_uri, CDSP.status, None)))
        assert len(status_triples) == 1, "Should have exactly one cdsp:status triple"
        assert str(status_triples[0][2]) == "PUBLISHED", "Status should be PUBLISHED"

        # Test with include_status=False (default) - create new service with fresh graph
        catalogue_service2 = CatalogueService(
            dataset_repository=repository,
            applicable_legislation_repository=applicable_legislation_repository,
            data_service_repository=data_service_repository,
            data_dictionary_repository=mock_data_dictionary_repository,
            dataset_permissions_service=mock_dataset_permissions_service,
            config_service=config_service,
        )

        mime_type2, rdf_text2 = catalogue_service2.get_individual_dataset_catalogue(
            format_name, dataset_id, mock_identity, include_status=False
        )

        g2 = Graph()
        g2.parse(data=rdf_text2, format="turtle")

        # Check that cdsp:status is NOT present
        status_triples2 = list(g2.triples((dataset_uri, CDSP.status, None)))
        assert (
            len(status_triples2) == 0
        ), "Should have no cdsp:status triple when include_status=False"


def test_status_mapping_to_front_office(
    db_session,
    mock_dataset_series,
    setup_environment,
    config_service,
    mock_dataset_permissions_service,
    mock_data_dictionary_repository,
    mock_identity,
):
    repository = DatasetRepository(db_session)
    applicable_legislation_repository = ApplicableLegislationRepository(db_session)
    data_service_repository = DataServiceRepository(db_session)

    member1 = mock_dataset_series["member1"]
    dataset_id = member1.id

    with patch.object(data_service_repository, "get_data_services", return_value=[]):
        catalogue_service = CatalogueService(
            dataset_repository=repository,
            applicable_legislation_repository=applicable_legislation_repository,
            data_service_repository=data_service_repository,
            data_dictionary_repository=mock_data_dictionary_repository,
            dataset_permissions_service=mock_dataset_permissions_service,
            config_service=config_service,
        )

        base_url = "https://test.example.com"
        dataset_uri = URIRef(f"{base_url}/datasets/{member1.identifier}")

        # Test 1: PUBLISHED -> "PUBLISHED"
        with patch.object(repository, "get_dataset_by_id") as mock_get:
            member1.status = "PUBLISHED"
            member1.released_at = None
            mock_get.return_value = member1

            mime_type, rdf_text = catalogue_service.get_individual_dataset_catalogue(
                "ttl", dataset_id, mock_identity, include_status=True
            )

            g = Graph()
            g.parse(data=rdf_text, format="turtle")
            status_triples = list(g.triples((dataset_uri, CDSP.status, None)))
            assert len(status_triples) == 1
            assert str(status_triples[0][2]) == "PUBLISHED"

        # Test 2: DEPRECATED -> "DEPRECATED"
        catalogue_service2 = CatalogueService(
            dataset_repository=repository,
            applicable_legislation_repository=applicable_legislation_repository,
            data_service_repository=data_service_repository,
            data_dictionary_repository=mock_data_dictionary_repository,
            dataset_permissions_service=mock_dataset_permissions_service,
            config_service=config_service,
        )

        with patch.object(repository, "get_dataset_by_id") as mock_get:
            member1.status = "DEPRECATED"
            member1.released_at = None
            mock_get.return_value = member1

            mime_type, rdf_text = catalogue_service2.get_individual_dataset_catalogue(
                "ttl", dataset_id, mock_identity, include_status=True
            )

            g2 = Graph()
            g2.parse(data=rdf_text, format="turtle")
            status_triples = list(g2.triples((dataset_uri, CDSP.status, None)))
            assert len(status_triples) == 1
            assert str(status_triples[0][2]) == "DEPRECATED"

        # Test 3: APPROVED with released_at -> "WITHDRAWN" (unpublished)
        catalogue_service3 = CatalogueService(
            dataset_repository=repository,
            applicable_legislation_repository=applicable_legislation_repository,
            data_service_repository=data_service_repository,
            data_dictionary_repository=mock_data_dictionary_repository,
            dataset_permissions_service=mock_dataset_permissions_service,
            config_service=config_service,
        )

        with patch.object(repository, "get_dataset_by_id") as mock_get:
            member1.status = "APPROVED"
            member1.released_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_get.return_value = member1

            mime_type, rdf_text = catalogue_service3.get_individual_dataset_catalogue(
                "ttl", dataset_id, mock_identity, include_status=True
            )

            g3 = Graph()
            g3.parse(data=rdf_text, format="turtle")
            status_triples = list(g3.triples((dataset_uri, CDSP.status, None)))
            assert len(status_triples) == 1
            assert str(status_triples[0][2]) == "WITHDRAWN"

        # Test 4: APPROVED without released_at -> "APPROVED" (never published)
        catalogue_service4 = CatalogueService(
            dataset_repository=repository,
            applicable_legislation_repository=applicable_legislation_repository,
            data_service_repository=data_service_repository,
            data_dictionary_repository=mock_data_dictionary_repository,
            dataset_permissions_service=mock_dataset_permissions_service,
            config_service=config_service,
        )

        with patch.object(repository, "get_dataset_by_id") as mock_get:
            member1.status = "APPROVED"
            member1.released_at = None
            mock_get.return_value = member1

            mime_type, rdf_text = catalogue_service4.get_individual_dataset_catalogue(
                "ttl", dataset_id, mock_identity, include_status=True
            )

            g4 = Graph()
            g4.parse(data=rdf_text, format="turtle")
            status_triples = list(g4.triples((dataset_uri, CDSP.status, None)))
            assert len(status_triples) == 1
            assert str(status_triples[0][2]) == "APPROVED"


def test_contact_point_rdf_generation(
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

    # Setup organization
    organisation = MagicMock(spec=Organisation)
    organisation.id = 1
    organisation.name = "Test Organisation"
    organisation.email = "publisher@example.com"
    organisation.type = "national_authority"

    # Setup contact person
    contact = MagicMock(spec=Contact)
    contact.id = 10
    contact.name = "Jane Smith"
    contact.email = "jane.smith@example.com"
    contact.role = "Data Steward"

    # Test 1: Dataset WITH contact - should use vcard:Individual
    dataset_with_contact = MagicMock(spec=Dataset)
    dataset_with_contact.id = 100
    dataset_with_contact.title = "Dataset With Contact"
    dataset_with_contact.description = "Dataset that has a dedicated contact"
    dataset_with_contact.identifier = str(uuid.uuid4())
    dataset_with_contact.periodicity = (
        "http://publications.europa.eu/resource/authority/frequency/ANNUAL"
    )
    dataset_with_contact.time_period_start = date(2023, 1, 1)
    dataset_with_contact.time_period_end = date(2023, 12, 31)
    dataset_with_contact.rights_statement = (
        "http://publications.europa.eu/resource/authority/access-right/PUBLIC"
    )
    dataset_with_contact.publisher = organisation
    dataset_contact = MagicMock()
    dataset_contact.contact = contact
    dataset_contact.contact_id = contact.id
    dataset_with_contact.contacts = [dataset_contact]
    dataset_with_contact.themes = []
    dataset_with_contact.qualified_attributions = []
    dataset_with_contact.spatial_coverages = []
    dataset_with_contact.applicable_legislations = []
    dataset_with_contact.dataset_types = []
    dataset_with_contact.languages = []
    dataset_with_contact.distributions = []
    dataset_with_contact.source_relations = []
    dataset_with_contact.keywords = []
    dataset_with_contact.data_protection_types = []
    dataset_with_contact.data_dictionaries = []
    dataset_with_contact.conforms_to_values = []
    dataset_with_contact.creators = set()
    dataset_with_contact.provenance = None
    dataset_with_contact.release_date = None
    dataset_with_contact.modified_at = None
    dataset_with_contact.version = "1.0"
    dataset_with_contact.version_notes = None
    dataset_with_contact.user_id = 1
    dataset_with_contact.submitted_at = datetime(2023, 1, 1, 0, 0, 0)
    dataset_with_contact.landing_pages = []
    dataset_with_contact.documentation_entries = []
    dataset_with_contact.is_dataset_series = False
    dataset_with_contact.series_memberships = []
    dataset_with_contact.other_identifiers = []
    dataset_with_contact.was_generated_by = []
    dataset_with_contact.spatial_resolutions = []
    dataset_with_contact.temporal_resolution = None
    dataset_with_contact.status = "PUBLISHED"
    dataset_with_contact.released_at = None

    catalogue_service1 = CatalogueService(
        dataset_repository=repository,
        applicable_legislation_repository=applicable_legislation_repository,
        data_service_repository=data_service_repository,
        data_dictionary_repository=mock_data_dictionary_repository,
        dataset_permissions_service=mock_dataset_permissions_service,
        config_service=config_service,
    )

    with patch.object(
        repository, "get_dataset_by_id", return_value=dataset_with_contact
    ), patch.object(data_service_repository, "get_data_services", return_value=[]):

        _, rdf_text = catalogue_service1.get_individual_dataset_catalogue(
            "ttl", dataset_with_contact.id, mock_identity
        )

        g1 = Graph()
        g1.parse(data=rdf_text, format="turtle")

        base_url = "https://test.example.com"
        dataset_uri = URIRef(f"{base_url}/datasets/{dataset_with_contact.identifier}")

        # Find contact point blank node
        contact_points = list(g1.objects(dataset_uri, DCAT.contactPoint))
        assert len(contact_points) == 1, "Should have exactly one contact point"
        contact_point = contact_points[0]

        # Verify it's a vcard:Individual
        assert (contact_point, RDF.type, VCARD.Individual) in g1

        # Verify required DCAT-AP properties
        fn_values = list(g1.objects(contact_point, VCARD.fn))
        assert len(fn_values) == 1
        assert str(fn_values[0]) == "Jane Smith"

        email_values = list(g1.objects(contact_point, VCARD.hasEmail))
        assert len(email_values) == 1
        assert str(email_values[0]) == "mailto:jane.smith@example.com"

        # Verify optional role property
        role_values = list(g1.objects(contact_point, VCARD.role))
        assert len(role_values) == 1
        assert str(role_values[0]) == "Data Steward"
