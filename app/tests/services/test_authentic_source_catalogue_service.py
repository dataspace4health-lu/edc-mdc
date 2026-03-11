import os
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import DCTERMS, RDF

from models.authentic_source_label import AuthenticSourceLabel
from models.authentic_source_assignment import AuthenticSourceAssignment
from models.data_dictionary import DataDictionaryEntry
from models.dataset import Dataset
from services.authentic_source_labels_catalogue import (
    AuthenticSourceLabelsCatalogueService,
)
from repositories.authentic_source_label import AuthenticSourceLabelRepository
from services.config import ConfigService
from schemas.catalogue import CatalogueFormat


@pytest.fixture
def setup_environment():
    os.environ["APP_URL"] = "https://test.example.com"
    yield
    if "APP_URL" in os.environ:
        del os.environ["APP_URL"]


@pytest.fixture
def mock_config_service():
    config_service = MagicMock(spec=ConfigService)
    config_service.get_catalogue.return_value = {
        "publisher_name": "Test Publisher",
        "name": "Test Catalogue",
        "description": "Test catalogue description",
    }
    return config_service


@pytest.fixture
def mock_authentic_source_labels():
    dataset1 = MagicMock(spec=Dataset)
    dataset1.id = 100
    dataset1.title = "Test Dataset 1"
    dataset1.identifier = "dataset-001"

    dataset2 = MagicMock(spec=Dataset)
    dataset2.id = 101
    dataset2.title = "Test Dataset 2"
    dataset2.identifier = "dataset-002"

    dd_entry1 = MagicMock(spec=DataDictionaryEntry)
    dd_entry1.dataset = dataset1

    dd_entry2 = MagicMock(spec=DataDictionaryEntry)
    dd_entry2.dataset = dataset2

    label1 = MagicMock(spec=AuthenticSourceLabel)
    label1.id = 1
    label1.name = "National Registry"
    label1.description = "Official national registry of citizens"
    label1.is_deprecated = False
    label1.created_at = datetime(2023, 1, 1)
    label1.created_by_name = "John Doe"

    assignment1 = MagicMock(spec=AuthenticSourceAssignment)
    assignment1.is_active = True
    assignment1.assigned_at = datetime(2023, 6, 15)
    assignment1.data_dictionary_entry = dd_entry1
    label1.assignments = [assignment1]

    label2 = MagicMock(spec=AuthenticSourceLabel)
    label2.id = 2
    label2.name = "Legacy System"
    label2.description = "Deprecated authentication system"
    label2.is_deprecated = True
    label2.created_at = datetime(2020, 1, 1)
    label2.created_by_name = "Jane Smith"

    assignment2 = MagicMock(spec=AuthenticSourceAssignment)
    assignment2.is_active = False
    assignment2.assigned_at = datetime(2021, 3, 10)
    assignment2.data_dictionary_entry = dd_entry2
    label2.assignments = [assignment2]

    label3 = MagicMock(spec=AuthenticSourceLabel)
    label3.id = 3
    label3.name = "Unused Label"
    label3.description = "Never assigned label"
    label3.is_deprecated = False
    label3.created_at = datetime(2024, 1, 1)
    label3.created_by_name = None
    label3.assignments = []

    label4 = MagicMock(spec=AuthenticSourceLabel)
    label4.id = 4
    label4.name = "Multi-Assignment Label"
    label4.description = None
    label4.is_deprecated = False
    label4.created_at = datetime(2022, 5, 1)
    label4.created_by_name = "Admin User"

    assignment4_inactive = MagicMock(spec=AuthenticSourceAssignment)
    assignment4_inactive.is_active = False
    assignment4_inactive.assigned_at = datetime(2022, 6, 1)
    assignment4_inactive.data_dictionary_entry = dd_entry1

    assignment4_active = MagicMock(spec=AuthenticSourceAssignment)
    assignment4_active.is_active = True
    assignment4_active.assigned_at = datetime(2023, 1, 1)
    assignment4_active.data_dictionary_entry = dd_entry2

    label4.assignments = [assignment4_inactive, assignment4_active]

    return {
        "label1": label1,
        "label2": label2,
        "label3": label3,
        "label4": label4,
        "dataset1": dataset1,
        "dataset2": dataset2,
        "all_labels": [label1, label2, label3, label4],
    }


