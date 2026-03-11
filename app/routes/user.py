from typing import Annotated, List
from fastapi import Request

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import Response
from models.identity_context import IdentityContext
from schemas.user import (
    ResourceUser,
    PaginatedUserResponse,
    UserListRequest,
)

from services.user import UserService
from routes.auth import validate_and_retrieve_identity_context

router = APIRouter()


@router.post(
    "/api/v1/users",
    response_model=PaginatedUserResponse,
    tags=["user"],
)
def users(
    request: Annotated[UserListRequest, Body()],
    service: Annotated[UserService, Depends(UserService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            ["roles:manage", "roles:manage:organisation"]
        )
    ),
) -> List[ResourceUser]:
    return service.get_users(
        page=request.page,
        page_size=request.page_size,
        query=request.query,
        organisation_ids=request.organisation_ids,
        role_ids=request.role_ids,
        only_unassigned=request.only_unassigned,
        identity=identity,
        is_deprecated=request.is_deprecated,
    )


@router.delete(
    "/api/v1/users/{user_id}",
    response_class=Response,
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["user"],
)
def delete_unassigned_user(
    user_id: int,
    service: Annotated[UserService, Depends(UserService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(["roles:manage"])
    ),
) -> None:
    service.delete_unassigned_user(
        user_id=user_id,
        identity=identity,
    )


@router.post("/api/v1/switch-organisation/{org_id}")
def switch_organisation(
    org_id: int,
    request: Request,
    user_service: Annotated[UserService, Depends(UserService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:edit:draft:my",
                "datasets:edit:draft:organisation",
                "datasets:edit:draft",
            ]
        )
    ),
):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = user_service.find_by_id(user_id)

    has_access = any(
        ua.organisation_id == org_id for ua in user.organisation_assignments
    )

    if not has_access or "roles:manage" in identity.permissions:
        raise HTTPException(
            status_code=403, detail="Not allowed to switch to this organization"
        )

    request.session["current_organisation_id"] = org_id
    return {"message": "Organization switched successfully"}


@router.patch(
    "/api/v1/users/{user_id}/toggle-deprecation",
    response_class=Response,
    tags=["user"],
    status_code=status.HTTP_200_OK,
)
def change_deprecation_status(
    user_id: int,
    service: Annotated[UserService, Depends(UserService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(["roles:manage"])
    ),
) -> None:
    return service.update_deprecation_status(user_id, identity=identity)


@router.delete(
    "/api/v1/users/{user_id}/iam-roles",
    response_class=Response,
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["user"],
)
def remove_user_iam_roles(
    user_id: int,
    service: Annotated[UserService, Depends(UserService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(["roles:manage"])
    ),
) -> None:
    service.remove_iam_roles(user_id=user_id, identity=identity)
