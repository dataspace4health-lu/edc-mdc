from typing import Set, List
from pydantic import BaseModel


class UserAssignmentDto(BaseModel):
    email: str
    role_id: int

    class Config:
        orm_mode = True


class ResourceRole(BaseModel):
    id: int
    name: str


class ResourceUserAssignment(BaseModel):
    roles: List[ResourceRole]
    user_id: int
    name: str


class ResourceOrganisationAssignment(BaseModel):
    organisation_id: int
    organisation_name: str
    roles: List[ResourceRole]
    is_deprecated: bool = False
