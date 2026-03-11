from fastapi import Depends, HTTPException
from schemas.contact import ResourceContact, ContactDto, contact_entity_to_resource
from models.contact import Contact
from models.identity_context import IdentityContext
from repositories.contact import ContactRepository
from repositories.organisation import OrganisationRepository
from typing import List
from services.activity_logs.organisation_activity_log import (
    OrganisationActivityLogService,
)
from services.organisation_cache import OrganisationCache, get_organisation_cache
from services.permissions.contact_permissions import ContactPermissionsService


class ContactService:
    def __init__(
        self,
        contact_repository: ContactRepository = Depends(ContactRepository),
        activity_log_service: OrganisationActivityLogService = Depends(
            OrganisationActivityLogService
        ),
        organisation_repository: OrganisationRepository = Depends(
            OrganisationRepository
        ),
        organisation_cache: OrganisationCache = Depends(get_organisation_cache),
        contact_permissions_service: ContactPermissionsService = Depends(
            ContactPermissionsService
        ),
    ):
        self._contact_repository = contact_repository
        self._organisation_repository = organisation_repository
        self._activity_log_service = activity_log_service
        self._contact_permissions_service = contact_permissions_service
        self._cache = organisation_cache

    def add_contact(
        self,
        organisation_id: int,
        contact_dto: ContactDto,
        identity: IdentityContext,
        skip_permission_validation: bool = False,
    ) -> ResourceContact:
        if not skip_permission_validation:
            self._contact_permissions_service.validate_contact_permissions(
                organisation_id, identity
            )

        organisation = self._organisation_repository.get_organisation(organisation_id)
        if not organisation:
            raise HTTPException(
                status_code=404, detail=f"Organisation[{organisation_id}] not found."
            )

        if organisation.is_deprecated == True:
            raise HTTPException(
                status_code=403,
                detail=f"Organisation[{organisation_id}] is deprecated and cannot accept new contacts.",
            )

        if self._contact_repository.exists_by_name_or_email(
            organisation_id, contact_dto.name, contact_dto.email
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Contact with name {contact_dto.name} or email {contact_dto.email} already exists.",
            )
        contact = Contact(
            name=contact_dto.name,
            email=contact_dto.email,
            role=contact_dto.role,
            organisation_id=organisation_id,
            is_deprecated=False,
        )
        self._contact_repository.add(contact)
        self._contact_repository.commit()

        self._activity_log_service.log_contact_added_to_organisation(
            identity.user_id,
            organisation_id,
            contact,
        )
        self._cache.invalidate()

        return contact_entity_to_resource(contact)

    def update_contact(
        self,
        organisation_id: int,
        contact_id: int,
        contact_dto: ContactDto,
        identity: IdentityContext,
        skip_permission_validation: bool = False,
    ) -> ResourceContact:
        if not skip_permission_validation:
            self._contact_permissions_service.validate_contact_permissions(
                organisation_id, identity
            )

        contact = self._contact_repository.get_contact_by_id(
            organisation_id, contact_id
        )

        contact_before = contact.to_dict()

        if not contact:
            raise HTTPException(
                status_code=404, detail=f"Contact with id {contact_id} not found."
            )

        for key, value in contact_dto.dict().items():
            setattr(contact, key, value)

        self._contact_repository.update(contact)
        self._contact_repository.commit()

        self._activity_log_service.log_contact_updated_in_organisation(
            identity.user_id, organisation_id, contact_before, contact
        )

        return contact_entity_to_resource(contact)

    def delete_contact(
        self,
        organisation_id: int,
        contact_id: int,
        identity: IdentityContext,
        skip_permission_validation: bool = False,
    ) -> None:
        if not skip_permission_validation:
            self._contact_permissions_service.validate_contact_permissions(
                organisation_id, identity
            )

        contact = self._contact_repository.get_contact_by_id(
            organisation_id, contact_id
        )

        if not contact:
            raise HTTPException(
                status_code=404, detail=f"Contact with id {contact_id} not found."
            )

        # Check if contact is assigned to any datasets
        if self._contact_repository.is_contact_assigned_to_dataset(contact_id):
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete contact {contact.name}. Contact is currently assigned to one or more datasets.",
            )

        contact_before = contact.to_dict()

        self._contact_repository.delete(contact)
        self._contact_repository.commit()

        self._activity_log_service.log_contact_deleted_from_organisation(
            identity.user_id,
            organisation_id,
            contact_before,
        )

        self._cache.invalidate()

    def update_deprecation_status(
        self, organisation_id: int, contact_id: int, identity: IdentityContext
    ) -> ResourceContact:
        self._contact_permissions_service.validate_contact_permissions(
            organisation_id, identity
        )

        contact = self._contact_repository.get_contact_by_id(
            organisation_id,
            contact_id,
        )

        if not contact:
            raise HTTPException(
                status_code=404, detail=f"Contact with id {contact_id} not found."
            )

        if not contact.is_deprecated:
            self._contact_repository.set_deprecation_status(
                organisation_id, contact_id, True
            )
        else:
            self._contact_repository.set_deprecation_status(
                organisation_id, contact_id, False
            )

        self._cache.invalidate()
        updated_contact = self._contact_repository.get_contact_by_id(
            organisation_id, contact_id
        )
        self._activity_log_service.log_contact_deprecated_in_organisation(
            identity.user_id,
            organisation_id,
            updated_contact.to_dict(),
        )
        return contact_entity_to_resource(updated_contact)
