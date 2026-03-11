from pydantic import BaseModel, Field, field_serializer
from models.authentic_source_label import AuthenticSourceLabel
from models.dataset import Dataset
from models.authentic_source_assignment import AuthenticSourceAssignment
from typing import Optional, Annotated


class AuthenticSourceLabelDto(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=1, max_length=200, description="Label name (1-100 characters)"
        ),
    ]
    description: Optional[
        Annotated[
            str,
            Field(max_length=500, description="Label description (max 500 characters)"),
        ]
    ] = None
    is_deprecated: bool = Field(default=False)

    class Config:
        from_attributes = True
        extra = "forbid"
        str_strip_whitespace = True


class ResourceAuthenticSourceLabel(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: str
    created_by: Optional[int] = None
    created_by_name: Optional[str] = None
    data_dictionary_entry_id: Optional[int] = None
    dataset_id: Optional[int] = None
    dataset_title: Optional[str] = None
    dataset_is_deprecated: Optional[bool] = None
    is_deprecated: Optional[bool] = Field(default=False)

    class Config:
        from_attributes = True


class LabelAssignmentHistory(BaseModel):
    dataset_id: Optional[int] = None
    dataset_title: Optional[str] = None
    dataset_description: Optional[str] = None
    asignment_datetime: Optional[str] = None
    is_deprecated: bool = False
    dataset_is_deprecated: Optional[bool] = None

    class Config:
        from_attributes = True


def dataset_to_label_assignment_history(
    dataset: Dataset, assignment: AuthenticSourceAssignment
):
    return LabelAssignmentHistory(
        dataset_id=dataset.id,
        dataset_title=dataset.title,
        dataset_description=dataset.description,
        asignment_datetime=assignment.assigned_at.isoformat(),
        is_deprecated=assignment.label.is_deprecated if assignment.label else False,
        dataset_is_deprecated=(
            bool(getattr(dataset, "deprecated_at", None))
            or (getattr(dataset, "status", None) == "DEPRECATED")
        ),
    )


def authentic_source_label_entity_to_resource(
    label: AuthenticSourceLabel,
) -> ResourceAuthenticSourceLabel:
    active_assignment = next(
        (assignment for assignment in label.assignments if assignment.is_active),
        None,
    )
    data_dictionary_entry = (
        active_assignment.data_dictionary_entry
        if active_assignment and active_assignment.data_dictionary_entry
        else None
    )

    dataset = data_dictionary_entry.dataset if data_dictionary_entry else None

    dataset_is_deprecated: Optional[bool] = None
    if dataset is not None:
        dataset_is_deprecated = bool(getattr(dataset, "deprecated_at", None)) or (
            getattr(dataset, "status", None) == "DEPRECATED"
        )

    return ResourceAuthenticSourceLabel(
        id=label.id,
        name=label.name,
        description=label.description,
        created_at=label.created_at.isoformat(),
        created_by=label.created_by,
        created_by_name=label.creator.name if label.creator else None,
        data_dictionary_entry_id=(
            data_dictionary_entry.id if data_dictionary_entry else None
        ),
        dataset_id=(
            data_dictionary_entry.dataset.id if data_dictionary_entry else None
        ),
        dataset_title=(
            data_dictionary_entry.dataset.title if data_dictionary_entry else None
        ),
        dataset_is_deprecated=dataset_is_deprecated,
        is_deprecated=label.is_deprecated,
    )
