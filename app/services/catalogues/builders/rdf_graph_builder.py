import os
from rdflib import BNode, Graph, URIRef, Literal
from rdflib.namespace import FOAF
from services.catalogues.mappers.namespace_constants import (
    NAMESPACE_BINDINGS,
    EU_R5R,
    ELI,
    RDF,
    RDFS,
    DCTERMS,
    SKOS,
)
from services.catalogues.mappers.type_mappers import TypeMappers

# Language URI to label mapping
LANGUAGE_LABELS = {
    "http://publications.europa.eu/resource/authority/language/DEU": "German",
    "http://publications.europa.eu/resource/authority/language/FRA": "French",
    "http://publications.europa.eu/resource/authority/language/ENG": "English",
    "http://publications.europa.eu/resource/authority/language/LTZ": "Luxembourgish",
}


class RDFGraphBuilder:
    def __init__(
        self, catalogue_url: str, uri_templates: dict = None, hdab_config: dict = None
    ):
        self.catalogue_url = catalogue_url
        self.uri_templates = uri_templates or {
            "datasets": "/api/v1/datasets/{identifier}",
            "data_services": "/api/v1/data-services/{id}",
            "sample_distribution_download": "/api/v1/datasets/{identifier}/data-dictionaries/download",
        }
        self.hdab_config = hdab_config or {}
        self.graph = Graph()
        self._bind_namespaces()

    def _bind_namespaces(self) -> None:
        for prefix, namespace in NAMESPACE_BINDINGS.items():
            self.graph.bind(prefix, namespace)

    def get_graph(self) -> Graph:
        return self.graph

    def get_catalogue_uri(self) -> URIRef:
        return URIRef(self.catalogue_url)

    def get_health_data_access_body_config(self) -> dict:
        return self.hdab_config

    def get_dataset_uri(
        self,
        dataset_identifier: str,
        is_latest_version: bool = True,
        version_number: str = None,
    ) -> URIRef:
        pattern = self.uri_templates["datasets"].format(identifier=dataset_identifier)
        base_uri = f"{self.catalogue_url}{pattern}"

        # Append fragment for past versions
        if not is_latest_version and version_number:
            return URIRef(f"{base_uri}#version-{version_number}")

        return URIRef(base_uri)

    def get_data_service_uri(self, service_id: int) -> URIRef:
        pattern = self.uri_templates["data_services"].format(id=service_id)
        return URIRef(f"{self.catalogue_url}{pattern}")

    def get_sample_distribution_download_uri(self, dataset_identifier: str) -> URIRef:
        pattern = self.uri_templates["sample_distribution_download"].format(
            identifier=dataset_identifier
        )
        return URIRef(f"{self.catalogue_url}{pattern}")

    def get_authentic_source_label_uri(self, label_id: int) -> URIRef:

        app_url = os.getenv("APP_URL")
        return URIRef(f"{app_url}/api/v1/authentic-source-labels/{label_id}")

    def serialize(self, format_type: str) -> tuple[str, str]:
        media_type = TypeMappers.map_media_type(format_type)
        rdflib_format = TypeMappers.map_rdflib_format(format_type)

        # Use max_depth to force inlining of URI resources in pretty-xml
        serialize_kwargs = {"format": rdflib_format}
        if rdflib_format == "pretty-xml":
            serialize_kwargs["max_depth"] = 10

        serialized_content = self.graph.serialize(**serialize_kwargs)
        return media_type, serialized_content

    def add_triple(self, subject: URIRef, predicate: URIRef, obj) -> None:
        self.graph.add((subject, predicate, obj))

    def reset(self) -> None:
        self.graph = Graph()
        self._bind_namespaces()

    def add_uri_resource_with_label(
        self,
        subject_uri: URIRef,
        property: URIRef,
        rdf_type: URIRef,
        value_uri: str,
        label: str = None,
    ) -> None:
        """Add a URI resource with RDF type and label (auto-generated from URI if not provided)."""
        resource_uri = URIRef(value_uri)
        self.graph.add((subject_uri, property, resource_uri))
        self.graph.add((resource_uri, RDF.type, rdf_type))

        # Use provided label or extract from URI
        if label is None:
            label = self._extract_label_from_uri(value_uri)
        self.graph.add((resource_uri, SKOS.prefLabel, Literal(label, lang="eng")))

    def _extract_label_from_uri(self, uri: str) -> str:
        """Extract human-readable label from URI by taking the last segment and formatting it."""
        # Get the last part after the final /
        label = uri.rstrip("/").split("/")[-1]
        # Replace underscores and hyphens with spaces
        label = label.replace("_", " ").replace("-", " ")
        # Title case (capitalize first letter of each word)
        return label.title()

    def convert_camelcase_to_label(self, text: str) -> str:
        """Convert camelCase or PascalCase to human-readable label with spaces."""
        import re

        # Insert space before uppercase letters (except at start)
        label = re.sub(r"(?<!^)(?=[A-Z])", " ", text)
        return label

    def add_document(
        self, subject_uri: URIRef, property: URIRef, document_url: str
    ) -> None:
        """Add a document resource (no label needed for external URLs)."""
        document_uri = URIRef(document_url)
        self.graph.add((subject_uri, property, document_uri))
        self.graph.add((document_uri, RDF.type, FOAF.Document))

    def add_language(self, uri: URIRef, lang: str) -> None:
        # Get label from mapping or auto-generate from URI
        label = LANGUAGE_LABELS.get(lang)
        self.add_uri_resource_with_label(
            uri, DCTERMS.language, DCTERMS.LinguisticSystem, lang, label
        )

    def add_legal_resource(
        self, uri: URIRef, legislation, resources, title_getter
    ) -> None:
        # Find the full resource object to get the link
        resource_obj = next(
            (x for x in resources if x.key == legislation.key),
            None,
        )

        # Use link if present, otherwise fall back to key
        legislation_uri = URIRef(
            resource_obj.link if resource_obj and resource_obj.link else legislation.key
        )

        legislation_title = (
            title_getter(resource_obj, legislation.key) if resource_obj else None
        )

        # Direct IRI reference required by DCAT-AP
        self.graph.add((uri, EU_R5R.applicableLegislation, legislation_uri))

        # Add type declaration for the legal resource
        self.graph.add((legislation_uri, RDF.type, ELI.LegalResource))

        # Optionally add label to the external resource
        if legislation_title:
            self.graph.add(
                (
                    legislation_uri,
                    RDFS.label,
                    Literal(lang="eng", lexical_or_value=legislation_title),
                )
            )
