from __future__ import annotations

from typing import List, Optional

from fastapi import Depends
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import DCAT, RDF

from repositories.organisation import OrganisationRepository
from schemas.qualified_attribution import QualifiedAttributionDto
from services.catalogues.mappers.namespace_constants import FOAF, PROV


class QualifiedAttributionRDFMapper:
    def __init__(
        self,
        organisation_repository: OrganisationRepository = Depends(
            OrganisationRepository
        ),
    ):
        self._organisation_repository = organisation_repository

    def map_qualified_attributions(
        self, graph: Graph, dataset_uri: URIRef | BNode
    ) -> List[QualifiedAttributionDto]:
        results: List[QualifiedAttributionDto] = []

        for attribution_node in graph.objects(dataset_uri, PROV.qualifiedAttribution):
            # Extract agent (organisation)
            agent_name = None
            for agent_node in graph.objects(attribution_node, PROV.agent):
                agent_name = self._get_literal(graph, agent_node, FOAF.name)
                if agent_name:
                    break

            if not agent_name:
                continue

            # Resolve organisation by name
            organisation = self._organisation_repository.find_by_name(agent_name)
            if not organisation:
                continue

            # Extract role
            role = None
            for role_uri in graph.objects(attribution_node, DCAT.hadRole):
                if isinstance(role_uri, URIRef):
                    # Extract role from INSPIRE URI pattern
                    # e.g., http://inspire.ec.europa.eu/metadata-codelist/ResponsiblePartyRole/pointofcontact
                    uri_str = str(role_uri)
                    if "/ResponsiblePartyRole/" in uri_str:
                        role_token = uri_str.split("/ResponsiblePartyRole/")[-1]
                        # Convert from lowercase no-space format to underscore format
                        # e.g., "pointofcontact" -> "point_of_contact"
                        role = self._normalize_role_from_uri(role_token)
                    break

            if not role:
                continue

            results.append(
                QualifiedAttributionDto(
                    organisation_id=organisation.id,
                    role=role,
                )
            )

        return results

    def _get_literal(
        self,
        graph: Graph,
        subject: URIRef | BNode,
        predicate: URIRef,
        languages: tuple = ("eng", "en", None),
    ) -> Optional[str]:
        candidates: list[Literal] = [
            obj for obj in graph.objects(subject, predicate) if isinstance(obj, Literal)
        ]
        for lang in languages:
            for literal in candidates:
                if literal.language == lang:
                    return str(literal)
        if candidates:
            return str(candidates[0])
        return None

    def _normalize_role_from_uri(self, role_token: str) -> str:
        # Map from INSPIRE lowercase format to DB camelCase format
        role_mapping = {
            "author": "author",
            "custodian": "custodian",
            "distributor": "distributor",
            "originator": "originator",
            "owner": "owner",
            "pointofcontact": "pointOfContact",
            "principalinvestigator": "principalInvestigator",
            "processor": "processor",
            "resourceprovider": "resourceProvider",
            "user": "user",
        }

        return role_mapping.get(role_token.lower(), role_token)
