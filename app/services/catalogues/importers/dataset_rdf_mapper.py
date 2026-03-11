from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Iterable, Optional, Set, List

from fastapi import Depends, HTTPException, status
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import DCAT, DCTERMS, RDF, RDFS

from models.dataset import DatasetStatus
from repositories.keyword import KeywordRepository
from repositories.applicable_legislation import ApplicableLegislationRepository
from repositories.organisation import OrganisationRepository
from schemas.dataset import DatasetDto
from services.catalogues.importers.documentation_utils import get_documentation_values
from services.catalogues.importers.distribution_rdf_mapper import (
    DistributionRDFMapper,
)
from services.catalogues.mappers.namespace_constants import (
    ADMS,
    CDSP,
    DPV,
    EU_R5R,
    FOAF,
    HEALTHDCATAP,
    PROV,
    SKOS,
    DPVPD,
)


class DatasetRDFMapper:
    def __init__(
        self,
        keyword_repository: KeywordRepository = Depends(KeywordRepository),
        applicable_legislation_repository: ApplicableLegislationRepository = Depends(
            ApplicableLegislationRepository
        ),
        organisation_repository: OrganisationRepository = Depends(
            OrganisationRepository
        ),
        distribution_rdf_mapper: DistributionRDFMapper = Depends(DistributionRDFMapper),
    ):
        self._keyword_repository = keyword_repository
        self._applicable_legislation_repository = applicable_legislation_repository
        self._organisation_repository = organisation_repository
        self._distribution_rdf_mapper = distribution_rdf_mapper

    def parse_graph(self, rdf_content: str, rdf_format: str) -> Graph:
        graph = Graph()
        parse_format = self._normalise_rdf_format(rdf_format)
        try:
            graph.parse(data=rdf_content, format=parse_format)
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to parse RDF payload: {error}",
            ) from error
        return graph

    def select_dataset_resource(self, graph: Graph) -> URIRef | BNode:
        resources = list(graph.subjects(RDF.type, DCAT.Dataset))
        if not resources:
            resources = list(graph.subjects(RDF.type, DCAT.DatasetSeries))
        if not resources:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No DCAT dataset resource found in RDF payload.",
            )
        return resources[0]

    def map_dataset(
        self,
        graph: Graph,
        dataset_uri: URIRef | BNode,
        status_override: Optional[str] = None,
        released_at_override: Optional[str] = None,
        version_change_type_override: Optional[str] = None,
        contact_ids: Optional[set[int]] = None,
        source: Optional[str] = None,
        source_dataset_id: Optional[int] = None,
    ) -> tuple[DatasetDto, Optional[str]]:
        title = self._get_literal(
            graph, dataset_uri, DCTERMS.title
        ) or self._raise_missing("dcterms:title")
        description = self._get_literal(
            graph, dataset_uri, DCTERMS.description
        ) or self._raise_missing("dcterms:description")
        identifier = self._get_literal(graph, dataset_uri, DCTERMS.identifier)

        periodicity = self._get_uri_value(
            graph, dataset_uri, DCTERMS.accrualPeriodicity
        )

        rights_statement = self._get_uri_value(graph, dataset_uri, DCTERMS.accessRights)
        if not rights_statement:
            rights_statement = self._raise_missing("dcterms:accessRights")

        time_period_start, time_period_end = self._get_temporal_coverage(
            graph, dataset_uri
        )

        modified_at = self._get_date_literal(graph, dataset_uri, DCTERMS.modified)
        release_date = self._get_date_literal(graph, dataset_uri, DCTERMS.issued)

        dataset_types = self._get_uri_set(graph, dataset_uri, DCTERMS.type)
        if not dataset_types:
            dataset_types = self._raise_missing("dcterms:type")

        themes = self._get_uri_set(graph, dataset_uri, DCAT.theme)
        if not themes:
            themes = self._raise_missing("dcat:theme")

        keywords = self._get_keywords(graph, dataset_uri)

        languages = self._get_uri_set(graph, dataset_uri, DCTERMS.language)
        spatial_coverages = self._get_uri_set(graph, dataset_uri, DCTERMS.spatial)
        applicable_legislations = self._get_legal_information(graph, dataset_uri)
        provenance = self._get_provenance(graph, dataset_uri)
        health_legal_basis = self._get_health_legal_basis(graph, dataset_uri)
        landing_pages = self._get_uri_list(graph, dataset_uri, DCAT.landingPage)
        documentation = get_documentation_values(graph, dataset_uri, FOAF.page)

        spatial_resolution_values = self._get_int_literals(
            graph, dataset_uri, DCAT.spatialResolutionInMeters
        )
        temporal_resolution = self._get_literal(
            graph, dataset_uri, DCAT.temporalResolution
        )

        was_generated_by = self._get_was_generated_by(graph, dataset_uri)
        other_identifiers = self._get_identifier_notations(graph, dataset_uri)

        publisher_id = self.get_publisher_id(graph, dataset_uri)
        creator_ids = self._find_creator_ids(graph, dataset_uri)

        version = self._get_literal(graph, dataset_uri, DCAT.version)
        version_notes = self._get_literal_list(graph, dataset_uri, ADMS.versionNotes)

        data_protection_types = self._get_data_protection_types(graph, dataset_uri)

        # Parse typical age fields
        min_typical_age = self._get_int_literal(
            graph, dataset_uri, HEALTHDCATAP.minTypicalAge
        )
        max_typical_age = self._get_int_literal(
            graph, dataset_uri, HEALTHDCATAP.maxTypicalAge
        )

        # Parse health statistics fields
        number_of_records = self._get_int_literal(
            graph, dataset_uri, HEALTHDCATAP.numberOfRecords
        )
        number_of_unique_individuals = self._get_int_literal(
            graph, dataset_uri, HEALTHDCATAP.numberOfUniqueIndividuals
        )

        population_coverage = self._get_literal(
            graph, dataset_uri, HEALTHDCATAP.populationCoverage
        )

        code_values_values = self._get_literal_list(
            graph, dataset_uri, HEALTHDCATAP.hasCodeValues
        )
        purpose = self._get_purpose_values(graph, dataset_uri)

        coding_systems_values = [
            str(uri) for uri in graph.objects(dataset_uri, HEALTHDCATAP.hasCodingSystem)
        ]

        distributions = self._distribution_rdf_mapper.map_distributions(
            graph, dataset_uri
        )

        personal_data = self._get_personal_data_list(graph, dataset_uri)

        # Parse released_at if provided as override and convert to UTC
        released_at_parsed = None
        if released_at_override:
            released_at_parsed = datetime.fromisoformat(
                released_at_override
            ).astimezone(timezone.utc)

        dataset_dto = DatasetDto(
            status=status_override or DatasetStatus.DRAFT.value,
            title=title,
            description=description,
            contact_ids=contact_ids,
            publisher_id=publisher_id,
            time_period_start=time_period_start,
            time_period_end=time_period_end,
            retention_period_start=None,
            retention_period_end=None,
            release_date=release_date,
            modified_at=modified_at,
            deprecated_at=None,
            released_at=released_at_parsed,
            rights_statement=rights_statement,
            periodicity=periodicity,
            dataset_types=set(dataset_types),
            themes=set(themes),
            keywords=set(keywords),
            health_categories={},
            health_themes=set(),
            spatial_coverages=set(spatial_coverages),
            conventions=set(),
            areas_of_work=set(),
            areas_of_competence=set(),
            applicable_legislations=set(applicable_legislations),
            notes=None,
            duration_of_administrative_utility=None,
            max_typical_age=max_typical_age,
            min_typical_age=min_typical_age,
            number_of_records=number_of_records,
            number_of_unique_individuals=number_of_unique_individuals,
            final_disposition=None,
            version=version,
            version_change_type=version_change_type_override,
            creator_ids=set(creator_ids) if creator_ids else set(),
            group_managers=None,
            data_protection_types=set(data_protection_types),
            monitoring_location=None,
            provenance=provenance,
            health_legal_basis=health_legal_basis,
            conforms_to=self._get_uri_list(graph, dataset_uri, DCTERMS.conformsTo),
            languages=frozenset(languages),
            landing_pages=landing_pages,
            documentation=documentation,
            purpose=purpose,
            is_dataset_series=self._is_series(graph, dataset_uri),
            member_datasets=None,
            was_generated_by=frozenset(was_generated_by),
            other_identifiers=frozenset(other_identifiers),
            version_notes=version_notes,
            spatial_resolutions=spatial_resolution_values,
            temporal_resolution=temporal_resolution,
            population_coverage=population_coverage,
            code_values=set(code_values_values),
            coding_systems=set(coding_systems_values),
            distributions=distributions,
            source=source,
            source_dataset_id=source_dataset_id,
            personal_data=personal_data,
        )

        return dataset_dto, identifier

    def _normalise_rdf_format(self, rdf_format: str) -> str:
        fmt = (rdf_format or "").lower()
        if fmt in {"rdf", "pretty-xml", "application/rdf+xml", "xml"}:
            return "xml"
        if fmt in {"jsonld", "json-ld", "application/ld+json"}:
            return "json-ld"
        if fmt in {"ttl", "turtle", "text/turtle"}:
            return "turtle"
        return fmt or "turtle"

    def _raise_missing(self, context: str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Required value missing: {context}",
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

    def _get_literal_set(
        self, graph: Graph, subject: URIRef | BNode, predicate: URIRef
    ) -> Set[str]:
        values: Set[str] = set()
        for obj in graph.objects(subject, predicate):
            if isinstance(obj, Literal):
                values.add(str(obj))
        return values

    def _get_uri_value(
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

    def _get_uri_list(
        self, graph: Graph, subject: URIRef | BNode, predicate: URIRef
    ) -> list[str]:
        values: list[str] = []
        seen: set[str] = set()
        for obj in graph.objects(subject, predicate):
            if isinstance(obj, URIRef):
                value = str(obj)
                if value not in seen:
                    seen.add(value)
                    values.append(value)
        return values

    def get_keyword_literals(
        self, graph: Graph, dataset_uri: URIRef | BNode
    ) -> Set[str]:
        """Return raw keyword literals exactly as they appear in the RDF payload."""
        results: Set[str] = set()
        for obj in graph.objects(dataset_uri, DCAT.keyword):
            if isinstance(obj, Literal):
                value = str(obj).strip()
                if value:
                    results.add(value)
        return results

    def _get_keywords(self, graph: Graph, dataset_uri: URIRef | BNode) -> Set[str]:
        results: Set[str] = set()
        for keyword_value in self.get_keyword_literals(graph, dataset_uri):
            keyword = self._keyword_repository.get(keyword_value)
            if keyword:
                results.add(keyword.key)
                continue
            keyword = self._keyword_repository.get_by_eng_label(keyword_value)
            if keyword:
                results.add(keyword.key)
                continue
            # fallback: treat literal as key
            results.add(keyword_value)
        return results

    def _get_temporal_coverage(
        self, graph: Graph, dataset_uri: URIRef | BNode
    ) -> tuple[Optional[date], Optional[date]]:
        for temporal_node in graph.objects(dataset_uri, DCTERMS.temporal):
            start_literal = self._get_literal(graph, temporal_node, DCAT.startDate)
            end_literal = self._get_literal(graph, temporal_node, DCAT.endDate)
            start_date = self._parse_date_literal(start_literal)
            end_date = self._parse_date_literal(end_literal)
            return start_date, end_date
        return None, None

    def _parse_date_literal(self, value: Optional[str]) -> Optional[date]:
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None

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

    def _get_int_literals(
        self, graph: Graph, subject: URIRef | BNode, predicate: URIRef
    ) -> Set[int]:
        values: Set[int] = set()
        for obj in graph.objects(subject, predicate):
            if isinstance(obj, Literal):
                try:
                    values.add(int(float(str(obj))))
                except ValueError:
                    continue
        return values

    def _get_provenance(self, graph: Graph, dataset_uri: URIRef | BNode) -> list[str]:
        values: list[str] = []
        seen: set[str] = set()
        for provenance_node in graph.objects(dataset_uri, DCTERMS.provenance):
            value = self._get_literal(graph, provenance_node, SKOS.prefLabel)
            if value and value not in seen:
                seen.add(value)
                values.append(value)
                continue
            label = self._get_literal(graph, provenance_node, RDFS.label)
            if label and label not in seen:
                seen.add(label)
                values.append(label)
                continue
            description = self._get_literal(graph, provenance_node, DCTERMS.description)
            if description and description not in seen:
                seen.add(description)
                values.append(description)
        return values

    def _get_literal_list(
        self, graph: Graph, subject: URIRef | BNode, predicate: URIRef
    ) -> list[str]:
        values: list[str] = []
        seen: set[str] = set()
        for obj in graph.objects(subject, predicate):
            if isinstance(obj, Literal):
                value = str(obj)
                if value not in seen:
                    seen.add(value)
                    values.append(value)
        return values

    def _get_personal_data_list(
        self, graph: Graph, dataset_uri: URIRef | BNode
    ) -> list[str]:
        values: list[str] = []
        seen: set[str] = set()
        for obj in graph.objects(dataset_uri, DPV.hasPersonalData):
            if isinstance(obj, URIRef):
                local_name = str(obj).removeprefix(str(DPVPD))
                if local_name and local_name not in seen:
                    seen.add(local_name)
                    values.append(local_name)
        return values

    def _get_purpose_values(
        self, graph: Graph, dataset_uri: URIRef | BNode
    ) -> Set[str]:
        values: Set[str] = set()
        for purpose_node in graph.objects(dataset_uri, DPV.hasPurpose):
            if isinstance(purpose_node, Literal):
                purpose_value = str(purpose_node).strip()
                if purpose_value:
                    values.add(purpose_value)
                continue

            description = self._get_literal(graph, purpose_node, DCTERMS.description)
            if description:
                values.add(description)
                continue

            label = self._get_literal(graph, purpose_node, SKOS.prefLabel)
            if label:
                values.add(label)

        return values

    def _get_health_legal_basis(
        self, graph: Graph, dataset_uri: URIRef | BNode
    ) -> list[str]:
        values = []
        for legal_basis_node in graph.objects(dataset_uri, DPV.hasLegalBasis):
            description = self._get_literal(
                graph, legal_basis_node, DCTERMS.description
            )
            if description:
                values.append(description)
        return values

    def _get_first_uri(
        self, graph: Graph, subject: URIRef | BNode, predicate: URIRef
    ) -> Optional[str]:
        for obj in graph.objects(subject, predicate):
            if isinstance(obj, URIRef):
                return str(obj)
        return None

    def _get_identifier_notations(
        self, graph: Graph, dataset_uri: URIRef | BNode
    ) -> Set[str]:
        results: Set[str] = set()
        for identifier_node in graph.objects(dataset_uri, ADMS.identifier):
            if isinstance(identifier_node, Literal):
                continue
            notation = self._get_literal(
                graph, identifier_node, SKOS.notation, languages=(None,)
            )
            if notation:
                results.add(notation)
        return results

    def _get_was_generated_by(
        self, graph: Graph, dataset_uri: URIRef | BNode
    ) -> Set[str]:
        values: Set[str] = set()
        for activity in graph.objects(dataset_uri, PROV.wasGeneratedBy):
            label = self._get_literal(graph, activity, RDFS.label)
            if label:
                values.add(label)
        return values

    def get_applicable_legislation_values(
        self, graph: Graph, dataset_uri: URIRef | BNode
    ) -> Set[str]:
        """Return all legislation URIs referenced by the dataset."""
        values: Set[str] = set()
        for obj in graph.objects(dataset_uri, EU_R5R.applicableLegislation):
            if isinstance(obj, URIRef):
                values.add(str(obj))
        return values

    def get_applicable_legislation_with_titles(
        self, graph: Graph, dataset_uri: URIRef | BNode
    ) -> dict[str, str]:
        result: dict[str, str] = {}
        for obj in graph.objects(dataset_uri, EU_R5R.applicableLegislation):
            if isinstance(obj, URIRef):
                uri = str(obj)
                title = self._get_literal(graph, obj, DCTERMS.title)
                if not title:
                    title = self._get_literal(graph, obj, RDFS.label)
                result[uri] = title or uri
        return result

    def _get_legal_information(
        self, graph: Graph, dataset_uri: URIRef | BNode
    ) -> Set[str]:
        applicable_legislations = self.get_applicable_legislation_values(
            graph, dataset_uri
        )
        return applicable_legislations

    def _is_series(self, graph: Graph, dataset_uri: URIRef | BNode) -> bool:
        return (dataset_uri, RDF.type, DCAT.DatasetSeries) in graph or any(
            graph.objects(dataset_uri, DCAT.inSeries)
        )

    def get_publisher_id(self, graph: Graph, dataset_uri: URIRef | BNode) -> int:
        for publisher_node in graph.objects(dataset_uri, DCTERMS.publisher):
            publisher_name = self._get_literal(
                graph, publisher_node, FOAF.name, languages=("eng", "en", None)
            )
            if publisher_name:
                organisation = self._organisation_repository.find_by_name(
                    publisher_name
                )
                if organisation:
                    return organisation.id
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Publisher in RDF does not match any known organisation. Publisher name: '{publisher_name}'",
        )

    def _find_creator_ids(self, graph: Graph, dataset_uri: URIRef | BNode) -> List[int]:
        creator_ids = []
        for creator_node in graph.objects(dataset_uri, DCTERMS.creator):
            creator_name = self._get_literal(
                graph, creator_node, FOAF.name, languages=("eng", "en", None)
            )
            if creator_name:
                organisation = self._organisation_repository.find_by_name(creator_name)
                if organisation:
                    creator_ids.append(organisation.id)
        return creator_ids

    def _get_data_protection_types(
        self, graph: Graph, dataset_uri: URIRef | BNode
    ) -> Set[str]:
        results: Set[str] = set()
        for obj in graph.objects(dataset_uri, DPV.dataProtectionType):
            if isinstance(obj, Literal):
                # Convert label back to key format (e.g., "Personal Data" -> "PersonalData")
                protection_type_label = str(obj)
                protection_type_key = protection_type_label.replace(" ", "")
                results.add(protection_type_key)
        return results
