import json
from services.activity_log import ActivityLogService


class DataDictionaryActivityLogService(ActivityLogService):
    def get_entity_type(self) -> str:
        return "dataset"

    def log_order_change(self, user_id: int, dataset_id: int) -> None:
        diff = [
            {
                "field": "data_dictionaries.position",
                "old_value": None,
                "new_value": None,
                "change_type": "order_changed",
            }
        ]

        self._log_activity(user_id, "reorder", "dataset", dataset_id, json.dumps(diff))
