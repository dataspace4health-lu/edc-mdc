from datetime import datetime
from typing import List
from rdflib import BNode, Literal, URIRef
from rdflib.namespace import DCAT, DCTERMS, FOAF, RDF, RDFS, XSD
from services.catalogues.mappers.namespace_constants import VCARD, SKOS

from models.dataset import Dataset
from models.data_service import DataService
from services.catalogues.builders.rdf_graph_builder import RDFGraphBuilder
from services.config import ConfigService


class CatalogueRDFBuilder:

    def __init__(self, graph_builder: RDFGraphBuilder, config: ConfigService) -> None:
        self.config = config
        self.graph_builder = graph_builder
        self.graph = graph_builder.get_graph()

    def add_catalogue_metadata(
        self, datasets: List[Dataset], data_services: List[DataService]
    ) -> None:
        catalogue_uri = self.graph_builder.get_catalogue_uri()
        self.graph.add((catalogue_uri, RDF.type, DCAT.Catalog))
        self.graph_builder.add_language(
            catalogue_uri,
            "http://publications.europa.eu/resource/authority/language/ENG",
        )
        self._add_theme_taxonomy(catalogue_uri)
        self._add_publisher(catalogue_uri)
        self._add_basic_metadata(catalogue_uri)
        self.graph_builder.add_uri_resource_with_label(
            catalogue_uri,
            DCTERMS.license,
            DCTERMS.LicenseDocument,
            "http://creativecommons.org/publicdomain/zero/1.0/",
        )

        homepage_url = self.config.get_catalogue()["url"]
        self.graph_builder.add_document(catalogue_uri, FOAF.homepage, homepage_url)

        self._add_data_service_links(catalogue_uri, data_services)

        self.graph.add(
            (
                catalogue_uri,
                DCTERMS.modified,
                Literal(datetime.now().isoformat(), datatype=XSD.dateTime),
            )
        )
        self.graph.add(
            (
                catalogue_uri,
                DCTERMS.issued,
                Literal(datetime.now().isoformat(), datatype=XSD.dateTime),
            )
        )

    def _add_publisher(self, catalogue_uri: URIRef) -> None:
        publisher = BNode()
        self.graph.add((publisher, RDF.type, FOAF.Organization))
        self.graph.add(
            (
                publisher,
                FOAF.name,
                Literal(
                    lang="eng",
                    lexical_or_value=self.config.get_catalogue()["publisher_name"],
                ),
            )
        )
        self.graph.add((catalogue_uri, DCTERMS.publisher, publisher))

        contact_node = BNode()
        self.graph.add((catalogue_uri, DCAT.contactPoint, contact_node))
        self.graph.add((contact_node, RDF.type, VCARD.Kind))
        self.graph.add((contact_node, RDF.type, VCARD.Organization))
        self.graph.add(
            (
                contact_node,
                VCARD.fn,
                Literal(self.config.get_catalogue()["publisher_name"], lang="eng"),
            )
        )

    def _add_basic_metadata(self, catalogue_uri: URIRef) -> None:
        # Title
        self.graph.add(
            (
                catalogue_uri,
                DCTERMS.title,
                Literal(
                    lang="eng", lexical_or_value=self.config.get_catalogue()["name"]
                ),
            )
        )

        # Description
        self.graph.add(
            (
                catalogue_uri,
                DCTERMS.description,
                Literal(
                    lang="eng",
                    lexical_or_value=self.config.get_catalogue()["description"],
                ),
            )
        )

    def _add_data_service_links(
        self, catalogue_uri: URIRef, data_services: List[DataService]
    ) -> None:
        for data_service in data_services:
            service_uri = self.graph_builder.get_data_service_uri(data_service.id)
            self.graph.add((catalogue_uri, DCAT.service, service_uri))

    def _add_theme_taxonomy(self, catalogue_uri: URIRef) -> None:
        theme_taxonomy_uri = URIRef(
            "http://publications.europa.eu/resource/authority/data-theme"
        )
        self.graph.add((catalogue_uri, DCAT.themeTaxonomy, theme_taxonomy_uri))
        self.graph.add((theme_taxonomy_uri, RDF.type, SKOS.ConceptScheme))
        self.graph.add(
            (
                theme_taxonomy_uri,
                SKOS.prefLabel,
                Literal("EU Data Theme Taxonomy", lang="eng"),
            )
        )
        self.graph.add(
            (
                theme_taxonomy_uri,
                DCTERMS.title,
                Literal("EU Data Theme Taxonomy", lang="eng"),
            )
        )
