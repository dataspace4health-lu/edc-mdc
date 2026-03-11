from typing import Optional
from rdflib import Literal, URIRef
from rdflib.namespace import DCTERMS, RDF, XSD, SKOS
from services.catalogues.mappers.namespace_constants import CDSP
from services.catalogues.builders.rdf_graph_builder import RDFGraphBuilder
from models.authentic_source_label import AuthenticSourceLabel
from models.authentic_source_assignment import AuthenticSourceAssignment
from services.config import ConfigService
from datetime import datetime


class AuthenticSourceLabelRDFBuilder:
    def __init__(self, graph_builder: RDFGraphBuilder, config: ConfigService) -> None:
        self.graph_builder = graph_builder
        self.graph = graph_builder.get_graph()
        self.config = config

    def add_authentic_source_label(self, label: AuthenticSourceLabel) -> None:
        label_uri = self.graph_builder.get_authentic_source_label_uri(label.id)

        self.graph.add((label_uri, RDF.type, CDSP.AuthenticSourceLabel))

        self._add_label_basic_properties(label_uri, label)
        self._add_label_status(label_uri, label)
        self._add_current_assignment(label_uri, label)

    def _add_label_basic_properties(
        self, label_uri: URIRef, label: AuthenticSourceLabel
    ) -> None:
        self.graph.add((label_uri, DCTERMS.title, Literal(label.name, lang="en")))

        if label.description:
            self.graph.add(
                (label_uri, DCTERMS.description, Literal(label.description, lang="en"))
            )

        current_assignment = self._get_current_assignment(label)
        if current_assignment and hasattr(current_assignment, "assigned_at"):
            self.graph.add(
                (
                    label_uri,
                    CDSP.assignedAt,
                    Literal(
                        current_assignment.assigned_at.isoformat(),
                        datatype=XSD.dateTime,
                    ),
                )
            )

    def _add_label_status(self, label_uri: URIRef, label: AuthenticSourceLabel) -> None:
        status = "deprecated" if label.is_deprecated else "assigned"
        status_uri = f"http://mindig_lu.gitlab.io/DCAT-AP-LU/vocab/cdsp/status/{status}"
        self.graph_builder.add_uri_resource_with_label(
            label_uri, CDSP.status, SKOS.Concept, status_uri, status.title()
        )

    def _add_current_assignment(
        self, label_uri: URIRef, label: AuthenticSourceLabel
    ) -> None:
        current_assignment = self._get_current_assignment(label)
        if not current_assignment:
            return

        dde = getattr(current_assignment, "data_dictionary_entry", None)
        dataset = getattr(dde, "dataset", None) if dde else None
        if not dataset:
            return

        self.graph.add(
            (label_uri, CDSP.datasetTitle, Literal(dataset.title, lang="en"))
        )
        self.graph.add((label_uri, CDSP.datasetIdentifier, Literal(dataset.identifier)))

    def _get_current_assignment(
        self, label: AuthenticSourceLabel
    ) -> Optional[AuthenticSourceAssignment]:
        if not label.assignments:
            return None
        return max(
            label.assignments,
            key=lambda a: getattr(a, "assigned_at", datetime.min) or datetime.min,
        )
