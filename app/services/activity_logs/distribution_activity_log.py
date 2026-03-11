import json
from typing import Dict, Any, Optional
from services.activity_log import ActivityLogService
from utils.distribution_diff import DistributionDiff


class DistributionActivityLogService(ActivityLogService):
    def get_entity_type(self) -> str:
        return "dataset"

    def log_distribution_created(
        self,
        user_id: int,
        dataset_id: int,
        distribution_id: int,
        distribution_title: str | None = None,
    ) -> None:
        distribution_data = {
            "dataset_id": dataset_id,
            "distribution_id": distribution_id,
            "distribution_title": distribution_title,
        }

        changes = [
            {
                "field": "distribution",
                "old_value": None,
                "new_value": distribution_data,
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

    def log_distribution_updated(
        self,
        user_id: int,
        dataset_id: int,
        old_distribution: Dict[str, Any],
        new_distribution: Dict[str, Any],
        distribution_title: Optional[str] = None,
    ) -> None:
        diff = DistributionDiff.compute(old_distribution, new_distribution)
        changes = json.loads(diff)
        if not changes:
            return

        if distribution_title:
            for change in changes:
                change["field"] = (
                    f"distributions.{distribution_title}.{change['field']}"
                )

        self._log_activity(
            user_id,
            "update",
            "dataset",
            dataset_id,
            json.dumps(changes),
        )

    def log_distribution_deleted(
        self,
        user_id: int,
        dataset_id: int,
        distribution_id: int,
        distribution_title: str | None = None,
    ) -> None:
        distribution_data = {
            "dataset_id": dataset_id,
            "distribution_id": distribution_id,
            "distribution_title": distribution_title,
        }

        changes = [
            {
                "field": "distribution",
                "old_value": distribution_data,
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
