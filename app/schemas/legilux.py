from pydantic import BaseModel
from typing import Optional


class LegiluxLegislation(BaseModel):
    id: str
    label: str
    description: str
    link: str

    class Config:
        from_attributes = True
