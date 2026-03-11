from pydantic import BaseModel, Field, EmailStr
from models.contact import Contact
from typing import Optional, Annotated


class ContactDto(BaseModel):
    name: Annotated[
        str,
        Field(min_length=1, max_length=255, description="Full name (1-255 characters)"),
    ]
    email: EmailStr  # Built-in email validation
    role: Optional[
        Annotated[
            str, Field(max_length=50, description="Role/title (max 50 characters)")
        ]
    ] = None

    class Config:
        from_attributes = True
        extra = "forbid"
        str_strip_whitespace = True


class ResourceContact(BaseModel):
    id: int
    name: str
    email: str
    role: Optional[str] = Field(default=None)
    is_deprecated: bool = Field(
        default=False, description="Indicates if the contact is active or deprecated"
    )

    class Config:
        from_attributes = True

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "is_deprecated": self.is_deprecated,
        }


def contact_entity_to_resource(
    contact: Contact,
) -> ResourceContact:
    return ResourceContact(
        id=contact.id,
        name=contact.name,
        email=contact.email,
        role=contact.role,
        is_deprecated=contact.is_deprecated,
    )
