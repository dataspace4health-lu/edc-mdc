import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import RDF, DCAT, DCTERMS, SKOS, XSD

from models.dataset import Dataset, DatasetCodingSystem
from models.dataset_relation import DatasetRelation
from models.data_dictionary import DataDictionaryEntry
from models.authentic_source_assignment import AuthenticSourceAssignment
from models.authentic_source_label import AuthenticSourceLabel
from services.catalogues.builders.dataset_rdf_builder import DatasetRDFBuilder
from services.catalogues.builders.rdf_graph_builder import RDFGraphBuilder
from repositories.applicable_legislation import ApplicableLegislationRepository
from repositories.data_dictionary import DataDictionaryRepository
from models.dataset import DatasetHealthLegalBasisEntry
from services.catalogues.mappers.namespace_constants import (
    CDSP,
    DPV,
    HEALTHDCATAP,
)


@pytest.fixture
def mock_authentic_source_data():
    # Create authentic source labels
    label1 = MagicMock(spec=AuthenticSourceLabel)
    label1.id = 1
    label1.name = "test-label-1"
    label1.description = "First test label description"

    label2 = MagicMock(spec=AuthenticSourceLabel)
    label2.id = 2
    label2.name = "test-label-2"
    label2.description = None  # Test case without description

    # Create data dictionary entries
    entry1 = MagicMock(spec=DataDictionaryEntry)
    entry1.id = 1
    entry1.field_name = "field_1"
    entry1.description = "Description for field 1"
    entry1.data_type = "string"
    entry1.is_authentic_source = True

    entry2 = MagicMock(spec=DataDictionaryEntry)
    entry2.id = 2
    entry2.field_name = "field_2"
    entry2.description = "Description for field 2"
    entry2.data_type = "integer"
    entry2.is_authentic_source = True

    entry3 = MagicMock(spec=DataDictionaryEntry)
    entry3.id = 3
    entry3.field_name = "field_3"
    entry3.description = "Description for field 3"
    entry3.data_type = "boolean"
    entry3.is_authentic_source = False  # Not an authentic source

    # Create assignments
    assignment1 = MagicMock(spec=AuthenticSourceAssignment)
    assignment1.id = 1
    assignment1.label = label1
    assignment1.is_active = True
    assignment1.assigned_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    assignment2 = MagicMock(spec=AuthenticSourceAssignment)
    assignment2.id = 2
    assignment2.label = label2
    assignment2.is_active = True
    assignment2.assigned_at = datetime(2023, 1, 2, 12, 0, 0, tzinfo=timezone.utc)

    assignment3 = MagicMock(spec=AuthenticSourceAssignment)
    assignment3.id = 3
    assignment3.label = label1
    assignment3.is_active = False  # Inactive assignment
    assignment3.assigned_at = datetime(2023, 1, 3, 12, 0, 0, tzinfo=timezone.utc)

    # Link assignments to entries
    entry1.authentic_source_assignments = [
        assignment1,
        assignment3,
    ]  # One active, one inactive
    entry2.authentic_source_assignments = [assignment2]  # One active
    entry3.authentic_source_assignments = []  # No assignments

    # Create dataset
    dataset = MagicMock(spec=Dataset)
    dataset.id = 100
    dataset.title = "Test Dataset with Authentic Sources"
    dataset.data_dictionaries = [entry1, entry2, entry3]

    return {
        "dataset": dataset,
        "entry1": entry1,
        "entry2": entry2,
        "entry3": entry3,
        "label1": label1,
        "label2": label2,
        "assignment1": assignment1,
        "assignment2": assignment2,
        "assignment3": assignment3,
    }


@pytest.fixture
def setup_rdf_builder():
    catalogue_url = "https://test.example.com"
    graph_builder = RDFGraphBuilder(catalogue_url)

    applicable_legislation_repo = MagicMock(spec=ApplicableLegislationRepository)
    data_dictionary_repo = MagicMock(spec=DataDictionaryRepository)

    return DatasetRDFBuilder(
        graph_builder, applicable_legislation_repo, data_dictionary_repo
    )


