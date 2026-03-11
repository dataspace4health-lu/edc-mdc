from sqlalchemy.orm import Session
from dependencies.database import get_db_session
from models.user import User
from typing import Annotated, List, Optional
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from repositories.user import UserRepository
from repositories.dataset import DatasetRepository
from repositories.activity_log import ActivityLogRepository
from repositories.applicable_legislation import ApplicableLegislationRepository
from repositories.keyword import KeywordRepository
from services.config import ConfigService, get_config_service
from schemas.user import PaginatedUserResponse, PaginationMeta, user_entity_to_resource
from models.identity_context import IdentityContext
from repositories.user_assignment import UserAssignmentRepository
from services.user_assignment_permissions import UserAssignmentPermissionsService
from services.activity_logs.user_assignment_activity_log import (
    UserAssignmentActivityLogService,
)


class UserService:
    def __init__(
        self,
        db_session: Annotated[Session, Depends(get_db_session)],
        user_repository: Annotated[UserRepository, Depends(UserRepository)],
        user_assignment_repository: Annotated[
            UserAssignmentRepository, Depends(UserAssignmentRepository)
        ],
        user_assignment_permissions_service: Annotated[
            UserAssignmentPermissionsService, Depends(UserAssignmentPermissionsService)
        ],
        activity_log_repository: Annotated[
            ActivityLogRepository, Depends(ActivityLogRepository)
        ],
        user_assignment_activity_log_service: Annotated[
            UserAssignmentActivityLogService, Depends(UserAssignmentActivityLogService)
        ],
        dataset_repository: Annotated[DatasetRepository, Depends(DatasetRepository)],
        applicable_legislation_repository: Annotated[
            ApplicableLegislationRepository, Depends(ApplicableLegislationRepository)
        ],
        keyword_repository: Annotated[KeywordRepository, Depends(KeywordRepository)],
        config_service: ConfigService = Depends(get_config_service),
    ):
        self.db_session = db_session
        self.user_repository = user_repository
        self.user_assignment_repository = user_assignment_repository
        self.dataset_repository = dataset_repository
        self.applicable_legislation_repository = applicable_legislation_repository
        self.keyword_repository = keyword_repository
        self.config_service = config_service
        self.user_assignment_permissions_service = user_assignment_permissions_service
        self.activity_log_repository = activity_log_repository
        self.user_assignment_activity_log_service = user_assignment_activity_log_service

    def create_or_find(
        self, email: str | None, name: str, external_id: str, iam_roles: list[str]
    ) -> User:
        # Normalize email to lowercase for consistent matching (if provided)
        email_normalized = email.lower() if email else None

        # First, try to find by external_id (current IAM)
        user_entry = (
            self.db_session.query(User).filter_by(external_id=external_id).first()
        )

        # If not found by external_id and email is provided, try to find by email (handles IAM migration)
        if not user_entry and email_normalized:
            user_entry = (
                self.db_session.query(User)
                .filter(User.email.ilike(email_normalized))
                .first()
            )

            # If found by email, update external_id to new IAM's sub
            if user_entry:
                user_entry.external_id = external_id

        # If still not found, create new user
        if not user_entry:
            user_entry = User(
                email=email_normalized,
                name=name,
                external_id=external_id,
                iam_roles=",".join(iam_roles),
            )
            self.db_session.add(user_entry)
            self.db_session.commit()

        # Update name and IAM roles on every login
        user_entry.name = name
        user_entry.iam_roles = ",".join(iam_roles)
        user_entry.last_login_at = datetime.now(timezone.utc)
        self.db_session.commit()

        return user_entry

    def find_by_id(self, user_id: int) -> User:
        return self.db_session.query(User).filter_by(id=user_id).first()

    def remove_iam_roles(self, user_id: int, identity: IdentityContext) -> None:
        if "roles:manage" not in identity.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to remove IAM roles.",
            )

        user = self.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user.iam_roles = ""
        self.db_session.commit()

    def find_by_iam_role(self, role: str) -> list[User]:
        return self.db_session.query(User).filter(User.iam_roles.contains(role)).all()

    def find_dataset_validator_users(self) -> list[User]:
        roles = self.config_service.get_roles_by_permission(
            "datasets:status-change:validate:group"
        )

        role_names = [role["name"] for role in roles]
        return self.user_repository.get_users_with_roles(role_names)

    def get_users(
        self,
        page: int,
        page_size: int,
        query: Optional[str],
        organisation_ids: Optional[List[int]] = None,
        role_ids: Optional[List[int]] = None,
        only_unassigned: Optional[bool] = False,
        identity: Optional[IdentityContext] = None,
        is_deprecated: Optional[bool] = False,
    ) -> PaginatedUserResponse:

        permission_filter = (
            self.user_assignment_permissions_service.get_user_permission_filters(
                identity
            )
        )

        users, total = self.user_repository.get_users(
            page=page,
            page_size=page_size,
            query=query,
            organisation_ids=organisation_ids,
            role_ids=role_ids,
            only_unassigned=only_unassigned,
            permission_filter=permission_filter,
            is_deprecated=is_deprecated,
        )

        resource_users = []
        for u in users:
            resource_users.append(
                user_entity_to_resource(
                    user=u,
                    current_org_id=None,
                    permissions=[],
                    feature_flag_data={},
                    default_themes=set(),
                    show_notice_on_homepage=None,
                )
            )

        return PaginatedUserResponse(
            items=resource_users,
            meta=PaginationMeta(
                total_items=total,
                page=page,
                page_size=page_size,
                total_pages=(total + page_size - 1) // page_size,
            ),
        )

    def update_deprecation_status(
        self, user_id: int, identity: IdentityContext
    ) -> None:
        if "roles:manage" not in identity.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to deprecate users.",
            )
        user = self.user_repository.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not exist",
            )
        if not user.is_deprecated:
            self.user_repository.set_deprecation_status(user_id, True)
            self.user_assignment_activity_log_service.log_user_deprecation_status_change(
                user_id=identity.user_id,
                target_user_id=user_id,
                target_user_email=user.email,
                target_user_name=user.name,
                change_type="deprecated",
            )
        else:
            self.user_repository.set_deprecation_status(user_id, False)
            self.user_assignment_activity_log_service.log_user_deprecation_status_change(
                user_id=identity.user_id,
                target_user_id=user_id,
                target_user_email=user.email,
                target_user_name=user.name,
                change_type="restored",
            )

    def delete_unassigned_user(self, user_id: int, identity: IdentityContext) -> None:
        if "roles:manage" not in identity.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete users.",
            )

        user = self.user_repository.get_user(user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

        reasons = self._get_deletion_reasons(user.id, user.iam_roles)

        if reasons:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete this user because: " + "; ".join(reasons),
            )

        self.user_repository.delete_user(user_id)

    def _get_deletion_reasons(
        self, user_id: int, iam_roles: Optional[str]
    ) -> List[str]:
        iam_roles = [r.strip() for r in (iam_roles or "").split(",") if r.strip()]
        reasons = []

        if "CATALOGUE_MANAGER" in iam_roles:
            reasons.append("user is a catalogue manager")

        if self.user_assignment_repository.get_user_organisation_assignments(user_id):
            reasons.append("user is assigned to an organisation.")

        if self.dataset_repository.get_count_for_user(user_id) > 0:
            reasons.append("user has datasets assigned.")

        if self.applicable_legislation_repository.get_count_for_user(user_id) > 0:
            reasons.append("user has applicable legislations assigned.")

        if self.keyword_repository.get_count_for_user(user_id) > 0:
            reasons.append("user has keywords assigned.")

        return reasons
