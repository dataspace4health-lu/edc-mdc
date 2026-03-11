from datetime import datetime, timezone

import pytest
from unittest.mock import Mock
from repositories.dataset import DatasetRepository
from services.released_datasets import ReleasedDatasetsService
from schemas.released_datasets import PaginatedReleasedDatasetsResponse
from test_factory import sample_dataset
from models.dataset import DatasetStatus, DatasetVersionChangeType


@pytest.fixture
def released_datasets_service() -> ReleasedDatasetsService:
    return ReleasedDatasetsService(
        dataset_repository=Mock(spec=DatasetRepository),
    )


def test_get_released_datasets(
    released_datasets_service: ReleasedDatasetsService,
    sample_dataset,
):
    # Set released_at on sample dataset
    sample_dataset.released_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    sample_dataset.status = DatasetStatus.PUBLISHED.value
    sample_dataset.version_change_type = DatasetVersionChangeType.METADATA_ONLY.value

    # Mock repository response
    released_datasets_service._dataset_repository.get_released_datasets_paginated.return_value = (
        [sample_dataset],
        1,
    )

    # Call service
    result = released_datasets_service.get_released_datasets(page=1, page_size=10)

    # Assertions
    assert isinstance(result, PaginatedReleasedDatasetsResponse)
    assert len(result.items) == 1
    assert result.meta.total_items == 1
    assert result.meta.page == 1
    assert result.meta.page_size == 10
    assert result.meta.total_pages == 1

    # Check returned item
    assert result.items[0].id == sample_dataset.id
    assert result.items[0].identifier == sample_dataset.identifier
    assert result.items[0].status == DatasetStatus.PUBLISHED.value
    assert result.items[0].released_at == "2024-01-01T12:00:00+00:00"
    assert (
        result.items[0].version_change_type
        == DatasetVersionChangeType.METADATA_ONLY.value
    )
