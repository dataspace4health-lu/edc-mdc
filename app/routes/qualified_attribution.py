from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from services.qualified_attribution import QualifiedAttributionService
from schemas.qualified_attribution import (
    QualifiedAttributionDto,
    ResourceQualifiedAttribution,
)
from routes.auth import validate_and_retrieve_identity_context
from models.identity_context import IdentityContext

router = APIRouter()


@router.get(
    "/api/v1/datasets/{dataset_id}/qualified-attributions",
    response_model=list[ResourceQualifiedAttribution],
    tags=["qualified-attributions"],
)
def get_qualified_attributions_by_dataset_id(
    dataset_id: int,
    service: Annotated[
        QualifiedAttributionService, Depends(QualifiedAttributionService)
    ],
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
) -> list[ResourceQualifiedAttribution]:
    return service.get_qualified_attributions_by_dataset_id(dataset_id, identity)


@router.post(
    "/api/v1/datasets/{dataset_id}/qualified-attributions",
    response_model=ResourceQualifiedAttribution,
    tags=["qualified-attributions"],
    status_code=status.HTTP_201_CREATED,
)
def add_qualified_attribution(
    dataset_id: int,
    data: QualifiedAttributionDto,
    service: Annotated[
        QualifiedAttributionService, Depends(QualifiedAttributionService)
    ],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:edit:draft:my",
                "datasets:edit:draft:organisation",
                "datasets:edit:draft:group",
                "datasets:edit:draft",
            ]
        )
    ),
) -> ResourceQualifiedAttribution:
    return service.add_qualified_attribution(dataset_id, data, identity)


@router.put(
    "/api/v1/datasets/{dataset_id}/qualified-attributions/{attribution_id}",
    response_model=ResourceQualifiedAttribution,
    tags=["qualified-attributions"],
)
def update_qualified_attribution(
    dataset_id: int,
    attribution_id: int,
    data: QualifiedAttributionDto,
    service: Annotated[
        QualifiedAttributionService, Depends(QualifiedAttributionService)
    ],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:edit:draft:my",
                "datasets:edit:draft:organisation",
                "datasets:edit:draft:group",
                "datasets:edit:draft",
            ]
        )
    ),
) -> ResourceQualifiedAttribution:
    return service.update_qualified_attribution(
        dataset_id, attribution_id, data, identity
    )


@router.delete(
    "/api/v1/datasets/{dataset_id}/qualified-attributions/{attribution_id}",
    tags=["qualified-attributions"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_qualified_attribution(
    dataset_id: int,
    attribution_id: int,
    service: Annotated[
        QualifiedAttributionService, Depends(QualifiedAttributionService)
    ],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:edit:draft:my",
                "datasets:edit:draft:organisation",
                "datasets:edit:draft:group",
                "datasets:edit:draft",
            ]
        )
    ),
) -> Response:
    service.delete_qualified_attribution(dataset_id, attribution_id, identity)
    return Response(content=None, status_code=status.HTTP_204_NO_CONTENT)
