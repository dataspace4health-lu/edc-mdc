from fastapi import Depends, HTTPException, status
from typing import List, Annotated, Optional
from repositories.authentic_source_label import AuthenticSourceLabelRepository
from repositories.authentic_source_assignment import AuthenticSourceAssignmentRepository
from repositories.dataset import DatasetRepository
from models.authentic_source_label import AuthenticSourceLabel
from models.identity_context import IdentityContext
from models.dataset import Dataset
from schemas.authentic_source_label import (
    AuthenticSourceLabelDto,
    ResourceAuthenticSourceLabel,
    LabelAssignmentHistory,
    authentic_source_label_entity_to_resource,
    dataset_to_label_assignment_history,
)
from services.activity_logs.authentic_source_label_activity_log import (
    AuthenticSourceLabelActivityLogService,
)


class AuthenticSourceLabelService:
    def __init__(
        self,
        label_repo: Annotated[
            AuthenticSourceLabelRepository, Depends(AuthenticSourceLabelRepository)
        ],
        assignment_repo: Annotated[
            AuthenticSourceAssignmentRepository,
            Depends(AuthenticSourceAssignmentRepository),
        ],
        activity_log_service: Annotated[
            AuthenticSourceLabelActivityLogService,
            Depends(AuthenticSourceLabelActivityLogService),
        ],
    ):
        self._label_repo = label_repo
        self._assignment_repo = assignment_repo
        self._activity_log_service = activity_log_service

    def create_label(
        self, label_dto: AuthenticSourceLabelDto, identity: IdentityContext
    ) -> ResourceAuthenticSourceLabel:
        existing_label = self._label_repo.get_by_name(label_dto.name)
        if existing_label:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Authentic source label with name '{label_dto.name}' already exists",
            )

        new_label = AuthenticSourceLabel(
            name=label_dto.name,
            description=label_dto.description,
            created_by=identity.user_id,
        )

        self._label_repo.add(new_label)
        self._label_repo.commit()
        self._label_repo.refresh(new_label)

        self._activity_log_service.log_label_created(
            user_id=identity.user_id,
            label_id=new_label.id,
            label_name=new_label.name,
            label_description=new_label.description,
        )

        return authentic_source_label_entity_to_resource(new_label)

    def get_all_labels(
        self, include_deprecated: bool = False
    ) -> List[ResourceAuthenticSourceLabel]:
        labels = self._label_repo.get_all(include_deprecated=include_deprecated)
        return [authentic_source_label_entity_to_resource(label) for label in labels]

    def get_previous_label_assigned_datasets(
        self, label_id
    ) -> List[LabelAssignmentHistory]:
        assignments = self._assignment_repo.get_previous_assignments_for_label(label_id)
        datasets = []
        for assignment in assignments:
            entry = assignment.data_dictionary_entry
            dataset = entry.dataset
            datasets.append(dataset_to_label_assignment_history(dataset, assignment))
        return datasets

    def update_label(
        self,
        label_id: int,
        label_dto: AuthenticSourceLabelDto,
        identity: IdentityContext,
    ) -> ResourceAuthenticSourceLabel:
        existing_label = self._label_repo.get_by_id(label_id)
        if not existing_label:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Authentic source label with ID {label_id} not found",
            )

        # Check if another label with the same name exists (excluding current label)
        label_with_same_name = self._label_repo.get_by_name(label_dto.name)
        if label_with_same_name and label_with_same_name.id != label_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Authentic source label with name '{label_dto.name}' already exists",
            )

        # Store old values for activity log
        old_name = existing_label.name
        old_description = existing_label.description

        # Update the label
        existing_label.name = label_dto.name
        existing_label.description = label_dto.description
        existing_label.created_by = identity.user_id

        self._label_repo.commit()
        self._label_repo.refresh(existing_label)

        # Log the update activity
        self._activity_log_service.log_label_updated(
            user_id=identity.user_id,
            label_id=existing_label.id,
            old_name=old_name,
            new_name=existing_label.name,
            old_description=old_description,
            new_description=existing_label.description,
        )

        return authentic_source_label_entity_to_resource(existing_label)

    def delete_label(self, label_id: int, identity: IdentityContext) -> None:
        # Check if label exists
        existing_label = self._label_repo.get_by_id(label_id)
        if not existing_label:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Authentic source label with ID {label_id} not found",
            )

        # Check if label has any assignments
        if self._assignment_repo.get_current_assignment_for_label(label_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete authentic source label that has active assignments",
            )

        # Store label info for activity log before deletion
        label_name = existing_label.name
        label_description = existing_label.description

        # Delete the label
        self._label_repo.delete(existing_label)
        self._label_repo.commit()

        # Log the deletion activity
        self._activity_log_service.log_label_deleted(
            user_id=identity.user_id,
            label_id=label_id,
            label_name=label_name,
            label_description=label_description,
        )

    def update_deprecation_status(
        self, label_id: int, identity: IdentityContext
    ) -> ResourceAuthenticSourceLabel:
        label = self._label_repo.get_by_id(label_id)

        if not label:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Authentic source label with ID {label_id} not found",
            )

        if not label.is_deprecated:
            self._label_repo.set_deprecation_status(label.id, True)

        else:
            self._label_repo.set_deprecation_status(label.id, False)
        updated_label = self._label_repo.get_by_id(label.id)
        self._activity_log_service.log_label_deprecated(
            user_id=identity.user_id,
            label_data=authentic_source_label_entity_to_resource(updated_label).dict(),
        )
        return authentic_source_label_entity_to_resource(updated_label)