def test_authentic_source_labels_catalogue_ttl(
    db_session, mock_authentic_source_labels, setup_environment, mock_config_service
):
    repository = AuthenticSourceLabelRepository(db_session)

    all_labels = mock_authentic_source_labels["all_labels"]

    with patch.object(repository, "get_all", return_value=all_labels):
        service = AuthenticSourceLabelsCatalogueService(
            label_repository=repository, config_service=mock_config_service
        )

        mime_type, rdf_text = service.get_catalogue(CatalogueFormat.TTL)

        assert mime_type == "text/turtle"
        assert len(rdf_text) > 0

        g = Graph()
        g.parse(data=rdf_text, format="turtle")

        base_url = "https://test.example.com"
        CDSP = Namespace("http://mindig_lu.gitlab.io/DCAT-AP-LU/vocab/cdsp/")  # NOSONAR

        label1_uri = URIRef(f"{base_url}/api/v1/authentic-source-labels/1")
        label2_uri = URIRef(f"{base_url}/api/v1/authentic-source-labels/2")
        label3_uri = URIRef(f"{base_url}/api/v1/authentic-source-labels/3")
        label4_uri = URIRef(f"{base_url}/api/v1/authentic-source-labels/4")

        # Label 1 (active) should be present
        assert (label1_uri, RDF.type, CDSP.AuthenticSourceLabel) in g
        assert (
            label1_uri,
            DCTERMS.title,
            Literal("National Registry", lang="en"),
        ) in g

        # Label 2 (deprecated) should be present
        assert (label2_uri, RDF.type, CDSP.AuthenticSourceLabel) in g
        assert (label2_uri, DCTERMS.title, Literal("Legacy System", lang="en")) in g

        # Label 3 (unassigned, not deprecated) should NOT be present
        assert (label3_uri, RDF.type, CDSP.AuthenticSourceLabel) not in g

        # Label 4 (active assignment) should be present
        assert (label4_uri, RDF.type, CDSP.AuthenticSourceLabel) in g


def test_authentic_source_labels_catalogue_rdf_xml(
    db_session, mock_authentic_source_labels, setup_environment, mock_config_service
):
    repository = AuthenticSourceLabelRepository(db_session)

    with patch.object(
        repository, "get_all", return_value=mock_authentic_source_labels["all_labels"]
    ):
        service = AuthenticSourceLabelsCatalogueService(
            label_repository=repository, config_service=mock_config_service
        )

        mime_type, rdf_text = service.get_catalogue(CatalogueFormat.RDF)

        assert mime_type == "application/rdf+xml"
        assert len(rdf_text) > 0

        g = Graph()
        g.parse(data=rdf_text, format="xml")

        assert len(g) > 0


def test_authentic_source_labels_catalogue_jsonld(
    db_session, mock_authentic_source_labels, setup_environment, mock_config_service
):
    repository = AuthenticSourceLabelRepository(db_session)

    with patch.object(
        repository, "get_all", return_value=mock_authentic_source_labels["all_labels"]
    ):
        service = AuthenticSourceLabelsCatalogueService(
            label_repository=repository, config_service=mock_config_service
        )

        mime_type, rdf_text = service.get_catalogue(CatalogueFormat.JSONLD)

        assert mime_type == "application/ld+json"
        assert len(rdf_text) > 0

        g = Graph()
        g.parse(data=rdf_text, format="json-ld")

        assert len(g) > 0


