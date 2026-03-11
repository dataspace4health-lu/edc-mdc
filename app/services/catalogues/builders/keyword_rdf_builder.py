from rdflib import Literal, BNode
from rdflib.namespace import RDF, SKOS
from services.catalogues.builders.rdf_graph_builder import RDFGraphBuilder
from models.dataset import Keyword


class KeywordRDFBuilder:
    def __init__(self, graph_builder: RDFGraphBuilder) -> None:
        self.graph_builder = graph_builder
        self.graph = graph_builder.get_graph()

    def add_keyword(self, keyword: Keyword) -> None:
        keyword_node = BNode()

        self.graph.add((keyword_node, RDF.type, SKOS.Concept))
        self.graph.add(
            (keyword_node, SKOS.prefLabel, Literal(keyword.eng_label, lang="en"))
        )
