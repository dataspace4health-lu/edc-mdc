from typing import Annotated
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import Response
from models.identity_context import IdentityContext
from repositories.dataset import DatasetRepository
from schemas.released_datasets import PaginatedReleasedDatasetsResponse
from schemas.catalogue import CatalogueFormat
from services.released_datasets import ReleasedDatasetsService
from services.catalogue import CatalogueService
from utils.error_responses import ErrorResponse
from auth.dependencies import validate_and_retrieve_identity_context

router = APIRouter()


@router.get(
    "/api/v1/released-datasets",
    response_model=PaginatedReleasedDatasetsResponse,
    tags=["released-datasets"],
)
def get_released_datasets(
    page: int = Query(default=1, ge=1, description="Page number (starting from 1)"),
    page_size: int = Query(default=50, ge=1, le=500, description="Items per page"),
    service: Annotated[
        ReleasedDatasetsService, Depends(ReleasedDatasetsService)
    ] = None,
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(["system:admin"])
    ),
) -> PaginatedReleasedDatasetsResponse:
    return service.get_released_datasets(page=page, page_size=page_size)


@router.get(
    "/api/v1/released-datasets/{dataset_id}/download",
    tags=["released-datasets"],
)
def download_released_dataset_rdf(
    dataset_id: int,
    format: CatalogueFormat = Query(default=CatalogueFormat.TTL),
    catalogue_service: Annotated[CatalogueService, Depends(CatalogueService)] = None,
    dataset_repository: Annotated[DatasetRepository, Depends(DatasetRepository)] = None,
) -> Response:
    # Verify dataset exists and is released
    dataset = dataset_repository.get_dataset(dataset_id)
    if not dataset or dataset.released_at is None:
        raise HTTPException(status_code=404, detail="Dataset not found or not released")

    # Create public identity context for accessing released data
    # user_id=0 represents anonymous/public access
    # datasets:read:all-after-complete covers VALIDATED, APPROVED, PUBLISHED, INTERNAL_ONLY, DEPRECATED
    public_identity = IdentityContext(
        user_id=0,
        permissions=["datasets:read:all-after-complete"],
        current_organisation_id=None,
    )

    media_type, content = catalogue_service.get_individual_dataset_catalogue(
        format, dataset_id, public_identity
    )
    return Response(
        content=content,
        media_type=media_type,
        status_code=200,
    )
