from fastapi import Depends, status, APIRouter, Response
from typing import List, Annotated
from services.dataset_comment import DatasetCommentService
from schemas.dataset_comment import ResourceDatasetComment
from models.identity_context import IdentityContext
from routes.auth import validate_and_retrieve_identity_context

router = APIRouter()


@router.get(
    "/api/v1/datasets/{dataset_id}/comments",
    response_model=List[ResourceDatasetComment],
    tags=["dataset-comments"],
)
def get_dataset_comments(
    dataset_id: int,
    service: DatasetCommentService = Depends(DatasetCommentService),
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
) -> List[ResourceDatasetComment]:
    return service.get_comments_by_dataset(dataset_id, identity)


@router.delete(
    "/api/v1/dataset-comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["dataset-comments"],
)
def delete_comment(
    comment_id: int,
    service: DatasetCommentService = Depends(DatasetCommentService),
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(["comments:delete"])
    ),
):
    service.delete_comment(comment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
