import json
from services.activity_log import ActivityLogService
from typing import Optional, List


class PolicyActionActivityLogService(ActivityLogService):
    def get_entity_type(self) -> str:
        return "policy_action"

    def log_policy_action_created(
        self,
        user_id: int,
        dataset_id: int,
        distribution_id: int,
        distribution_title: str,
        policy_action_type: str,
        policy_constraint_type: str,
    ) -> None:
        policy_action_data = {
            "dataset_id": dataset_id,
            "distribution_id": distribution_id,
            "distribution_title": distribution_title,
            "policy_action_type": policy_action_type,
            "policy_constraint_type": policy_constraint_type,
        }

        changes = [
            {
                "field": "policy_action",
                "old_value": None,
                "new_value": policy_action_data,
                "change_type": "created",
            }
        ]

        self._log_activity(
            user_id,
            "update",
            "dataset",
            dataset_id,
            json.dumps(changes),
        )

    def log_policy_action_updated(
        self,
        user_id: int,
        dataset_id: int,
        distribution_id: int,
        distribution_title: str,
        policy_action_type: str,
        policy_constraint_type: str,
    ) -> None:
        policy_action_data = {
            "dataset_id": dataset_id,
            "distribution_id": distribution_id,
            "distribution_title": distribution_title,
            "policy_action_type": policy_action_type,
            "policy_constraint_type": policy_constraint_type,
        }

        changes = [
            {
                "field": "policy_action",
                "old_value": None,
                "new_value": policy_action_data,
                "change_type": "updated",
            }
        ]

        self._log_activity(
            user_id,
            "update",
            "dataset",
            dataset_id,
            json.dumps(changes),
        )

    def log_policy_action_deleted(
        self,
        user_id: int,
        dataset_id: int,
        distribution_id: int,
        distribution_title: str,
        policy_action_type: str,
        policy_constraint_type: str,
    ) -> None:
        policy_action_data = {
            "dataset_id": dataset_id,
            "distribution_id": distribution_id,
            "distribution_title": distribution_title,
            "policy_action_type": policy_action_type,
            "policy_constraint_type": policy_constraint_type,
        }

        changes = [
            {
                "field": "policy_action",
                "old_value": policy_action_data,
                "new_value": None,
                "change_type": "deleted",
            }
        ]

        self._log_activity(
            user_id,
            "update",
            "dataset",
            dataset_id,
            json.dumps(changes),
        )
