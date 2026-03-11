from fastapi import APIRouter, Depends, HTTPException, status
from schemas.activity_logs import ResourceActivityLog
from typing import List, Annotated
from services.activity_log import ActivityLogService
from services.activity_logs.dataset_activity_log import DatasetActivityLogService
from models.identity_context import IdentityContext
from routes.auth import validate_and_retrieve_identity_context
from services.activity_logs.user_assignment_activity_log import (
    UserAssignmentActivityLogService,
)
from services.activity_logs.authentic_source_label_activity_log import (
    AuthenticSourceLabelActivityLogService,
)
from services.user_assignment_permissions import UserAssignmentPermissionsService

router = APIRouter()


@router.get(
    "/api/v1/datasets/{dataset_id}/activity-logs",
    response_model=List[ResourceActivityLog],
    tags=["activity-log"],
)
def retrieve_activity_logs_from_dataset(
    dataset_id: int,
    service: Annotated[DatasetActivityLogService, Depends(DatasetActivityLogService)],
    page: int = 1,
    page_size: int = 10,
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:edit:draft:my",
                "datasets:edit:draft:organisation",
                "datasets:edit:draft:group",
                "datasets:edit:draft",
                "datasets:read:all-after-draft",
                "datasets:read:all-after-draft:organisation",
                "datasets:read:all-after-complete",
                "datasets:read:completed",
                "datasets:read:validated",
                "datasets:read:approved",
                "datasets:read:published",
            ]
        )
    ),
) -> List[ResourceActivityLog]:
    return service.get_activity_logs_from_dataset(dataset_id, page, page_size)


@router.get(
    "/api/v1/organisations/{organisation_id}/activity-logs",
    response_model=List[ResourceActivityLog],
    tags=["activity-log"],
)
def retrieve_activity_logs_from_organisation(
    organisation_id: int,
    service: Annotated[ActivityLogService, Depends(ActivityLogService)],
    page: int = 1,
    page_size: int = 10,
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            ["contacts:edit", "contacts:edit:organisation"]
        )
    ),
) -> List[ResourceActivityLog]:
    return service.get_activity_logs_from_organisation(organisation_id, page, page_size)


@router.get(
    "/api/v1/organisations/activity-logs",
    response_model=List[ResourceActivityLog],
    tags=["activity-log"],
)
def retrieve_all_organisations_activity_logs(
    service: Annotated[ActivityLogService, Depends(ActivityLogService)],
    permissions_service: Annotated[
        UserAssignmentPermissionsService, Depends(UserAssignmentPermissionsService)
    ],
    multi_tenant: bool = True,
    page: int = 1,
    page_size: int = 10,
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            ["contacts:edit:organisation", "roles:manage"]
        )
    ),
) -> List[ResourceActivityLog]:

    organisation_ids = permissions_service.get_organisations_ids_for_logs(
        identity, multi_tenant
    )

    return service.get_all_activity_logs_from_organisations(
        organisation_ids, page, page_size
    )


@router.get(
    "/api/v1/{form_field}/activity-logs",
    response_model=List[ResourceActivityLog],
    tags=["activity-log"],
)
def retrieve_all_form_fields_activity_logs(
    form_field: str,
    service: Annotated[ActivityLogService, Depends(ActivityLogService)],
    page: int = 1,
    page_size: int = 10,
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            ["form-fields:edit", "form-fields:edit:my", "form-fields:edit:organisation"]
        )
    ),
) -> List[ResourceActivityLog]:
    if form_field not in ["keyword", "applicable_legislation"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid form field provided.",
        )
    return service.get_activity_logs_from_form_field(form_field, page, page_size)


@router.get(
    "/api/v1/activity-logs/assignments",
    response_model=List[ResourceActivityLog],
    tags=["activity-log"],
)
def retrieve_user_assignment_activity_logs(
    service: Annotated[
        UserAssignmentActivityLogService, Depends(UserAssignmentActivityLogService)
    ],
    permissions_service: Annotated[
        UserAssignmentPermissionsService, Depends(UserAssignmentPermissionsService)
    ],
    page: int = 1,
    page_size: int = 10,
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            ["roles:manage", "roles:manage:organisation"]
        )
    ),
) -> List[ResourceActivityLog]:

    filters = permissions_service.get_user_permission_filters(identity)

    if filters is None:
        return service.get_all_activity_logs(page, page_size)

    organisation_ids = filters.get("organisation_ids", [])
    return service.get_activity_logs_for_organisations(
        organisation_ids, page, page_size
    )


@router.get(
    "/api/v1/activity-logs/authentic_source_labels",
    response_model=List[ResourceActivityLog],
    tags=["activity-log"],
)
def retrieve_authentic_source_label_activity_logs(
    service: Annotated[
        AuthenticSourceLabelActivityLogService,
        Depends(AuthenticSourceLabelActivityLogService),
    ],
    page: int = 1,
    page_size: int = 10,
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:read:published",
                "datasets:read:all-after-draft",
                "datasets:read:all-after-draft:organisation",
            ]
        )
    ),
) -> List[ResourceActivityLog]:
    return service.get_all_activity_logs(page, page_size)
