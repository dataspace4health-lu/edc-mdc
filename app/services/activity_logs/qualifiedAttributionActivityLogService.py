import json
from services.activity_log import ActivityLogService


class QualifiedAttributionActivityLogService(ActivityLogService):
    def get_entity_type(self) -> str:
        return "dataset"

    def log_qualified_attribution_added(
        self,
        user_id: int,
        dataset_id: int,
        organisation_name: str,
        role: str,
    ) -> None:
        changes = [
            {
                "field": "qualified_attributions",
                "change_type": "qualified_attribution_added",
                "old_value": None,
                "new_value": {
                    "organisation_name": organisation_name,
                    "role": role,
                },
            }
        ]

        self._log_activity(
            user_id=user_id,
            action_type="update",
            entity_type=self.get_entity_type(),
            entity_id=dataset_id,
            diff=json.dumps(changes),
        )

    def log_qualified_attribution_updated(
        self,
        user_id: int,
        dataset_id: int,
        old_organisation_name: str,
        old_role: str,
        new_organisation_name: str,
        new_role: str,
    ) -> None:
        changes = [
            {
                "field": "qualified_attributions",
                "change_type": "qualified_attribution_updated",
                "old_value": {
                    "organisation_name": old_organisation_name,
                    "role": old_role,
                },
                "new_value": {
                    "organisation_name": new_organisation_name,
                    "role": new_role,
                },
            }
        ]

        self._log_activity(
            user_id=user_id,
            action_type="update",
            entity_type=self.get_entity_type(),
            entity_id=dataset_id,
            diff=json.dumps(changes),
        )

    def log_qualified_attribution_removed(
        self,
        user_id: int,
        dataset_id: int,
        organisation_name: str,
        role: str,
    ) -> None:
        changes = [
            {
                "field": "qualified_attributions",
                "change_type": "qualified_attribution_removed",
                "old_value": {
                    "organisation_name": organisation_name,
                    "role": role,
                },
                "new_value": None,
            }
        ]

        self._log_activity(
            user_id=user_id,
            action_type="update",
            entity_type=self.get_entity_type(),
            entity_id=dataset_id,
            diff=json.dumps(changes),
        )
