from typing import Dict, List, Any
from deepdiff import DeepDiff
import json


class DistributionDiff:
    @staticmethod
    def _collection_to_string(collection: List[Any]) -> str:
        if not collection:
            return ""
        sorted_collection = sorted(str(item) for item in collection)
        return ", ".join(sorted_collection)

    @staticmethod
    def _preprocess_distribution_for_diff(
        distribution: Dict[str, Any],
    ) -> Dict[str, Any]:
        processed = distribution.copy()

        if "languages" in processed:
            processed["languages"] = DistributionDiff._collection_to_string(
                processed["languages"]
            )
        if "applicable_legislations" in processed:
            processed["applicable_legislations"] = (
                DistributionDiff._collection_to_string(
                    processed["applicable_legislations"]
                )
            )
        if "linked_schemas" in processed:
            processed["linked_schemas"] = DistributionDiff._collection_to_string(
                processed["linked_schemas"]
            )
        if "access_service_ids" in processed:
            processed["access_service_ids"] = DistributionDiff._collection_to_string(
                processed["access_service_ids"]
            )
        if "access_urls" in processed:
            processed["access_urls"] = DistributionDiff._collection_to_string(
                processed["access_urls"]
            )
        if "download_urls" in processed:
            processed["download_urls"] = DistributionDiff._collection_to_string(
                processed["download_urls"]
            )
        if "policy_actions" in processed and isinstance(
            processed["policy_actions"], list
        ):
            normalized_actions = []
            for action in processed["policy_actions"]:
                if not isinstance(action, dict):
                    normalized_actions.append(action)
                    continue
                action_copy = action.copy()
                if "spatial_restrictions" in action_copy:
                    if action_copy["spatial_restrictions"] is None:
                        action_copy["spatial_restrictions"] = ""
                    elif isinstance(action_copy["spatial_restrictions"], list):
                        action_copy["spatial_restrictions"] = (
                            DistributionDiff._collection_to_string(
                                action_copy["spatial_restrictions"]
                            )
                        )
                normalized_actions.append(action_copy)
            processed["policy_actions"] = normalized_actions

        return processed

    @staticmethod
    def compute(original_data: Dict[str, Any], updated_data: Dict[str, Any]) -> str:
        original_data_processed = DistributionDiff._preprocess_distribution_for_diff(
            original_data
        )
        updated_data_processed = DistributionDiff._preprocess_distribution_for_diff(
            updated_data
        )

        diff = DeepDiff(
            original_data_processed,
            updated_data_processed,
            ignore_order=True,
        )

        return DistributionDiff._format_diff(diff.to_dict())

    @staticmethod
    def _format_diff(diff: Dict[str, Any]) -> str:
        formatted_diff: List[Dict[str, Any]] = []

        def build_field_from_key(key: str) -> str:
            return (
                key.replace("']['", ".")
                .replace("root['", "")
                .replace("']", "")
                .replace("['", ".")
            )

        def process_diff_dict(diff_dict: Dict[str, Any], change_type: str) -> None:
            if isinstance(diff_dict, dict):
                for key, value in diff_dict.items():
                    if (
                        isinstance(value, dict)
                        and "new_value" in value
                        and "old_value" in value
                    ):
                        formatted_change = {
                            "field": build_field_from_key(key),
                            "old_value": value["old_value"],
                            "new_value": value["new_value"],
                            "change_type": change_type,
                        }
                        formatted_diff.append(formatted_change)
                    elif change_type in [
                        "iterable_item_added",
                        "iterable_item_removed",
                    ]:
                        formatted_change = {
                            "field": build_field_from_key(key),
                            "old_value": (
                                None if change_type == "iterable_item_added" else value
                            ),
                            "new_value": (
                                value if change_type == "iterable_item_added" else None
                            ),
                            "change_type": change_type,
                        }
                        formatted_diff.append(formatted_change)
            elif change_type in ["dictionary_item_added", "dictionary_item_removed"]:
                for path in diff_dict:
                    field = build_field_from_key(path)
                    formatted_change = {
                        "field": field,
                        "change_type": change_type,
                        "old_value": (
                            None
                            if change_type == "dictionary_item_added"
                            else "Item was removed"
                        ),
                        "new_value": (
                            "Item was added"
                            if change_type == "dictionary_item_added"
                            else None
                        ),
                    }
                    formatted_diff.append(formatted_change)

        for change_type, diff_dict in diff.items():
            process_diff_dict(diff_dict, change_type)

        return json.dumps(formatted_diff)
