from typing import Annotated, List, Optional
from fastapi import Depends, HTTPException, status
from transitions import Machine
from services.database_session_manager import DatabaseSessionManager
from services.email_service import EmailService
from services.activity_logs.dataset_activity_log import DatasetActivityLogService
from models.dataset import (
    Dataset,
    DatasetStatus,
    DatasetVersionChangeType,
)
from repositories.dataset import DatasetRepository
from schemas.dataset import ResourceDataset, dataset_entity_to_resource
from models.identity_context import IdentityContext
from datetime import datetime, timezone
from services.emails.dataset_versioning_email import DatasetVersioningEmailService
from services.config import ConfigService, get_config_service
from services.dataset_permissions_service import DatasetPermissionsService
from services.version_change_validation import (
    normalize_text,
    normalize_version_notes,
)

APPROVE_PERMISSIONS = ["datasets:status-change:approve"]

PUBLISH_PERMISSIONS = ["datasets:status-change:publish"]

DEPRECATE_PERMISSIONS = ["datasets:status-change:deprecate"]

INTERNAL_ONLY_PERMISSIONS = ["datasets:status-change:internal-only"]


class DatasetStatusService:
    def __init__(
        self,
        dataset_repository: Annotated[DatasetRepository, Depends(DatasetRepository)],
        database_session_manager: Annotated[
            DatabaseSessionManager, Depends(DatabaseSessionManager)
        ],
        identity: IdentityContext = Annotated[
            IdentityContext, Depends(IdentityContext)
        ],
        dataset_id: Optional[int] = None,
        dataset: Optional[Dataset] = None,
        email_service: Annotated[EmailService, Depends(EmailService)] = None,
        activity_log_service: Annotated[
            DatasetActivityLogService, Depends(DatasetActivityLogService)
        ] = None,
        dataset_versioning_email_service: Annotated[
            DatasetVersioningEmailService, Depends(DatasetVersioningEmailService)
        ] = None,
        config_service: Annotated[ConfigService, Depends(get_config_service)] = None,
        dataset_permissions_service: Annotated[
            DatasetPermissionsService, Depends(DatasetPermissionsService)
        ] = None,
    ):
        self._dataset_repository = dataset_repository
        self._database_session_manager = database_session_manager
        self._identity = identity
        self._permissions = self._identity.permissions if self._identity else None
        self._email_service = email_service
        self._activity_log_service = activity_log_service
        self._dataset_versioning_email_service = dataset_versioning_email_service
        self._config_service = config_service
        self._dataset_permissions_service = dataset_permissions_service

        if dataset is not None:
            self._dataset = dataset
        elif dataset_id is not None:
            self._dataset = self._load_dataset(dataset_id)
        else:
            raise ValueError("Either dataset_id or dataset must be provided")

        self._old_status = self._dataset.status
        self._setup_state_machine()

    def update_status(self, trigger) -> ResourceDataset:
        if self._dataset.source:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Status transitions are disabled for imported datasets.",
            )
        if trigger == "complete" and not self._has_at_least_one_distribution():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one distribution is required before submitting the dataset.",
            )
        if (
            trigger == "complete"
            and self._is_underlying_data_version_without_required_fields()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "This version is marked as an underlying data change. "
                    "Please fill in the 'version' field and add at least one "
                    "'version note' before submitting."
                ),
            )
        if (
            trigger == "complete"
            and not self._is_underlying_data_version_changed_from_previous()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "This version is marked as an underlying data change. "
                    "Please update the 'version' field and add at least one new "
                    "'version note' compared to the previous version."
                ),
            )
        self._dataset_permissions_service.validate_status_change_permissions(
            dataset_id=self._dataset.id,
            publisher_id=self._dataset.publisher_id,
            identity=self._identity,
        )
        if not getattr(self._dataset, f"may_{trigger}")():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Transition not allowed."
            )

        getattr(self._dataset, trigger)()
        return dataset_entity_to_resource(self._dataset, self.get_triggers())

    def get_triggers(self) -> List[str]:
        if self._dataset.source:
            return []
        possible_triggers = [
            "back_to_draft",
            "complete",
            "validate",
            "approve",
            "publish",
            "unpublish",
            "mark_internal",
            "restore_approved",
            "deprecate",
        ]
        return [
            trigger
            for trigger in possible_triggers
            if getattr(self._dataset, f"may_{trigger}")()
        ]

    def _load_dataset(self, dataset_id: int) -> Dataset:
        dataset = self._dataset_repository.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found"
            )
        return dataset

    def _setup_state_machine(self):
        states = [state.value for state in DatasetStatus]
        transitions = [
            {
                "trigger": "complete",
                "source": "DRAFT",
                "dest": "COMPLETED",
                "after": self._commit_status_change,
                "conditions": self._can_complete,
            },
            {
                "trigger": "validate",
                "source": "COMPLETED",
                "dest": "VALIDATED",
                "after": self._commit_status_change,
                "conditions": self._can_validate,
            },
            {
                "trigger": "approve",
                "source": "VALIDATED",
                "dest": "APPROVED",
                "after": self._commit_status_change,
                "conditions": self._can_approve,
            },
            {
                "trigger": "mark_internal",
                "source": ["APPROVED", "VALIDATED"],
                "dest": "INTERNAL_ONLY",
                "after": self._commit_status_change,
                "conditions": self._can_mark_internal,
            },
            {
                "trigger": "restore_approved",
                "source": "INTERNAL_ONLY",
                "dest": "APPROVED",
                "after": self._commit_status_change,
                "conditions": self._can_mark_internal,
            },
            {
                "trigger": "publish",
                "source": "APPROVED",
                "dest": "PUBLISHED",
                "after": [
                    self._set_release_date,
                    self._complete_authentic_source_review_if_no_dictionaries,
                    self._commit_status_change,
                ],
                "conditions": self._can_publish,
            },
            {
                "trigger": "unpublish",
                "source": "PUBLISHED",
                "dest": "APPROVED",
                "after": self._commit_status_change,
                "conditions": self._can_publish,
            },
            {
                "trigger": "deprecate",
                "source": "PUBLISHED",
                "dest": "DEPRECATED",
                "after": [self._set_deprecate_date, self._commit_status_change],
                "conditions": self._can_deprecate,
            },
            {
                "trigger": "deprecate",
                "source": "INTERNAL_ONLY",
                "dest": "DEPRECATED",
                "after": [self._set_deprecate_date, self._commit_status_change],
                "conditions": self._can_deprecate,
            },
            {
                "trigger": "back_to_draft",
                "source": [
                    "COMPLETED",
                    "VALIDATED",
                    "APPROVED",
                    "PUBLISHED",
                ],
                "dest": "DRAFT",
                "after": self._commit_status_change,
                "conditions": self._can_draft,
            },
        ]

        self._state_machine = Machine(
            model=self._dataset,
            states=states,
            transitions=transitions,
            initial=self._dataset.status,
            auto_transitions=False,
            model_attribute="status",
        )

    def _commit_status_change(self):
        self._dataset_repository.merge(self._dataset)
        self._database_session_manager.commit()
        self._activity_log_service.log_dataset_status_change(
            self._identity.user_id,
            self._dataset.id,
            self._old_status,
            self._dataset.status,
        )

        if self._dataset.status == DatasetStatus.COMPLETED.value:
            self._email_service.notify_dataset_completed(self._dataset)

        if self._dataset.status == DatasetStatus.VALIDATED.value:
            self._email_service.notify_dataset_validated(self._dataset)

        if self._dataset.status == DatasetStatus.APPROVED.value:
            self._email_service.notify_dataset_approved(self._dataset)

        if self._dataset.status == DatasetStatus.DRAFT.value:
            self._email_service.notify_dataset_back_to_draft(self._dataset)

        if self._dataset.status == DatasetStatus.PUBLISHED.value:
            if not self._dataset.previous_version_dataset_id:
                self._email_service.notify_dataset_published(self._dataset)

            self._deprecate_previous_version()

        if self._dataset.status == DatasetStatus.INTERNAL_ONLY.value:
            self._email_service.notify_dataset_marked_as_internal(self._dataset)

        if self._dataset.status == DatasetStatus.DEPRECATED.value:
            self._email_service.notify_dataset_deprecated(self._dataset)

    def _can_complete(self):
        if self._permissions is None:
            return False

        if not self._is_local_dataset():
            return False

        if (
            "datasets:status-change:complete" in self._permissions
            or "datasets:status-change:complete:group" in self._permissions
        ):
            return True

        if "datasets:status-change:complete:organisation" in self._permissions:
            if self._identity.current_organisation_id is None:
                return False
            return self._dataset.publisher_id == self._identity.current_organisation_id

        if "datasets:status-change:complete:my" in self._permissions:
            return self._dataset.user_id == self._identity.user_id

        return False

    def _can_validate(self):
        if self._permissions is None:
            return False

        if not self._is_local_dataset():
            return False

        if "datasets:status-change:validate" in self._permissions:
            return True

        if "datasets:status-change:validate:group" in self._permissions:
            group_manager_ids = {gm.user_id for gm in self._dataset.group_managers}

            return self._identity.user_id in group_manager_ids

    def _can_approve(self):
        if self._permissions is None:
            return False
        if not self._is_local_dataset():
            return False
        return any(
            permission in self._permissions for permission in APPROVE_PERMISSIONS
        )

    def _set_release_date(self):
        self._dataset.released_at = datetime.now(timezone.utc)

    def _complete_authentic_source_review_if_no_dictionaries(self):
        if len(self._dataset.data_dictionaries) == 0:
            self._dataset_repository.complete_authentic_source_review(self._dataset.id)

    def _set_deprecate_date(self):
        self._dataset.deprecated_at = datetime.now(timezone.utc)

    def _has_publish_permissions(self):
        if self._permissions is None:
            return False
        return any(
            permission in self._permissions for permission in PUBLISH_PERMISSIONS
        )

    def _can_mark_internal(self):
        if self._permissions is None:
            return False
        if not self._is_local_dataset():
            return False
        return any(
            permission in self._permissions for permission in INTERNAL_ONLY_PERMISSIONS
        )

    def _can_publish(self):
        if not self._is_local_dataset():
            return False
        if not self._has_publish_permissions():
            return False

        # Cannot publish if a newer version is already published
        if self._dataset_repository.has_published_newer_version(self._dataset.id):
            return False

        return True

    def _can_draft(self):
        if self._permissions is None:
            return False

        if not self._is_local_dataset():
            return False

        if (
            self._dataset.released_at is not None
            and self._config_service.get_enable_multi_tenants()
        ):
            return False

        if "datasets:status-change:draft" in self._permissions:
            return True

        if "datasets:status-change:draft:group" in self._permissions:
            group_manager_ids = {gm.user_id for gm in self._dataset.group_managers}

            return (
                self._identity.user_id in group_manager_ids
                and self._old_status == DatasetStatus.COMPLETED.value
            )

        if self._old_status == DatasetStatus.COMPLETED.value and (
            "datasets:status-change:validate" in self._permissions
            or (
                "datasets:status-change:validate:group" in self._permissions
                and self._identity.user_id
                in {gm.user_id for gm in self._dataset.group_managers}
            )
        ):
            return True

        if self._old_status == DatasetStatus.VALIDATED.value and any(
            permission in self._permissions for permission in APPROVE_PERMISSIONS
        ):
            return True

        if self._old_status == DatasetStatus.APPROVED.value and any(
            permission in self._permissions for permission in PUBLISH_PERMISSIONS
        ):
            return True

        if self._old_status == DatasetStatus.PUBLISHED.value and any(
            permission in self._permissions for permission in PUBLISH_PERMISSIONS
        ):
            return True

        return False

    def _can_deprecate(self):
        if self._permissions is None:
            return False
        if not self._is_local_dataset():
            return False
        return any(
            permission in self._permissions for permission in DEPRECATE_PERMISSIONS
        )

    def _is_local_dataset(self) -> bool:
        return not bool(self._dataset.source)

    def _has_at_least_one_distribution(self) -> bool:
        return bool(getattr(self._dataset, "distributions", None))

    def _is_underlying_data_version_without_required_fields(self) -> bool:
        if (
            self._dataset.version_change_type
            != DatasetVersionChangeType.UNDERLYING_DATA.value
        ):
            return False

        has_version = bool(self._dataset.version and self._dataset.version.strip())
        has_version_notes = bool(normalize_version_notes(self._dataset.version_notes))
        return not (has_version and has_version_notes)

    def _is_underlying_data_version_changed_from_previous(self) -> bool:
        if (
            self._dataset.version_change_type
            != DatasetVersionChangeType.UNDERLYING_DATA.value
        ):
            return True

        previous_version_id = self._dataset.previous_version_dataset_id
        if not previous_version_id:
            return True

        previous_dataset = self._dataset_repository.get_dataset(previous_version_id)
        if not previous_dataset:
            return True

        current_version = normalize_text(self._dataset.version)
        previous_version = normalize_text(previous_dataset.version)
        has_updated_version = current_version != previous_version

        current_notes = normalize_version_notes(self._dataset.version_notes)
        previous_notes = normalize_version_notes(previous_dataset.version_notes)
        has_new_version_note = len(current_notes - previous_notes) > 0

        return has_updated_version and has_new_version_note

    def _deprecate_previous_version(self):
        if self._dataset.previous_version_dataset_id:
            previous_dataset = self._dataset_repository.get_dataset(
                self._dataset.previous_version_dataset_id
            )
            if previous_dataset and previous_dataset.status in [
                DatasetStatus.PUBLISHED.value,
                DatasetStatus.APPROVED.value,
            ]:
                previous_dataset.status = DatasetStatus.DEPRECATED.value
                previous_dataset.deprecated_at = datetime.now(timezone.utc)
                self._dataset_repository.merge(previous_dataset)
                self._database_session_manager.commit()
                self._dataset_versioning_email_service.notify_old_dataset_deprecated(
                    previous_dataset, self._dataset
                )
