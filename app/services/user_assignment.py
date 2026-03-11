from fastapi import Depends, HTTPException, status
from repositories.organisation import OrganisationRepository
from repositories.user_assignment import UserAssignmentRepository
from repositories.user import UserRepository
from models.identity_context import IdentityContext
from schemas.organisation import ResourceOrganisation, organisation_entity_to_resource
from models.organisation import Organisation
from models.user_assignment import UserOrganisationAssignment, RoleAssignment
from schemas.user_assignment import UserAssignmentDto
from services.user_assignment_permissions import UserAssignmentPermissionsService
from services.email_service import EmailService
from typing import List, Annotated
from services.activity_logs.user_assignment_activity_log import (
    UserAssignmentActivityLogService,
)


class UserAssignmentService:
    def __init__(
        self,
        organisation_repository: OrganisationRepository = Depends(
            OrganisationRepository
        ),
        user_assignment_repository: UserAssignmentRepository = Depends(
            UserAssignmentRepository
        ),
        user_repository: UserRepository = Depends(UserRepository),
        permissions_service: UserAssignmentPermissionsService = Depends(
            UserAssignmentPermissionsService
        ),
        activity_log_service: UserAssignmentActivityLogService = Depends(
            UserAssignmentActivityLogService
        ),
        email_service: EmailService = Depends(EmailService),
    ):
        self._organisation_repository = organisation_repository
        self._user_assignment_repository = user_assignment_repository
        self._user_repository = user_repository
        self._permissions_service = permissions_service
        self._activity_log_service = activity_log_service
        self._email_service = email_service

    def create_user_organisation_assignment(
        self,
        organisation_id: int,
        assignment_dto: UserAssignmentDto,
        identity: IdentityContext,
    ) -> ResourceOrganisation:

        organisation = self._organisation_repository.get_organisation(organisation_id)
        if not organisation:
            raise HTTPException(
                status_code=404,
                detail=f"Organisation[{organisation_id}] does not exist.",
            )
        if organisation.is_deprecated == True:
            raise HTTPException(
                status_code=400,
                detail=f"Organisation[{organisation_id}] is deprecated and cannot accept new assignments.",
            )

        user = self._user_repository.get_user_by_email(assignment_dto.email)
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User[{assignment_dto.email}] does not exist."
            )
        if user.is_deprecated:
            raise HTTPException(
                status_code=404, detail=f"User[{assignment_dto.email}] is deprecated."
            )

        self._permissions_service.validate_role_assignment_permissions(
            organisation_id=organisation_id,
            target_user_id=user.id,
            identity=identity,
        )

        existing_assignment = (
            self._user_assignment_repository.get_user_organisation_assignment(
                organisation_id=organisation_id, user_id=user.id
            )
        )

        if existing_assignment:
            role_ids = {ra.role_id for ra in existing_assignment.roles}
            if assignment_dto.role_id in role_ids:
                raise HTTPException(
                    status_code=409,
                    detail=f"User[{assignment_dto.email}] already has Role[{assignment_dto.role_id}] in Organisation[{organisation_id}]",
                )
            new_role = RoleAssignment(role_id=assignment_dto.role_id)
            existing_assignment.roles.add(new_role)
            self._user_assignment_repository.commit()
            self._user_assignment_repository.refresh(existing_assignment)

            self._activity_log_service.log_user_assignment_role_added(
                user_id=identity.user_id,
                organisation_id=organisation_id,
                target_user_id=user.id,
                target_user_email=assignment_dto.email,
                role_id=assignment_dto.role_id,
            )
            self._email_service.notify_role_assigned(
                target_user_id=user.id,
                organisation_id=organisation_id,
                role_id=assignment_dto.role_id,
                assigner_user_id=identity.user_id,
            )

        else:
            organisation_assignment = UserOrganisationAssignment(
                user_id=user.id,
                organisation_id=organisation_id,
            )

            organisation_assignment.roles.add(
                RoleAssignment(role_id=assignment_dto.role_id)
            )

            self._user_assignment_repository.add_user_organisation_assignment(
                organisation_assignment
            )
            self._user_assignment_repository.commit()
            self._user_assignment_repository.refresh(organisation_assignment)

            self._activity_log_service.log_user_assignment_created(
                user_id=identity.user_id,
                organisation_id=organisation_id,
                target_user_id=user.id,
                target_user_email=assignment_dto.email,
                role_id=assignment_dto.role_id,
            )

            self._email_service.notify_role_assigned(
                target_user_id=user.id,
                organisation_id=organisation_id,
                role_id=assignment_dto.role_id,
                assigner_user_id=identity.user_id,
            )

        organisation = self._organisation_repository.get_organisation(organisation_id)
        return organisation_entity_to_resource(organisation)

    def delete_user_organisation_assignment(
        self,
        organisation_id: int,
        user_id: int,
        identity: IdentityContext,
    ) -> None:
        self._permissions_service.validate_role_assignment_permissions(
            organisation_id=organisation_id,
            target_user_id=user_id,
            identity=identity,
        )

        existing_assignment = (
            self._user_assignment_repository.get_user_organisation_assignment(
                organisation_id=organisation_id, user_id=user_id
            )
        )

        if not existing_assignment:
            raise HTTPException(
                status_code=404,
                detail=f"User[{user_id}] is not assigned to Organisation[{organisation_id}]",
            )

        user = self._user_repository.get_user_by_id(user_id)
        user_email = user.email if user else None
        role_ids = [role.role_id for role in existing_assignment.roles]

        self._user_assignment_repository.delete_user_organisation_assignment(
            existing_assignment
        )
        self._user_assignment_repository.commit()

        self._activity_log_service.log_user_assignment_deleted(
            user_id=identity.user_id,
            organisation_id=organisation_id,
            target_user_id=user_id,
            target_user_email=user_email,
            role_ids=role_ids,
        )

    def delete_user_role_assignment(
        self,
        organisation_id: int,
        user_id: int,
        role_id: int,
        identity: IdentityContext,
    ) -> None:
        self._permissions_service.validate_role_assignment_permissions(
            organisation_id=organisation_id,
            target_user_id=user_id,
            identity=identity,
        )

        assignment = self._user_assignment_repository.get_user_organisation_assignment(
            organisation_id=organisation_id, user_id=user_id
        )

        if not assignment:
            raise HTTPException(
                status_code=404,
                detail=f"User[{user_id}] is not assigned to Organisation[{organisation_id}]",
            )

        role_to_remove = next(
            (role for role in assignment.roles if role.role_id == role_id), None
        )

        if not role_to_remove:
            raise HTTPException(
                status_code=404,
                detail=f"User does not have Role[{role_id}] in Organisation[{organisation_id}]",
            )

        user = self._user_repository.get_user_by_id(user_id)
        user_email = user.email if user else None

        if len(assignment.roles) == 1:
            self._user_assignment_repository.delete_user_organisation_assignment(
                assignment
            )
        else:
            assignment.roles.remove(role_to_remove)

        self._user_assignment_repository.commit()

        self._activity_log_service.log_user_assignment_role_removed(
            user_id=identity.user_id,
            organisation_id=organisation_id,
            target_user_id=user_id,
            target_user_email=user_email,
            role_id=role_id,
        )
