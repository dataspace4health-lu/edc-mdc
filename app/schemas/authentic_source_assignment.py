from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Annotated


class LabelAssignmentDto(BaseModel):
    label_id: Annotated[int, Field(gt=0, description="Must be a positive integer")]
    assigned_entry_id: Optional[Annotated[int, Field(gt=0)]] = None

    class Config:
        from_attributes = True
        extra = "forbid"  # Prevent additional fields


class BulkLabelAssignmentDto(BaseModel):
    label_assignments: Annotated[
        List[LabelAssignmentDto],
        Field(min_length=1, max_length=100, description="1-100 assignments allowed"),
    ]

    class Config:
        from_attributes = True
        extra = "forbid"
