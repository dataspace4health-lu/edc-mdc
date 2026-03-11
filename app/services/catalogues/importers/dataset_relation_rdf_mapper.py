from __future__ import annotations

from typing import List, Optional

from fastapi import Depends
from rdflib import BNode, Graph, URIRef
from rdflib.namespace import DCAT, DCTERMS, RDF, RDFS

from repositories.dataset import DatasetRepository
from schemas.dataset_relations import AddRelation
from services.catalogues.mappers.namespace_constants import SKOS


class DatasetRelationRDFMapper:
    # DCTERMS properties that represent dataset relations
    RELATION_PREDICATES = {
        DCTERMS.hasVersion: "dct:hasVersion",
        DCTERMS.isVersionOf: "dct:isVersionOf",
        DCTERMS.source: "dct:source",
        DCTERMS.relation: "dct:relation",
        DCTERMS.hasPart: "dct:hasPart",
        DCTERMS.isPartOf: "dct:isPartOf",
        DCTERMS.conformsTo: "dct:conformsTo",
        DCTERMS.hasFormat: "dct:hasFormat",
        DCTERMS.isFormatOf: "dct:isFormatOf",
        DCTERMS.isReferencedBy: "dct:isReferencedBy",
        DCTERMS.references: "dct:references",
        DCTERMS.isReplacedBy: "dct:isReplacedBy",
        DCTERMS.replaces: "dct:replaces",
        DCTERMS.isRequiredBy: "dct:isRequiredBy",
        DCTERMS.requires: "dct:requires",
    }

    def __init__(
        self,
        dataset_repository: DatasetRepository = Depends(DatasetRepository),
    ):
        self._dataset_repository = dataset_repository

    def map_dataset_relations(
        self, graph: Graph, dataset_uri: URIRef | BNode
    ) -> List[AddRelation]:
        """
        Extract dataset relations from RDF graph.

        Two types of relations:
        1. Dataset-to-dataset: DCTERMS properties pointing to other datasets
        2. External (qualified): dcat:qualifiedRelation with external URLs
        """
        relations: List[AddRelation] = []

        # Extract dataset-to-dataset relations
        for predicate, relation_type in self.RELATION_PREDICATES.items():
            for target_uri in graph.objects(dataset_uri, predicate):
                if isinstance(target_uri, URIRef):
                    target_dataset_id = self._resolve_dataset_id_from_uri(
                        str(target_uri)
                    )
                    if target_dataset_id:
                        relations.append(
                            AddRelation(
                                relation_kind="dataset",
                                target_dataset=target_dataset_id,
                                relation_type=relation_type,
                            )
                        )
                    elif predicate == DCTERMS.isReferencedBy:
                        relations.append(
                            AddRelation(
                                relation_kind="external",
                                external_url=str(target_uri),
                                external_role="is-referenced-by",
                            )
                        )

        # Extract external (qualified) relations
        for relation_node in graph.objects(dataset_uri, DCAT.qualifiedRelation):
            external_relation = self._map_external_relation(graph, relation_node)
            if external_relation:
                relations.append(external_relation)

        return relations

    def _map_external_relation(
        self, graph: Graph, relation_node: URIRef | BNode
    ) -> Optional[AddRelation]:
        """
        Map dcat:qualifiedRelation to AddRelation DTO.

        Structure:
        - dcterms:relation → external_url
        - dcat:hadRole → external_role
        - rdfs:label → external_description
        """
        # Extract external URL
        external_url = None
        for obj in graph.objects(relation_node, DCTERMS.relation):
            if isinstance(obj, URIRef):
                external_url = str(obj)
                break

        if not external_url:
            return None

        # Extract role from IANA URI
        external_role = None
        for role_uri in graph.objects(relation_node, DCAT.hadRole):
            if isinstance(role_uri, URIRef):
                # Extract role from IANA URI or use prefLabel
                role_label = self._get_literal(graph, role_uri, SKOS.prefLabel)
                if role_label:
                    external_role = role_label
                else:
                    # Fallback: extract from URI
                    uri_str = str(role_uri)
                    if "/relation/" in uri_str:
                        role_token = uri_str.split("/relation/")[-1]
                        external_role = self._denormalize_role_token(role_token)
                break

        # Extract description
        external_description = self._get_literal(graph, relation_node, RDFS.label)

        return AddRelation(
            relation_kind="external",
            external_url=external_url,
            external_role=external_role,
            external_description=external_description,
        )

    def _resolve_dataset_id_from_uri(self, uri: str) -> Optional[int]:
        """
        Extract dataset identifier from URI and look up dataset ID.

        Example URI: https://data.statec.lu/api/v1/datasets/dataset-123
        """
        # Try to extract identifier from common patterns
        if "/datasets/" in uri:
            identifier = uri.split("/datasets/")[-1].split("/")[0].split("?")[0]
            dataset = self._dataset_repository.get_dataset_by_identifier(identifier)
            if dataset:
                return dataset.id
        return None

    def _get_literal(
        self,
        graph: Graph,
        subject: URIRef | BNode,
        predicate: URIRef,
        languages: tuple = ("eng", "en", None),
    ) -> Optional[str]:
        from rdflib import Literal

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

    def _denormalize_role_token(self, token: str) -> str:
        """
        Convert from URI-safe format back to display format.
        Example: "related-resource" -> "related resource"
        """
        return token.replace("-", " ")
