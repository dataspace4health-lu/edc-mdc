from typing import Annotated, Tuple, Optional

from fastapi import Depends, HTTPException, status
from models.identity_context import IdentityContext
from repositories.dataset import DatasetRepository
from repositories.organisation import OrganisationRepository
from models.dataset import DatasetStatus
from services.config import ConfigService, get_config_service
from services.permissions.base_permissions import BasePermissionsService


class DatasetPermissionsService(BasePermissionsService):
    def __init__(
        self,
        dataset_repository: Annotated[DatasetRepository, Depends(DatasetRepository)],
        organisation_repository: Annotated[
            OrganisationRepository, Depends(OrganisationRepository)
        ] = None,
        config_service: Annotated[ConfigService, Depends(get_config_service)] = None,
    ):
        super().__init__(
            user_assignment_repository=None,
            organisation_repository=organisation_repository,
            config_service=config_service,
        )
        self._dataset_repository = dataset_repository

    def _ensure_not_imported(self, dataset_id: int) -> None:
        if self._dataset_repository.is_dataset_imported(dataset_id):
            raise HTTPException(
                status_code=403,
                detail="Imported datasets are read-only and cannot be modified.",
            )

    def _is_system_admin(self, identity: IdentityContext) -> bool:
        return "system:admin" in identity.permissions

    def validate_read_permissions(
        self, dataset_id: int, identity: IdentityContext
    ) -> None:
        if self._is_system_admin(identity):
            return

        [status, publisher_id, user_id] = (
            self._dataset_repository.get_dataset_status_publisher_id_and_user_id(
                dataset_id
            )
        )
        group_manager_user_ids = (
            self._dataset_repository.get_dataset_group_manager_user_ids(dataset_id)
        )

        if (
            identity.current_organisation_id is not None
            and publisher_id != identity.current_organisation_id
            and status != "PUBLISHED"
        ):
            raise HTTPException(
                status_code=403,
                detail=f"You are not allowed to retrieve this dataset",
            )

        if status is None and user_id is None:
            raise HTTPException(
                status_code=404, detail=f"Dataset[{dataset_id}] not found"
            )

        if "datasets:edit:draft" in identity.permissions and status == "DRAFT":
            return

        if (
            "datasets:read:all-after-draft" in identity.permissions
            and status != "DRAFT"
        ):
            return

        if (
            "datasets:read:all-after-draft:organisation" in identity.permissions
            and status != "DRAFT"
            and identity.current_organisation_id is not None
            and publisher_id == identity.current_organisation_id
        ):
            return

        if (
            "datasets:read:all-after-complete" in identity.permissions
            and status != "COMPLETED"
            and status != "DRAFT"
        ):
            return

        if user_id == identity.user_id:
            return

        if (
            "datasets:edit:draft:group" in identity.permissions
            and identity.user_id in group_manager_user_ids
        ):
            return

        if (
            "datasets:edit:draft:organisation" in identity.permissions
            and status == "DRAFT"
            and identity.current_organisation_id is not None
            and publisher_id == identity.current_organisation_id
        ):
            return

        if (
            identity.current_organisation_id is not None
            and publisher_id == identity.current_organisation_id
        ):

            if (
                "datasets:read:completed" in identity.permissions
                and status == "COMPLETED"
            ):
                return

            if (
                "datasets:read:validated" in identity.permissions
                and status == "VALIDATED"
            ):
                return

            if (
                "datasets:read:approved" in identity.permissions
                and status == "APPROVED"
            ):
                return

        if "datasets:read:published" in identity.permissions and status == "PUBLISHED":
            if (
                identity.current_organisation_id is not None
                and publisher_id != identity.current_organisation_id
            ):
                raise HTTPException(
                    status_code=403,
                    detail=f"You are not allowed to retrieve this dataset",
                )
            return

        raise HTTPException(
            status_code=403, detail=f"You are not allowed to retrieve this dataset"
        )

    def validate_edit_permissions(
        self,
        dataset_id: int,
        identity: IdentityContext,
    ) -> None:
        if self._is_system_admin(identity):
            return

        [status, publisher_id, user_id] = (
            self._dataset_repository.get_dataset_status_publisher_id_and_user_id(
                dataset_id
            )
        )

        if (
            identity.current_organisation_id is not None
            and publisher_id != identity.current_organisation_id
        ):
            raise HTTPException(
                status_code=403,
                detail=f"You are not allowed to update this dataset",
            )

        group_manager_user_ids = (
            self._dataset_repository.get_dataset_group_manager_user_ids(dataset_id)
        )

        if status == None and user_id == None:
            raise HTTPException(
                status_code=404,
                detail=f"Dataset[{dataset_id}] not found",
            )

        self._ensure_not_imported(dataset_id)

        if status != "DRAFT":
            raise HTTPException(
                status_code=409,
                detail=f"This dataset cannot be edited anymore, as it is not in draft mode anymore",
            )

        self._validate_organisation_ctie_access(publisher_id)

        if "datasets:edit:draft" in identity.permissions and status == "DRAFT":
            return

        if (
            "datasets:edit:draft:my" in identity.permissions
            and user_id == identity.user_id
        ):
            return

        if (
            "datasets:edit:draft:group" in identity.permissions
            and identity.user_id in group_manager_user_ids
        ):
            return

        if (
            "datasets:edit:draft:organisation" in identity.permissions
            and identity.current_organisation_id is not None
            and publisher_id == identity.current_organisation_id
        ):
            return

        raise HTTPException(
            status_code=403, detail=f"You are not allowed to edit this dataset"
        )

    def validate_delete_permissions(
        self, dataset_id: int, identity: IdentityContext
    ) -> None:
        if self._is_system_admin(identity):
            return

        [status, publisher_id, user_id] = (
            self._dataset_repository.get_dataset_status_publisher_id_and_user_id(
                dataset_id
            )
        )

        if (
            identity.current_organisation_id is not None
            and publisher_id != identity.current_organisation_id
        ):
            raise HTTPException(
                status_code=403,
                detail=f"You are not allowed to delete this dataset",
            )

        if status is None:
            raise HTTPException(
                status_code=404, detail=f"Dataset[{dataset_id}] not found"
            )

        self._ensure_not_imported(dataset_id)

        if status != "DRAFT":
            raise HTTPException(
                status_code=403,
                detail="This dataset cannot be deleted as it is not in the draft state.",
            )

        if "datasets:delete:draft" in identity.permissions:
            return

        if (
            "datasets:delete:draft:my" in identity.permissions
            and user_id == identity.user_id
        ):
            return

        if (
            "datasets:delete:draft:organisation" in identity.permissions
            and identity.current_organisation_id is not None
            and publisher_id == identity.current_organisation_id
        ):
            return

        raise HTTPException(
            status_code=403, detail="You do not have permission to delete this dataset."
        )

    def get_dataset_list_access_params(
        self, identity: IdentityContext, status: str
    ) -> Tuple[int, int]:
        created_by_user_id = None
        group_manager_user_id = None
        organisation_id = identity.current_organisation_id

        if status == DatasetStatus.DRAFT.value:
            if "datasets:edit:draft" in identity.permissions:
                # Can view all draft datasets
                return None, None, organisation_id
            elif "datasets:edit:draft:organisation" in identity.permissions:
                # Can view all draft datasets from their organisation
                return None, None, organisation_id
            elif "datasets:edit:draft:group" in identity.permissions:
                # Can view drafts for their group + own drafts
                return identity.user_id, identity.user_id, organisation_id
            else:
                # Otherwise can only view own drafts
                return identity.user_id, None, organisation_id

        elif status == DatasetStatus.COMPLETED.value:
            if "datasets:read:all-after-draft" in identity.permissions:
                # Can view all completed datasets
                return None, None, organisation_id
            elif "datasets:read:all-after-draft:organisation" in identity.permissions:
                # Can view all completed datasets from their organisation
                return None, None, organisation_id
            elif "datasets:status-change:validate:group" in identity.permissions:
                # GROUP_MANAGER can see completed datasets from their group + own
                return identity.user_id, identity.user_id, organisation_id
            elif "datasets:read:completed" in identity.permissions:
                return None, None, organisation_id
            else:
                # Otherwise can only view own completed datasets
                return identity.user_id, None, organisation_id

        elif (
            status == DatasetStatus.VALIDATED.value
            and "datasets:read:validated" in identity.permissions
        ):
            # If status is VALIDATED, can view all validated datasets
            return None, None, organisation_id

        elif (
            status == DatasetStatus.APPROVED.value
            and "datasets:read:approved" in identity.permissions
        ):
            # If status is APPROVED, can view all approved datasets
            return None, None, organisation_id

        elif (
            status == DatasetStatus.PUBLISHED.value
            and "datasets:read:published" in identity.permissions
        ):
            return None, None, organisation_id

        # If status is VALIDATED, APPROVED, PUBLISHED, INTERNAL_ONLY or DEPRECATED
        elif status in [
            DatasetStatus.VALIDATED.value,
            DatasetStatus.APPROVED.value,
            DatasetStatus.PUBLISHED.value,
            DatasetStatus.INTERNAL_ONLY.value,
            DatasetStatus.DEPRECATED.value,
        ]:
            if (
                "datasets:read:all-after-draft" in identity.permissions
                or "datasets:read:all-after-complete" in identity.permissions
            ):
                return None, None, organisation_id
            elif "datasets:read:all-after-draft:organisation" in identity.permissions:
                # Can view all datasets after draft from their organisation
                return None, None, organisation_id
            else:
                return identity.user_id, None, organisation_id

        # Fallback - if no specific rules match, only show own datasets
        return identity.user_id, None, organisation_id

    def validate_bulk_update_authentic_source_permissions(
        self,
        dataset_id: int,
        identity: IdentityContext,
    ) -> None:
        if self._is_system_admin(identity):
            return

        [status, publisher_id, user_id] = (
            self._dataset_repository.get_dataset_status_publisher_id_and_user_id(
                dataset_id
            )
        )

        if (
            identity.current_organisation_id is not None
            and publisher_id != identity.current_organisation_id
        ):
            raise HTTPException(
                status_code=403,
                detail=f"You are not allowed to update this dataset",
            )

        if status == None and user_id == None:
            raise HTTPException(
                status_code=404,
                detail=f"Dataset[{dataset_id}] not found",
            )

        if status != "PUBLISHED":
            raise HTTPException(
                status_code=409,
                detail=f"Authentic source can only be updated for published datasets",
            )

        if user_id == identity.user_id:
            return

        if "authentic-source:assign" in identity.permissions:
            return

        raise HTTPException(
            status_code=403, detail=f"You are not allowed to update this dataset"
        )

    def validate_create_permissions(
        self,
        publisher_id: Optional[int],
        identity: IdentityContext,
    ) -> None:
        if self._is_system_admin(identity):
            return

        if "datasets:edit:draft" in identity.permissions:
            self._validate_organisation_ctie_access(publisher_id)
            return

        if ("datasets:edit:draft:my" in identity.permissions) or (
            "datasets:edit:draft:organisation" in identity.permissions
        ):
            if identity.current_organisation_id is None:
                return

            if publisher_id == identity.current_organisation_id:
                self._validate_organisation_ctie_access(publisher_id)
                return

        raise HTTPException(
            status_code=403,
            detail="You are not allowed to create a dataset for this publisher",
        )

    def validate_status_change_permissions(
        self,
        dataset_id: int,
        publisher_id: Optional[int],
        identity: IdentityContext,
    ) -> None:
        if self._is_system_admin(identity):
            return

        self._ensure_not_imported(dataset_id)

        if "datasets:edit:draft" in identity.permissions:
            return

        if identity.current_organisation_id is None:
            return

        if publisher_id == identity.current_organisation_id:
            return

        raise HTTPException(
            status_code=403,
            detail="You are not allowed to change the dataset status for this publisher",
        )