def test_add_authentic_sources_with_active_assignments(
    setup_rdf_builder, mock_authentic_source_data
):
    dataset_rdf_builder = setup_rdf_builder
    dataset = mock_authentic_source_data["dataset"]

    # Mock repository to return data dictionary entries
    dataset_rdf_builder.data_dictionary_repository.get_data_dictionaries_by_dataset_id.return_value = (
        dataset.data_dictionaries
    )

    # Get the graph and dataset URI
    graph = dataset_rdf_builder.graph
    dataset_uri = dataset_rdf_builder.graph_builder.get_dataset_uri(dataset.id)

    dataset_rdf_builder._add_authentic_sources(dataset_uri, dataset)

    # Check that authentic source triples were added
    authentic_source_triples = list(
        graph.triples((dataset_uri, CDSP.hasAuthenticSource, None))
    )
    assert (
        len(authentic_source_triples) == 2
    ), "Should have 2 authentic sources (entry1 and entry2)"

    # Collect all authentic source nodes
    auth_nodes = [triple[2] for triple in authentic_source_triples]

    # Check properties of authentic source nodes
    entry_names = []
    label_names = []

    for auth_node in auth_nodes:
        # Check entry name
        entry_name_triples = list(graph.triples((auth_node, CDSP.entryName, None)))
        assert (
            len(entry_name_triples) == 1
        ), f"Each authentic source should have exactly one entry name"
        entry_names.append(str(entry_name_triples[0][2]))

        # Check entry description
        entry_desc_triples = list(
            graph.triples((auth_node, CDSP.entryDescription, None))
        )
        assert (
            len(entry_desc_triples) == 1
        ), f"Each authentic source should have exactly one entry description"

        # Check label name
        label_name_triples = list(graph.triples((auth_node, CDSP.labelName, None)))
        assert (
            len(label_name_triples) == 1
        ), f"Each authentic source should have exactly one label name"
        label_names.append(str(label_name_triples[0][2]))

    # Verify we have the expected field names
    assert "field_1" in entry_names, "field_1 should be present"
    assert "field_2" in entry_names, "field_2 should be present"
    assert (
        "field_3" not in entry_names
    ), "field_3 should not be present (not authentic source)"

    # Verify we have the expected label names
    assert "test-label-1" in label_names, "test-label-1 should be present"
    assert "test-label-2" in label_names, "test-label-2 should be present"


def test_add_authentic_sources_no_data_dictionaries(setup_rdf_builder):
    dataset_rdf_builder = setup_rdf_builder

    # Create dataset without data dictionaries
    dataset = MagicMock(spec=Dataset)
    dataset.id = 200
    dataset.data_dictionaries = []

    # Mock repository to return empty list
    dataset_rdf_builder.data_dictionary_repository.get_data_dictionaries_by_dataset_id.return_value = (
        []
    )

    graph = dataset_rdf_builder.graph
    dataset_uri = dataset_rdf_builder.graph_builder.get_dataset_uri(dataset.id)

    # Should not raise an exception
    dataset_rdf_builder._add_authentic_sources(dataset_uri, dataset)

    # Should have no authentic source triples
    authentic_source_triples = list(
        graph.triples((dataset_uri, CDSP.hasAuthenticSource, None))
    )
    assert len(authentic_source_triples) == 0, "Should have no authentic sources"


