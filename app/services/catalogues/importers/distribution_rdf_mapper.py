from __future__ import annotations

from datetime import date, datetime
from typing import Iterable, Optional, Set

from fastapi import Depends
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import DCAT, DCTERMS, RDF, RDFS, FOAF

from repositories.applicable_legislation import ApplicableLegislationRepository
from schemas.distribution import DistributionDto, PolicyActionDto
from services.catalogues.importers.documentation_utils import get_documentation_values
from services.catalogues.mappers.namespace_constants import (
    ADMS,
    EU_R5R,
    HEALTHDCATAP,
    ODRL,
    SPDX,
)


class DistributionRDFMapper:
    def __init__(
        self,
        applicable_legislation_repository: ApplicableLegislationRepository = Depends(
            ApplicableLegislationRepository
        ),
    ):
        self._applicable_legislation_repository = applicable_legislation_repository

    def map_distributions(
        self, graph: Graph, dataset_uri: URIRef | BNode
    ) -> list[DistributionDto]:
        distributions: list[DistributionDto] = []

        # Map normal distributions (dcat:distribution)
        for dist_node in graph.objects(dataset_uri, DCAT.distribution):
            try:
                dist_dto = self._map_single_distribution(
                    graph, dist_node, is_analytics=False
                )
                if dist_dto:
                    distributions.append(dist_dto)
            except Exception:
                # Skip distributions that fail to parse
                continue

        # Map analytics distributions (healthdcatap:analytics)
        for dist_node in graph.objects(dataset_uri, HEALTHDCATAP.analytics):
            try:
                dist_dto = self._map_single_distribution(
                    graph, dist_node, is_analytics=True
                )
                if dist_dto:
                    distributions.append(dist_dto)
            except Exception:
                # Skip distributions that fail to parse
                continue

        return distributions

    def _map_single_distribution(
        self, graph: Graph, dist_uri: URIRef | BNode, is_analytics: bool = False
    ) -> Optional[DistributionDto]:
        # Check if this is a sample distribution (data dictionary)
        is_sample = any(
            s for s in graph.subjects(ADMS.sample, dist_uri) if s is not None
        )
        if is_sample:
            return None  # Skip sample distributions

        # Basic required fields
        title = self._get_literal(graph, dist_uri, DCTERMS.title)
        if not title:
            return None

        description = self._get_literal(graph, dist_uri, DCTERMS.description)
        # Description is optional, but if provided must be at least 8 characters
        if description is not None and len(description) < 8:
            return None

        rights_statement = self._get_uri_value(graph, dist_uri, DCTERMS.rights)
        if not rights_statement:
            return None

        # Optional fields
        download_urls = self._get_uri_set(graph, dist_uri, DCAT.downloadURL)
        access_urls = self._get_uri_set(graph, dist_uri, DCAT.accessURL)

        file_type = self._get_uri_value(graph, dist_uri, DCTERMS.format)
        media_type = self._extract_media_type(graph, dist_uri, DCAT.mediaType)
        compression_format = self._extract_media_type(
            graph, dist_uri, DCAT.compressFormat
        )
        packaging_format = self._extract_media_type(graph, dist_uri, DCAT.packageFormat)

        languages = self._get_uri_set(graph, dist_uri, DCTERMS.language)
        applicable_legislations = self._get_legal_information(graph, dist_uri)

        release_date = self._get_date_literal(graph, dist_uri, DCTERMS.issued)
        modification_date = self._get_date_literal(graph, dist_uri, DCTERMS.modified)

        license = self._extract_license(graph, dist_uri)
        availability = self._get_uri_value(graph, dist_uri, EU_R5R.availability)
        documentation = get_documentation_values(graph, dist_uri, FOAF.page)

        byte_size = self._get_int_literal(graph, dist_uri, DCAT.byteSize)
        checksum = self._get_checksum(graph, dist_uri)

        linked_schemas = self._get_uri_set(graph, dist_uri, DCTERMS.conformsTo)
        distribution_dcat_status = self._get_status(graph, dist_uri)

        spatial_resolution = self._get_int_literal(
            graph, dist_uri, DCAT.spatialResolutionInMeters
        )
        temporal_resolution = self._get_literal(
            graph, dist_uri, DCAT.temporalResolution
        )

        policy_actions = self._get_policy_actions(graph, dist_uri)

        return DistributionDto(
            title=title,
            description=description,
            download_urls=list(download_urls),
            access_urls=list(access_urls),
            file_type=file_type,
            rights_statement=rights_statement,
            internal_only=False,
            is_analytics=is_analytics,
            applicable_legislations=frozenset(applicable_legislations),
            languages=frozenset(languages),
            notes=None,
            license=license,
            distribution_path=None,
            policy_actions=tuple(policy_actions),
            availability=availability,
            documentation=list(documentation),
            modification_date=modification_date,
            release_date=release_date,
            linked_schemas=list(linked_schemas),
            byte_size=byte_size,
            checksum=checksum,
            media_type=media_type,
            compression_format=compression_format,
            packaging_format=packaging_format,
            distribution_dcat_status=distribution_dcat_status,
            spatial_resolution=spatial_resolution,
            temporal_resolution=temporal_resolution,
            access_service_ids=frozenset(),
        )

    def _get_literal(
        self,
        graph: Graph,
        subject: URIRef | BNode,
        predicate: URIRef,
        languages: Iterable[str] = ("eng", "en", None),
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

    def _get_uri_value(
        self, graph: Graph, subject: URIRef | BNode, predicate: URIRef
    ) -> Optional[str]:
        for obj in graph.objects(subject, predicate):
            if isinstance(obj, URIRef):
                return str(obj)
        return None

    def _get_first_uri(
        self, graph: Graph, subject: URIRef | BNode, predicate: URIRef
    ) -> Optional[str]:
        for obj in graph.objects(subject, predicate):
            if isinstance(obj, URIRef):
                return str(obj)
        return None

    def _get_uri_set(
        self, graph: Graph, subject: URIRef | BNode, predicate: URIRef
    ) -> Set[str]:
        values: Set[str] = set()
        for obj in graph.objects(subject, predicate):
            if isinstance(obj, URIRef):
                values.add(str(obj))
        return values

    def _get_date_literal(
        self, graph: Graph, subject: URIRef | BNode, predicate: URIRef
    ) -> Optional[date]:
        literal = self._get_literal(graph, subject, predicate)
        try:
            return date.fromisoformat(literal) if literal else None
        except ValueError:
            if literal:
                try:
                    normalized = literal.replace("Z", "+00:00")
                    return datetime.fromisoformat(normalized).date()
                except ValueError:
                    return None
            return None

    def _get_int_literal(
        self, graph: Graph, subject: URIRef | BNode, predicate: URIRef
    ) -> Optional[int]:
        literal = self._get_literal(graph, subject, predicate)
        if literal is None:
            return None
        try:
            return int(float(literal))
        except ValueError:
            return None

    def _extract_media_type(
        self, graph: Graph, dist_uri: URIRef | BNode, predicate: URIRef
    ) -> Optional[str]:
        uri = self._get_uri_value(graph, dist_uri, predicate)
        if not uri:
            return None
        # Extract the last part after the last slash
        # e.g., "http://www.iana.org/assignments/media-types/text/csv" -> "text/csv"
        if "media-types/" in uri:
            return uri.split("media-types/", 1)[1]
        return None

    def _extract_license(self, graph: Graph, dist_uri: URIRef | BNode) -> Optional[str]:
        license_uri = self._get_uri_value(graph, dist_uri, DCTERMS.license)
        if not license_uri:
            return None
        # Extract license ID from SPDX URI
        # e.g., "http://spdx.org/licenses/MIT" -> "MIT"
        if "spdx.org/licenses/" in license_uri:
            return license_uri.split("spdx.org/licenses/", 1)[1]
        return None

    def _get_checksum(self, graph: Graph, dist_uri: URIRef | BNode) -> Optional[str]:
        for checksum_node in graph.objects(dist_uri, SPDX.checksum):
            checksum_value = self._get_literal(graph, checksum_node, SPDX.checksumValue)
            if checksum_value:
                return checksum_value
        return None

    def _get_status(self, graph: Graph, dist_uri: URIRef | BNode) -> Optional[str]:
        status_uri = self._get_uri_value(graph, dist_uri, ADMS.status)
        if not status_uri:
            return None
        if "/" not in status_uri:
            return None

        raw_value = status_uri.rsplit("/", 1)[-1]
        if not raw_value:
            return None

        normalised = raw_value.replace("_", " ").strip().lower().title()
        return normalised

    def _get_legal_information(
        self, graph: Graph, dist_uri: URIRef | BNode
    ) -> Set[str]:
        applicable_legislation_keys = {
            item.key for item in self._applicable_legislation_repository.get_all()
        }

        applicable_legislations: Set[str] = set()

        for obj in graph.objects(dist_uri, EU_R5R.applicableLegislation):
            if not isinstance(obj, URIRef):
                continue
            value = str(obj)
            if value in applicable_legislation_keys:
                applicable_legislations.add(value)
        return applicable_legislations

    def _get_policy_actions(
        self, graph: Graph, dist_uri: URIRef | BNode
    ) -> list[PolicyActionDto]:
        policy_actions = []

        for policy_node in graph.objects(dist_uri, ODRL.hasPolicy):
            # Get permissions
            for permission_node in graph.objects(policy_node, ODRL.permission):
                action = self._parse_policy_rule(graph, permission_node, "permission")
                if action:
                    policy_actions.append(action)

            # Get prohibitions
            for prohibition_node in graph.objects(policy_node, ODRL.prohibition):
                action = self._parse_policy_rule(graph, prohibition_node, "prohibition")
                if action:
                    policy_actions.append(action)

        return policy_actions

    def _parse_policy_rule(
        self, graph: Graph, rule_node: URIRef | BNode, action_type: str
    ) -> Optional[PolicyActionDto]:
        constraints = list(graph.objects(rule_node, ODRL.constraint))
        if not constraints:
            return PolicyActionDto(
                policy_action_type=action_type,
                policy_constraint_type=None,
                policy_constraint_value=None,
            )

        # Determine constraint type
        constraint_type = None
        constraint_value = None
        temporal_start = None
        temporal_end = None
        spatial_restrictions = set()

        for constraint in constraints:
            left_operand = self._get_uri_value(graph, constraint, ODRL.leftOperand)

            if left_operand and "dateTime" in str(left_operand):
                constraint_type = "temporal"
                operator = self._get_uri_value(graph, constraint, ODRL.operator)
                right_operand = self._get_literal(graph, constraint, ODRL.rightOperand)

                if right_operand:
                    try:
                        constraint_date = date.fromisoformat(right_operand)
                        if operator and "gteq" in str(operator):
                            temporal_start = constraint_date
                        elif operator and "lteq" in str(operator):
                            temporal_end = constraint_date
                    except ValueError:
                        pass

            elif left_operand and "spatial" in str(left_operand):
                constraint_type = "spatial"
                right_operand = self._get_literal(graph, constraint, ODRL.rightOperand)
                if right_operand:
                    spatial_restrictions.add(right_operand)

            elif left_operand and "purpose" in str(left_operand):
                constraint_type = "purpose"
                right_operand = self._get_uri_value(
                    graph, constraint, ODRL.rightOperand
                )
                if right_operand:
                    # Extract DUO code
                    if "/" in right_operand:
                        duo_code = right_operand.split("/")[-1]
                        constraint_value = duo_code.replace("_", ":")

            elif left_operand and "industry" in str(left_operand):
                constraint_type = "industry"
                constraint_value = self._get_literal(
                    graph, constraint, ODRL.rightOperand
                )

        return PolicyActionDto(
            policy_action_type=action_type,
            policy_constraint_type=constraint_type,
            policy_constraint_value=constraint_value,
            temporal_restriction_start=temporal_start,
            temporal_restriction_end=temporal_end,
            spatial_restrictions=frozenset(spatial_restrictions),
        )
