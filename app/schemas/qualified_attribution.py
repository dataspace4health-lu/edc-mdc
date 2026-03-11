from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated
from models.qualified_attribution import DatasetQualifiedAttribution


class QualifiedAttributionDto(BaseModel):
    organisation_id: Annotated[
        int, Field(gt=0, description="Must be a positive integer")
    ]
    role: Annotated[
        str,
        Field(
            min_length=1,
            max_length=255,
            description="Role of the organisation (1-255 characters)",
        ),
    ]


class ResourceQualifiedAttribution(BaseModel):
    id: int
    dataset_id: int
    organisation_id: int
    role: str
    organisation_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


def qualified_attribution_entity_to_resource(
    attribution: DatasetQualifiedAttribution,
) -> ResourceQualifiedAttribution:
    return ResourceQualifiedAttribution(
        id=attribution.id,
        dataset_id=attribution.dataset_id,
        organisation_id=attribution.organisation_id,
        role=attribution.role,
        organisation_name=(
            attribution.organisation.name if attribution.organisation else None
        ),
    )
