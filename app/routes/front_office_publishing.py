from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from models.identity_context import IdentityContext
from routes.auth import validate_and_retrieve_identity_context
from services.front_office import (
    BaseFrontOfficeService,
    FrontOfficeDatasetPublishingService,
    FrontOfficeAuthenticSourcePublishingService,
)
from schemas.front_office_publishing import (
    FrontOfficePublishingResult,
    FrontOfficeFileInfo,
)

router = APIRouter()


@router.post(
    "/api/v1/datasets/{dataset_id}/publish-to-front-office",
    tags=["publishing"],
    status_code=status.HTTP_201_CREATED,
    response_model=FrontOfficePublishingResult,
)
def publish_dataset_to_front_office(
    dataset_id: int,
    publishing_service: Annotated[
        FrontOfficeDatasetPublishingService,
        Depends(FrontOfficeDatasetPublishingService),
    ],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:status-change:publish",
            ]
        )
    ),
) -> FrontOfficePublishingResult:
    return publishing_service.generate_and_publish_dataset_catalogues(
        dataset_id, identity
    )


@router.post(
    "/api/v1/authentic-source/publish-to-front-office",
    tags=["publishing"],
    status_code=status.HTTP_201_CREATED,
    response_model=FrontOfficePublishingResult,
)
def publish_authentic_source_to_front_office(
    publishing_service: Annotated[
        FrontOfficeAuthenticSourcePublishingService,
        Depends(FrontOfficeAuthenticSourcePublishingService),
    ],
) -> FrontOfficePublishingResult:
    return publishing_service.generate_and_publish_authentic_source()


@router.get(
    "/api/v1/front-office-files",
    tags=["publishing"],
    status_code=status.HTTP_200_OK,
    response_model=List[FrontOfficeFileInfo],
)
def list_front_office_files(
    service: Annotated[
        BaseFrontOfficeService,
        Depends(BaseFrontOfficeService),
    ],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(["datasets:status-change:publish"])
    ),
) -> List[FrontOfficeFileInfo]:
    return service.list_files()
