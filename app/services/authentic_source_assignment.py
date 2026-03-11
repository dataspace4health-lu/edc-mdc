from fastapi import Depends, HTTPException, status
from typing import List, Annotated, Optional
from repositories.authentic_source_assignment import AuthenticSourceAssignmentRepository
from repositories.authentic_source_label import AuthenticSourceLabelRepository
from models.identity_context import IdentityContext
from schemas.authentic_source_label import (
    ResourceAuthenticSourceLabel,
    authentic_source_label_entity_to_resource,
)
from schemas.authentic_source_assignment import (
    BulkLabelAssignmentDto,
)
from repositories.dataset import DatasetRepository
from repositories.data_dictionary import DataDictionaryRepository
from services.database_session_manager import DatabaseSessionManager
from services.activity_logs.authentic_source_label_activity_log import (
    AuthenticSourceLabelActivityLogService,
)
from services.emails.authentic_source_email import AuthenticSourceEmailService


class AuthenticSourceAssignmentService:
    def __init__(
        self,
        label_repo: Annotated[
            AuthenticSourceLabelRepository, Depends(AuthenticSourceLabelRepository)
        ],
        assignment_repo: Annotated[
            AuthenticSourceAssignmentRepository,
            Depends(AuthenticSourceAssignmentRepository),
        ],
        dataset_repo: Annotated[DatasetRepository, Depends(DatasetRepository)],
        dictionary_repo: Annotated[
            DataDictionaryRepository, Depends(DataDictionaryRepository)
        ],
        db_session_manager: Annotated[
            DatabaseSessionManager, Depends(DatabaseSessionManager)
        ],
        activity_log_service: Annotated[
            AuthenticSourceLabelActivityLogService,
            Depends(AuthenticSourceLabelActivityLogService),
        ],
        email_service: Annotated[
            AuthenticSourceEmailService, Depends(AuthenticSourceEmailService)
        ],
    ):
        self._assignment_repo = assignment_repo
        self._label_repo = label_repo
        self._dataset_repo = dataset_repo
        self._dictionary_repo = dictionary_repo
        self._db_session_manager = db_session_manager
        self._activity_log_service = activity_log_service
        self._email_service = email_service

    def assign_labels(
        self, dto: BulkLabelAssignmentDto, identity: IdentityContext
    ) -> List[ResourceAuthenticSourceLabel]:
        # Track assignment changes for email notifications
        assignment_changes = []

        for label_assignment in dto.label_assignments:
            label = self._label_repo.get_by_id(label_assignment.label_id)
            if not label:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Label with ID {label_assignment.label_id} not found",
                )

            # Get current assignment to track what's changing
            current_assignment = self._assignment_repo.get_current_assignment_for_label(
                label_assignment.label_id
            )
            old_entry_id = (
                current_assignment.data_dictionary_entry_id
                if current_assignment
                else None
            )
            new_entry_id = label_assignment.assigned_entry_id

            old_dataset_id = (
                self._dictionary_repo.get_data_dictionary_entry(old_entry_id).dataset_id
                if old_entry_id
                else None
            )

            new_dataset_id = (
                self._dictionary_repo.get_data_dictionary_entry(new_entry_id).dataset_id
                if new_entry_id
                else None
            )

            # Process the assignment
            self._assignment_repo.process_label_assignment(
                label_id=label_assignment.label_id,
                new_entry_id=new_entry_id,
                assigned_by=identity.user_id,
            )

            # Log the assignment change and capture the details for email
            change_details = self._log_assignment_change(
                user_id=identity.user_id,
                label_id=label_assignment.label_id,
                label_name=label.name,
                old_entry_id=old_entry_id,
                new_entry_id=new_entry_id,
                old_dataset_id=old_dataset_id,
                new_dataset_id=new_dataset_id,
            )

            # Add to email changes if there was an actual change
            if change_details:
                assignment_changes.append(change_details)

        self._assignment_repo.commit()

        # Send email notifications for all changes
        if assignment_changes:
            self._send_assignment_notifications(assignment_changes, identity.user_id)

        labels = self._label_repo.get_all()
        return [authentic_source_label_entity_to_resource(label) for label in labels]

    def _log_assignment_change(
        self,
        user_id: int,
        label_id: int,
        label_name: str,
        old_entry_id: Optional[int],
        new_entry_id: Optional[int],
        old_dataset_id: Optional[int] = None,
        new_dataset_id: Optional[int] = None,
    ) -> Optional[dict]:
        change_details = None

        if old_entry_id is None and new_entry_id is not None:
            # New assignment
            self._activity_log_service.log_label_assigned(
                user_id=user_id,
                label_id=label_id,
                label_name=label_name,
                entry_id=new_entry_id,
                old_entry_id=old_entry_id,
                dataset_id=new_dataset_id,
                old_dataset_id=old_dataset_id,
            )
            change_details = {
                "label_name": label_name,
                "change_type": "assigned",
                "old_dataset_id": old_dataset_id,
                "new_dataset_id": new_dataset_id,
            }

        elif old_entry_id is not None and new_entry_id is None:
            # Unassignment
            self._activity_log_service.log_label_unassigned(
                user_id=user_id,
                label_id=label_id,
                label_name=label_name,
                old_entry_id=old_entry_id,
                old_dataset_id=old_dataset_id,
            )
            change_details = {
                "label_name": label_name,
                "change_type": "unassigned",
                "old_dataset_id": old_dataset_id,
                "new_dataset_id": new_dataset_id,
            }

        elif (
            old_entry_id is not None
            and new_entry_id is not None
            and old_entry_id != new_entry_id
        ):
            # Reassignment
            self._activity_log_service.log_label_reassigned(
                user_id=user_id,
                label_id=label_id,
                label_name=label_name,
                old_entry_id=old_entry_id,
                new_entry_id=new_entry_id,
                old_dataset_id=old_dataset_id,
                new_dataset_id=new_dataset_id,
            )
            change_details = {
                "label_name": label_name,
                "change_type": "reassigned",
                "old_dataset_id": old_dataset_id,
                "new_dataset_id": new_dataset_id,
            }

        return change_details

    def _send_assignment_notifications(
        self, assignment_changes: List[dict], assigner_user_id: int
    ):
        dataset_changes = {}

        for change in assignment_changes:
            # Add to old dataset group if it exists
            if change["old_dataset_id"]:
                if change["old_dataset_id"] not in dataset_changes:
                    dataset_changes[change["old_dataset_id"]] = []
                dataset_changes[change["old_dataset_id"]].append(change)

            # Add to new dataset group if it exists and different from old
            if (
                change["new_dataset_id"]
                and change["new_dataset_id"] != change["old_dataset_id"]
            ):
                if change["new_dataset_id"] not in dataset_changes:
                    dataset_changes[change["new_dataset_id"]] = []
                dataset_changes[change["new_dataset_id"]].append(change)

        # Send notification for each affected dataset
        for dataset_id, relevant_changes in dataset_changes.items():
            dataset = self._dataset_repo.get_dataset(dataset_id)
            if dataset:
                self._email_service.notify_authentic_source_assignment_changed(
                    dataset=dataset,
                    assignment_changes=relevant_changes,
                    assigner_user_id=assigner_user_id,
                )

    def complete_authentic_source_review(self, dataset_id: int) -> None:
        dataset = self._dataset_repo.complete_authentic_source_review(dataset_id)
        self._db_session_manager.commit()
