from typing import Annotated, Optional, Union, List

from fastapi import Depends, HTTPException
from models.identity_context import IdentityContext
from repositories.user_assignment import UserAssignmentRepository
from repositories.organisation import OrganisationRepository
from repositories.user import UserRepository
from services.config import ConfigService, get_config_service
from services.permissions.base_permissions import BasePermissionsService


class UserAssignmentPermissionsService(BasePermissionsService):
    def __init__(
        self,
        user_assignment_repository: Annotated[
            UserAssignmentRepository, Depends(UserAssignmentRepository)
        ],
        organisation_repository: Annotated[
            OrganisationRepository, Depends(OrganisationRepository)
        ],
        user_repository: Annotated[UserRepository, Depends(UserRepository)],
        config_service: Annotated[ConfigService, Depends(get_config_service)] = None,
    ):
        super().__init__(
            user_assignment_repository=user_assignment_repository,
            organisation_repository=organisation_repository,
            config_service=config_service,
        )
        self._user_repository = user_repository

    def validate_role_assignment_permissions(
        self, organisation_id: int, target_user_id: int, identity: IdentityContext
    ) -> None:
        self._validate_organisation_and_user_exist(organisation_id, target_user_id)

        self._validate_organisation_ctie_access(organisation_id)

        # Global permission - can manage roles for any user in any organisation
        if "roles:manage" in identity.permissions:
            return

        if (
            identity.current_organisation_id is not None
            and organisation_id != identity.current_organisation_id
        ):
            raise HTTPException(
                status_code=403,
                detail="You can only assign roles to your current organisation",
            )

        # Organisation-scoped permission - can only manage roles within organisations they belong to
        if "roles:manage:organisation" in identity.permissions:
            if self._is_user_assigned_to_organisation(
                identity.user_id, organisation_id
            ):
                return
            else:
                raise HTTPException(
                    status_code=403,
                    detail=f"You can only manage roles within organisations you belong to",
                )

        raise HTTPException(
            status_code=403,
            detail="You do not have permission to manage role assignments",
        )

    def get_user_permission_filters(self, identity: IdentityContext) -> Optional[dict]:
        if "roles:manage" in identity.permissions:
            return None

        if "roles:manage:organisation" in identity.permissions:

            user_assignments = (
                self._user_assignment_repository.get_user_organisation_assignments(
                    identity.user_id
                )
            )

            org_ids = [assignment.organisation_id for assignment in user_assignments]
            return {
                "organisation_ids": org_ids,
                "include_unassigned": False,
            }

        raise HTTPException(403, "You do not have permission to view users.")

    def _validate_organisation_and_user_exist(
        self, organisation_id: int, user_id: int
    ) -> None:
        organisation = self._organisation_repository.get_organisation(organisation_id)
        if not organisation:
            raise HTTPException(
                status_code=404, detail=f"Organisation[{organisation_id}] not found"
            )

        user = self._user_repository.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User[{user_id}] not found")

    def _is_user_assigned_to_organisation(
        self, user_id: int, organisation_id: int
    ) -> bool:
        assignment = self._user_assignment_repository.get_user_organisation_assignment(
            organisation_id=organisation_id, user_id=user_id
        )
        return assignment is not None

    def get_organisations_ids_for_logs(
        self, identity: IdentityContext, multi_tenant: bool
    ) -> Optional[List[int]]:
        if multi_tenant and "roles:manage" in identity.permissions:
            return None

        return [identity.current_organisation_id]