def test_add_typical_age_fields(setup_rdf_builder):
    dataset_rdf_builder = setup_rdf_builder

    # Test with both min and max typical age
    dataset = MagicMock(spec=Dataset)
    dataset.id = 300
    dataset.min_typical_age = 18
    dataset.max_typical_age = 65

    graph = dataset_rdf_builder.graph
    dataset_uri = dataset_rdf_builder.graph_builder.get_dataset_uri(dataset.id)

    dataset_rdf_builder._add_typical_age(dataset_uri, dataset)

    # Check minTypicalAge
    min_age_triples = list(
        graph.triples((dataset_uri, HEALTHDCATAP.minTypicalAge, None))
    )
    assert len(min_age_triples) == 1, "Should have exactly one minTypicalAge"
    assert str(min_age_triples[0][2]) == "18"
    assert min_age_triples[0][2].datatype == XSD.nonNegativeInteger

    # Check maxTypicalAge
    max_age_triples = list(
        graph.triples((dataset_uri, HEALTHDCATAP.maxTypicalAge, None))
    )
    assert len(max_age_triples) == 1, "Should have exactly one maxTypicalAge"
    assert str(max_age_triples[0][2]) == "65"
    assert max_age_triples[0][2].datatype == XSD.nonNegativeInteger

    # Test with None values - should not add any triples
    dataset2 = MagicMock(spec=Dataset)
    dataset2.id = 301
    dataset2.min_typical_age = None
    dataset2.max_typical_age = None

    dataset_uri2 = dataset_rdf_builder.graph_builder.get_dataset_uri(dataset2.id)
    dataset_rdf_builder._add_typical_age(dataset_uri2, dataset2)

    assert (
        len(list(graph.triples((dataset_uri2, HEALTHDCATAP.minTypicalAge, None)))) == 0
    )
    assert (
        len(list(graph.triples((dataset_uri2, HEALTHDCATAP.maxTypicalAge, None)))) == 0
    )


def test_add_number_of_records(setup_rdf_builder):
    dataset_rdf_builder = setup_rdf_builder

    dataset = MagicMock(spec=Dataset)
    dataset.id = 400
    dataset.number_of_records = 750000

    graph = dataset_rdf_builder.graph
    dataset_uri = dataset_rdf_builder.graph_builder.get_dataset_uri(dataset.id)

    dataset_rdf_builder._add_number_of_records(dataset_uri, dataset)

    records_triples = list(
        graph.triples((dataset_uri, HEALTHDCATAP.numberOfRecords, None))
    )
    assert len(records_triples) == 1, "Should have exactly one numberOfRecords"
    assert str(records_triples[0][2]) == "750000"
    assert records_triples[0][2].datatype == XSD.nonNegativeInteger

    dataset2 = MagicMock(spec=Dataset)
    dataset2.id = 401
    dataset2.number_of_records = None

    dataset_uri2 = dataset_rdf_builder.graph_builder.get_dataset_uri(dataset2.id)
    dataset_rdf_builder._add_number_of_records(dataset_uri2, dataset2)

    assert (
        len(list(graph.triples((dataset_uri2, HEALTHDCATAP.numberOfRecords, None))))
        == 0
    )


def test_add_number_of_unique_individuals(setup_rdf_builder):
    dataset_rdf_builder = setup_rdf_builder

    dataset = MagicMock(spec=Dataset)
    dataset.id = 500
    dataset.number_of_unique_individuals = 45000

    graph = dataset_rdf_builder.graph
    dataset_uri = dataset_rdf_builder.graph_builder.get_dataset_uri(dataset.id)

    dataset_rdf_builder._add_number_of_unique_individuals(dataset_uri, dataset)

    individuals_triples = list(
        graph.triples((dataset_uri, HEALTHDCATAP.numberOfUniqueIndividuals, None))
    )
    assert (
        len(individuals_triples) == 1
    ), "Should have exactly one numberOfUniqueIndividuals"
    assert str(individuals_triples[0][2]) == "45000"
    assert individuals_triples[0][2].datatype == XSD.nonNegativeInteger

    dataset2 = MagicMock(spec=Dataset)
    dataset2.id = 501
    dataset2.number_of_unique_individuals = None

    dataset_uri2 = dataset_rdf_builder.graph_builder.get_dataset_uri(dataset2.id)
    dataset_rdf_builder._add_number_of_unique_individuals(dataset_uri2, dataset2)

    assert (
        len(
            list(
                graph.triples(
                    (dataset_uri2, HEALTHDCATAP.numberOfUniqueIndividuals, None)
                )
            )
        )
        == 0
    )


