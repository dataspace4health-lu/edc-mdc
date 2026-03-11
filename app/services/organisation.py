from fastapi import Depends, HTTPException
from schemas.organisation import (
    OrganisationDto,
    ResourceOrganisation,
    organisation_entity_to_resource,
)
from models.organisation import Organisation, Contact
from repositories.organisation import OrganisationRepository
from models.identity_context import IdentityContext
from typing import List
from services.organisation_cache import OrganisationCache, get_organisation_cache
from services.activity_log import ActivityLogService
from services.permissions.organisation_permissions import OrganisationPermissionsService
from services.contact import ContactService
from models.organisation import Contact


class OrganisationService:
    def __init__(
        self,
        organisation_repository: OrganisationRepository = Depends(
            OrganisationRepository
        ),
        organisation_cache: OrganisationCache = Depends(get_organisation_cache),
        activity_log_service: ActivityLogService = Depends(ActivityLogService),
        organisation_permissions_service: OrganisationPermissionsService = Depends(
            OrganisationPermissionsService
        ),
        contact_service: ContactService = Depends(ContactService),
    ):
        self._organisation_repository = organisation_repository
        self._cache = organisation_cache
        self._activity_log_service = activity_log_service
        self._organisation_permissions_service = organisation_permissions_service
        self._contact_service = contact_service

    def get_organisations(self) -> List[ResourceOrganisation]:
        return self._cache.get_all()

    def get_organisation(
        self, organisation_id: int, identity: IdentityContext
    ) -> ResourceOrganisation:
        self._organisation_permissions_service.validate_get_organisation_permissions(
            organisation_id, identity
        )
        organisation = self._organisation_repository.get_organisation(organisation_id)
        return organisation_entity_to_resource(organisation)

    def create_organisation(
        self, organisation_dto: OrganisationDto, identity: IdentityContext
    ) -> ResourceOrganisation:
        if self._organisation_repository.exists_by_name(organisation_dto.name):
            raise HTTPException(
                status_code=400,
                detail=f"Organisation with name '{organisation_dto.name}' already exists.",
            )
        contacts = [
            Contact(
                name=contact.name,
                email=contact.email,
                role=contact.role,
                is_deprecated=False,
            )
            for contact in organisation_dto.contacts
        ]
        organisation = Organisation(
            name=organisation_dto.name,
            type=organisation_dto.type,
            email=organisation_dto.email,
            is_deprecated=False,
            category=organisation_dto.category,
            accessible_within_ctie=organisation_dto.accessible_within_ctie,
            contacts=contacts,
        )
        self._organisation_repository.add(organisation)
        self._organisation_repository.commit()
        self._organisation_repository.refresh(organisation)
        self._cache.invalidate()
        self._activity_log_service.log_organisation_activities(
            identity.user_id,
            organisation.id,
            {},
            organisation_dto,
            "create",
        )

        return organisation_entity_to_resource(organisation)

    def update_organisation(
        self,
        organisation_id: int,
        organisation_dto: OrganisationDto,
        identity: IdentityContext,
    ) -> ResourceOrganisation:
        self._organisation_permissions_service.validate_update_organisation_permissions(
            organisation_id, identity
        )
        organisation = self._organisation_repository.get_organisation(organisation_id)
        if not organisation:
            raise HTTPException(
                status_code=404, detail=f"Organisation[{organisation_id}] not found."
            )

        if organisation.is_deprecated:
            raise HTTPException(
                status_code=400,
                detail=f"Organisation[{organisation_id}] is deprecated and cannot be modified.",
            )

        org_diff = organisation.to_dict_for_diff()

        organisation.name = organisation_dto.name
        organisation.type = organisation_dto.type
        organisation.email = organisation_dto.email
        organisation.category = organisation_dto.category
        organisation.accessible_within_ctie = organisation_dto.accessible_within_ctie

        self._organisation_repository.commit()
        self._organisation_repository.refresh(organisation)
        self._cache.invalidate()

        self._activity_log_service.log_organisation_activities(
            identity.user_id,
            organisation.id,
            org_diff,
            organisation_dto,
            "update",
        )

        return organisation_entity_to_resource(organisation)

    def toggle_organisation_deprecation(
        self,
        organisation_id: int,
        identity: IdentityContext,
    ) -> ResourceOrganisation:
        self._organisation_permissions_service.validate_update_organisation_permissions(
            organisation_id, identity
        )

        organisation = self._organisation_repository.get_organisation(organisation_id)
        if not organisation:
            raise HTTPException(
                status_code=404, detail=f"Organisation[{organisation_id}] not found."
            )

        old_status = organisation.is_deprecated
        new_status = not old_status

        self._organisation_repository.set_deprecation_status(
            organisation_id, new_status
        )
        self._organisation_repository.commit()
        self._organisation_repository.refresh(organisation)
        self._cache.invalidate()

        action = "restore" if old_status else "deprecate"
        self._activity_log_service.log_organisation_activities(
            identity.user_id,
            organisation.id,
            {"is_deprecated": old_status},
            {"is_deprecated": new_status},
            action,
        )

        return organisation_entity_to_resource(organisation)
