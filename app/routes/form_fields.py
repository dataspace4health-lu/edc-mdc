from fastapi import Depends, status, APIRouter, HTTPException
from schemas.form_field import (
    CreateFormFieldDto,
    FormFieldDto,
    CreateApplicableLegislationFormFieldDto,
    ApplicableLegislationFormFieldDto,
    ResourceFormField,
    ApplicableLegislationFormField,
    PaginatedFormFieldResponse,
    FormFieldListRequest,
)
from services.form_fields_service import FormFieldsService
from typing import List, Annotated, Union
from models.identity_context import IdentityContext
from routes.auth import validate_and_retrieve_identity_context

router = APIRouter()


@router.post(
    "/api/v1/form-fields/{field_type}/all",
    response_model=PaginatedFormFieldResponse,
    tags=["form-fields"],
)
def get_all_form_fields(
    field_type: str,
    request: FormFieldListRequest,
    service: Annotated[FormFieldsService, Depends(FormFieldsService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "form-fields:edit",
                "form-fields:edit:my",
                "form-fields:edit:organisation",
            ]
        )
    ),
) -> PaginatedFormFieldResponse:
    return service.get_all_paginated(
        field_type,
        request.page,
        request.page_size,
        request.query,
        request.organisation_filters,
        identity,
    )


@router.post(
    "/api/v1/form-fields/applicable_legislation",
    response_model=ApplicableLegislationFormField,
    tags=["form-fields"],
    status_code=status.HTTP_201_CREATED,
)
def create_applicable_legislation_form_field(
    dto: CreateApplicableLegislationFormFieldDto,
    service: Annotated[FormFieldsService, Depends(FormFieldsService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            ["form-fields:edit", "form-fields:edit:my", "form-fields:edit:organisation"]
        )
    ),
) -> ApplicableLegislationFormField:
    return service.create("applicable_legislation", dto, identity)


@router.post(
    "/api/v1/form-fields/{field_type}",
    response_model=ResourceFormField,
    tags=["form-fields"],
    status_code=status.HTTP_201_CREATED,
)
def create_form_field(
    field_type: str,
    dto: CreateFormFieldDto,
    service: Annotated[FormFieldsService, Depends(FormFieldsService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            ["form-fields:edit", "form-fields:edit:my", "form-fields:edit:organisation"]
        )
    ),
) -> ResourceFormField:
    return service.create(field_type, dto, identity)


@router.put(
    "/api/v1/form-fields/applicable_legislation",
    response_model=ApplicableLegislationFormField,
    tags=["form-fields"],
)
def update_applicable_legislation_form_field(
    dto: ApplicableLegislationFormFieldDto,
    service: Annotated[FormFieldsService, Depends(FormFieldsService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            ["form-fields:edit", "form-fields:edit:my", "form-fields:edit:organisation"]
        )
    ),
) -> ApplicableLegislationFormField:
    return service.update("applicable_legislation", dto, identity)


@router.put(
    "/api/v1/form-fields/{field_type}",
    response_model=ResourceFormField,
    tags=["form-fields"],
)
def update_form_field(
    field_type: str,
    dto: FormFieldDto,
    service: Annotated[FormFieldsService, Depends(FormFieldsService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            ["form-fields:edit", "form-fields:edit:my", "form-fields:edit:organisation"]
        )
    ),
) -> ResourceFormField:
    return service.update(field_type, dto, identity)


@router.put(
    "/api/v1/form-fields/{field_type}/delete",
    tags=["form-fields"],
    status_code=status.HTTP_200_OK,
)
def delete_form_field(
    field_type: str,
    dto: FormFieldDto,
    service: Annotated[FormFieldsService, Depends(FormFieldsService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            ["form-fields:edit", "form-fields:edit:my", "form-fields:edit:organisation"]
        )
    ),
) -> None:
    service.delete(field_type, dto.key, identity)


@router.put(
    "/api/v1/form-fields/{field_type}/{key}/promote-global",
    response_model=Union[ResourceFormField, ApplicableLegislationFormField],
    tags=["form-fields"],
)
def promote_form_field_to_global(
    field_type: str,
    key: str,
    service: Annotated[FormFieldsService, Depends(FormFieldsService)],
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(["roles:manage"])
    ),
) -> Union[ResourceFormField, ApplicableLegislationFormField]:
    return service.promote_to_global(field_type, key, identity)
