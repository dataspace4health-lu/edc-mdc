import uuid
from datetime import UTC, datetime
from typing import Annotated, List, Optional

from fastapi import Depends, HTTPException, status
from models.dataset import (
    Dataset,
    DatasetAreaOfCompetence,
    DatasetAreaOfWork,
    DatasetCodeValue,
    DatasetCodingSystem,
    DatasetConformsTo,
    DatasetConvention,
    DatasetCreator,
    DatasetContact,
    DatasetDataProtectionType,
    DatasetDocumentation,
    DatasetGroupManagers,
    DatasetPersonalData,
    DatasetProvenanceEntry,
    DatasetPurpose,
    DatasetHealthLegalBasisEntry,
    DatasetVersionNote,
    DatasetHealthCategory,
    DatasetHealthTheme,
    DatasetKeyword,
    DatasetLandingPage,
    DatasetApplicableLegislation,
    DatasetSpatialCoverage,
    DatasetSpatialResolution,
    DatasetStatus,
    DatasetTheme,
    DatasetTypes,
    DatasetStatus,
    DatasetApplicableLegislation,
    DatasetGroupManagers,
    DatasetDataProtectionType,
    DatasetLanguage,
    SeriesMembership,
    WasGeneratedBy,
    OtherIdentifier,
    DatasetVersionChangeType,
)
from models.identity_context import IdentityContext
from repositories.contact import ContactRepository
from repositories.dataset import DatasetRepository
from repositories.organisation import OrganisationRepository
from schemas.dataset import (
    DatasetDto,
    DatasetCountsResponse,
    PaginatedDatasetResponse,
    PaginationMeta,
    ResourceDataset,
    dataset_entity_to_resource,
    generate_dataset_dto_from_dataset,
)
from services.activity_logs.dataset_activity_log import DatasetActivityLogService
from services.database_session_manager import DatabaseSessionManager
from services.dataset_permissions_service import DatasetPermissionsService
from services.dataset_status import DatasetStatusService
from services.distribution import DistributionService
from services.enun_values import EnumValuesService
from services.data_dictionary import DataDictionaryService
from services.dataset_relation import DatasetRelationService
from services.dataset_version import DatasetVersionService
from services.qualified_attribution import QualifiedAttributionService
from services.config import ConfigService, get_config_service


