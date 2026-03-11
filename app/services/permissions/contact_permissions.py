from typing import Annotated, Tuple, Optional
from fastapi import Depends, HTTPException
from models.identity_context import IdentityContext
from repositories.user_assignment import UserAssignmentRepository
from services.permissions.base_permissions import BasePermissionsService


class ContactPermissionsService(BasePermissionsService):
    def validate_contact_permissions(
        self, organisation_id: int, identity: IdentityContext
    ) -> None:
        if (
            "contacts:edit" in identity.permissions
            or "organisations:edit" in identity.permissions
        ):
            return

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
                    detail=f"You can only add/edit contacts within organisations you belong to",
                )

        raise HTTPException(
            status_code=403, detail=f"You do not have permission to add/edit contacts"
        )
