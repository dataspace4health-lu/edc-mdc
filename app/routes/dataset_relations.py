from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from services.dataset_relation import DatasetRelationService
from schemas.dataset_relations import AddRelation, ResourceRelation
from typing import List, Annotated
from models.identity_context import IdentityContext
from routes.auth import validate_and_retrieve_identity_context

router = APIRouter()


@router.get(
    "/api/v1/datasets/{dataset_id}/relations",
    response_model=List[ResourceRelation],
)
def get_relations_by_dataset_id(
    dataset_id: int,
    service: Annotated[DatasetRelationService, Depends(DatasetRelationService)],
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
) -> List[ResourceRelation]:
    return service.get_relations_by_dataset_id(dataset_id, identity)


@router.post(
    "/api/v1/datasets/{dataset_id}/relations",
    response_model=ResourceRelation,
    status_code=status.HTTP_201_CREATED,
)
def add_relation(
    dataset_id: int,
    add_relation: AddRelation,
    service: Annotated[DatasetRelationService, Depends(DatasetRelationService)],
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
) -> ResourceRelation:
    return service.add_relation(dataset_id, add_relation, identity)


@router.delete(
    "/api/v1/datasets/{dataset_id}/relations/{relation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_relation(
    dataset_id: int,
    relation_id: int,
    service: Annotated[DatasetRelationService, Depends(DatasetRelationService)],
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
    service.delete_relation(dataset_id, relation_id, identity)
    return Response(content=None, status_code=status.HTTP_204_NO_CONTENT)
