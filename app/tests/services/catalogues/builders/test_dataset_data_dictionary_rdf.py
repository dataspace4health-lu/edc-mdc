import pytest
from unittest.mock import MagicMock
from rdflib import Literal
from rdflib.namespace import XSD, RDFS, RDF

from models.dataset import Dataset
from models.data_dictionary import DataDictionaryEntry
from services.catalogues.builders.dataset_rdf_builder import DatasetRDFBuilder
from services.catalogues.builders.rdf_graph_builder import RDFGraphBuilder
from services.catalogues.mappers.namespace_constants import CSVW, CDSP, DPV
from repositories.applicable_legislation import ApplicableLegislationRepository
from repositories.data_dictionary import DataDictionaryRepository


@pytest.fixture
def dataset_rdf_builder():
    catalogue_url = "https://test.example.com"
    graph_builder = RDFGraphBuilder(catalogue_url)
    applicable_legislation_repo = MagicMock(spec=ApplicableLegislationRepository)
    data_dictionary_repo = MagicMock(spec=DataDictionaryRepository)
    return DatasetRDFBuilder(
        graph_builder, applicable_legislation_repo, data_dictionary_repo
    )


def test_add_data_dictionary_all_fields(dataset_rdf_builder):
    graph = dataset_rdf_builder.graph

    entry = MagicMock(spec=DataDictionaryEntry)
    entry.field_name = "population"
    entry.description = "Population count"
    entry.data_type = "integer"
    entry.personally_identifiable_variable = True
    entry.required = True
    entry.max_allowed_value = 100.0
    entry.min_allowed_value = 1.0
    entry.variable_unit = "persons"
    entry.allowed_values = "1, 2, 3"
    entry.allowed_values_description = "1=low;2=medium;3=high"
    entry.privacy_risk_type = "low"
    entry.is_authentic_source = False
    entry.authentic_source_assignments = []

    dataset = MagicMock(spec=Dataset)
    dataset.id = 1
    dataset.identifier = "dataset-123"
    dataset.data_dictionaries = [entry]

    # Mock repository to return data dictionary entries
    dataset_rdf_builder.data_dictionary_repository.get_data_dictionaries_by_dataset_id.return_value = [
        entry
    ]

    dataset_uri = dataset_rdf_builder.graph_builder.get_dataset_uri(dataset.identifier)
    dataset_rdf_builder._add_data_dictionary(dataset_uri, dataset)

    entry_nodes = list(graph.subjects(CSVW.name, Literal(entry.field_name)))
    assert len(entry_nodes) == 1, "Expected exactly one data dictionary entry node"
    entry_node = entry_nodes[0]

    assert (
        entry_node,
        CSVW.required,
        Literal(True, datatype=XSD.boolean),
    ) in graph
    assert (
        entry_node,
        RDF.type,
        DPV.PersonalData,
    ) in graph
    assert (
        entry_node,
        CSVW.maxInclusive,
        Literal(100.0, datatype=XSD.decimal),
    ) in graph
    assert (
        entry_node,
        CSVW.minInclusive,
        Literal(1.0, datatype=XSD.decimal),
    ) in graph
    assert (
        entry_node,
        CSVW.unit,
        Literal("persons"),
    ) in graph
    assert (
        entry_node,
        RDFS.comment,
        Literal(entry.allowed_values_description, lang="eng"),
    ) in graph

    in_values = list(graph.objects(entry_node, CSVW["in"]))
    assert len(in_values) == 1, "Expected a single allowed values literal"
    assert in_values[0] == Literal("1, 2, 3", lang="eng")

    assert (
        entry_node,
        CDSP.privacyRiskType,
        Literal(entry.privacy_risk_type, lang="eng"),
    ) in graph