def test_add_population_coverage(setup_rdf_builder):
    dataset_rdf_builder = setup_rdf_builder

    dataset = MagicMock(spec=Dataset)
    dataset.id = 600
    dataset.population_coverage = "Adults aged 18-65 in Luxembourg"

    graph = dataset_rdf_builder.graph
    dataset_uri = dataset_rdf_builder.graph_builder.get_dataset_uri(dataset.id)

    dataset_rdf_builder._add_population_coverage(dataset_uri, dataset)

    coverage_triples = list(
        graph.triples((dataset_uri, HEALTHDCATAP.populationCoverage, None))
    )
    assert len(coverage_triples) == 1, "Should have exactly one populationCoverage"
    assert str(coverage_triples[0][2]) == "Adults aged 18-65 in Luxembourg"
    assert coverage_triples[0][2].language == "eng"

    dataset2 = MagicMock(spec=Dataset)
    dataset2.id = 601
    dataset2.population_coverage = None

    dataset_uri2 = dataset_rdf_builder.graph_builder.get_dataset_uri(dataset2.id)
    dataset_rdf_builder._add_population_coverage(dataset_uri2, dataset2)

    assert (
        len(list(graph.triples((dataset_uri2, HEALTHDCATAP.populationCoverage, None))))
        == 0
    )


def test_add_code_values(setup_rdf_builder):
    dataset_rdf_builder = setup_rdf_builder

    dataset = MagicMock(spec=Dataset)
    dataset.id = 602
    code_value_entry = MagicMock()
    code_value_entry.value = "ICD-10 Codes"
    dataset.code_values = [code_value_entry]

    graph = dataset_rdf_builder.graph
    dataset_uri = dataset_rdf_builder.graph_builder.get_dataset_uri(dataset.id)

    dataset_rdf_builder._add_code_values(dataset_uri, dataset)

    code_values_triples = list(
        graph.triples((dataset_uri, HEALTHDCATAP.hasCodeValues, None))
    )
    assert len(code_values_triples) == 1, "Should have exactly one hasCodeValues"
    assert str(code_values_triples[0][2]) == "ICD-10 Codes"
    assert code_values_triples[0][2].language == "eng"

    dataset2 = MagicMock(spec=Dataset)
    dataset2.id = 603
    dataset2.code_values = []

    dataset_uri2 = dataset_rdf_builder.graph_builder.get_dataset_uri(dataset2.id)
    dataset_rdf_builder._add_code_values(dataset_uri2, dataset2)

    assert (
        len(list(graph.triples((dataset_uri2, HEALTHDCATAP.hasCodeValues, None)))) == 0
    )


def test_add_purpose(setup_rdf_builder):
    dataset_rdf_builder = setup_rdf_builder

    dataset = MagicMock(spec=Dataset)
    dataset.id = 604
    dataset.purpose_entries = [
        MagicMock(value="Clinical research"),
        MagicMock(value="Public health monitoring"),
    ]

    graph = dataset_rdf_builder.graph
    dataset_uri = dataset_rdf_builder.graph_builder.get_dataset_uri(dataset.id)

    dataset_rdf_builder._add_purpose(dataset_uri, dataset)

    purpose_triples = list(graph.triples((dataset_uri, DPV.hasPurpose, None)))
    assert (
        len(purpose_triples) == 2
    ), "Should have one hasPurpose triple per purpose value"

    purpose_descriptions = {
        str(description)
        for _, _, purpose_node in purpose_triples
        for _, _, description in graph.triples(
            (purpose_node, DCTERMS.description, None)
        )
    }
    assert purpose_descriptions == {"Clinical research", "Public health monitoring"}

    purpose_types = [
        triple
        for _, _, purpose_node in purpose_triples
        for triple in graph.triples((purpose_node, RDF.type, DPV.Purpose))
    ]
    assert len(purpose_types) == 2, "Each purpose node should be typed as dpv:Purpose"

    dataset2 = MagicMock(spec=Dataset)
    dataset2.id = 605
    dataset2.purpose_entries = []
    dataset_uri2 = dataset_rdf_builder.graph_builder.get_dataset_uri(dataset2.id)
    dataset_rdf_builder._add_purpose(dataset_uri2, dataset2)

    assert len(list(graph.triples((dataset_uri2, DPV.hasPurpose, None)))) == 0


