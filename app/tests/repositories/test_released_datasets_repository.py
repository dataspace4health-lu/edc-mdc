from datetime import datetime, timezone

import pytest
from models.dataset import Dataset, DatasetStatus
from models.organisation import Organisation
from repositories.dataset import DatasetRepository
from sqlalchemy.orm import Session
from test_factory import sample_dataset


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    yield
    db_session.query(Dataset).delete()
    db_session.commit()


@pytest.fixture
def dataset_repository(db_session: Session) -> DatasetRepository:
    return DatasetRepository(db_session)


def test_get_released_datasets_paginated(
    dataset_repository: DatasetRepository, db_session: Session, sample_dataset: Dataset
):
    # Set accessible_within_ctie to False on the publisher
    publisher = (
        db_session.query(Organisation)
        .filter(Organisation.id == sample_dataset.publisher_id)
        .first()
    )
    publisher.accessible_within_ctie = False

    # Set released_at on the sample dataset
    sample_dataset.released_at = datetime.now(timezone.utc)
    sample_dataset.status = DatasetStatus.PUBLISHED.value
    db_session.add(sample_dataset)
    db_session.commit()

    # Get released datasets
    datasets, total_count = dataset_repository.get_released_datasets_paginated(
        page=1, page_size=10
    )

    assert total_count == 1
    assert len(datasets) == 1
    assert datasets[0].id == sample_dataset.id
    assert datasets[0].released_at is not None


def test_get_released_datasets_excludes_unreleased(
    dataset_repository: DatasetRepository, db_session: Session, sample_dataset: Dataset
):
    # Set accessible_within_ctie to False on the publisher
    publisher = (
        db_session.query(Organisation)
        .filter(Organisation.id == sample_dataset.publisher_id)
        .first()
    )
    publisher.accessible_within_ctie = False

    # Keep released_at as None (default)
    sample_dataset.released_at = None
    sample_dataset.status = DatasetStatus.DRAFT.value
    db_session.add(sample_dataset)
    db_session.commit()

    # Get released datasets
    datasets, total_count = dataset_repository.get_released_datasets_paginated(
        page=1, page_size=10
    )

    assert total_count == 0
    assert len(datasets) == 0
