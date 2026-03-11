from fastapi import Depends, status, APIRouter, HTTPException, Query
from fastapi.responses import Response
from typing import List, Annotated
from services.authentic_source_label import AuthenticSourceLabelService
from schemas.authentic_source_label import (
    AuthenticSourceLabelDto,
    ResourceAuthenticSourceLabel,
    LabelAssignmentHistory,
)
from models.identity_context import IdentityContext
from routes.auth import validate_and_retrieve_identity_context
from schemas.catalogue import CatalogueFormat
from utils.error_responses import ErrorResponse
from services.authentic_source_labels_catalogue import (
    AuthenticSourceLabelsCatalogueService,
)

router = APIRouter()


@router.post(
    "/api/v1/authentic-source-labels",
    response_model=ResourceAuthenticSourceLabel,
    tags=["authentic-source-labels"],
    status_code=status.HTTP_201_CREATED,
)
def create_authentic_source_label(
    label_dto: AuthenticSourceLabelDto,
    service: Annotated[
        AuthenticSourceLabelService, Depends(AuthenticSourceLabelService)
    ],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(["authentic-source:assign"])
    ),
) -> ResourceAuthenticSourceLabel:
    return service.create_label(label_dto, identity)


@router.get(
    "/api/v1/authentic-source-labels/{label_id}/history",
    response_model=List[LabelAssignmentHistory],
    tags=["authentic-source-labels-history"],
)
def get_authentic_source_label_history(
    label_id: int,
    service: Annotated[
        AuthenticSourceLabelService,
        Depends(AuthenticSourceLabelService),
    ],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:read:published",
                "datasets:read:all-after-draft",
                "datasets:read:all-after-draft:organisation",
            ]
        )
    ),
) -> List[LabelAssignmentHistory]:
    return service.get_previous_label_assigned_datasets(label_id)


@router.get(
    "/api/v1/authentic-source-labels",
    response_model=List[ResourceAuthenticSourceLabel],
    tags=["authentic-source-labels"],
)
def get_authentic_source_labels(
    service: Annotated[
        AuthenticSourceLabelService, Depends(AuthenticSourceLabelService)
    ],
    include_deprecated: bool = Query(False),
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:read:published",
                "datasets:read:all-after-draft",
                "datasets:read:all-after-draft:organisation",
            ]
        )
    ),
) -> List[ResourceAuthenticSourceLabel]:
    return service.get_all_labels(include_deprecated=include_deprecated)


@router.put(
    "/api/v1/authentic-source-labels/{label_id}",
    response_model=ResourceAuthenticSourceLabel,
    tags=["authentic-source-labels"],
    status_code=status.HTTP_200_OK,
)
def update_authentic_source_label(
    label_id: int,
    label_dto: AuthenticSourceLabelDto,
    service: Annotated[
        AuthenticSourceLabelService, Depends(AuthenticSourceLabelService)
    ],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(["authentic-source:assign"])
    ),
) -> ResourceAuthenticSourceLabel:
    return service.update_label(label_id, label_dto, identity)


@router.delete(
    "/api/v1/authentic-source-labels/{label_id}",
    tags=["authentic-source-labels"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_authentic_source_label(
    label_id: int,
    service: Annotated[
        AuthenticSourceLabelService, Depends(AuthenticSourceLabelService)
    ],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(["authentic-source:assign"])
    ),
):
    service.delete_label(label_id, identity)
    return Response(content=None, status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/api/v1/authentic-source-labels/{label_id}/toggle-deprecation",
    response_model=ResourceAuthenticSourceLabel,
    tags=["authentic-source-labels"],
    status_code=status.HTTP_200_OK,
)
def change_deprecation_status(
    label_id: int,
    service: Annotated[
        AuthenticSourceLabelService, Depends(AuthenticSourceLabelService)
    ],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(["authentic-source:assign"])
    ),
) -> ResourceAuthenticSourceLabel:
    return service.update_deprecation_status(label_id, identity)


@router.get(
    "/api/v1/authentic-source-labels/catalogue.{format}",
    tags=["authentic-source-labels"],
)
def retrieve_authentic_source_labels_catalogue(
    service: Annotated[
        AuthenticSourceLabelsCatalogueService,
        Depends(AuthenticSourceLabelsCatalogueService),
    ],
    format: CatalogueFormat,
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:read:published",
                "datasets:read:all-after-draft",
                "datasets:read:all-after-draft:organisation",
            ]
        )
    ),
) -> Response:
    try:
        media_type, content = service.get_catalogue(format)
        return Response(
            content=content,
            media_type=media_type,
            status_code=200,
        )
    except Exception:
        return ErrorResponse.create(
            status_code=500,
            detail="Failed to retrieve authentic source labels catalogue due to an internal error.",
            title="Authentic Source Labels Catalogue Retrieval Error",
        )
