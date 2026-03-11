from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import Optional, Annotated
from models.dataset_comment import DatasetComment


@dataclass(frozen=True)
class DatasetCommentDto(BaseModel):
    content: Annotated[
        str,
        Field(
            min_length=1,
            max_length=2000,
            description="Comment content (1-2000 characters)",
        ),
    ]
    user_id: Annotated[int, Field(gt=0, description="Must be a positive integer")]
    dataset_id: Annotated[int, Field(gt=0, description="Must be a positive integer")]
    action_type: Annotated[
        str,
        Field(min_length=1, max_length=50, description="Action type (1-50 characters)"),
    ]

    class Config:
        extra = "forbid"
        str_strip_whitespace = True


@dataclass(frozen=True)
class ResourceDatasetComment(BaseModel):
    id: int
    content: str
    author: str
    dataset_id: int
    timestamp: str


def dataset_comment_entity_to_resource(
    comment: DatasetComment,
) -> ResourceDatasetComment:
    return ResourceDatasetComment(
        id=comment.id,
        content=comment.content,
        author=comment.user.name,
        dataset_id=comment.dataset_id,
        timestamp=comment.timestamp.isoformat(),
    )
