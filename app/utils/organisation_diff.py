from typing import Dict, Any, List
from deepdiff import DeepDiff
import json


class OrganisationDiff:
    @staticmethod
    def _preprocess_organisation_for_diff(
        organisation: Dict[str, Any],
    ) -> Dict[str, Any]:
        processed_organisation = organisation.copy()
        return processed_organisation

    @staticmethod
    def compute(original_data: Dict[str, Any], updated_data: Dict[str, Any]) -> str:
        original_data_processed = OrganisationDiff._preprocess_organisation_for_diff(
            original_data
        )
        updated_data_processed = OrganisationDiff._preprocess_organisation_for_diff(
            updated_data
        )

        try:
            diff = DeepDiff(
                original_data_processed, updated_data_processed, ignore_order=True
            )
        except Exception as e:
            print(f"Error computing diff: {str(e)}")
            return json.dumps([])

        return OrganisationDiff._format_diff(diff)

    @staticmethod
    def _format_diff(diff: Dict[str, Any]) -> str:
        formatted_diff = []

        def build_field_from_key(key: str) -> str:
            return key.replace("']['", ".").replace("root['", "").replace("']", "")

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
                    elif isinstance(value, list):
                        for index, item in enumerate(value):
                            if (
                                isinstance(item, dict)
                                and "new_value" in item
                                and "old_value" in item
                            ):
                                formatted_change = {
                                    "field": f"{build_field_from_key(key)}[{index}]",
                                    "old_value": item["old_value"],
                                    "new_value": item["new_value"],
                                    "change_type": change_type,
                                }
                                formatted_diff.append(formatted_change)

        for change_type, diff_dict in diff.items():
            process_diff_dict(diff_dict, change_type)

        return json.dumps(formatted_diff)
