import json
from services.activity_log import ActivityLogService
from typing import List
from schemas.activity_logs import ResourceActivityLog, activity_log_entity_to_resource


class UserAssignmentActivityLogService(ActivityLogService):
    def get_entity_type(self) -> str:
        return "user_assignment"

    def log_user_assignment_created(
        self,
        user_id: int,
        organisation_id: int,
        target_user_id: int,
        target_user_email: str,
        role_id: int,
    ) -> None:
        entity_id = f"{target_user_id}:{organisation_id}"
        changes = [
            {
                "field": "user_assignment",
                "old_value": None,
                "new_value": {
                    "target_user_id": target_user_id,
                    "target_user_email": target_user_email,
                    "organisation_id": organisation_id,
                    "role_id": role_id,
                },
                "change_type": "created",
            }
        ]
        self._log_activity(
            user_id, "create", self.get_entity_type(), entity_id, json.dumps(changes)
        )

    def log_user_assignment_deleted(
        self,
        user_id: int,
        organisation_id: int,
        target_user_id: int,
        target_user_email: str,
        role_ids: List[int],
    ) -> None:
        entity_id = f"{target_user_id}:{organisation_id}"
        changes = [
            {
                "field": "user_assignment",
                "old_value": {
                    "target_user_id": target_user_id,
                    "target_user_email": target_user_email,
                    "organisation_id": organisation_id,
                    "role_ids": role_ids,
                },
                "new_value": None,
                "change_type": "deleted",
            }
        ]
        self._log_activity(
            user_id, "delete", self.get_entity_type(), entity_id, json.dumps(changes)
        )

    def log_user_assignment_role_added(
        self,
        user_id: int,
        organisation_id: int,
        target_user_id: int,
        target_user_email: str,
        role_id: int,
    ) -> None:
        entity_id = f"{target_user_id}:{organisation_id}"
        changes = [
            {
                "field": "roles",
                "old_value": None,
                "new_value": {
                    "target_user_id": target_user_id,
                    "target_user_email": target_user_email,
                    "organisation_id": organisation_id,
                    "role_id": role_id,
                },
                "change_type": "role_added",
            }
        ]
        self._log_activity(
            user_id, "update", self.get_entity_type(), entity_id, json.dumps(changes)
        )

    def log_user_assignment_role_removed(
        self,
        user_id: int,
        organisation_id: int,
        target_user_id: int,
        target_user_email: str,
        role_id: int,
    ) -> None:
        entity_id = f"{target_user_id}:{organisation_id}"
        changes = [
            {
                "field": "roles",
                "old_value": {
                    "target_user_id": target_user_id,
                    "target_user_email": target_user_email,
                    "organisation_id": organisation_id,
                    "role_id": role_id,
                },
                "new_value": None,
                "change_type": "role_removed",
            }
        ]
        self._log_activity(
            user_id, "update", self.get_entity_type(), entity_id, json.dumps(changes)
        )

    def get_activity_logs_for_organisations(
        self, organisation_ids: List[int], page: int, page_size: int
    ) -> List[ResourceActivityLog]:
        all_logs = self._repository.get_all_activity_logs_for_entity(
            self.get_entity_type(), page, page_size
        )
        if not organisation_ids:
            return [activity_log_entity_to_resource(log) for log in all_logs]

        org_suffixes = {f":{org_id}" for org_id in organisation_ids}
        filtered_logs = [
            log
            for log in all_logs
            if log.entity_id and any(suffix in log.entity_id for suffix in org_suffixes)
        ]
        return [activity_log_entity_to_resource(log) for log in filtered_logs]

    def log_user_deprecation_status_change(
        self,
        user_id: int,
        target_user_id: int,
        target_user_email: str,
        target_user_name: str,
        change_type: str,
    ) -> None:
        entity_id = str(target_user_id)
        old_deprecated_status = False if change_type == "deprecated" else True
        new_deprecated_status = True if change_type == "deprecated" else False

        changes = [
            {
                "field": "is_deprecated",
                "old_value": {
                    "target_user_id": target_user_id,
                    "target_user_email": target_user_email,
                    "target_user_name": target_user_name,
                    "is_deprecated": old_deprecated_status,
                },
                "new_value": {
                    "target_user_id": target_user_id,
                    "target_user_email": target_user_email,
                    "target_user_name": target_user_name,
                    "is_deprecated": new_deprecated_status,
                },
                "change_type": change_type,
            }
        ]
        self._log_activity(
            user_id, "update", self.get_entity_type(), entity_id, json.dumps(changes)
        )
