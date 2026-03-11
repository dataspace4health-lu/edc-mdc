from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, Annotated, Literal
from models.dataset_relation import DatasetRelation
from validators.dataset_relation_validator import validate_relation_type


class AddRelation(BaseModel):
    relation_kind: Literal["dataset", "external"]
    target_dataset: Optional[
        Annotated[int, Field(gt=0, description="Must be a positive integer")]
    ] = None
    relation_type: Optional[
        Annotated[
            str,
            Field(
                min_length=1,
                max_length=100,
                description="Relation type (1-100 characters)",
            ),
        ]
    ] = None

    external_url: Optional[
        Annotated[
            str,
            Field(
                min_length=1,
                max_length=2048,
                description="External resource URL (1-2048 characters)",
            ),
        ]
    ] = None
    external_role: Optional[
        Annotated[str, Field(max_length=100, description="Role or relationship type")]
    ] = None
    external_description: Optional[str] = None

    @model_validator(mode="after")
    def validate_relation_fields(self):
        if self.relation_kind == "dataset":
            if self.target_dataset is None or self.relation_type is None:
                raise ValueError(
                    "Target dataset and RelationType are required for dataset relations"
                )
            validate_relation_type(self.relation_type)
        elif self.relation_kind == "external":
            if self.external_url is None:
                raise ValueError("External URL is required for external relations")
        return self


class ResourceRelation(BaseModel):
    id: Optional[int] = None
    source_dataset: int
    relation_kind: Literal["dataset", "external"]

    target_dataset: Optional[int] = None
    relation_type: Optional[str] = None

    external_url: Optional[str] = None
    external_role: Optional[str] = None
    external_description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


def dataset_relation_entity_to_resource(
    dataset_relation: DatasetRelation,
) -> ResourceRelation:
    if dataset_relation.is_dataset_relation:
        return ResourceRelation(
            id=dataset_relation.id,
            source_dataset=dataset_relation.source_dataset,
            relation_kind="dataset",
            target_dataset=dataset_relation.target_dataset,
            relation_type=dataset_relation.relation_type,
        )
    else:
        return ResourceRelation(
            id=dataset_relation.id,
            source_dataset=dataset_relation.source_dataset,
            relation_kind="external",
            external_url=dataset_relation.external_url,
            external_role=dataset_relation.external_role,
            external_description=dataset_relation.external_description,
        )
