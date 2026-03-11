from __future__ import annotations

from typing import Annotated, Optional

from fastapi import Depends

from models.identity_context import IdentityContext
from schemas.dataset import DatasetDto
from services.catalogues.importers.contact_import_service import ContactImportService
from services.catalogues.importers.dataset_rdf_mapper import DatasetRDFMapper
from services.catalogues.importers.dataset_relation_rdf_mapper import (
    DatasetRelationRDFMapper,
)
from services.catalogues.importers.qualified_attribution_rdf_mapper import (
    QualifiedAttributionRDFMapper,
)
from services.catalogues.importers.data_dictionary_rdf_mapper import (
    DataDictionaryRDFMapper,
)
from services.dataset import DatasetService
from services.dataset_relation import DatasetRelationService
from services.qualified_attribution import QualifiedAttributionService
from services.data_dictionary import DataDictionaryService
from services.distribution import DistributionService
from rdflib import Graph

from services.form_fields.form_fields_import_service import FormFieldsImportService
from services.activity_logs.dataset_activity_log import DatasetActivityLogService


class DatasetRDFImportService:
    def __init__(
        self,
        dataset_service: DatasetService = Depends(DatasetService),
        dataset_rdf_mapper: DatasetRDFMapper = Depends(DatasetRDFMapper),
        qualified_attribution_service: Annotated[
            QualifiedAttributionService, Depends(QualifiedAttributionService)
        ] = Depends(QualifiedAttributionService),
        qualified_attribution_rdf_mapper: Annotated[
            QualifiedAttributionRDFMapper, Depends(QualifiedAttributionRDFMapper)
        ] = Depends(QualifiedAttributionRDFMapper),
        dataset_relation_service: Annotated[
            DatasetRelationService, Depends(DatasetRelationService)
        ] = Depends(DatasetRelationService),
        dataset_relation_rdf_mapper: Annotated[
            DatasetRelationRDFMapper, Depends(DatasetRelationRDFMapper)
        ] = Depends(DatasetRelationRDFMapper),
        form_fields_import_service: FormFieldsImportService = Depends(
            FormFieldsImportService
        ),
        contact_import_service: ContactImportService = Depends(ContactImportService),
        data_dictionary_service: Annotated[
            DataDictionaryService, Depends(DataDictionaryService)
        ] = Depends(DataDictionaryService),
        data_dictionary_rdf_mapper: Annotated[
            DataDictionaryRDFMapper, Depends(DataDictionaryRDFMapper)
        ] = Depends(DataDictionaryRDFMapper),
        distribution_service: DistributionService = Depends(DistributionService),
        dataset_activity_log_service: DatasetActivityLogService = Depends(
            DatasetActivityLogService
        ),
    ):
        self._dataset_service = dataset_service
        self._dataset_rdf_mapper = dataset_rdf_mapper
        self._qualified_attribution_service = qualified_attribution_service
        self._qualified_attribution_rdf_mapper = qualified_attribution_rdf_mapper
        self._dataset_relation_service = dataset_relation_service
        self._dataset_relation_rdf_mapper = dataset_relation_rdf_mapper
        self._form_fields_import_service = form_fields_import_service
        self._contact_import_service = contact_import_service
        self._data_dictionary_service = data_dictionary_service
        self._data_dictionary_rdf_mapper = data_dictionary_rdf_mapper
        self._distribution_service = distribution_service
        self._dataset_activity_log_service = dataset_activity_log_service

    def import_dataset(
        self,
        rdf_content: str,
        rdf_format: str,
        identity: IdentityContext,
        duplicates_check: bool = True,
        target_status: str | None = None,
        target_released_at: str | None = None,
        target_version_change_type: str | None = None,
        source: str | None = None,
        source_dataset_id: int | None = None,
    ):
        graph = self._dataset_rdf_mapper.parse_graph(rdf_content, rdf_format)
        dataset_uri = self._dataset_rdf_mapper.select_dataset_resource(graph)
        publisher_id = self._dataset_rdf_mapper.get_publisher_id(graph, dataset_uri)

        contact_ids = self._ensure_reference_data_exists(
            graph=graph,
            dataset_uri=dataset_uri,
            publisher_id=publisher_id,
            created_by_id=identity.user_id,
            identity=identity,
            source=source,
        )

        dataset_dto, identifier = self._dataset_rdf_mapper.map_dataset(
            graph,
            dataset_uri,
            status_override=target_status,
            released_at_override=target_released_at,
            version_change_type_override=target_version_change_type,
            contact_ids=contact_ids,
            source=source,
            source_dataset_id=source_dataset_id,
        )

        dataset = self._dataset_service.insert_dataset(
            dataset_dto,
            identity,
            duplicates_check=duplicates_check,
            identifier=identifier,
            suppress_create_logging=source is not None,
        )

        if dataset_dto.distributions:
            for distribution_dto in sorted(
                dataset_dto.distributions, key=lambda d: (d.title or "").lower()
            ):
                self._distribution_service.add_distribution(
                    dataset_id=dataset.id,
                    distribution_dto=distribution_dto,
                    identity=identity,
                )

        if source is not None and source_dataset_id is not None:
            self._dataset_activity_log_service.log_external_dataset_import(
                user_id=identity.user_id,
                dataset_id=dataset.id,
                source_instance=source,
                source_dataset_id=source_dataset_id,
                outcome="success",
            )

        # Extract and add qualified attributions using the dedicated service
        qualified_attributions = (
            self._qualified_attribution_rdf_mapper.map_qualified_attributions(
                graph, dataset_uri
            )
        )
        if qualified_attributions:
            for attribution_dto in qualified_attributions:
                self._qualified_attribution_service.add_qualified_attribution(
                    dataset_id=dataset.id,
                    data=attribution_dto,
                    identity=identity,
                )

        # Extract and add dataset relations using the dedicated service
        relations = self._dataset_relation_rdf_mapper.map_dataset_relations(
            graph, dataset_uri
        )
        if relations:
            for relation_dto in relations:
                self._dataset_relation_service.add_relation(
                    source_dataset_id=dataset.id,
                    add_relation=relation_dto,
                    identity=identity,
                )

        # Extract and add data dictionaries using the dedicated service
        data_dictionaries = self._data_dictionary_rdf_mapper.map_data_dictionaries(
            graph, dataset_uri
        )
        if data_dictionaries:
            for data_dict_entry in data_dictionaries:
                self._data_dictionary_service.add_data_dictionary(
                    dataset_id=dataset.id,
                    data=data_dict_entry,
                    identity=identity,
                )

        return dataset

    def _ensure_reference_data_exists(
        self,
        graph: Graph,
        dataset_uri,
        publisher_id: int,
        created_by_id: int | None,
        identity: IdentityContext,
        source: str | None = None,
    ) -> set[int] | None:
        """Create keywords, applicable legislations, and contacts referenced in RDF before dataset import.

        Returns a set of contact_ids if contacts were found/created, None otherwise.
        """
        keyword_literals = self._dataset_rdf_mapper.get_keyword_literals(
            graph, dataset_uri
        )
        if keyword_literals:
            self._form_fields_import_service.ensure_keywords_exist(
                keyword_values=keyword_literals,
                organisation_id=publisher_id,
                created_by_id=created_by_id,
                source_instance=source,
            )

        applicable_legislation_with_titles = (
            self._dataset_rdf_mapper.get_applicable_legislation_with_titles(
                graph, dataset_uri
            )
        )
        if applicable_legislation_with_titles:
            self._form_fields_import_service.ensure_applicable_legislations_with_titles_exist(
                applicable_legislation_data=applicable_legislation_with_titles,
                organisation_id=publisher_id,
                created_by_id=created_by_id,
                source_instance=source,
            )

        # Ensure all contacts exist and return their IDs as a set
        contact_resources = self._contact_import_service.ensure_contacts_from_graph(
            graph=graph,
            dataset_uri=dataset_uri,
            organisation_id=publisher_id,
            identity=identity,
            skip_permission_validation=True,
        )

        return {c.id for c in contact_resources} if contact_resources else None

    def parse_dataset_dto(
        self,
        rdf_content: str,
        rdf_format: str,
    ) -> tuple[DatasetDto, Optional[str]]:
        graph = self._dataset_rdf_mapper.parse_graph(rdf_content, rdf_format)
        dataset_uri = self._dataset_rdf_mapper.select_dataset_resource(graph)
        return self._dataset_rdf_mapper.map_dataset(graph, dataset_uri)
