from dataclasses import dataclass
from models.user import User
from typing import Set, Union, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from schemas.user_assignment import ResourceOrganisationAssignment, ResourceRole


@dataclass(frozen=True)
class FeatureOptions:
    enable_duration_of_data: bool
    enable_conventions: bool
    enable_area_of_work_and_competence: bool
    enable_distribution_path: bool
    enable_notes: bool
    enable_distribution_notes: bool
    enable_validation_via_group_manager: bool
    enable_monitoring_location: bool
    enable_authentic_source: bool
    enable_multi_tenants: bool
    enable_upload_datasets_to_front_office: bool
    enable_dual_instance: bool


class ResourceUserOrganisation(BaseModel):
    id: int
    name: str
    type: Optional[str]
    email: Optional[str]


@dataclass(frozen=True)
class ResourceUser:
    id: int
    name: str
    email: str
    feature_options: FeatureOptions
    iam_roles: list[str]
    permissions: list[str]
    assignments: list[ResourceOrganisationAssignment]
    current_organisation: Optional[ResourceUserOrganisation]
    show_notice_on_homepage: Union[str, None]
    can_edit_form_fields: bool = False
    default_themes: Set[str] = None
    is_deprecated: bool = False
    last_login_at: Optional[datetime] = None
    has_ctie_only_access: bool = False


def user_entity_to_resource(
    user: User,
    permissions: list[str],
    feature_flag_data: dict,
    default_themes: Set[str],
    show_notice_on_homepage: str,
    current_org_id: Optional[int],
    has_ctie_only_access: bool = False,
) -> ResourceUser:

    feature_options = FeatureOptions(
        enable_notes=feature_flag_data.get("enable_notes", False),
        enable_distribution_notes=feature_flag_data.get(
            "enable_distribution_notes", False
        ),
        enable_distribution_path=feature_flag_data.get(
            "enable_distribution_path", False
        ),
        enable_duration_of_data=feature_flag_data.get("enable_duration_of_data", False),
        enable_conventions=feature_flag_data.get("enable_conventions", False),
        enable_area_of_work_and_competence=feature_flag_data.get(
            "enable_area_of_work_and_competence", False
        ),
        enable_validation_via_group_manager=feature_flag_data.get(
            "enable_validation_via_group_manager", False
        ),
        enable_monitoring_location=feature_flag_data.get(
            "enable_monitoring_location", False
        ),
        enable_authentic_source=feature_flag_data.get("enable_authentic_source", False),
        enable_upload_datasets_to_front_office=feature_flag_data.get(
            "enable_upload_datasets_to_front_office", False
        ),
        enable_multi_tenants=feature_flag_data.get("enable_multi_tenants", False),
        enable_dual_instance=feature_flag_data.get("enable_dual_instance", False),
    )

    iam_roles = (
        [role.strip() for role in user.iam_roles.split(",")] if user.iam_roles else []
    )

    current_organisation = None

    if current_org_id and user.organisation_assignments:
        for assignment in user.organisation_assignments:
            if assignment.organisation_id == current_org_id:
                current_organisation = ResourceUserOrganisation(
                    id=assignment.organisation.id,
                    name=assignment.organisation.name,
                    type=assignment.organisation.type,
                    email=assignment.organisation.email,
                )
                break

    return ResourceUser(
        id=user.id,
        current_organisation=current_organisation,
        name=user.name,
        email=user.email,
        feature_options=feature_options,
        permissions=permissions,
        iam_roles=iam_roles,
        can_edit_form_fields="form-fields:edit" in permissions
        or "form-fields:edit:my" in permissions
        or "form-fields:edit:organisation" in permissions,
        default_themes=default_themes,
        show_notice_on_homepage=show_notice_on_homepage,
        assignments=[
            ResourceOrganisationAssignment(
                organisation_id=assignment.organisation_id,
                organisation_name=assignment.organisation.name,
                roles=[
                    ResourceRole(id=rs.role.id, name=rs.role.name)
                    for rs in assignment.roles
                ],
                is_deprecated=assignment.organisation.is_deprecated,
            )
            for assignment in user.organisation_assignments
        ],
        is_deprecated=user.is_deprecated,
        last_login_at=user.last_login_at,
        has_ctie_only_access=has_ctie_only_access,
    )


class PaginationMeta(BaseModel):
    total_items: int
    page: int
    page_size: int
    total_pages: int


class PaginatedUserResponse(BaseModel):
    items: List[ResourceUser]
    meta: PaginationMeta


class UserListRequest(BaseModel):
    page: int = 1
    page_size: int = 10
    query: Optional[str] = None
    organisation_ids: Optional[List[int]] = None
    role_ids: Optional[List[int]] = None
    only_unassigned: Optional[bool] = False
    is_deprecated: Optional[bool] = False
