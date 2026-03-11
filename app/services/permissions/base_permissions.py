from typing import Annotated
from fastapi import Depends, HTTPException, status
from repositories.user_assignment import UserAssignmentRepository
from repositories.organisation import OrganisationRepository
from services.config import ConfigService, get_config_service


class BasePermissionsService:
    def __init__(
        self,
        user_assignment_repository: Annotated[
            UserAssignmentRepository, Depends(UserAssignmentRepository)
        ] = None,
        organisation_repository: Annotated[
            OrganisationRepository, Depends(OrganisationRepository)
        ] = None,
        config_service: Annotated[ConfigService, Depends(get_config_service)] = None,
    ):
        self._user_assignment_repository = user_assignment_repository
        self._organisation_repository = organisation_repository
        self._config_service = config_service

    def _is_user_assigned_to_organisation(
        self, user_id: int, organisation_id: int
    ) -> bool:
        assignment = self._user_assignment_repository.get_user_organisation_assignment(
            organisation_id=organisation_id, user_id=user_id
        )
        return assignment is not None

    def _validate_organisation_ctie_access(self, organisation_id: int) -> None:
        if self._organisation_repository is None or self._config_service is None:
            return

        if not self._config_service.get_enable_dual_instance():
            return

        if not self._config_service.get_enable_multi_tenants():
            return

        org = self._organisation_repository.get_organisation(organisation_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organisation {organisation_id} not found.",
            )

        is_ctie_instance = self._config_service.is_ctie_instance()
        if is_ctie_instance and org.accessible_within_ctie is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Organisation '{org.name}' cannot be used in CTIE instance.",
            )
        elif not is_ctie_instance and org.accessible_within_ctie is True:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Organisation '{org.name}' is CTIE-only and cannot be used here.",
            )
