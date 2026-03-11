from typing import Annotated, List
from fastapi import Depends, HTTPException, status
from models.identity_context import IdentityContext
from models.qualified_attribution import DatasetQualifiedAttribution
from repositories.qualified_attribution import QualifiedAttributionRepository
from repositories.organisation import OrganisationRepository
from repositories.dataset import DatasetRepository
from schemas.qualified_attribution import (
    QualifiedAttributionDto,
    ResourceQualifiedAttribution,
    qualified_attribution_entity_to_resource,
)
from services.database_session_manager import DatabaseSessionManager
from services.dataset_permissions_service import DatasetPermissionsService
from services.activity_logs.qualifiedAttributionActivityLogService import (
    QualifiedAttributionActivityLogService,
)


class QualifiedAttributionService:
    def __init__(
        self,
        repository: Annotated[
            QualifiedAttributionRepository, Depends(QualifiedAttributionRepository)
        ],
        database_session_manager: Annotated[
            DatabaseSessionManager, Depends(DatabaseSessionManager)
        ],
        dataset_permissions_service: Annotated[
            DatasetPermissionsService, Depends(DatasetPermissionsService)
        ],
        organisation_repository: Annotated[
            OrganisationRepository, Depends(OrganisationRepository)
        ],
        dataset_repository: Annotated[DatasetRepository, Depends(DatasetRepository)],
        qualified_attribution_activity_log_service: Annotated[
            QualifiedAttributionActivityLogService,
            Depends(QualifiedAttributionActivityLogService),
        ],
    ):
        self._repository = repository
        self._database_session_manager = database_session_manager
        self._dataset_permissions_service = dataset_permissions_service
        self._organisation_repository = organisation_repository
        self._dataset_repository = dataset_repository
        self._qualified_attribution_activity_log_service = (
            qualified_attribution_activity_log_service
        )

    def get_qualified_attributions_by_dataset_id(
        self, dataset_id: int, identity: IdentityContext
    ) -> List[ResourceQualifiedAttribution]:
        self._dataset_permissions_service.validate_read_permissions(
            dataset_id, identity
        )
        attributions = self._repository.get_attributions_by_dataset_id(dataset_id)
        return [qualified_attribution_entity_to_resource(attr) for attr in attributions]

    def add_qualified_attribution(
        self, dataset_id: int, data: QualifiedAttributionDto, identity: IdentityContext
    ) -> ResourceQualifiedAttribution:
        try:
            self._dataset_permissions_service.validate_edit_permissions(
                dataset_id, identity
            )

            if self._repository.exists(dataset_id, data.organisation_id, data.role):
                organisation = self._organisation_repository.get_organisation(
                    data.organisation_id
                )
                role_label = data.role
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"The attribution '{organisation.name}' with role '{role_label}' already exists for this dataset.",
                )

            organisation = self._organisation_repository.get_organisation(
                data.organisation_id
            )

            attribution = DatasetQualifiedAttribution(
                dataset_id=dataset_id,
                organisation_id=data.organisation_id,
                role=data.role,
            )

            self._repository.add(attribution)
            self._database_session_manager.commit()
            self._database_session_manager.refresh(attribution)

            self._qualified_attribution_activity_log_service.log_qualified_attribution_added(
                user_id=identity.user_id,
                dataset_id=dataset_id,
                organisation_name=organisation.name,
                role=data.role,
            )

            return qualified_attribution_entity_to_resource(attribution)
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

    def update_qualified_attribution(
        self,
        dataset_id: int,
        attribution_id: int,
        data: QualifiedAttributionDto,
        identity: IdentityContext,
    ) -> ResourceQualifiedAttribution:
        try:
            self._dataset_permissions_service.validate_edit_permissions(
                dataset_id, identity
            )

            attribution = self._repository.get_qualified_attribution(attribution_id)

            if attribution.dataset_id != dataset_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Qualified attribution does not belong to this dataset",
                )

            new_organisation = self._organisation_repository.get_organisation(
                data.organisation_id
            )
            if not new_organisation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Organisation not found",
                )

            if (
                attribution.organisation_id != data.organisation_id
                or attribution.role != data.role
            ):
                if self._repository.exists(dataset_id, data.organisation_id, data.role):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"The attribution '{new_organisation.name}' with role '{data.role}' already exists for this dataset.",
                    )

            old_organisation = self._organisation_repository.get_organisation(
                attribution.organisation_id
            )
            old_role = attribution.role

            self._repository.update(
                attribution,
                organisation_id=data.organisation_id,
                role=data.role,
            )
            self._database_session_manager.commit()
            self._database_session_manager.refresh(attribution)

            self._qualified_attribution_activity_log_service.log_qualified_attribution_updated(
                user_id=identity.user_id,
                dataset_id=dataset_id,
                old_organisation_name=old_organisation.name,
                old_role=old_role,
                new_organisation_name=new_organisation.name,
                new_role=data.role,
            )

            return qualified_attribution_entity_to_resource(attribution)
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

    def delete_qualified_attribution(
        self, dataset_id: int, attribution_id: int, identity: IdentityContext
    ) -> None:
        self._dataset_permissions_service.validate_edit_permissions(
            dataset_id, identity
        )

        attribution = self._repository.get_qualified_attribution(attribution_id)

        if attribution.dataset_id != dataset_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Qualified attribution does not belong to this dataset",
            )

        organisation = self._organisation_repository.get_organisation(
            attribution.organisation_id
        )
        old_role = attribution.role

        self._repository.delete(attribution_id)
        self._database_session_manager.commit()

        self._qualified_attribution_activity_log_service.log_qualified_attribution_removed(
            user_id=identity.user_id,
            dataset_id=dataset_id,
            organisation_name=organisation.name,
            role=old_role,
        )

    def copy_qualified_attributions(
        self, source_dataset_id: int, target_dataset_id: int
    ) -> None:
        attributions = self._repository.get_attributions_by_dataset_id(
            source_dataset_id
        )
        for attr in attributions:
            new_attr = DatasetQualifiedAttribution(
                dataset_id=target_dataset_id,
                organisation_id=attr.organisation_id,
                role=attr.role,
            )
            self._repository.add(new_attr)
        self._database_session_manager.commit()
