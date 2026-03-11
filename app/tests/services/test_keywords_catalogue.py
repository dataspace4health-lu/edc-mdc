import os
import pytest
from unittest.mock import patch, MagicMock
from rdflib import Graph, Literal
from rdflib.namespace import RDF, SKOS

from models.dataset import Keyword
from services.keywords_catalogue import KeywordsCatalogueService
from repositories.keyword import KeywordRepository
from schemas.catalogue import CatalogueFormat


@pytest.fixture
def setup_environment():
    os.environ["APP_URL"] = "https://test.example.com"
    yield
    if "APP_URL" in os.environ:
        del os.environ["APP_URL"]


@pytest.fixture
def mock_keywords():
    keyword1 = MagicMock(spec=Keyword)
    keyword1.key = "keyword-1"
    keyword1.eng_label = "First Keyword"

    keyword2 = MagicMock(spec=Keyword)
    keyword2.key = "keyword-2"
    keyword2.eng_label = "Second Keyword"

    return [keyword1, keyword2]


def test_keywords_catalogue_rdf(db_session, mock_keywords, setup_environment):
    repository = KeywordRepository(db_session)

    with patch.object(repository, "get_all", return_value=mock_keywords):
        service = KeywordsCatalogueService(keyword_repository=repository)

        mime_type, rdf_text = service.get_catalogue(CatalogueFormat.RDF)

        assert mime_type == "application/rdf+xml"
        assert len(rdf_text) > 0

        g = Graph()
        g.parse(data=rdf_text, format="xml")

        # Check that concepts exist
        concepts = list(g.subjects(RDF.type, SKOS.Concept))
        assert len(concepts) == 2

        # Check that labels exist
        labels = [str(label) for label in g.objects(None, SKOS.prefLabel)]
        assert "First Keyword" in labels
        assert "Second Keyword" in labels
