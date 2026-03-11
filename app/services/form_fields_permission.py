from typing import Annotated, List, Optional
from fastapi import Depends, HTTPException
from models.identity_context import IdentityContext
from repositories.keyword import KeywordRepository
from repositories.applicable_legislation import ApplicableLegislationRepository
from repositories.user_assignment import UserAssignmentRepository
from repositories.keyword_assignment import KeywordAssignmentRepository
from repositories.applicable_legislation_assignment import (
    ApplicableLegislationAssignmentRepository,
)


class FormFieldsPermissionsService:
    def __init__(
        self,
        keyword_repository: Annotated[KeywordRepository, Depends(KeywordRepository)],
        keyword_assignment_repository: Annotated[
            KeywordAssignmentRepository, Depends(KeywordAssignmentRepository)
        ],
        applicable_legislation_repository: Annotated[
            ApplicableLegislationRepository, Depends(ApplicableLegislationRepository)
        ],
        applicable_legislation_assignment_repository: Annotated[
            ApplicableLegislationAssignmentRepository,
            Depends(ApplicableLegislationAssignmentRepository),
        ],
        user_assignment_repository: Annotated[
            UserAssignmentRepository, Depends(UserAssignmentRepository)
        ],
    ):
        self._keyword_repository = keyword_repository
        self._keyword_assignment_repository = keyword_assignment_repository
        self._applicable_legislation_repository = applicable_legislation_repository
        self._applicable_legislation_assignment_repository = (
            applicable_legislation_assignment_repository
        )
        self._user_assignment_repository = user_assignment_repository

    def get_user_organisation_ids(
        self, identity: IdentityContext
    ) -> Optional[List[int]]:
        if "form-fields:edit" in identity.permissions:
            return None

        if self._has_any(
            identity, "form-fields:edit:my", "form-fields:edit:organisation"
        ):
            return [identity.current_organisation_id]

        raise HTTPException(
            status_code=403, detail="You do not have permission to edit form fields"
        )

    def validate_create_permissions(
        self, field_type: str, selected_org_ids: List[int], identity: IdentityContext
    ) -> None:
        if "form-fields:edit" in identity.permissions:
            return

        self._require_global_create_if_empty(field_type, selected_org_ids, identity)

        if not self._has_any(
            identity, "form-fields:edit:my", "form-fields:edit:organisation"
        ):
            raise HTTPException(
                403, f"You do not have permission to create {field_type}"
            )

        user_assignments = (
            self._user_assignment_repository.get_user_organisation_assignments(
                user_id=identity.user_id
            )
        )
        user_accessible_orgs = {a.organisation_id for a in user_assignments}

        for org_id in selected_org_ids:
            if org_id not in user_accessible_orgs:
                raise HTTPException(
                    403,
                    f"You don't have permission to create {field_type} for organization ID {org_id}. "
                    "You can only create within organizations you belong to.",
                )

    def validate_edit_and_delete_permissions(
        self,
        field_type: str,
        key: str,
        organisation_id: Optional[int],
        identity: IdentityContext,
    ) -> None:
        repository = self._get_repository(field_type)
        form_field = repository.get(key)
        if form_field is None:
            raise HTTPException(
                status_code=404, detail=f"{field_type.capitalize()}[{key}] not found"
            )

        if "form-fields:edit" in identity.permissions:
            return

        # Check if field has multiple organization assignments and block non-catalogue managers
        if field_type in ["keyword", "applicable_legislation"]:
            assignments = self._get_field_assignments(field_type, key)
            if len(assignments) > 1 and not self.can_create_global_fields(identity):
                raise HTTPException(
                    status_code=403,
                    detail="Only Catalogue Managers can update form fields assigned to multiple organisations",
                )

        if organisation_id is None:
            raise HTTPException(
                status_code=403,
                detail="You must be in an organization context to edit form fields",
            )

        is_assigned_to_user_org = self._is_field_assigned_to_user_org(
            field_type, key, organisation_id
        )
        is_global_field = not self._field_has_assignments(field_type, key)

        if not is_assigned_to_user_org and not is_global_field:
            raise HTTPException(
                status_code=403,
                detail=f"This {field_type} is not assigned to your organization",
            )

        if (
            "form-fields:edit:my" in identity.permissions
            and form_field.created_by_id == identity.user_id
            and self._is_user_assigned_to_organisation(
                identity.user_id, organisation_id
            )
        ):
            return

        if (
            "form-fields:edit:organisation" in identity.permissions
            and self._is_user_assigned_to_organisation(
                identity.user_id, organisation_id
            )
        ):
            return

        raise HTTPException(
            status_code=403,
            detail=f"You do not have permission to edit this {field_type}",
        )

    def can_create_global_fields(self, identity: IdentityContext) -> bool:
        return "form-fields:edit" in identity.permissions

    def validate_selected_organizations(
        self, identity: IdentityContext, selected_org_ids: List[int]
    ) -> None:
        if "form-fields:edit" in identity.permissions:
            return

        user_assignments = (
            self._user_assignment_repository.get_user_organisation_assignments(
                user_id=identity.user_id
            )
        )
        user_accessible_orgs = {a.organisation_id for a in user_assignments}

        for org_id in selected_org_ids:
            if org_id not in user_accessible_orgs:
                raise HTTPException(
                    status_code=403,
                    detail=f"You don't have access to organization with ID {org_id}",
                )

    def _has_any(self, identity: IdentityContext, *permissions: str) -> bool:
        # Check if user has any of the specified permissions
        return any(perm in identity.permissions for perm in permissions)

    def _require_global_create_if_empty(
        self, field_type: str, selected_org_ids: List[int], identity: IdentityContext
    ) -> None:
        if len(selected_org_ids) == 0 and not self.can_create_global_fields(identity):
            raise HTTPException(
                status_code=403,
                detail=f"Only Catalogue Managers can create global {field_type}. Please select at least one organization.",
            )

    def _is_field_assigned_to_user_org(
        self, field_type: str, field_key: str, organisation_id: int
    ) -> bool:
        if field_type == "keyword":
            assignment = (
                self._keyword_assignment_repository.get_keyword_organisation_assignment(
                    field_key, organisation_id
                )
            )
            return assignment is not None
        elif field_type == "applicable_legislation":
            assignment = self._applicable_legislation_assignment_repository.get_applicable_legislation_organisation_assignment(
                field_key, organisation_id
            )
            return assignment is not None
        return False

    def _field_has_assignments(self, field_type: str, field_key: str) -> bool:
        if field_type == "keyword":
            assignments = self._keyword_assignment_repository.get_keyword_organisation_assignments(
                field_key
            )
            return len(assignments) > 0
        elif field_type == "applicable_legislation":
            assignments = self._applicable_legislation_assignment_repository.get_applicable_legislation_organisation_assignments(
                field_key
            )
            return len(assignments) > 0
        return False

    def _get_repository(self, field_type: str):
        if field_type == "keyword":
            return self._keyword_repository
        elif field_type == "applicable_legislation":
            return self._applicable_legislation_repository
        else:
            raise ValueError(f"Unsupported field type: {field_type}")

    def _get_field_assignments(self, field_type: str, field_key: str):
        if field_type == "keyword":
            return self._keyword_assignment_repository.get_keyword_organisation_assignments(
                field_key
            )
        elif field_type == "applicable_legislation":
            return self._applicable_legislation_assignment_repository.get_applicable_legislation_organisation_assignments(
                field_key
            )
        return []

    def _is_user_assigned_to_organisation(
        self, user_id: int, organisation_id: int
    ) -> bool:
        assignment = self._user_assignment_repository.get_user_organisation_assignment(
            organisation_id=organisation_id, user_id=user_id
        )
        return assignment is not None
