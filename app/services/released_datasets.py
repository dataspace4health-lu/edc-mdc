from typing import Annotated
from fastapi import Depends
from repositories.dataset import DatasetRepository
from schemas.released_datasets import (
    ReleasedDatasetItem,
    PaginatedReleasedDatasetsResponse,
    PaginationMeta,
)


class ReleasedDatasetsService:
    def __init__(
        self,
        dataset_repository: Annotated[DatasetRepository, Depends(DatasetRepository)],
    ):
        self._dataset_repository = dataset_repository

    def get_released_datasets(
        self, page: int, page_size: int
    ) -> PaginatedReleasedDatasetsResponse:
        datasets, total_count = (
            self._dataset_repository.get_released_datasets_paginated(
                page=page,
                page_size=page_size,
            )
        )

        dataset_items = [
            ReleasedDatasetItem(
                id=dataset.id,
                identifier=dataset.identifier,
                status=dataset.status,
                released_at=(
                    dataset.released_at.isoformat() if dataset.released_at else None
                ),
                previous_version_dataset_id=dataset.previous_version_dataset_id,
                version_change_type=dataset.version_change_type,
            )
            for dataset in datasets
        ]

        total_pages = (
            (total_count + page_size - 1) // page_size if total_count > 0 else 1
        )

        return PaginatedReleasedDatasetsResponse(
            items=dataset_items,
            meta=PaginationMeta(
                total_items=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
            ),
        )
