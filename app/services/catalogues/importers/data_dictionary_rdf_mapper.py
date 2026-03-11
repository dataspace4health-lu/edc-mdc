from __future__ import annotations

from typing import Optional, Set

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS

from schemas.data_dictionary import AddDataDictionaryEntry
from services.catalogues.mappers.namespace_constants import CDSP, CSVW, DPV, FOAF
from services.catalogues.mappers.type_mappers import TypeMappers


class DataDictionaryRDFMapper:
    def map_data_dictionaries(
        self, graph: Graph, dataset_uri: URIRef | BNode
    ) -> Optional[list[AddDataDictionaryEntry]]:
        data_dict_entries: list[AddDataDictionaryEntry] = []

        # Find the data dictionary node (FOAF.page with CSVW.TableSchema type)
        for page_node in graph.objects(dataset_uri, FOAF.page):
            # Check if this page is a TableSchema (data dictionary)
            if (page_node, RDF.type, CSVW.TableSchema) not in graph:
                continue

            # Iterate through all columns in the table schema
            for column_node in graph.objects(page_node, CSVW.column):
                # Extract field name (required)
                field_name = self._get_literal(graph, column_node, CSVW.name)
                if not field_name:
                    continue  # Skip entries without field name

                # Extract description (required field with min_length=1)
                description = self._get_literal(graph, column_node, DCTERMS.description)
                if not description:
                    description = "No description provided"  # Default placeholder for missing description

                # Extract data type (required)
                data_type_uri = self._get_first_uri(graph, column_node, CSVW.datatype)
                data_type = (
                    TypeMappers.map_xsd_to_dca_type(data_type_uri)
                    if data_type_uri
                    else "String"
                )

                # Extract personally_identifiable_variable
                personally_identifiable_variable = (
                    column_node,
                    RDF.type,
                    DPV.PersonalData,
                ) in graph

                # Extract required (boolean)
                required_literal = self._get_literal(graph, column_node, CSVW.required)
                required = (
                    required_literal.lower() == "true" if required_literal else None
                )

                # Extract max/min allowed values
                max_allowed_value_str = self._get_literal(
                    graph, column_node, CSVW.maxInclusive
                )
                max_allowed_value = (
                    float(max_allowed_value_str) if max_allowed_value_str else None
                )

                min_allowed_value_str = self._get_literal(
                    graph, column_node, CSVW.minInclusive
                )
                min_allowed_value = (
                    float(min_allowed_value_str) if min_allowed_value_str else None
                )

                # Extract variable unit
                variable_unit = self._get_literal(graph, column_node, CSVW.unit)

                # Extract allowed values (stored as literal string)
                allowed_values = self._get_literal(graph, column_node, CSVW["in"])

                # Extract allowed values description
                allowed_values_description = self._get_literal(
                    graph, column_node, RDFS.comment
                )

                # Extract privacy risk type
                privacy_risk_type = self._get_literal(
                    graph, column_node, CDSP.privacyRiskType
                )

                # Create AddDataDictionaryEntry DTO
                try:
                    entry = AddDataDictionaryEntry(
                        field_name=field_name,
                        description=description,
                        data_type=data_type,
                        personally_identifiable_variable=(
                            personally_identifiable_variable
                            if personally_identifiable_variable
                            else None
                        ),
                        required=required,
                        max_allowed_value=max_allowed_value,
                        min_allowed_value=min_allowed_value,
                        variable_unit=variable_unit,
                        allowed_values=allowed_values,
                        allowed_values_description=allowed_values_description,
                        privacy_risk_type=privacy_risk_type,
                        table_name="",  # Empty string - table name is not stored in RDF
                    )
                    data_dict_entries.append(entry)
                except Exception as e:
                    # Skip invalid entries - log error for debugging
                    import logging

                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"Skipping invalid data dictionary entry '{field_name}': {e}"
                    )
                    continue

        return data_dict_entries if data_dict_entries else None

    def _get_literal(
        self,
        graph: Graph,
        subject: URIRef | BNode,
        predicate: URIRef,
    ) -> Optional[str]:
        """Get literal value from graph, preferring English language."""
        candidates = [
            obj for obj in graph.objects(subject, predicate) if isinstance(obj, Literal)
        ]
        # Prefer English language
        for literal in candidates:
            if literal.language in ("eng", "en"):
                return str(literal)
        # Otherwise return first available
        if candidates:
            return str(candidates[0])
        return None

    def _get_first_uri(
        self, graph: Graph, subject: URIRef | BNode, predicate: URIRef
    ) -> Optional[str]:
        """Get first URI object for the given predicate."""
        for obj in graph.objects(subject, predicate):
            if isinstance(obj, URIRef):
                return str(obj)
        return None
