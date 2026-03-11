from fastapi import APIRouter, Depends, status, HTTPException, Response
from typing import Annotated, List
from services.user_assignment import UserAssignmentService
from schemas.user_assignment import UserAssignmentDto
from models.identity_context import IdentityContext
from routes.auth import validate_and_retrieve_identity_context

router = APIRouter()


@router.post(
    "/api/v1/organisations/{organisation_id}/assignments",
    tags=["user-assignments"],
    status_code=status.HTTP_201_CREATED,
)
def create_organisation_assignment(
    organisation_id: int,
    assignment_dto: UserAssignmentDto,
    service: Annotated[UserAssignmentService, Depends(UserAssignmentService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            ["roles:manage", "roles:manage:organisation"]
        )
    ),
):
    return service.create_user_organisation_assignment(
        organisation_id, assignment_dto, identity
    )


@router.delete(
    "/api/v1/organisations/{organisation_id}/assignments/{user_id}",
    tags=["user-assignments"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_organisation_assignment(
    organisation_id: int,
    user_id: int,
    service: Annotated[UserAssignmentService, Depends(UserAssignmentService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            ["roles:manage", "roles:manage:organisation"]
        )
    ),
) -> Response:
    service.delete_user_organisation_assignment(organisation_id, user_id, identity)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/api/v1/organisations/{organisation_id}/assignments/{user_id}/roles/{role_id}",
    tags=["user-assignments"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user_role_assignment(
    organisation_id: int,
    user_id: int,
    role_id: int,
    service: Annotated[UserAssignmentService, Depends(UserAssignmentService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            ["roles:manage", "roles:manage:organisation"]
        )
    ),
) -> Response:
    service.delete_user_role_assignment(organisation_id, user_id, role_id, identity)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
