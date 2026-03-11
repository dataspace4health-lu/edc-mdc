from fastapi import Depends, status, APIRouter, HTTPException
from typing import List, Annotated
from services.authentic_source_assignment import AuthenticSourceAssignmentService
from schemas.authentic_source_label import (
    ResourceAuthenticSourceLabel,
    authentic_source_label_entity_to_resource,
)
from schemas.authentic_source_assignment import (
    BulkLabelAssignmentDto,
)
from models.identity_context import IdentityContext
from routes.auth import validate_and_retrieve_identity_context
from fastapi.responses import Response

router = APIRouter()


@router.post(
    "/api/v1/authentic-source-assignments",
    response_model=List[ResourceAuthenticSourceLabel],
    tags=["authentic-source-assignments"],
    status_code=status.HTTP_200_OK,
)
def assign_authentic_source_label(
    assignment_dto: BulkLabelAssignmentDto,
    service: Annotated[
        AuthenticSourceAssignmentService, Depends(AuthenticSourceAssignmentService)
    ],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(["authentic-source:assign"])
    ),
) -> ResourceAuthenticSourceLabel:
    return service.assign_labels(assignment_dto, identity)


@router.post(
    "/api/v1/datasets/{dataset_id}/authentic-source/complete-review",
    tags=["authentic-source-assignments"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def complete_authentic_source_review(
    dataset_id: int,
    service: Annotated[
        AuthenticSourceAssignmentService, Depends(AuthenticSourceAssignmentService)
    ],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(["authentic-source:assign"])
    ),
) -> Response:
    service.complete_authentic_source_review(dataset_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
