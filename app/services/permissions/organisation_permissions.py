from typing import Annotated, Tuple, Optional
from fastapi import Depends, HTTPException
from models.identity_context import IdentityContext
from repositories.user_assignment import UserAssignmentRepository
from services.permissions.base_permissions import BasePermissionsService


class OrganisationPermissionsService(BasePermissionsService):

    def validate_get_organisation_permissions(
        self, organisation_id: int, identity: IdentityContext
    ) -> None:
        # Global permissions - can access any organisation
        if (
            "contacts:edit" in identity.permissions
            or "organisations:edit" in identity.permissions
        ):
            return

        if (
            identity.current_organisation_id is not None
            and organisation_id != identity.current_organisation_id
        ):
            raise HTTPException(
                status_code=403,
                detail="You can only view your current organisation",
            )

        # Organisation-scoped permissions - can only access organisations they belong to
        if (
            "contacts:edit:organisation" in identity.permissions
            or "organisations:edit:organisation" in identity.permissions
        ):
            if self._is_user_assigned_to_organisation(
                identity.user_id, organisation_id
            ):
                return
            else:
                raise HTTPException(
                    status_code=403,
                    detail="You can only access organisations you belong to",
                )

        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this organisation",
        )

    def validate_update_organisation_permissions(
        self, organisation_id: int, identity: IdentityContext
    ) -> None:
        if (
            identity.current_organisation_id is not None
            and organisation_id != identity.current_organisation_id
        ):
            raise HTTPException(
                status_code=403,
                detail="You can only update your current organisation",
            )

        # Global permission - can update any organisation
        if "organisations:edit" in identity.permissions:
            return

        # Organisation-scoped permission - can only update organisations they belong to
        if "organisations:edit:organisation" in identity.permissions:
            if self._is_user_assigned_to_organisation(
                identity.user_id, organisation_id
            ):
                return
            else:
                raise HTTPException(
                    status_code=403,
                    detail="You can only update organisations you belong to",
                )

        raise HTTPException(
            status_code=403, detail="You do not have permission to update organisations"
        )
