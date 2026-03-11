from fastapi import Depends, status, APIRouter
from fastapi.responses import Response
from typing import List, Annotated
from services.contact import ContactService
from schemas.contact import ResourceContact, ContactDto
from models.identity_context import IdentityContext
from routes.auth import validate_and_retrieve_identity_context

router = APIRouter()


@router.post(
    "/api/v1/organisations/{organisation_id}/contacts",
    response_model=ResourceContact,
    tags=["contacts"],
    status_code=status.HTTP_201_CREATED,
)
def add_contact(
    organisation_id: int,
    contact_dto: ContactDto,
    service: Annotated[ContactService, Depends(ContactService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "contacts:edit",
                "contacts:edit:organisation",
                "organisations:edit",
                "organisations:edit:organisation",
            ]
        )
    ),
) -> ResourceContact:
    return service.add_contact(organisation_id, contact_dto, identity)


@router.put(
    "/api/v1/organisations/{organisation_id}/contacts/{contact_id}",
    response_model=ResourceContact,
    tags=["contacts"],
)
def update_contact(
    organisation_id: int,
    contact_id: int,
    contact_dto: ContactDto,
    service: Annotated[ContactService, Depends(ContactService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "contacts:edit",
                "contacts:edit:organisation",
                "organisations:edit",
                "organisations:edit:organisation",
            ]
        )
    ),
) -> ResourceContact:
    return service.update_contact(organisation_id, contact_id, contact_dto, identity)


@router.delete(
    "/api/v1/organisations/{organisation_id}/contacts/{contact_id}",
    tags=["contacts"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_contact(
    organisation_id: int,
    contact_id: int,
    service: Annotated[ContactService, Depends(ContactService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "contacts:edit",
                "contacts:edit:organisation",
                "organisations:edit",
                "organisations:edit:organisation",
            ]
        )
    ),
) -> None:
    service.delete_contact(organisation_id, contact_id, identity)
    return Response(content=None, status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/api/v1/organisations/{organisation_id}/contacts/{contact_id}/toggle-deprecation",
    tags=["contacts"],
    response_model=ResourceContact,
    status_code=status.HTTP_200_OK,
)
def change_deprecation_status(
    organisation_id: int,
    contact_id: int,
    service: Annotated[ContactService, Depends(ContactService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "contacts:edit",
                "contacts:edit:organisation",
                "organisations:edit",
                "organisations:edit:organisation",
            ]
        )
    ),
) -> ResourceContact:
    return service.update_deprecation_status(organisation_id, contact_id, identity)