def test_add_coding_systems(setup_rdf_builder):
    dataset_rdf_builder = setup_rdf_builder

    dataset = MagicMock(spec=Dataset)
    dataset.id = 606
    coding_systems_obj = MagicMock(spec=DatasetCodingSystem)
    coding_systems_obj.value = "https://www.wikidata.org/entity/Q9006342"
    dataset.coding_systems = [coding_systems_obj]

    graph = dataset_rdf_builder.graph
    dataset_uri = dataset_rdf_builder.graph_builder.get_dataset_uri(dataset.id)

    dataset_rdf_builder._add_coding_systems(dataset_uri, dataset)

    coding_systems_triples = list(
        graph.triples((dataset_uri, HEALTHDCATAP.hasCodingSystem, None))
    )
    assert len(coding_systems_triples) == 1, "Should have exactly one hasCodingSystem"
    assert (
        str(coding_systems_triples[0][2]) == "https://www.wikidata.org/entity/Q9006342"
    )
    assert isinstance(coding_systems_triples[0][2], URIRef)

    type_triples = list(
        graph.triples((coding_systems_triples[0][2], RDF.type, DCTERMS.Standard))
    )
    assert len(type_triples) == 1, "Coding system should be typed as dct:Standard"

    dataset2 = MagicMock(spec=Dataset)
    dataset2.id = 607
    dataset2.coding_systems = []

    dataset_uri2 = dataset_rdf_builder.graph_builder.get_dataset_uri(dataset2.id)
    dataset_rdf_builder._add_coding_systems(dataset_uri2, dataset2)

    assert (
        len(list(graph.triples((dataset_uri2, HEALTHDCATAP.hasCodingSystem, None))))
        == 0
    )


def test_add_external_relation_is_referenced_by(setup_rdf_builder):
    dataset_rdf_builder = setup_rdf_builder

    relation = MagicMock(spec=DatasetRelation)
    relation.external_url = "https://example.com/referencing-doc"
    relation.external_role = "is-referenced-by"
    relation.external_description = None

    graph = dataset_rdf_builder.graph
    dataset_uri = dataset_rdf_builder.graph_builder.get_dataset_uri(700)

    dataset_rdf_builder._add_external_relation(dataset_uri, relation)

    is_referenced_by_triples = list(
        graph.triples((dataset_uri, DCTERMS.isReferencedBy, None))
    )
    assert len(is_referenced_by_triples) == 1
    assert str(is_referenced_by_triples[0][2]) == "https://example.com/referencing-doc"

    # Should NOT have a qualifiedRelation blank node
    qualified_triples = list(graph.triples((dataset_uri, DCAT.qualifiedRelation, None)))
    assert len(qualified_triples) == 0


def test_add_health_legal_basis(setup_rdf_builder):
    dataset_rdf_builder = setup_rdf_builder

    entry1 = MagicMock(spec=DatasetHealthLegalBasisEntry)
    entry1.value = "CSI Deliberation no. 21/028"
    entry2 = MagicMock(spec=DatasetHealthLegalBasisEntry)
    entry2.value = "GDPR Article 6"

    dataset = MagicMock(spec=Dataset)
    dataset.id = 700
    dataset.health_legal_basis_entries = [entry1, entry2]

    graph = dataset_rdf_builder.graph
    dataset_uri = dataset_rdf_builder.graph_builder.get_dataset_uri(dataset.id)

    dataset_rdf_builder._add_health_legal_basis(dataset_uri, dataset)

    legal_basis_triples = list(graph.triples((dataset_uri, DPV.hasLegalBasis, None)))
    assert len(legal_basis_triples) == 2, "Should have two hasLegalBasis entries"

    descriptions = set()
    for _, _, node in legal_basis_triples:
        type_triples = list(graph.triples((node, RDF.type, DPV.LegalBasis)))
        assert len(type_triples) == 1, "Each node should be typed as dpv:LegalBasis"
        desc_triples = list(graph.triples((node, DCTERMS.description, None)))
        assert len(desc_triples) == 1
        assert desc_triples[0][2].language == "eng"
        descriptions.add(str(desc_triples[0][2]))

    assert descriptions == {"CSI Deliberation no. 21/028", "GDPR Article 6"}
