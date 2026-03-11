import json
from services.activity_log import ActivityLogService
from typing import List, Optional
from schemas.activity_logs import ResourceActivityLog, activity_log_entity_to_resource


class AuthenticSourceLabelActivityLogService(ActivityLogService):
    def get_entity_type(self) -> str:
        return "authentic_source_label"

    def log_label_created(
        self,
        user_id: int,
        label_id: int,
        label_name: str,
        label_description: str,
    ) -> None:
        entity_id = str(label_id)
        changes = [
            {
                "field": "authentic_source_label",
                "old_value": None,
                "new_value": {
                    "id": label_id,
                    "name": label_name,
                    "description": label_description,
                },
                "change_type": "created",
            }
        ]
        self._log_activity(
            user_id, "create", self.get_entity_type(), entity_id, json.dumps(changes)
        )

    def log_label_assigned(
        self,
        user_id: int,
        label_id: int,
        label_name: str,
        entry_id: int,
        old_entry_id: Optional[int] = None,
        dataset_id: Optional[int] = None,
        old_dataset_id: Optional[int] = None,
    ) -> None:
        entity_id = str(label_id)
        changes = [
            {
                "field": "authentic_source_label",
                "old_value": {
                    "entry_id": old_entry_id if old_entry_id else None,
                    "dataset_id": old_dataset_id if old_dataset_id else None,
                },
                "new_value": {
                    "id": label_id,
                    "name": label_name,
                    "entry_id": entry_id,
                    "dataset_id": dataset_id if dataset_id else None,
                },
                "change_type": "assigned",
            }
        ]
        self._log_activity(
            user_id, "update", self.get_entity_type(), entity_id, json.dumps(changes)
        )

        if dataset_id:
            self._log_label_activity_for_dataset(
                user_id,
                dataset_id,
                label_id,
                label_name,
                "assigned",
                entry_id,
                old_entry_id,
            )

    def log_label_unassigned(
        self,
        user_id: int,
        label_id: int,
        label_name: str,
        old_entry_id: int,
        old_dataset_id: Optional[int] = None,
    ) -> None:
        entity_id = str(label_id)
        changes = [
            {
                "field": "authentic_source_label",
                "old_value": {
                    "id": label_id,
                    "name": label_name,
                    "entry_id": old_entry_id,
                    "dataset_id": old_dataset_id if old_dataset_id else None,
                },
                "new_value": None,
                "change_type": "unassigned",
            }
        ]
        self._log_activity(
            user_id, "update", self.get_entity_type(), entity_id, json.dumps(changes)
        )

        if old_dataset_id:
            self._log_label_activity_for_dataset(
                user_id,
                old_dataset_id,
                label_id,
                label_name,
                "unassigned",
                None,
                old_entry_id,
            )

    def log_label_reassigned(
        self,
        user_id: int,
        label_id: int,
        label_name: str,
        old_entry_id: int,
        new_entry_id: int,
        old_dataset_id: Optional[int] = None,
        new_dataset_id: Optional[int] = None,
    ) -> None:
        entity_id = str(label_id)
        changes = [
            {
                "field": "authentic_source_label",
                "old_value": {
                    "id": label_id,
                    "name": label_name,
                    "entry_id": old_entry_id,
                    "dataset_id": old_dataset_id if old_dataset_id else None,
                },
                "new_value": {
                    "id": label_id,
                    "name": label_name,
                    "entry_id": new_entry_id,
                    "dataset_id": new_dataset_id if new_dataset_id else None,
                },
                "change_type": "reassigned",
            }
        ]
        self._log_activity(
            user_id, "update", self.get_entity_type(), entity_id, json.dumps(changes)
        )

        if old_dataset_id and old_dataset_id != new_dataset_id:
            self._log_label_activity_for_dataset(
                user_id,
                old_dataset_id,
                label_id,
                label_name,
                "unassigned",
                None,
                old_entry_id,
            )

        # Log activity for new dataset if it exists
        if new_dataset_id:
            self._log_label_activity_for_dataset(
                user_id,
                new_dataset_id,
                label_id,
                label_name,
                "assigned",
                new_entry_id,
                old_entry_id if old_dataset_id == new_dataset_id else None,
            )

    def log_label_updated(
        self,
        user_id: int,
        label_id: int,
        old_name: str,
        new_name: str,
        old_description: str,
        new_description: str,
    ) -> None:
        entity_id = str(label_id)
        # Build changes array for modified fields
        changes = []
        if old_name != new_name:
            changes.append(
                {
                    "field": "name",
                    "old_value": old_name,
                    "new_value": new_name,
                    "change_type": "updated",
                }
            )
        if old_description != new_description:
            changes.append(
                {
                    "field": "description",
                    "old_value": old_description,
                    "new_value": new_description,
                    "change_type": "updated",
                }
            )
        # Add overall label update change
        changes.append(
            {
                "field": "authentic_source_label",
                "old_value": {
                    "id": label_id,
                    "name": old_name,
                    "description": old_description,
                },
                "new_value": {
                    "id": label_id,
                    "name": new_name,
                    "description": new_description,
                },
                "change_type": "updated",
            }
        )
        self._log_activity(
            user_id, "update", self.get_entity_type(), entity_id, json.dumps(changes)
        )

    def log_label_deleted(
        self,
        user_id: int,
        label_id: int,
        label_name: str,
        label_description: str,
    ) -> None:
        entity_id = str(label_id)

        changes = [
            {
                "field": "authentic_source_label",
                "old_value": {
                    "id": label_id,
                    "name": label_name,
                    "description": label_description,
                },
                "new_value": None,
                "change_type": "deleted",
            }
        ]

        self._log_activity(
            user_id, "delete", self.get_entity_type(), entity_id, json.dumps(changes)
        )

    def log_label_deprecated(
        self,
        user_id: int,
        label_data: dict,
    ) -> None:
        entity_id = str(label_data["id"])
        current_deprecated_status = label_data.get("is_deprecated", False)

        if current_deprecated_status:
            action_type = "deprecate"
            old_value = {**label_data, "is_deprecated": False}
            new_value = label_data
        else:
            action_type = "restore"
            old_value = {**label_data, "is_deprecated": True}
            new_value = label_data

        diff = json.dumps(
            [
                {
                    "field": "authentic_source_label",
                    "old_value": old_value,
                    "new_value": new_value,
                    "change_type": "values_changed",
                }
            ]
        )

        self._log_activity(
            user_id, action_type, self.get_entity_type(), entity_id, diff
        )

    def _log_label_activity_for_dataset(
        self,
        user_id: int,
        dataset_id: int,
        label_id: int,
        label_name: str,
        action: str,  # "assigned", "unassigned"
        new_entry_id: Optional[int] = None,
        old_entry_id: Optional[int] = None,
    ) -> None:
        if action == "assigned":
            old_value = None
            if old_entry_id:
                old_value = {"entry_id": old_entry_id}

            changes = [
                {
                    "field": "authentic_source_label",
                    "old_value": old_value,
                    "new_value": {
                        "id": label_id,
                        "name": label_name,
                        "entry_id": new_entry_id,
                    },
                    "change_type": "label_assigned",
                }
            ]
        elif action == "unassigned":
            changes = [
                {
                    "field": "authentic_source_label",
                    "old_value": {
                        "id": label_id,
                        "name": label_name,
                        "entry_id": old_entry_id,
                    },
                    "new_value": None,
                    "change_type": "label_unassigned",
                }
            ]

        # Log activity for the dataset entity
        self._log_activity(
            user_id, "update", "dataset", str(dataset_id), json.dumps(changes)
        )
