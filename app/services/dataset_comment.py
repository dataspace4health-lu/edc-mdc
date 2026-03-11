from fastapi import Depends, HTTPException
from models.dataset import Dataset
from models.identity_context import IdentityContext
from sqlalchemy.orm import Session
from typing import List
from models.dataset_comment import DatasetComment
from repositories.dataset_comment import DatasetCommentRepository
from schemas.dataset_comment import (
    DatasetCommentDto,
    ResourceDatasetComment,
    dataset_comment_entity_to_resource,
)

from services.activity_logs.comment_activity_log import CommentActivityLogService
from services.dataset_permissions_service import DatasetPermissionsService


class DatasetCommentService:
    def __init__(
        self,
        comment_repository: DatasetCommentRepository = Depends(
            DatasetCommentRepository
        ),
        activity_log_service: CommentActivityLogService = Depends(
            CommentActivityLogService
        ),
        dataset_permissions_service: DatasetPermissionsService = Depends(
            DatasetPermissionsService
        ),
    ):
        self._comment_repository = comment_repository
        self._activity_log_service = activity_log_service
        self._dataset_permissions_service = dataset_permissions_service

    def get_comments_by_dataset(
        self, dataset_id: int, identity: IdentityContext
    ) -> List[ResourceDatasetComment]:
        self._dataset_permissions_service.validate_read_permissions(
            dataset_id, identity
        )

        comments = self._comment_repository.get_dataset_comments(dataset_id)
        return [dataset_comment_entity_to_resource(comment) for comment in comments]

    def add_dataset_comment(
        self, comment_dto: DatasetCommentDto
    ) -> ResourceDatasetComment:
        comment = DatasetComment(
            content=comment_dto.content,
            user_id=comment_dto.user_id,
            dataset_id=comment_dto.dataset_id,
        )
        self._comment_repository.add(comment)
        self._comment_repository.commit()

        self._activity_log_service.log_dataset_comment(
            user_id=comment_dto.user_id,
            dataset_id=comment_dto.dataset_id,
            comment=comment_dto.content,
            action_type="add_comment",
        )
        return dataset_comment_entity_to_resource(comment)

    def delete_comment(self, comment_id: int) -> None:
        comment = self._comment_repository._db_session.get(DatasetComment, comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        dataset = self._comment_repository._db_session.get(Dataset, comment.dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        if dataset.status in ("PUBLISHED", "DEPRECATED", "INTERNAL_ONLY"):
            raise HTTPException(
                status_code=403,
                detail="Cannot delete comments from published, internal only or deprecated datasets",
            )
        try:
            self._activity_log_service.log_dataset_comment(
                user_id=comment.user_id,
                dataset_id=comment.dataset_id,
                comment=comment.content,
                action_type="delete_comment",
            )

            self._comment_repository.delete_comment_by_id(comment_id)
            self._comment_repository.commit()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
