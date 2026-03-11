from typing import Dict, List, Any, Optional
from deepdiff import DeepDiff
import json


class DatasetDiff:
    @staticmethod
    def _preprocess_dataset_for_diff(dataset: Dict[str, Any]) -> Dict[str, Any]:
        processed_dataset = dataset.copy()
        # Distributions are managed separately and should not be part of dataset activity logs.
        processed_dataset.pop("distributions", None)
        if "dataset_types" in processed_dataset:
            processed_dataset["dataset_types"] = DatasetDiff._collection_to_string(
                processed_dataset["dataset_types"]
            )
        if "themes" in processed_dataset:
            processed_dataset["themes"] = DatasetDiff._collection_to_string(
                processed_dataset["themes"]
            )
        if "keywords" in processed_dataset:
            processed_dataset["keywords"] = DatasetDiff._collection_to_string(
                processed_dataset["keywords"]
            )
        if "health_categories" in processed_dataset:
            processed_dataset["health_categories"] = DatasetDiff._collection_to_string(
                processed_dataset["health_categories"]
            )
        if "health_themes" in processed_dataset:
            processed_dataset["health_themes"] = DatasetDiff._collection_to_string(
                processed_dataset["health_themes"]
            )
        if "spatial_coverages" in processed_dataset:
            processed_dataset["spatial_coverages"] = DatasetDiff._collection_to_string(
                processed_dataset["spatial_coverages"]
            )
        if "spatial_resolutions" in processed_dataset:
            # Normalize None to empty string to match empty list behavior
            if processed_dataset["spatial_resolutions"] is None:
                processed_dataset["spatial_resolutions"] = ""
            elif isinstance(
                processed_dataset["spatial_resolutions"], (list, set, frozenset)
            ):
                sorted_sr = sorted(map(str, processed_dataset["spatial_resolutions"]))
                processed_dataset["spatial_resolutions"] = ", ".join(sorted_sr)
        if "conventions" in processed_dataset:
            processed_dataset["conventions"] = DatasetDiff._collection_to_string(
                processed_dataset["conventions"]
            )
        if "areas_of_work" in processed_dataset:
            processed_dataset["areas_of_work"] = DatasetDiff._collection_to_string(
                processed_dataset["areas_of_work"]
            )
        if "areas_of_competence" in processed_dataset:
            processed_dataset["areas_of_competence"] = (
                DatasetDiff._collection_to_string(
                    processed_dataset["areas_of_competence"]
                )
            )
        if "applicable_legislations" in processed_dataset:
            processed_dataset["applicable_legislations"] = (
                DatasetDiff._collection_to_string(
                    processed_dataset["applicable_legislations"]
                )
            )
        if "data_protection_types" in processed_dataset:
            processed_dataset["data_protection_types"] = (
                DatasetDiff._collection_to_string(
                    processed_dataset["data_protection_types"]
                )
            )
        if "group_managers" in processed_dataset and isinstance(
            processed_dataset["group_managers"], list
        ):
            sorted_group_managers = sorted(
                map(str, processed_dataset["group_managers"])
            )
            processed_dataset["group_managers"] = ", ".join(sorted_group_managers)
        if "creator_ids" in processed_dataset and isinstance(
            processed_dataset["creator_ids"], list
        ):
            sorted_creator_ids = sorted(map(str, processed_dataset["creator_ids"]))
            processed_dataset["creator_ids"] = ", ".join(sorted_creator_ids)
        if "contact_ids" in processed_dataset:
            # Normalize None to empty string to match empty list behavior
            if processed_dataset["contact_ids"] is None:
                processed_dataset["contact_ids"] = ""
            elif isinstance(processed_dataset["contact_ids"], (list, set)):
                sorted_contact_ids = sorted(map(str, processed_dataset["contact_ids"]))
                processed_dataset["contact_ids"] = ", ".join(sorted_contact_ids)
        if "was_generated_by" in processed_dataset:
            processed_dataset["was_generated_by"] = DatasetDiff._collection_to_string(
                processed_dataset["was_generated_by"]
            )
        if "other_identifiers" in processed_dataset:
            processed_dataset["other_identifiers"] = DatasetDiff._collection_to_string(
                processed_dataset["other_identifiers"]
            )
        if "landing_pages" in processed_dataset:
            processed_dataset["landing_pages"] = DatasetDiff._collection_to_string(
                processed_dataset["landing_pages"]
            )
        if "documentation" in processed_dataset:
            processed_dataset["documentation"] = DatasetDiff._collection_to_string(
                processed_dataset["documentation"]
            )
        if "purpose" in processed_dataset:
            processed_dataset["purpose"] = DatasetDiff._collection_to_string(
                processed_dataset["purpose"]
            )
        if "code_values" in processed_dataset:
            processed_dataset["code_values"] = DatasetDiff._collection_to_string(
                processed_dataset["code_values"]
            )
        if "coding_systems" in processed_dataset:
            processed_dataset["coding_systems"] = DatasetDiff._collection_to_string(
                processed_dataset["coding_systems"]
            )
        if "languages" in processed_dataset:
            processed_dataset["languages"] = DatasetDiff._collection_to_string(
                processed_dataset["languages"]
            )
        if "conforms_to" in processed_dataset:
            if processed_dataset["conforms_to"] is None:
                processed_dataset["conforms_to"] = ""
            elif isinstance(processed_dataset["conforms_to"], (list, set)):
                processed_dataset["conforms_to"] = DatasetDiff._collection_to_string(
                    processed_dataset["conforms_to"]
                )
        if "provenance" in processed_dataset:
            if processed_dataset["provenance"] is None:
                processed_dataset["provenance"] = ""
            elif isinstance(processed_dataset["provenance"], (list, set)):
                processed_dataset["provenance"] = DatasetDiff._collection_to_string(
                    processed_dataset["provenance"]
                )
        if "health_legal_basis" in processed_dataset:
            if processed_dataset["health_legal_basis"] is None:
                processed_dataset["health_legal_basis"] = ""
            elif isinstance(processed_dataset["health_legal_basis"], (list, set)):
                processed_dataset["health_legal_basis"] = (
                    DatasetDiff._collection_to_string(
                        processed_dataset["health_legal_basis"]
                    )
                )
        if "version_notes" in processed_dataset:
            if processed_dataset["version_notes"] is None:
                processed_dataset["version_notes"] = ""
            elif isinstance(processed_dataset["version_notes"], (list, set)):
                processed_dataset["version_notes"] = DatasetDiff._collection_to_string(
                    processed_dataset["version_notes"]
                )
        if "member_datasets" in processed_dataset and isinstance(
            processed_dataset["member_datasets"], list
        ):
            member_datasets = sorted(map(str, processed_dataset["member_datasets"]))
            if len(member_datasets) > 0:
                processed_dataset["member_datasets"] = ", ".join(member_datasets)
            else:
                processed_dataset["member_datasets"] = None
        if "personal_data" in processed_dataset:
            processed_dataset["personal_data"] = DatasetDiff._collection_to_string(
                processed_dataset["personal_data"]
            )

        return processed_dataset

    @staticmethod
    def _collection_to_string(collection: List[str]) -> str:
        if not collection:
            return ""
        sorted_collection = sorted(str(item) for item in collection)
        return ", ".join(sorted_collection)

    @staticmethod
    def compute(original_data: Dict[str, Any], updated_data: Dict[str, Any]) -> str:
        original_data_processed = DatasetDiff._preprocess_dataset_for_diff(
            original_data
        )
        updated_data_processed = DatasetDiff._preprocess_dataset_for_diff(updated_data)

        # Exclude internal tracking fields that are not user-editable
        diff = DeepDiff(
            original_data_processed,
            updated_data_processed,
            ignore_order=True,
            exclude_paths=[
                "root['source']",
                "root['source_dataset_id']",
                "root['version_change_type']",
            ],
        )

        return DatasetDiff._format_diff(
            diff.to_dict(), original_data_processed, updated_data_processed
        )

    @staticmethod
    def _format_diff(
        diff: Dict[str, Any],
        original_data: Dict[str, Any],
        updated_data: Dict[str, Any],
    ) -> str:
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
            elif change_type in ["dictionary_item_added", "dictionary_item_removed"]:
                for path in diff_dict:
                    field = build_field_from_key(path)
                    # Skip if we couldn't extract a distribution title or if this isn't a distribution field
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
