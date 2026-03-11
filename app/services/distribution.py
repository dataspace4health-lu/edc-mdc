from datetime import UTC, datetime
from typing import Annotated, List
from fastapi import Depends, HTTPException, status
from models.distribution import (
    Distribution,
    DistributionAccessUrl,
    DistributionDownloadUrl,
    DistributionLanguage,
    DistributionApplicableLegislation,
    DistributionDocumentation,
    LinkedSchema,
    DistributionAccessService,
    PolicyType,
)
from models.identity_context import IdentityContext
from repositories.dataset import DatasetRepository
from repositories.distribution import DistributionRepository
from schemas.distribution import (
    DistributionDto,
    ResourceDistribution,
    distribution_entity_to_resource,
    generate_distribution_dto_from_distribution,
)
from services.enun_values import EnumValuesService
from services.policy_action_manager import PolicyActionManager
from services.dataset_permissions_service import DatasetPermissionsService
from services.activity_logs.distribution_activity_log import (
    DistributionActivityLogService,
)
from services.distribution_title_generator import (
    generate_unique_distribution_title,
    normalize_distribution_title,
)


class DistributionService:
    def __init__(
        self,
        vocabulary_service: Annotated[EnumValuesService, Depends(EnumValuesService)],
        dataset_repository: Annotated[DatasetRepository, Depends(DatasetRepository)],
        distribution_repository: Annotated[
            DistributionRepository, Depends(DistributionRepository)
        ],
        policy_action_manager: Annotated[
            PolicyActionManager, Depends(PolicyActionManager)
        ],
        dataset_permissions_service: Annotated[
            DatasetPermissionsService, Depends(DatasetPermissionsService)
        ],
        distribution_activity_log_service: Annotated[
            DistributionActivityLogService, Depends(DistributionActivityLogService)
        ],
    ):
        self._vocabulary_service = vocabulary_service
        self._dataset_repository = dataset_repository
        self._distribution_repository = distribution_repository
        self._policy_action_manager = policy_action_manager
        self._dataset_permissions_service = dataset_permissions_service
        self._distribution_activity_log_service = distribution_activity_log_service

    def get_distributions_by_dataset_id(
        self, dataset_id: int, identity: IdentityContext
    ) -> List[ResourceDistribution]:
        self._dataset_permissions_service.validate_read_permissions(
            dataset_id, identity
        )
        distributions = self._distribution_repository.get_distributions_from_dataset(
            dataset_id
        )
        return [distribution_entity_to_resource(dist) for dist in distributions]

    def add_distribution(
        self,
        dataset_id: int,
        distribution_dto: DistributionDto,
        identity: IdentityContext,
    ) -> ResourceDistribution:
        self._dataset_permissions_service.validate_edit_permissions(
            dataset_id, identity
        )
        resolved_title = self._resolve_distribution_title(
            dataset_id=dataset_id,
            distribution_dto=distribution_dto,
        )
        self._validate_unique_distribution_title(
            dataset_id=dataset_id, title=resolved_title
        )

        new_distribution = Distribution(dataset_id=dataset_id)
        merged_distribution = self.merge_distribution_dto_to_entity(
            new_distribution,
            distribution_dto,
            identity.user_id,
            resolved_title=resolved_title,
        )
        self._distribution_repository.refresh(merged_distribution)

        self._distribution_activity_log_service.log_distribution_created(
            user_id=identity.user_id,
            dataset_id=dataset_id,
            distribution_id=merged_distribution.id,
            distribution_title=merged_distribution.title,
        )

        return distribution_entity_to_resource(merged_distribution)

    def update_distribution(
        self,
        dataset_id: int,
        distribution_id: int,
        distribution_dto: DistributionDto,
        identity: IdentityContext,
    ) -> ResourceDistribution:
        self._dataset_permissions_service.validate_edit_permissions(
            dataset_id, identity
        )

        existing_distribution = self._distribution_repository.get_distribution(
            distribution_id
        )
        if existing_distribution.dataset_id != dataset_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Distribution does not belong to the specified dataset",
            )
        resolved_title = self._resolve_distribution_title(
            dataset_id=dataset_id,
            distribution_dto=distribution_dto,
            existing_distribution=existing_distribution,
        )
        self._validate_unique_distribution_title(
            dataset_id=dataset_id,
            title=resolved_title,
            exclude_distribution_id=distribution_id,
        )

        old_title = existing_distribution.title
        old_distribution_data = existing_distribution.to_dict_for_diff()

        merged_distribution = self.merge_distribution_dto_to_entity(
            existing_distribution,
            distribution_dto,
            identity.user_id,
            resolved_title=resolved_title,
        )
        self._distribution_repository.refresh(merged_distribution)
        new_distribution_data = merged_distribution.to_dict_for_diff()

        self._distribution_activity_log_service.log_distribution_updated(
            user_id=identity.user_id,
            dataset_id=dataset_id,
            old_distribution=old_distribution_data,
            new_distribution=new_distribution_data,
            distribution_title=merged_distribution.title or old_title,
        )

        return distribution_entity_to_resource(merged_distribution)

    def delete_distribution_by_id(
        self, dataset_id: int, distribution_id: int, identity: IdentityContext
    ) -> None:
        self._dataset_permissions_service.validate_edit_permissions(
            dataset_id, identity
        )

        existing_distribution = self._distribution_repository.get_distribution(
            distribution_id
        )
        if existing_distribution.dataset_id != dataset_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Distribution does not belong to the specified dataset",
            )

        distribution_title = existing_distribution.title

        self.delete_distribution(distribution_id)
        self._distribution_repository.commit()

        self._distribution_activity_log_service.log_distribution_deleted(
            user_id=identity.user_id,
            dataset_id=dataset_id,
            distribution_id=distribution_id,
            distribution_title=distribution_title,
        )

    def get_distribution(self, distribution_id: int) -> Distribution:
        return self._distribution_repository.get_distribution(distribution_id)

    def merge_distribution_dto_to_entity(
        self,
        distribution: Distribution,
        distribution_dto: DistributionDto,
        user_id: int,
        resolved_title: str | None = None,
    ) -> Distribution:
        distribution.title = (
            resolved_title
            or self._normalize_title(distribution_dto.title)
            or distribution.title
        )
        if not distribution.title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to determine distribution title.",
            )
        distribution.description = distribution_dto.description
        distribution.file_type = distribution_dto.file_type
        distribution.rights_statement = distribution_dto.rights_statement
        distribution.internal_only = distribution_dto.internal_only
        distribution.is_analytics = distribution_dto.is_analytics
        distribution.notes = distribution_dto.notes
        distribution.license = distribution_dto.license
        distribution.distribution_path = distribution_dto.distribution_path
        distribution.policy_type = PolicyType.SET.value
        distribution.availability = distribution_dto.availability
        distribution.modification_date = distribution_dto.modification_date
        distribution.release_date = distribution_dto.release_date
        distribution.byte_size = distribution_dto.byte_size
        distribution.checksum = distribution_dto.checksum
        distribution.media_type = distribution_dto.media_type
        distribution.compression_format = distribution_dto.compression_format
        distribution.packaging_format = distribution_dto.packaging_format
        distribution.distribution_dcat_status = (
            distribution_dto.distribution_dcat_status
        )
        distribution.spatial_resolution = distribution_dto.spatial_resolution
        distribution.temporal_resolution = distribution_dto.temporal_resolution

        self._persist_languages(distribution, distribution_dto)
        self._persist_applicable_legislations(distribution, distribution_dto)
        self._persist_linked_schemas(distribution, distribution_dto)
        self._persist_documentation(distribution, distribution_dto)
        self._presist_access_services(distribution, distribution_dto)

        if not distribution.id:
            distribution.created_at = datetime.now(UTC)
            self._distribution_repository.add(distribution)
        else:
            self._distribution_repository.merge(distribution)
            self._distribution_repository._db_session.flush()
        self._persist_download_urls(distribution, distribution_dto)
        self._persist_access_urls(distribution, distribution_dto)
        self._persist_policy_actions(distribution, distribution_dto, user_id)
        self._distribution_repository.commit()
        return distribution

    def _validate_unique_distribution_title(
        self,
        dataset_id: int,
        title: str,
        exclude_distribution_id: int | None = None,
    ) -> None:
        normalized_title = title.strip().lower()
        for (
            distribution
        ) in self._distribution_repository.get_distributions_from_dataset(dataset_id):
            if (
                exclude_distribution_id is not None
                and distribution.id == exclude_distribution_id
            ):
                continue
            if (
                distribution.title
                and distribution.title.strip().lower() == normalized_title
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A distribution with this title already exists.",
                )

    def _normalize_title(self, title: str | None) -> str | None:
        return normalize_distribution_title(title)

    def _resolve_distribution_title(
        self,
        dataset_id: int,
        distribution_dto: DistributionDto,
        existing_distribution: Distribution | None = None,
    ) -> str:
        explicit_title = self._normalize_title(distribution_dto.title)
        if explicit_title:
            return explicit_title

        if existing_distribution and existing_distribution.title:
            return existing_distribution.title

        existing_titles = [
            dist.title
            for dist in self._distribution_repository.get_distributions_from_dataset(
                dataset_id
            )
            if dist.title
        ]
        return generate_unique_distribution_title(distribution_dto, existing_titles)

    def _persist_policy_actions(
        self,
        distribution: Distribution,
        distribution_dto: DistributionDto,
        user_id: int,
    ) -> None:
        self._policy_action_manager.update_policy_actions(
            distribution, distribution_dto.policy_actions, user_id
        )

    def _persist_languages(
        self, distribution: Distribution, distribution_dto: DistributionDto
    ) -> None:
        def update_strategy(enum_value: DistributionLanguage) -> None:
            enum_value.distribution_id = distribution.id
            enum_value.distribution = distribution

        self._vocabulary_service.persist_enum_values(
            entity_update_strategy=update_strategy,
            existing_enum_values=distribution.languages,
            dto_values=distribution_dto.languages,
            clazz=DistributionLanguage,
        )

    def _persist_applicable_legislations(
        self, distribution: Distribution, distribution_dto: DistributionDto
    ) -> None:
        def update_strategy(enum_value: DistributionApplicableLegislation) -> None:
            enum_value.distribution = distribution
            enum_value.distribution_id = distribution.id

        self._vocabulary_service.persist_enum_values(
            entity_update_strategy=update_strategy,
            existing_enum_values=distribution.applicable_legislations,
            dto_values=distribution_dto.applicable_legislations,
            clazz=DistributionApplicableLegislation,
        )

    def _persist_access_urls(
        self, distribution: Distribution, distribution_dto: DistributionDto
    ) -> None:
        if distribution.id:
            self._distribution_repository._db_session.query(
                DistributionAccessUrl
            ).filter_by(distribution_id=distribution.id).delete()
        distribution.access_urls.clear()
        if distribution_dto.access_urls:
            for url in distribution_dto.access_urls:
                distribution.access_urls.append(DistributionAccessUrl(url=str(url)))

    def _persist_download_urls(
        self, distribution: Distribution, distribution_dto: DistributionDto
    ) -> None:
        if distribution.id:
            self._distribution_repository._db_session.query(
                DistributionDownloadUrl
            ).filter_by(distribution_id=distribution.id).delete()
        distribution.download_urls.clear()
        if distribution_dto.download_urls:
            for url in distribution_dto.download_urls:
                distribution.download_urls.append(DistributionDownloadUrl(url=str(url)))

    def _persist_linked_schemas(
        self, distribution: Distribution, distribution_dto: DistributionDto
    ) -> None:
        distribution.linked_schemas.clear()
        for linked_schema in distribution_dto.linked_schemas:
            distribution.linked_schemas.append(
                LinkedSchema(key=linked_schema, distribution_id=distribution.id)
            )

    def _persist_documentation(
        self, distribution: Distribution, distribution_dto: DistributionDto
    ) -> None:
        distribution.documentation_entries.clear()
        for doc_url in distribution_dto.documentation:
            distribution.documentation_entries.append(
                DistributionDocumentation(
                    value=str(doc_url), distribution_id=distribution.id
                )
            )

    def _presist_access_services(
        self, distribution: Distribution, distribution_dto: DistributionDto
    ) -> None:
        distribution.access_services.clear()
        for id in distribution_dto.access_service_ids:
            distribution.access_services.add(
                DistributionAccessService(
                    data_service_id=id, distribution_id=distribution.id
                )
            )

    def delete_distribution(self, distribution_id: int) -> None:
        self._distribution_repository.delete(distribution_id)

    def clone_distribution(
        self,
        original_distribution: Distribution,
        target_dataset_id: int = None,
        user_id: int = 1,
    ) -> Distribution:
        # Generate DTO from original distribution
        distribution_dto = generate_distribution_dto_from_distribution(
            original_distribution
        )

        # Create new distribution entity
        cloned_distribution = Distribution(
            dataset_id=target_dataset_id or original_distribution.dataset_id
        )

        # Use existing merge method to populate the distribution
        return self.merge_distribution_dto_to_entity(
            cloned_distribution,
            distribution_dto,
            user_id,
            resolved_title=self._normalize_title(distribution_dto.title),
        )
