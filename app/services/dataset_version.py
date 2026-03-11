from typing import Optional
from models.dataset import Dataset


class DatasetVersionService:
    def get_latest_version_dataset_id(self, dataset: Dataset) -> Optional[int]:
        if not dataset.versions:  # No newer versions, this is the latest
            return None

        # Start from current dataset and traverse newer versions to find the latest
        latest_dataset = dataset
        processed_ids = {dataset.id}  # Prevent infinite loops

        while latest_dataset.versions:
            # Get the next version (there should only be one direct child in the chain)
            next_versions = [
                v for v in latest_dataset.versions if v.id not in processed_ids
            ]
            if not next_versions:
                break

            # In a proper version chain, there should be only one next version
            # If there are multiple, take the most recent one
            next_dataset = max(next_versions, key=lambda v: v.submitted_at)
            processed_ids.add(next_dataset.id)
            latest_dataset = next_dataset

        # Return the latest version ID only if it's different from the current dataset
        return latest_dataset.id if latest_dataset.id != dataset.id else None
