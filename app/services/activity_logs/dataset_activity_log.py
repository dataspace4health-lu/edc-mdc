import json
from typing import Annotated, List, Dict

from fastapi import Depends

from models.dataset import Dataset
from repositories.activity_log import ActivityLogRepository
from schemas.activity_logs import ResourceActivityLog, activity_log_entity_to_resource
from schemas.dataset import DatasetDto
from services.activity_log import ActivityLogService
from utils.dataset_diff import DatasetDiff


class DatasetActivityLogService(ActivityLogService):
    def get_entity_type(self) -> str:
        return "dataset"

    def log_dataset_activities(
        self,
        user_id: int,
        dataset: Dataset,
        updated_dataset_dto: DatasetDto,
        action_type: str,
    ) -> None:
        entity_type = "dataset"
        entity_id = dataset.id
        original_data = dataset.to_dict_for_diff()
        updated_data = json.loads(updated_dataset_dto.model_dump_json())

        diff = DatasetDiff.compute(original_data, updated_data)
        if diff and json.loads(diff):
            self._log_activity(user_id, action_type, entity_type, entity_id, diff)

    def log_dictionary_item_activities(
        self,
        user_id: int,
        dataset_id: int,
        field: str,
        old_value: Dict[str, str],
        new_value: Dict[str, str],
    ) -> None:
        if old_value and new_value:
            change_type = "dictionary_item_updated"
        elif old_value:
            change_type = "dictionary_item_removed"
        else:
            change_type = "dictionary_item_added"

        formatted_diff = [
            {
                "field": field,
                "change_type": change_type,
                "old_value": old_value,
                "new_value": new_value,
            }
        ]

        self._log_activity(
            user_id, "update", "dataset", dataset_id, json.dumps(formatted_diff)
        )

    def log_dataset_status_change(
        self, user_id: int, dataset_id: int, old_status: str, new_status: str
    ) -> None:
        formatted_diff = [
            {
                "field": "status",
                "change_type": "status_change",
                "old_value": old_status,
                "new_value": new_status,
            }
        ]

        self._log_activity(
            user_id, "update", "dataset", dataset_id, json.dumps(formatted_diff)
        )

    def log_external_dataset_import(
        self,
        user_id: int,
        dataset_id: int,
        source_instance: str,
        source_dataset_id: int,
        outcome: str = "success",
        error_message: str | None = None,
    ) -> None:
        formatted_diff = [
            {
                "field": "import",
                "change_type": "external_import",
                "source_instance": source_instance,
                "source_dataset_id": source_dataset_id,
                "outcome": outcome,
                "error_message": error_message,
            }
        ]

        self._log_activity(
            user_id, "create", "dataset", dataset_id, json.dumps(formatted_diff)
        )

    def log_external_status_sync(
        self,
        user_id: int,
        dataset_id: int,
        source_instance: str,
        source_dataset_id: int,
        old_status: str,
        new_status: str,
    ) -> None:
        formatted_diff = [
            {
                "field": "status",
                "change_type": "external_status_sync",
                "source_instance": source_instance,
                "source_dataset_id": source_dataset_id,
                "old_value": old_status,
                "new_value": new_status,
            }
        ]

        self._log_activity(
            user_id, "update", "dataset", dataset_id, json.dumps(formatted_diff)
        )

    def get_activity_logs_from_dataset(
        self, dataset_id: int, page: int, page_size: int
    ) -> List[ResourceActivityLog]:
        activity_logs = self._repository.get_activity_logs_from_dataset(
            dataset_id, page, page_size
        )
        return [activity_log_entity_to_resource(it) for it in activity_logs]
