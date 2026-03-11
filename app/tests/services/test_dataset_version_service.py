from datetime import UTC, datetime
from unittest.mock import MagicMock
from services.dataset_version import DatasetVersionService


def test_get_latest_version_dataset_id_returns_none_for_latest_dataset():
    service = DatasetVersionService()
    dataset = MagicMock()
    dataset.id = 1
    dataset.versions = []  # No newer versions

    result = service.get_latest_version_dataset_id(dataset)

    assert result is None


def test_get_latest_version_dataset_id_returns_latest_version_id():
    service = DatasetVersionService()

    # Create a chain: dataset_A -> dataset_B -> dataset_C (where C is the latest)
    dataset_A = MagicMock()
    dataset_A.id = 1
    dataset_A.submitted_at = datetime(2023, 1, 1, tzinfo=UTC)

    dataset_B = MagicMock()
    dataset_B.id = 2
    dataset_B.submitted_at = datetime(2023, 2, 1, tzinfo=UTC)
    dataset_B.versions = []  # No newer versions, this is the latest

    dataset_C = MagicMock()
    dataset_C.id = 3
    dataset_C.submitted_at = datetime(2023, 3, 1, tzinfo=UTC)
    dataset_C.versions = []  # No newer versions, this is the latest

    # Dataset A has B as newer version
    dataset_A.versions = [dataset_B]

    # Dataset B has C as newer version
    dataset_B.versions = [dataset_C]

    result = service.get_latest_version_dataset_id(dataset_A)

    assert result == 3


def test_get_latest_version_dataset_id_handles_single_version_chain():
    service = DatasetVersionService()

    dataset_A = MagicMock()
    dataset_A.id = 1
    dataset_A.submitted_at = datetime(2023, 1, 1, tzinfo=UTC)

    dataset_B = MagicMock()
    dataset_B.id = 2
    dataset_B.submitted_at = datetime(2023, 2, 1, tzinfo=UTC)
    dataset_B.versions = []  # No newer versions

    dataset_A.versions = [dataset_B]

    result = service.get_latest_version_dataset_id(dataset_A)

    assert result == 2


def test_get_latest_version_dataset_id_prevents_infinite_loop():
    service = DatasetVersionService()

    dataset_A = MagicMock()
    dataset_A.id = 1
    dataset_A.submitted_at = datetime(2023, 1, 1, tzinfo=UTC)

    dataset_B = MagicMock()
    dataset_B.id = 2
    dataset_B.submitted_at = datetime(2023, 2, 1, tzinfo=UTC)

    # Create circular reference (shouldn't happen in real data, but test safety)
    dataset_A.versions = [dataset_B]
    dataset_B.versions = [dataset_A]

    result = service.get_latest_version_dataset_id(dataset_A)

    # Should stop at B since A is already processed
    assert result == 2


def test_get_latest_version_dataset_id_chooses_most_recent_when_multiple_versions():
    service = DatasetVersionService()

    dataset_A = MagicMock()
    dataset_A.id = 1
    dataset_A.submitted_at = datetime(2023, 1, 1, tzinfo=UTC)

    dataset_B = MagicMock()
    dataset_B.id = 2
    dataset_B.submitted_at = datetime(2023, 2, 1, tzinfo=UTC)  # Earlier
    dataset_B.versions = []

    dataset_C = MagicMock()
    dataset_C.id = 3
    dataset_C.submitted_at = datetime(2023, 3, 1, tzinfo=UTC)  # Later
    dataset_C.versions = []

    # Dataset A has both B and C as newer versions (unusual but possible)
    dataset_A.versions = [dataset_B, dataset_C]

    result = service.get_latest_version_dataset_id(dataset_A)

    # Should choose C (id=3) since it has a later submitted_at time
    assert result == 3