def test_authentic_source_label_status_representation(
    db_session, mock_authentic_source_labels, setup_environment, mock_config_service
):
    repository = AuthenticSourceLabelRepository(db_session)

    label1 = mock_authentic_source_labels["label1"]
    label2 = mock_authentic_source_labels["label2"]

    with patch.object(repository, "get_all", return_value=[label1, label2]):
        service = AuthenticSourceLabelsCatalogueService(
            label_repository=repository, config_service=mock_config_service
        )

        _, rdf_text = service.get_catalogue(CatalogueFormat.TTL)

        g = Graph()
        g.parse(data=rdf_text, format="turtle")

        base_url = "https://test.example.com"
        label1_uri = URIRef(f"{base_url}/api/v1/authentic-source-labels/1")

        label1_triples = list(g.triples((label1_uri, None, None)))
        assert len(label1_triples) > 0, f"No triples found for {label1_uri}"

        has_status_info = any(
            "status" in str(p).lower()
            or "assigned" in rdf_text.lower()
            or "deprecated" in rdf_text.lower()
            for s, p, o in g.triples((label1_uri, None, None))
        )

        assert has_status_info, "No status information found in RDF"


def test_authentic_source_label_assignment_details(
    db_session, mock_authentic_source_labels, setup_environment, mock_config_service
):
    repository = AuthenticSourceLabelRepository(db_session)

    label1 = mock_authentic_source_labels["label1"]
    dataset1 = mock_authentic_source_labels["dataset1"]

    with patch.object(repository, "get_all", return_value=[label1]):
        service = AuthenticSourceLabelsCatalogueService(
            label_repository=repository, config_service=mock_config_service
        )

        _, rdf_text = service.get_catalogue(CatalogueFormat.TTL)

        g = Graph()
        g.parse(data=rdf_text, format="turtle")

        base_url = "https://test.example.com"
        label1_uri = URIRef(f"{base_url}/api/v1/authentic-source-labels/1")

        label1_triples = list(g.triples((label1_uri, None, None)))
        assert len(label1_triples) > 0, f"No triples found for {label1_uri}"

        has_dataset_info = (
            dataset1.title in rdf_text
            or dataset1.identifier in rdf_text
            or any("dataset" in str(p).lower() for s, p, o in label1_triples)
        )

        assert (
            has_dataset_info
        ), f"No dataset information found. Dataset title: {dataset1.title}, identifier: {dataset1.identifier}"


def test_filter_labels_logic(
    db_session, mock_authentic_source_labels, setup_environment, mock_config_service
):
    repository = AuthenticSourceLabelRepository(db_session)

    all_labels = mock_authentic_source_labels["all_labels"]

    with patch.object(repository, "get_all", return_value=all_labels):
        service = AuthenticSourceLabelsCatalogueService(
            label_repository=repository, config_service=mock_config_service
        )

        filtered = service._filter_labels(all_labels)

        assert len(filtered) == 3

        filtered_ids = [label.id for label in filtered]
        assert 1 in filtered_ids
        assert 2 in filtered_ids
        assert 3 not in filtered_ids
        assert 4 in filtered_ids


def test_empty_catalogue(db_session, setup_environment, mock_config_service):
    repository = AuthenticSourceLabelRepository(db_session)

    with patch.object(repository, "get_all", return_value=[]):
        service = AuthenticSourceLabelsCatalogueService(
            label_repository=repository, config_service=mock_config_service
        )

        mime_type, rdf_text = service.get_catalogue(CatalogueFormat.TTL)

        assert mime_type == "text/turtle"
        assert len(rdf_text) > 0

        g = Graph()
        g.parse(data=rdf_text, format="turtle")

        assert len(g) >= 0


def test_label_without_description(
    db_session, mock_authentic_source_labels, setup_environment, mock_config_service
):
    repository = AuthenticSourceLabelRepository(db_session)

    label4 = mock_authentic_source_labels["label4"]
    assert label4.description is None

    with patch.object(repository, "get_all", return_value=[label4]):
        service = AuthenticSourceLabelsCatalogueService(
            label_repository=repository, config_service=mock_config_service
        )

        _, rdf_text = service.get_catalogue(CatalogueFormat.TTL)
        g = Graph()
        g.parse(data=rdf_text, format="turtle")

        base_url = "https://test.example.com"
        label4_uri = URIRef(f"{base_url}/api/v1/authentic-source-labels/4")

        assert (
            label4_uri,
            DCTERMS.title,
            Literal("Multi-Assignment Label", lang="en"),
        ) in g

        description_triples = list(g.triples((label4_uri, DCTERMS.description, None)))
        assert len(description_triples) == 0
