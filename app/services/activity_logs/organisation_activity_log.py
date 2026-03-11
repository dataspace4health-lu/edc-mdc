import json
from services.activity_log import ActivityLogService
from typing import List
from schemas.activity_logs import ResourceActivityLog, activity_log_entity_to_resource
from models.contact import Contact


class OrganisationActivityLogService(ActivityLogService):
    def get_entity_type(self) -> str:
        return "organisation"

    def log_contact_added_to_organisation(
        self, user_id: int, organisation_id: int, contact: Contact
    ) -> None:
        action_type = "add_contact"
        entity_id = organisation_id

        contact_data = contact.to_dict()

        diff = json.dumps(
            [
                {
                    "field": "contact",
                    "new_value": contact_data,
                    "change_type": "values_changed",
                }
            ]
        )

        self._log_activity(
            user_id, action_type, self.get_entity_type(), entity_id, diff
        )

    def log_contact_updated_in_organisation(
        self,
        user_id: int,
        organisation_id: int,
        old_data: dict,
        new_contact: Contact,
    ) -> None:
        entity_id = organisation_id
        action_type = "update_contact"

        changes = []

        new_data = new_contact.to_dict()

        for field, old_value in old_data.items():
            new_value = new_data.get(field)
            if old_value != new_value:
                changes.append(
                    {
                        "field": field,
                        "old_value": old_value,
                        "new_value": new_value,
                        "change_type": "values_changed",
                    }
                )

        if changes:
            self._log_activity(
                user_id,
                action_type,
                self.get_entity_type(),
                entity_id,
                json.dumps(changes),
            )

    def log_contact_deleted_from_organisation(
        self, user_id: int, organisation_id: int, contact_data: dict
    ) -> None:
        entity_id = organisation_id
        action_type = "delete_contact"

        diff = json.dumps(
            [
                {
                    "field": "contact",
                    "old_value": contact_data,
                    "change_type": "values_changed",
                }
            ]
        )

        self._log_activity(
            user_id, action_type, self.get_entity_type(), entity_id, diff
        )

    def log_contact_deprecated_in_organisation(
        self, user_id: int, organisation_id: int, contact_data: dict
    ) -> None:
        entity_id = organisation_id
        current_deprecated_status = contact_data.get("is_deprecated", False)

        if current_deprecated_status:
            action_type = "deprecate"
            old_value = {**contact_data, "is_deprecated": False}
            new_value = contact_data
        else:
            action_type = "restore"
            old_value = {**contact_data, "is_deprecated": True}
            new_value = contact_data

        diff = json.dumps(
            [
                {
                    "field": "contact",
                    "old_value": old_value,
                    "new_value": new_value,
                    "change_type": "values_changed",
                }
            ]
        )

        self._log_activity(
            user_id, action_type, self.get_entity_type(), entity_id, diff
        )
