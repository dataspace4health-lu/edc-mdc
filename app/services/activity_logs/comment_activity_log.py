import json
from services.activity_log import ActivityLogService


class CommentActivityLogService(ActivityLogService):
    def get_entity_type(self) -> str:
        return "comment"

    def log_dataset_comment(
        self, user_id: int, dataset_id: int, comment: str, action_type: str
    ) -> None:
        if action_type == "add_comment":
            diff = [
                {
                    "field": "comment",
                    "old_value": None,
                    "new_value": comment,
                    "change_type": "created",
                }
            ]
        elif action_type == "delete_comment":
            diff = [
                {
                    "field": "comment",
                    "old_value": comment,
                    "new_value": None,
                    "change_type": "deleted",
                }
            ]

        else:
            raise ValueError(f"Unsupported action_type: {action_type}")

        self._log_activity(
            user_id, action_type, "dataset", dataset_id, json.dumps(diff)
        )
