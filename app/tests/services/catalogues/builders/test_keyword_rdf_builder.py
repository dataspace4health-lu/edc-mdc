import pytest
from unittest.mock import MagicMock
from rdflib import Graph, Literal
from rdflib.namespace import RDF, SKOS

from models.dataset import Keyword
from services.catalogues.builders.keyword_rdf_builder import KeywordRDFBuilder
from services.catalogues.builders.rdf_graph_builder import RDFGraphBuilder


@pytest.fixture
def graph_builder():
    return RDFGraphBuilder("https://test.example.com")


@pytest.fixture
def keyword_rdf_builder(graph_builder):
    return KeywordRDFBuilder(graph_builder)


def test_add_keyword(graph_builder, keyword_rdf_builder):
    keyword = MagicMock(spec=Keyword)
    keyword.key = "test-keyword"
    keyword.eng_label = "Test Keyword"

    keyword_rdf_builder.add_keyword(keyword)

    g = graph_builder.get_graph()

    # Check that a blank node with SKOS.Concept type exists
    concepts = list(g.subjects(RDF.type, SKOS.Concept))
    assert len(concepts) == 1

    # Check that the label exists
    labels = list(g.objects(concepts[0], SKOS.prefLabel))
    assert len(labels) == 1
    assert labels[0] == Literal("Test Keyword", lang="en")
