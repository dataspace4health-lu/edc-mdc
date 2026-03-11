from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fastapi import Depends
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import DCAT, RDF

from models.identity_context import IdentityContext
from services.catalogues.mappers.namespace_constants import VCARD
from repositories.contact import ContactRepository
from schemas.contact import ContactDto, ResourceContact, contact_entity_to_resource
from services.contact import ContactService


@dataclass
class ContactRDFDetails:
    name: Optional[str]
    email: Optional[str]
    role: Optional[str]


class ContactImportService:
    def __init__(
        self,
        contact_service: ContactService = Depends(ContactService),
        contact_repository: ContactRepository = Depends(ContactRepository),
    ):
        self._contact_service = contact_service
        self._contact_repository = contact_repository

    def ensure_contacts_from_graph(
        self,
        graph: Graph,
        dataset_uri: URIRef | BNode,
        organisation_id: int,
        identity: IdentityContext,
        skip_permission_validation: bool = False,
    ) -> list[ResourceContact]:
        all_details = self._extract_all_contact_details(graph, dataset_uri)
        if not all_details:
            return []

        contacts = []
        for details in all_details:
            if details.email:
                contact = self._ensure_contact_exists(
                    details, organisation_id, identity, skip_permission_validation
                )
                contacts.append(contact)
        return contacts

    def _ensure_contact_exists(
        self,
        details: ContactRDFDetails,
        organisation_id: int,
        identity: IdentityContext,
        skip_permission_validation: bool,
    ) -> ResourceContact:
        contact_dto = ContactDto(
            name=details.name or details.email,
            email=details.email,
            role=details.role,
        )

        existing_contact = self._contact_repository.get_contact_by_email(
            organisation_id, contact_dto.email
        )

        if existing_contact:
            if self._needs_update(existing_contact, contact_dto):
                return self._contact_service.update_contact(
                    organisation_id,
                    existing_contact.id,
                    contact_dto,
                    identity,
                    skip_permission_validation=skip_permission_validation,
                )

            return contact_entity_to_resource(existing_contact)

        return self._contact_service.add_contact(
            organisation_id,
            contact_dto,
            identity,
            skip_permission_validation=skip_permission_validation,
        )

    def _needs_update(self, contact, contact_dto: ContactDto) -> bool:
        # Normalize empty string and None for comparison to avoid phantom updates
        current_role = contact.role or None
        new_role = contact_dto.role or None

        return contact.name != contact_dto.name or current_role != new_role

    def _extract_all_contact_details(
        self, graph: Graph, dataset_uri: URIRef | BNode
    ) -> list[ContactRDFDetails]:
        contacts = []
        for contact_point in graph.objects(dataset_uri, DCAT.contactPoint):
            name = self._get_literal(graph, contact_point, VCARD.fn)
            email_iri = self._get_first_uri(graph, contact_point, VCARD.hasEmail)
            role = self._get_literal(graph, contact_point, VCARD.role)

            email = self._normalise_email(email_iri)
            if not email:
                continue

            contacts.append(ContactRDFDetails(name=name, email=email, role=role))

        return contacts

    def _parse_graph(self, rdf_content: str, rdf_format: str) -> Graph:
        graph = Graph()
        graph.parse(data=rdf_content, format=self._normalise_rdf_format(rdf_format))
        return graph

    def _select_dataset_resource(self, graph: Graph) -> URIRef | BNode:
        resources = list(graph.subjects(RDF.type, DCAT.Dataset))
        if not resources:
            resources = list(graph.subjects(RDF.type, DCAT.DatasetSeries))
        if not resources:
            raise ValueError("No DCAT dataset resource found in RDF payload.")
        return resources[0]

    def _get_literal(
        self,
        graph: Graph,
        subject: URIRef | BNode,
        predicate: URIRef,
    ) -> Optional[str]:
        for obj in graph.objects(subject, predicate):
            if isinstance(obj, Literal):
                return str(obj)
        return None

    def _get_first_uri(
        self, graph: Graph, subject: URIRef | BNode, predicate: URIRef
    ) -> Optional[str]:
        for obj in graph.objects(subject, predicate):
            return str(obj)
        return None

    def _normalise_rdf_format(self, rdf_format: str) -> str:
        fmt = (rdf_format or "").lower()
        if fmt in {"rdf", "pretty-xml", "application/rdf+xml", "xml"}:
            return "xml"
        if fmt in {"jsonld", "json-ld", "application/ld+json"}:
            return "json-ld"
        if fmt in {"ttl", "turtle", "text/turtle"}:
            return "turtle"
        return fmt or "turtle"

    def _normalise_email(self, email_iri: Optional[str]) -> Optional[str]:
        if not email_iri:
            return None
        email_iri = email_iri.strip()
        if email_iri.startswith("mailto:"):
            return email_iri[len("mailto:") :]
        return email_iri
