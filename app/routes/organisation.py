from fastapi import Depends, status, APIRouter
from schemas.organisation import (
    OrganisationDto,
    ResourceOrganisation,
)
from services.organisation import OrganisationService
from typing import List, Annotated
from models.identity_context import IdentityContext
from routes.auth import validate_and_retrieve_identity_context

router = APIRouter()


@router.get(
    "/api/v1/organisations",
    response_model=List[ResourceOrganisation],
    tags=["organisations"],
)
def get_organisations(
    service: Annotated[OrganisationService, Depends(OrganisationService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "contacts:edit",
                "contacts:edit:organisation",
                "form-fields:edit:organisation",
                "form-fields:edit:my",
                "form-fields:edit",
            ]
        )
    ),
) -> List[ResourceOrganisation]:
    return service.get_organisations()


@router.get(
    "/api/v1/organisations/{organisation_id}",
    response_model=ResourceOrganisation,
    tags=["organisations"],
)
def get_organisation_by_id(
    organisation_id: int,
    service: Annotated[OrganisationService, Depends(OrganisationService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "organisations:edit",
                "organisations:edit:organisation",
                "contacts:edit",
                "contacts:edit:organisation",
            ]
        )
    ),
) -> ResourceOrganisation:
    return service.get_organisation(organisation_id, identity)


@router.post(
    "/api/v1/organisations",
    response_model=ResourceOrganisation,
    tags=["organisations"],
    status_code=status.HTTP_201_CREATED,
)
def create_organisation(
    organisation_dto: OrganisationDto,
    service: Annotated[OrganisationService, Depends(OrganisationService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(["organisations:edit"])
    ),
) -> ResourceOrganisation:
    return service.create_organisation(organisation_dto, identity)


@router.put(
    "/api/v1/organisations/{organisation_id}",
    response_model=ResourceOrganisation,
    tags=["organisations"],
)
def update_organisation(
    organisation_id: int,
    organisation_dto: OrganisationDto,
    service: Annotated[OrganisationService, Depends(OrganisationService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            ["organisations:edit", "organisations:edit:organisation"]
        )
    ),
) -> ResourceOrganisation:
    return service.update_organisation(organisation_id, organisation_dto, identity)


@router.patch(
    "/api/v1/organisations/{organisation_id}/toggle-deprecation",
    response_model=ResourceOrganisation,
    tags=["organisations"],
    status_code=status.HTTP_200_OK,
)
def toggle_organisation_deprecation(
    organisation_id: int,
    service: Annotated[OrganisationService, Depends(OrganisationService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            ["organisations:edit", "organisations:edit:organisation"]
        )
    ),
) -> ResourceOrganisation:
    return service.toggle_organisation_deprecation(organisation_id, identity)