class DatasetService:
    def __init__(
        self,
        vocabulary_service: Annotated[EnumValuesService, Depends(EnumValuesService)],
        distribution_service: Annotated[
            DistributionService, Depends(DistributionService)
        ],
        dataset_repository: Annotated[DatasetRepository, Depends(DatasetRepository)],
        activity_log_service: Annotated[
            DatasetActivityLogService, Depends(DatasetActivityLogService)
        ],
        database_session_manager: Annotated[
            DatabaseSessionManager, Depends(DatabaseSessionManager)
        ],
        organisation_repository: Annotated[
            OrganisationRepository, Depends(OrganisationRepository)
        ],
        dataset_permissions_service: Annotated[
            DatasetPermissionsService, Depends(DatasetPermissionsService)
        ],
        contact_repository: Annotated[ContactRepository, Depends(ContactRepository)],
        data_dictionary_service: Annotated[
            DataDictionaryService, Depends(DataDictionaryService)
        ],
        qualified_attribution_service: Annotated[
            QualifiedAttributionService, Depends(QualifiedAttributionService)
        ],
        dataset_relation_service: Annotated[
            DatasetRelationService, Depends(DatasetRelationService)
        ],
        config_service: Annotated[ConfigService, Depends(get_config_service)],
    ):
        self._vocabulary_service = vocabulary_service
        self._distribution_service = distribution_service
        self._dataset_repository = dataset_repository
        self._activity_log_service = activity_log_service
        self._database_session_manager = database_session_manager
        self._organisation_repository = organisation_repository
        self._dataset_permissions_service = dataset_permissions_service
        self._contact_repository = contact_repository
        self._data_dictionary_service = data_dictionary_service
        self._qualified_attributions_service = qualified_attribution_service
        self._dataset_relation_service = dataset_relation_service
        self._dataset_version_service = DatasetVersionService()
        self._config_service = config_service

    def get_paginated_datasets(
        self,
        identity: IdentityContext,
        status: str,
        page: int,
        page_size: int,
        query: str,
        dataset_types: list[str],
        rights_statements: list[str],
        keywords: list[str],
        themes: list[str],
        applicable_legislations: list[str],
        periodicities: list[str],
        organisations: list[int],
        has_unlabeled_authentic_source: bool = None,
        authentic_source_pending: bool = None,
    ) -> PaginatedDatasetResponse:
        valid_statuses = [
            DatasetStatus.PUBLISHED.value,
            DatasetStatus.INTERNAL_ONLY.value,
            DatasetStatus.APPROVED.value,
            DatasetStatus.VALIDATED.value,
            DatasetStatus.COMPLETED.value,
            DatasetStatus.DRAFT.value,
            DatasetStatus.DEPRECATED.value,
        ]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status parameter. Must be one of: {', '.join(valid_statuses)}",
            )

        created_by_user_id, group_manager_user_id, organisation_id = (
            self._dataset_permissions_service.get_dataset_list_access_params(
                identity, status
            )
        )

        datasets, total_count = self._dataset_repository.get_paginated_datasets(
            status=status,
            group_manager_user_id=group_manager_user_id,
            created_by_user_id=created_by_user_id,
            page=page,
            page_size=page_size,
            query=query,
            dataset_types=dataset_types,
            rights_statements=rights_statements,
            keywords=keywords,
            themes=themes,
            applicable_legislations=applicable_legislations,
            periodicities=periodicities,
            organisation_id=organisation_id,
            organisations=organisations,
            authentic_source_pending=authentic_source_pending,
            has_unlabeled_authentic_source=has_unlabeled_authentic_source,
        )

        dataset_resources = [
            dataset_entity_to_resource(
                it,
                self._get_dataset_status_triggers(it, identity),
                self._dataset_version_service.get_latest_version_dataset_id(it),
            )
            for it in datasets
        ]

        total_pages = (
            (total_count + page_size - 1) // page_size if total_count > 0 else 1
        )

        return PaginatedDatasetResponse(
            items=dataset_resources,
            meta=PaginationMeta(
                total_items=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
            ),
        )

    def get_dataset_counts(
        self,
        identity: IdentityContext,
    ) -> DatasetCountsResponse:
        result = {}
        total = 0
        for status in [
            DatasetStatus.DRAFT.value,
            DatasetStatus.COMPLETED.value,
            DatasetStatus.VALIDATED.value,
            DatasetStatus.APPROVED.value,
            DatasetStatus.PUBLISHED.value,
            DatasetStatus.INTERNAL_ONLY.value,
            DatasetStatus.DEPRECATED.value,
        ]:
            created_by_user_id, group_manager_user_id, organisation_id = (
                self._dataset_permissions_service.get_dataset_list_access_params(
                    identity, status
                )
            )
            count = self._dataset_repository.get_count_for_status(
                status=status,
                created_by_user_id=created_by_user_id,
                group_manager_user_id=group_manager_user_id,
                organisation_id=organisation_id,
            )
            result[status] = count
            total += count

        return DatasetCountsResponse(
            draft=result.get(DatasetStatus.DRAFT.value, 0),
            published=result.get(DatasetStatus.PUBLISHED.value, 0),
            completed=result.get(DatasetStatus.COMPLETED.value, 0),
            validated=result.get(DatasetStatus.VALIDATED.value, 0),
            approved=result.get(DatasetStatus.APPROVED.value, 0),
            internal_only=result.get(DatasetStatus.INTERNAL_ONLY.value, 0),
            deprecated=result.get(DatasetStatus.DEPRECATED.value, 0),
            total=total,
        )

    def get_datasets(self, identity: IdentityContext) -> List[ResourceDataset]:
        datasets = self._list_datasets_according_to_permissions(identity)

        return [
            dataset_entity_to_resource(
                it,
                self._get_dataset_status_triggers(it, identity),
                self._dataset_version_service.get_latest_version_dataset_id(it),
            )
            for it in datasets
        ]

    def _list_datasets_according_to_permissions(
        self, identity: IdentityContext
    ) -> List[Dataset]:
        datasets_dict = {}

        user_created_datasets = (
            self._dataset_repository.get_all_datasets_created_by_user(identity.user_id)
        )
        for dataset in user_created_datasets:
            datasets_dict[dataset.id] = dataset

        if "datasets:edit:draft" in identity.permissions:
            all_datasets = self._dataset_repository.get_draft_datasets()
            for dataset in all_datasets:
                datasets_dict[dataset.id] = dataset

        if "datasets:read:all-after-draft" in identity.permissions:
            after_draft_datasets = self._dataset_repository.get_datasets_after_draft()
            for dataset in after_draft_datasets:
                datasets_dict[dataset.id] = dataset

        if "datasets:read:all-after-complete" in identity.permissions:
            after_completed_datasets = (
                self._dataset_repository.get_datasets_after_completed()
            )
            for dataset in after_completed_datasets:
                datasets_dict[dataset.id] = dataset

        if "datasets:edit:draft:my" in identity.permissions:
            my_datasets = self._dataset_repository.get_draft_datasets_created_by_user(
                identity.user_id
            )
            for dataset in my_datasets:
                datasets_dict[dataset.id] = dataset

        if "datasets:edit:draft:group" in identity.permissions:
            group_datasets = self._dataset_repository.get_datasets_by_group(
                identity.user_id
            )
            for dataset in group_datasets:
                datasets_dict[dataset.id] = dataset

        return list(datasets_dict.values())

    def get_dataset(
        self, dataset_id: int, identity: IdentityContext
    ) -> ResourceDataset:
        self._dataset_permissions_service.validate_read_permissions(
            dataset_id, identity
        )

        dataset = self._dataset_repository.get_dataset(dataset_id)

        return dataset_entity_to_resource(
            dataset,
            self._get_dataset_status_triggers(dataset, identity),
            self._dataset_version_service.get_latest_version_dataset_id(dataset),
        )

    def insert_dataset(
        self,
        dataset_dto: DatasetDto,
        identity: IdentityContext,
        duplicates_check: bool = True,
        identifier: str = None,
        suppress_create_logging: bool = False,
    ) -> ResourceDataset:
        try:
            self._dataset_permissions_service.validate_create_permissions(
                publisher_id=dataset_dto.publisher_id,
                identity=identity,
            )
            if duplicates_check:
                if self._dataset_repository.exists_by_title_description_publisher(
                    dataset_dto.title, dataset_dto.description, dataset_dto.publisher_id
                ):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="A dataset with the same title, description, and publisher already exists.",
                    )

            dataset = Dataset(
                submitted_at=datetime.now(UTC),
                identifier=identifier if identifier else str(uuid.uuid1()),
            )

            dataset_resource = self._merge_and_commit_changes(
                dataset, dataset_dto, identity
            )

            if not suppress_create_logging:
                self._activity_log_service.log_dataset_activities(
                    identity.user_id, Dataset(id=dataset.id), dataset_dto, "create"
                )

            self._database_session_manager.commit()

            return dataset_resource
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

    def update_dataset(
        self,
        dataset_id: int,
        dataset_dto: DatasetDto,
        identity: IdentityContext,
    ) -> ResourceDataset:
        try:
            self._dataset_permissions_service.validate_edit_permissions(
                dataset_id, identity
            )

            dataset = self._dataset_repository.get_dataset(dataset_id)

            self._activity_log_service.log_dataset_activities(
                identity.user_id, dataset, dataset_dto, "update"
            )

            return self._merge_and_commit_changes(dataset, dataset_dto, identity)
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

    def clone_dataset(
        self, dataset_id: int, identity: IdentityContext
    ) -> ResourceDataset:
        self._dataset_permissions_service.validate_read_permissions(
            dataset_id, identity
        )

        original_dataset = self._dataset_repository.get_dataset(dataset_id)
        if not original_dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset with ID {dataset_id} not found.",
            )

        dataset_dto = generate_dataset_dto_from_dataset(original_dataset, clone=True)

        cloned_dataset_resource = self.insert_dataset(dataset_dto, identity)

        # Copy distributions from original dataset to cloned dataset
        self._copy_distributions(
            original_dataset.id, cloned_dataset_resource.id, identity.user_id
        )

        # Commit and refresh to get the distributions in the response
        self._database_session_manager.commit()

        self._data_dictionary_service.copy_data_dictionaries(
            original_dataset.id,
            cloned_dataset_resource.id,
            identity,
            preserve_authentic_source=False,
        )

        return self.get_dataset(cloned_dataset_resource.id, identity)

    def create_dataset_version(
        self,
        dataset_id: int,
        identity: IdentityContext,
        version_change_type: str = DatasetVersionChangeType.METADATA_ONLY.value,
    ) -> ResourceDataset:
        self._dataset_permissions_service.validate_read_permissions(
            dataset_id, identity
        )

        original_dataset = self._dataset_repository.get_dataset(dataset_id)
        if not original_dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset with ID {dataset_id} not found.",
            )

        dataset_dto = generate_dataset_dto_from_dataset(original_dataset, clone=False)
        dataset_dto = DatasetDto(
            **{
                **dataset_dto.model_dump(),
                "version_change_type": version_change_type,
            }
        )
        new_version_dataset_resource = self.insert_dataset(
            dataset_dto,
            identity,
            duplicates_check=False,
            identifier=original_dataset.identifier,
        )

        new_dataset_entity = self._dataset_repository.get_dataset(
            new_version_dataset_resource.id
        )
        new_dataset_entity.previous_version_dataset_id = original_dataset.id
        self._dataset_repository.merge(new_dataset_entity)

        # Copy distributions from original dataset to new version
        self._copy_distributions(
            original_dataset.id, new_version_dataset_resource.id, identity.user_id
        )

        self._data_dictionary_service.copy_data_dictionaries(
            source_dataset_id=dataset_id,
            target_dataset_id=new_version_dataset_resource.id,
            identity=identity,
            preserve_authentic_source=True,
        )

        self._dataset_relation_service.copy_dataset_relations(
            source_dataset_id=original_dataset.id,
            target_dataset_id=new_dataset_entity.id,
            identity=identity,
        )

        self._qualified_attributions_service.copy_qualified_attributions(
            source_dataset_id=original_dataset.id,
            target_dataset_id=new_dataset_entity.id,
        )

        self._database_session_manager.commit()
        self._database_session_manager.refresh(new_dataset_entity)

        return dataset_entity_to_resource(
            new_dataset_entity,
            self._get_dataset_status_triggers(new_dataset_entity, identity),
            self._dataset_version_service.get_latest_version_dataset_id(
                new_dataset_entity
            ),
        )

    def get_dataset_versions_chain(
        self, dataset_id: int, identity: IdentityContext
    ) -> List[Dataset]:
        self._dataset_permissions_service.validate_read_permissions(
            dataset_id, identity
        )

        chain = []
        current = self._dataset_repository.get_dataset(dataset_id)

        if not current:
            return chain

        previous_version_id = current.previous_version_dataset_id
        while previous_version_id:
            previous_dataset = self._dataset_repository.get_dataset(previous_version_id)
            if not previous_dataset:
                break
            chain.insert(0, previous_dataset)
            previous_version_id = previous_dataset.previous_version_dataset_id

        chain.append(current)

        return chain

    def delete_dataset(self, dataset_id: int, identity: IdentityContext) -> None:
        self._dataset_permissions_service.validate_delete_permissions(
            dataset_id, identity
        )

        self._dataset_repository.delete_dataset(dataset_id)
        self._database_session_manager.commit()

    def _merge_and_commit_changes(
        self, dataset: Dataset, dataset_dto: DatasetDto, identity: IdentityContext
    ) -> ResourceDataset:
        try:
            user_id = dataset.user_id if dataset.user_id else identity.user_id
            merged_dataset = self.merge_dataset_dto_to_entity(
                dataset, dataset_dto, user_id
            )
            self._database_session_manager.commit()
            self._database_session_manager.refresh(merged_dataset)

            return dataset_entity_to_resource(
                merged_dataset,
                self._get_dataset_status_triggers(merged_dataset, identity),
                self._dataset_version_service.get_latest_version_dataset_id(
                    merged_dataset
                ),
            )
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

    def merge_dataset_dto_to_entity(
        self, dataset: Dataset, dataset_dto: DatasetDto, user_id: int
    ) -> Dataset:
        dataset.title = dataset_dto.title
        dataset.user_id = user_id
        dataset.publisher_id = dataset_dto.publisher_id
        dataset.description = dataset_dto.description
        dataset.time_period_start = dataset_dto.time_period_start
        dataset.time_period_end = dataset_dto.time_period_end
        dataset.retention_period_start = dataset_dto.retention_period_start
        dataset.retention_period_end = dataset_dto.retention_period_end
        dataset.deprecated_at = dataset_dto.deprecated_at
        dataset.released_at = dataset_dto.released_at
        dataset.rights_statement = dataset_dto.rights_statement
        dataset.periodicity = dataset_dto.periodicity
        dataset.notes = dataset_dto.notes
        dataset.duration_of_administrative_utility = (
            dataset_dto.duration_of_administrative_utility
        )
        dataset.max_typical_age = dataset_dto.max_typical_age
        dataset.min_typical_age = dataset_dto.min_typical_age
        dataset.number_of_records = dataset_dto.number_of_records
        dataset.number_of_unique_individuals = dataset_dto.number_of_unique_individuals
        dataset.final_disposition = dataset_dto.final_disposition
        dataset.version = dataset_dto.version
        dataset.modified_at = dataset_dto.modified_at
        dataset.release_date = dataset_dto.release_date
        dataset.monitoring_location = dataset_dto.monitoring_location
        dataset.population_coverage = dataset_dto.population_coverage
        dataset.is_dataset_series = dataset_dto.is_dataset_series
        dataset.temporal_resolution = dataset_dto.temporal_resolution
        dataset.source = dataset_dto.source
        dataset.source_dataset_id = dataset_dto.source_dataset_id
        if dataset_dto.version_change_type is not None:
            dataset.version_change_type = dataset_dto.version_change_type
        elif not dataset.id:
            dataset.version_change_type = None
        dataset.status = dataset_dto.status or DatasetStatus.DRAFT.value

        self._persist_dataset_types(dataset, dataset_dto)
        self._persist_themes(dataset, dataset_dto)
        self._persist_keywords(dataset, dataset_dto)
        self._persist_health_categories(dataset, dataset_dto)
        self._persist_health_themes(dataset, dataset_dto)
        self._persist_spatial_coverages(dataset, dataset_dto)
        self._persist_conventions(dataset, dataset_dto)
        self._persist_areas_of_work(dataset, dataset_dto)
        self._persist_areas_of_competence(dataset, dataset_dto)
        self._persist_applicable_legislations(dataset, dataset_dto)
        self._persist_spatial_resolutions(dataset, dataset_dto)
        self._persist_group_managers(dataset, dataset_dto)
        self._persist_creators(dataset, dataset_dto)
        self._persist_contacts(dataset, dataset_dto)
        self._persist_landing_pages(dataset, dataset_dto)
        self._persist_documentation(dataset, dataset_dto)
        self._persist_purpose(dataset, dataset_dto)
        self._persist_data_protection_types(dataset, dataset_dto)
        self._persist_languages(dataset, dataset_dto)
        self._presist_was_generated_by(dataset, dataset_dto)
        self._presist_other_identifiers(dataset, dataset_dto)
        self._persist_conforms_to(dataset, dataset_dto)
        self._persist_provenance(dataset, dataset_dto)
        self._persist_health_legal_basis(dataset, dataset_dto)
        self._persist_version_notes(dataset, dataset_dto)
        self._persist_code_values(dataset, dataset_dto)
        self._persist_coding_systems(dataset, dataset_dto)
        self._persist_personal_data(dataset, dataset_dto)

        if dataset.is_dataset_series:
            self._persist_series_memberships(dataset, dataset_dto)

        if not dataset.id:
            self._dataset_repository.add(dataset)
        else:
            self._dataset_repository.merge(dataset)
        return dataset

    def _persist_dataset_types(self, dataset: Dataset, dataset_dto: DatasetDto) -> None:
        def update_strategy(enum_value: DatasetTypes) -> None:
            enum_value.dataset_id = dataset.id
            enum_value.dataset = dataset

        self._vocabulary_service.persist_enum_values(
            entity_update_strategy=update_strategy,
            existing_enum_values=dataset.dataset_types,
            dto_values=dataset_dto.dataset_types,
            clazz=DatasetTypes,
        )

    def _persist_themes(self, dataset: Dataset, dataset_dto: DatasetDto) -> None:
        def update_strategy(enum_value: DatasetTheme) -> None:
            enum_value.dataset_id = dataset.id
            enum_value.dataset = dataset

        self._vocabulary_service.persist_enum_values(
            entity_update_strategy=update_strategy,
            existing_enum_values=dataset.themes,
            dto_values=dataset_dto.themes,
            clazz=DatasetTheme,
        )

    def _persist_keywords(self, dataset: Dataset, dataset_dto: DatasetDto) -> None:
        def update_strategy(enum_value: DatasetKeyword) -> None:
            enum_value.dataset_id = dataset.id
            enum_value.dataset = dataset

        self._vocabulary_service.persist_enum_values(
            entity_update_strategy=update_strategy,
            existing_enum_values=dataset.keywords,
            dto_values=dataset_dto.keywords,
            clazz=DatasetKeyword,
        )

    def _persist_health_categories(
        self, dataset: Dataset, dataset_dto: DatasetDto
    ) -> None:
        def update_strategy(enum_value: DatasetHealthCategory) -> None:
            enum_value.dataset_id = dataset.id
            enum_value.dataset = dataset

        self._vocabulary_service.persist_enum_values(
            entity_update_strategy=update_strategy,
            existing_enum_values=dataset.health_categories,
            dto_values=dataset_dto.health_categories,
            clazz=DatasetHealthCategory,
        )

    def _persist_health_themes(self, dataset: Dataset, dataset_dto: DatasetDto) -> None:
        def update_strategy(enum_value: DatasetHealthTheme) -> None:
            enum_value.dataset_id = dataset.id
            enum_value.dataset = dataset

        self._vocabulary_service.persist_enum_values(
            entity_update_strategy=update_strategy,
            existing_enum_values=dataset.health_themes,
            dto_values=dataset_dto.health_themes,
            clazz=DatasetHealthTheme,
        )

    def _persist_spatial_coverages(
        self, dataset: Dataset, dataset_dto: DatasetDto
    ) -> None:
        def update_strategy(enum_value: DatasetSpatialCoverage) -> None:
            enum_value.dataset_id = dataset.id
            enum_value.dataset = dataset

        self._vocabulary_service.persist_enum_values(
            entity_update_strategy=update_strategy,
            existing_enum_values=dataset.spatial_coverages,
            dto_values=dataset_dto.spatial_coverages,
            clazz=DatasetSpatialCoverage,
        )

    def _persist_conventions(self, dataset: Dataset, dataset_dto: DatasetDto) -> None:
        def update_strategy(enum_value: DatasetConvention) -> None:
            enum_value.dataset_id = dataset.id
            enum_value.dataset = dataset

        self._vocabulary_service.persist_enum_values(
            entity_update_strategy=update_strategy,
            existing_enum_values=dataset.conventions,
            dto_values=dataset_dto.conventions,
            clazz=DatasetConvention,
        )

    def _persist_areas_of_work(self, dataset: Dataset, dataset_dto: DatasetDto) -> None:
        def update_strategy(enum_value: DatasetTheme) -> None:
            enum_value.dataset_id = dataset.id
            enum_value.dataset = dataset

        self._vocabulary_service.persist_enum_values(
            entity_update_strategy=update_strategy,
            existing_enum_values=dataset.areas_of_work,
            dto_values=dataset_dto.areas_of_work,
            clazz=DatasetAreaOfWork,
        )

    def _persist_areas_of_competence(
        self, dataset: Dataset, dataset_dto: DatasetDto
    ) -> None:
        def update_strategy(enum_value: DatasetTheme) -> None:
            enum_value.dataset_id = dataset.id
            enum_value.dataset = dataset

        self._vocabulary_service.persist_enum_values(
            entity_update_strategy=update_strategy,
            existing_enum_values=dataset.areas_of_competence,
            dto_values=dataset_dto.areas_of_competence,
            clazz=DatasetAreaOfCompetence,
        )

    def _persist_applicable_legislations(
        self, dataset: Dataset, dataset_dto: DatasetDto
    ) -> None:
        def update_strategy(enum_value: DatasetApplicableLegislation) -> None:
            enum_value.dataset_id = dataset.id
            enum_value.dataset = dataset

        self._vocabulary_service.persist_enum_values(
            entity_update_strategy=update_strategy,
            existing_enum_values=dataset.applicable_legislations,
            dto_values=dataset_dto.applicable_legislations,
            clazz=DatasetApplicableLegislation,
        )

    def _persist_group_managers(
        self, dataset: Dataset, dataset_dto: DatasetDto
    ) -> None:
        dataset.group_managers.clear()
        if dataset_dto.group_managers:
            for manager_id in dataset_dto.group_managers:
                dataset.group_managers.add(
                    DatasetGroupManagers(dataset_id=dataset.id, user_id=manager_id)
                )

    def _persist_creators(self, dataset: Dataset, dataset_dto: DatasetDto) -> None:
        dataset.creators.clear()
        if dataset_dto.creator_ids:
            for creator_id in dataset_dto.creator_ids:
                dataset.creators.add(
                    DatasetCreator(dataset_id=dataset.id, organisation_id=creator_id)
                )

    def _persist_contacts(self, dataset: Dataset, dataset_dto: DatasetDto) -> None:
        dataset.contacts.clear()
        if dataset_dto.contact_ids:
            for contact_id in dataset_dto.contact_ids:
                dataset.contacts.add(
                    DatasetContact(dataset_id=dataset.id, contact_id=contact_id)
                )

    def _persist_landing_pages(self, dataset: Dataset, dataset_dto: DatasetDto) -> None:
        dataset.landing_pages.clear()
        if dataset_dto.landing_pages:
            for url in dataset_dto.landing_pages:
                dataset.landing_pages.append(
                    DatasetLandingPage(dataset_id=dataset.id, url=str(url))
                )

    def _persist_documentation(self, dataset: Dataset, dataset_dto: DatasetDto) -> None:
        dataset.documentation_entries.clear()
        if dataset_dto.documentation:
            for doc_value in dataset_dto.documentation:
                dataset.documentation_entries.append(
                    DatasetDocumentation(dataset_id=dataset.id, value=doc_value)
                )

    def _persist_purpose(self, dataset: Dataset, dataset_dto: DatasetDto) -> None:
        dataset.purpose_entries.clear()
        if dataset_dto.purpose:
            for purpose_value in dataset_dto.purpose:
                dataset.purpose_entries.add(
                    DatasetPurpose(dataset_id=dataset.id, value=purpose_value)
                )

    def _persist_provenance(self, dataset: Dataset, dataset_dto: DatasetDto) -> None:
        dataset.provenance_entries.clear()
        if dataset_dto.provenance:
            for value in dataset_dto.provenance:
                dataset.provenance_entries.append(
                    DatasetProvenanceEntry(dataset_id=dataset.id, value=value)
                )

    def _persist_health_legal_basis(
        self, dataset: Dataset, dataset_dto: DatasetDto
    ) -> None:
        dataset.health_legal_basis_entries.clear()
        if dataset_dto.health_legal_basis:
            for value in dataset_dto.health_legal_basis:
                dataset.health_legal_basis_entries.append(
                    DatasetHealthLegalBasisEntry(dataset_id=dataset.id, value=value)
                )

    def _persist_version_notes(self, dataset: Dataset, dataset_dto: DatasetDto) -> None:
        dataset.version_notes.clear()
        if dataset_dto.version_notes:
            for value in dataset_dto.version_notes:
                dataset.version_notes.append(
                    DatasetVersionNote(dataset_id=dataset.id, value=value)
                )

    def _persist_coding_systems(
        self, dataset: Dataset, dataset_dto: DatasetDto
    ) -> None:
        dataset.coding_systems.clear()
        if dataset_dto.coding_systems:
            for value in dataset_dto.coding_systems:
                dataset.coding_systems.append(
                    DatasetCodingSystem(dataset_id=dataset.id, value=value)
                )

    def _persist_code_values(self, dataset: Dataset, dataset_dto: DatasetDto) -> None:
        dataset.code_values.clear()
        if dataset_dto.code_values:
            for value in dataset_dto.code_values:
                dataset.code_values.append(
                    DatasetCodeValue(dataset_id=dataset.id, value=value)
                )

    def _persist_data_protection_types(
        self, dataset: Dataset, dataset_dto: DatasetDto
    ) -> None:
        def update_strategy(enum_value: DatasetDataProtectionType) -> None:
            enum_value.dataset_id = dataset.id
            enum_value.dataset = dataset

        self._vocabulary_service.persist_enum_values(
            entity_update_strategy=update_strategy,
            existing_enum_values=dataset.data_protection_types,
            dto_values=dataset_dto.data_protection_types,
            clazz=DatasetDataProtectionType,
        )

    def _persist_languages(self, dataset: Dataset, dataset_dto: DatasetDto) -> None:
        def update_strategy(enum_value: DatasetLanguage) -> None:
            enum_value.dataset_id = dataset.id
            enum_value.dataset = dataset

        self._vocabulary_service.persist_enum_values(
            entity_update_strategy=update_strategy,
            existing_enum_values=dataset.languages,
            dto_values=dataset_dto.languages,
            clazz=DatasetLanguage,
        )

    def _persist_spatial_resolutions(
        self, dataset: Dataset, dataset_dto: DatasetDto
    ) -> None:
        dataset.spatial_resolutions.clear()

        if dataset_dto.spatial_resolutions:
            for resolution_value in dataset_dto.spatial_resolutions:
                dataset.spatial_resolutions.append(
                    DatasetSpatialResolution(
                        dataset_id=dataset.id, value=resolution_value
                    )
                )

    def _get_dataset_status_triggers(
        self, dataset: Dataset, identity: IdentityContext
    ) -> List[str]:
        status_service = DatasetStatusService(
            dataset=dataset,
            dataset_repository=self._dataset_repository,
            database_session_manager=self._database_session_manager,
            identity=identity,
            config_service=self._config_service,
            dataset_permissions_service=self._dataset_permissions_service,
        )
        return status_service.get_triggers()

    def _persist_series_memberships(
        self, dataset: Dataset, dataset_dto: DatasetDto
    ) -> None:
        if not dataset_dto.member_datasets:
            dataset.member_datasets.clear()
            return

        existing_memberships = {
            membership.dataset_id: membership for membership in dataset.member_datasets
        }

        dataset.member_datasets.clear()

        for position, member_id in enumerate(dataset_dto.member_datasets):
            if member_id == dataset.id:
                continue

            if member_id in existing_memberships:
                membership = existing_memberships[member_id]
                membership.position = position
            else:
                membership = SeriesMembership(
                    series_id=dataset.id, dataset_id=member_id, position=position
                )

            membership.is_first = position == 0
            membership.is_last = position == len(dataset_dto.member_datasets) - 1

            dataset.member_datasets.add(membership)

    def _presist_was_generated_by(
        self, dataset: Dataset, dataset_dto: DatasetDto
    ) -> None:
        dataset.was_generated_by.clear()
        for id in dataset_dto.was_generated_by:
            dataset.was_generated_by.add(WasGeneratedBy(dataset_id=dataset.id, key=id))

    def _presist_other_identifiers(
        self, dataset: Dataset, dataset_dto: DatasetDto
    ) -> None:
        dataset.other_identifiers.clear()
        for id in dataset_dto.other_identifiers:
            dataset.other_identifiers.add(
                OtherIdentifier(dataset_id=dataset.id, key=id)
            )

    def _persist_conforms_to(self, dataset: Dataset, dataset_dto: DatasetDto) -> None:
        dataset.conforms_to_values.clear()
        if dataset_dto.conforms_to:
            for value in dataset_dto.conforms_to:
                dataset.conforms_to_values.append(
                    DatasetConformsTo(dataset_id=dataset.id, key=str(value))
                )

    def _copy_distributions(
        self, source_dataset_id: int, target_dataset_id: int, user_id: int
    ) -> None:
        source_dataset = self._dataset_repository.get_dataset(source_dataset_id)

        if not source_dataset:
            return

        # Copy each distribution from source to target using distribution service
        for source_distribution in source_dataset.distributions:
            self._distribution_service.clone_distribution(
                source_distribution,
                target_dataset_id=target_dataset_id,
                user_id=user_id,
            )

    def _persist_personal_data(self, dataset: Dataset, dataset_dto: DatasetDto) -> None:
        dataset.personal_data.clear()
        for value in dataset_dto.personal_data:
            dataset.personal_data.append(
                DatasetPersonalData(dataset_id=dataset.id, key=value)
            )
