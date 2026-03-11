from fastapi import APIRouter, Depends, status
from services.distribution import DistributionService
from schemas.distribution import ResourceDistribution, DistributionDto
from typing import List, Annotated
from fastapi.responses import Response
from routes.auth import validate_and_retrieve_identity_context
from models.identity_context import IdentityContext

router = APIRouter()


@router.get(
    "/api/v1/datasets/{dataset_id}/distributions",
    response_model=List[ResourceDistribution],
    tags=["distributions"],
)
def get_distributions_by_dataset_id(
    dataset_id: int,
    service: Annotated[DistributionService, Depends(DistributionService)],
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
) -> List[ResourceDistribution]:
    return service.get_distributions_by_dataset_id(dataset_id, identity)


@router.post(
    "/api/v1/datasets/{dataset_id}/distributions",
    response_model=ResourceDistribution,
    tags=["distributions"],
    status_code=status.HTTP_201_CREATED,
)
def add_distribution(
    dataset_id: int,
    distribution_dto: DistributionDto,
    service: Annotated[DistributionService, Depends(DistributionService)],
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
) -> ResourceDistribution:
    return service.add_distribution(dataset_id, distribution_dto, identity)


@router.put(
    "/api/v1/datasets/{dataset_id}/distributions/{distribution_id}",
    response_model=ResourceDistribution,
    tags=["distributions"],
    status_code=status.HTTP_200_OK,
)
def update_distribution(
    dataset_id: int,
    distribution_id: int,
    distribution_dto: DistributionDto,
    service: Annotated[DistributionService, Depends(DistributionService)],
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
) -> ResourceDistribution:
    return service.update_distribution(
        dataset_id, distribution_id, distribution_dto, identity
    )


@router.delete(
    "/api/v1/datasets/{dataset_id}/distributions/{distribution_id}",
    tags=["distributions"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_distribution(
    dataset_id: int,
    distribution_id: int,
    service: Annotated[DistributionService, Depends(DistributionService)],
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
    service.delete_distribution_by_id(dataset_id, distribution_id, identity)
    return Response(content=None, status_code=status.HTTP_204_NO_CONTENT)
