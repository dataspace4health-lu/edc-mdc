from pydantic import BaseModel, Field
from typing import List, Optional
from models.organisation import Organisation
from schemas.contact import ContactDto, ResourceContact


class OrganisationDto(BaseModel):
    name: str = Field(min_length=1)
    type: Optional[str] = None
    email: Optional[str] = None
    category: Optional[str] = None
    accessible_within_ctie: Optional[bool] = None
    contacts: List[ContactDto] = Field(default_factory=list)

    class Config:
        orm_mode = True


class ResourceOrganisation(BaseModel):
    id: int
    name: str
    type: Optional[str]
    email: Optional[str]
    is_deprecated: bool = Field(
        default=False,
        description="Indicates if the organisation is active or deprecated",
    )
    category: Optional[str]
    accessible_within_ctie: Optional[bool]
    contacts: List[ResourceContact]

    class Config:
        orm_mode = True


def organisation_entity_to_resource(organisation: Organisation) -> ResourceOrganisation:
    return ResourceOrganisation(
        id=organisation.id,
        name=organisation.name,
        type=organisation.type,
        email=organisation.email,
        is_deprecated=organisation.is_deprecated,
        category=organisation.category,
        accessible_within_ctie=organisation.accessible_within_ctie,
        contacts=[
            ResourceContact(
                id=contact.id,
                name=contact.name,
                email=contact.email,
                role=contact.role,
                is_deprecated=contact.is_deprecated,
            )
            for contact in organisation.contacts
        ],
    )
