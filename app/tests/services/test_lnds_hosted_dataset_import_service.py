import pytest
from unittest.mock import Mock, patch
from models.dataset import Dataset
from repositories.dataset import DatasetRepository
from services.catalogues.importers.dataset_rdf_import_service import (
    DatasetRDFImportService,
)
from services.database_session_manager import DatabaseSessionManager
from services.activity_logs.dataset_activity_log import DatasetActivityLogService
from services.lnds_hosted_dataset_import_service import LNDSHostedDatasetImportService


@pytest.fixture
def mock_dependencies():
    return {
        "dataset_repository": Mock(spec=DatasetRepository),
        "dataset_rdf_import_service": Mock(spec=DatasetRDFImportService),
        "database_session_manager": Mock(spec=DatabaseSessionManager),
        "dataset_activity_log_service": Mock(spec=DatasetActivityLogService),
        "user_service": Mock(),
        "config_service": Mock(),
    }


@pytest.fixture
def sync_service(mock_dependencies):
    with patch("services.lnds_hosted_dataset_import_service.httpx.Client"), patch.dict(
        "os.environ",
        {
            "SOURCE_OIDC_ISSUER_URL": "https://issuer.example.com",
            "SOURCE_SERVICE_ACCOUNT_CLIENT_ID": "test-client",
            "SOURCE_SERVICE_ACCOUNT_CLIENT_SECRET": "test-secret",
        },
    ):
        # Mock user service to return a user with ID 1
        mock_user = Mock()
        mock_user.id = 1
        mock_dependencies["user_service"].create_or_find.return_value = mock_user

        service = LNDSHostedDatasetImportService(
            dataset_repository=mock_dependencies["dataset_repository"],
            dataset_rdf_import_service=mock_dependencies["dataset_rdf_import_service"],
            database_session_manager=mock_dependencies["database_session_manager"],
            dataset_activity_log_service=mock_dependencies[
                "dataset_activity_log_service"
            ],
            user_service=mock_dependencies["user_service"],
            config_service=mock_dependencies["config_service"],
            source_instance_url="http://test-source:8000",
            source_instance_name="test-instance",
            page_size=2,
        )
        # Mock the token acquisition
        service._access_token = "fake-token"
        service._service_account_user_id = 1
        yield service


def test_sync_creates_new_dataset(sync_service, mock_dependencies):
    """Test that sync creates a new dataset when it doesn't exist locally"""
    # Mock HTTP response for released datasets
    sync_service._http_client.get.return_value.json.return_value = {
        "items": [
            {
                "id": 100,
                "identifier": "test-dataset-uuid",
                "status": "PUBLISHED",
                "released_at": "2024-01-01T12:00:00+00:00",
                "previous_version_dataset_id": None,
                "version_change_type": "UNDERLYING_DATA",
            }
        ]
    }
    sync_service._http_client.get.return_value.raise_for_status = Mock()

    # Mock repository: dataset doesn't exist for source check
    mock_dependencies["dataset_repository"].get_dataset_by_source.return_value = None

    # Mock RDF download
    sync_service._http_client.get.return_value.text = "<rdf>fake</rdf>"

    # Mock import service - create a simple object to allow attribute assignment
    class ImportedDataset:
        def __init__(self):
            self.id = 1
            self.source = None
            self.source_dataset_id = None
            self.status = "PUBLISHED"
            self.released_at = None

    imported_dataset = ImportedDataset()
    imported_dataset_resource = (
        ImportedDataset()
    )  # The resource returned by import_dataset
    imported_dataset_resource.id = 1

    mock_dependencies["dataset_rdf_import_service"].import_dataset.return_value = (
        imported_dataset_resource
    )
    # Mock get_dataset to return the actual dataset object that will be modified
    mock_dependencies["dataset_repository"].get_dataset.return_value = imported_dataset

    # Run sync (max 1 page)
    stats = sync_service.import_released_datasets(max_pages=1)

    # Assertions
    assert stats["processed"] == 1
    assert stats["created"] == 1
    assert stats["updated"] == 0
    assert stats["failed"] == 0

    # Verify import was called with source parameters
    mock_dependencies["dataset_rdf_import_service"].import_dataset.assert_called_once()
    import_call = mock_dependencies[
        "dataset_rdf_import_service"
    ].import_dataset.call_args
    assert import_call.kwargs["target_status"] == "PUBLISHED"
    assert import_call.kwargs["target_version_change_type"] == "UNDERLYING_DATA"
    assert import_call.kwargs["source"] == "test-instance"
    assert import_call.kwargs["source_dataset_id"] == 100


def test_sync_updates_existing_dataset_status(sync_service, mock_dependencies):
    """Test that sync updates status when dataset exists with different status"""
    # Mock HTTP response
    sync_service._http_client.get.return_value.json.return_value = {
        "items": [
            {
                "id": 100,
                "identifier": "test-dataset-uuid",
                "status": "DEPRECATED",
                "released_at": "2024-01-01T12:00:00+00:00",
                "previous_version_dataset_id": None,
            }
        ]
    }
    sync_service._http_client.get.return_value.raise_for_status = Mock()

    # Mock repository: dataset exists with different status
    existing_dataset = Mock(spec=Dataset)
    existing_dataset.id = 5
    existing_dataset.status = "PUBLISHED"
    mock_dependencies["dataset_repository"].get_dataset_by_source.return_value = (
        existing_dataset
    )

    # Mock the front office push task
    with patch(
        "jobs.tasks.push_to_front_office.push_dataset_to_front_office_task"
    ) as mock_push_task:
        # Run sync
        stats = sync_service.import_released_datasets(max_pages=1)

        # Assertions
        assert stats["processed"] == 1
        assert stats["created"] == 0
        assert stats["updated"] == 1
        assert stats["failed"] == 0

        # Verify status was updated
        assert existing_dataset.status == "DEPRECATED"
        mock_dependencies["dataset_repository"].merge.assert_called_once_with(
            existing_dataset
        )
        # Two commits: one in _update_dataset_status() and one at end of import_released_datasets()
        assert mock_dependencies["database_session_manager"].commit.call_count == 2

        # Verify front office push was triggered for status update
        mock_push_task.delay.assert_called_once_with(5)


def test_sync_links_previous_version(sync_service, mock_dependencies):
    """Test that sync correctly links to previous version when importing"""
    # Mock HTTP response with previous_version_dataset_id
    sync_service._http_client.get.return_value.json.return_value = {
        "items": [
            {
                "id": 200,
                "identifier": "test-dataset-v2-uuid",
                "status": "PUBLISHED",
                "released_at": "2024-01-15T12:00:00+00:00",
                "previous_version_dataset_id": 100,
            }
        ]
    }
    sync_service._http_client.get.return_value.raise_for_status = Mock()

    # Mock repository responses
    # First call: new dataset doesn't exist (for version 2)
    # Second call: previous version exists (for version 1)
    previous_version = Mock(spec=Dataset)
    previous_version.id = 10  # Local ID of version 1
    mock_dependencies["dataset_repository"].get_dataset_by_source.side_effect = [
        None,  # New dataset doesn't exist
        previous_version,  # Previous version found
    ]

    # Mock RDF download
    sync_service._http_client.get.return_value.text = "<rdf>fake</rdf>"

    # Mock import service - create a simple object to allow attribute assignment
    class ImportedDataset:
        def __init__(self):
            self.id = 20
            self.source = None
            self.source_dataset_id = None
            self.previous_version_dataset_id = None
            self.status = "PUBLISHED"
            self.released_at = None

    imported_dataset = ImportedDataset()
    imported_dataset_resource = (
        ImportedDataset()
    )  # The resource returned by import_dataset
    imported_dataset_resource.id = 20

    mock_dependencies["dataset_rdf_import_service"].import_dataset.return_value = (
        imported_dataset_resource
    )
    # Mock get_dataset to return the actual dataset object that will be modified
    mock_dependencies["dataset_repository"].get_dataset.return_value = imported_dataset

    # Run sync
    stats = sync_service.import_released_datasets(max_pages=1)

    # Assertions
    assert stats["processed"] == 1
    assert stats["created"] == 1

    # Verify import was called with source parameters
    import_call = mock_dependencies[
        "dataset_rdf_import_service"
    ].import_dataset.call_args
    assert import_call.kwargs["target_status"] == "PUBLISHED"
    assert import_call.kwargs["source"] == "test-instance"
    assert import_call.kwargs["source_dataset_id"] == 200

    # Verify version linking (still done after import)
    assert imported_dataset.previous_version_dataset_id == 10


def test_sync_handles_pagination(sync_service, mock_dependencies):
    """Test that sync correctly handles multiple pages"""

    # Mock HTTP responses - page 1 has 2 items, page 2 has 1 item (last page)
    def mock_get_response(*args, **kwargs):
        url = args[0] if args else kwargs.get("url", "")
        params = kwargs.get("params", {})
        page = params.get("page", 1)

        mock_response = Mock()
        mock_response.raise_for_status = Mock()

        if "released-datasets" in url and page == 1:
            mock_response.json.return_value = {
                "items": [
                    {
                        "id": 100,
                        "identifier": "dataset-1",
                        "status": "PUBLISHED",
                        "released_at": "2024-01-01T12:00:00+00:00",
                        "previous_version_dataset_id": None,
                    },
                    {
                        "id": 101,
                        "identifier": "dataset-2",
                        "status": "PUBLISHED",
                        "released_at": "2024-01-02T12:00:00+00:00",
                        "previous_version_dataset_id": None,
                    },
                ]
            }
        elif "released-datasets" in url and page == 2:
            mock_response.json.return_value = {
                "items": [
                    {
                        "id": 102,
                        "identifier": "dataset-3",
                        "status": "PUBLISHED",
                        "released_at": "2024-01-03T12:00:00+00:00",
                        "previous_version_dataset_id": None,
                    }
                ]
            }
        else:
            # RDF download response
            mock_response.text = "<rdf>fake</rdf>"

        return mock_response

    sync_service._http_client.get.side_effect = mock_get_response

    # Mock repository: all datasets are new
    mock_dependencies["dataset_repository"].get_dataset_by_source.return_value = None

    # Mock import service
    def create_mock_dataset():
        dataset = Mock()
        dataset.id = Mock()
        return dataset

    mock_dependencies["dataset_rdf_import_service"].import_dataset.side_effect = (
        lambda **kwargs: create_mock_dataset()
    )

    # Run sync (no max_pages, should process all pages)
    stats = sync_service.import_released_datasets()

    # Assertions
    assert stats["processed"] == 3
    assert stats["created"] == 3
    assert stats["updated"] == 0
    assert stats["failed"] == 0


def test_sync_enqueues_push_to_front_office_after_import(
    sync_service, mock_dependencies
):
    """After each successful dataset import, enqueue a background push to front office task"""
    sync_service._http_client.get.return_value.json.return_value = {
        "items": [
            {
                "id": 100,
                "identifier": "dataset-1",
                "status": "PUBLISHED",
                "previous_version_dataset_id": None,
            },
            {
                "id": 200,
                "identifier": "dataset-2",
                "status": "APPROVED",
                "released_at": "2024-01-01T12:00:00+00:00",
                "previous_version_dataset_id": None,
            },
            {
                "id": 300,
                "identifier": "dataset-3",
                "status": "DEPRECATED",
                "previous_version_dataset_id": None,
            },
        ]
    }
    sync_service._http_client.get.return_value.raise_for_status = Mock()
    sync_service._http_client.get.return_value.text = "<rdf>fake</rdf>"

    mock_dependencies["dataset_repository"].get_dataset_by_source.return_value = None

    def create_mock_dataset():
        dataset = Mock()
        dataset.id = Mock()
        return dataset

    mock_dependencies["dataset_rdf_import_service"].import_dataset.side_effect = (
        lambda **kwargs: create_mock_dataset()
    )
    mock_dependencies["dataset_repository"].get_dataset.side_effect = lambda id: Mock(
        id=id
    )

    with patch(
        "jobs.tasks.push_to_front_office.push_dataset_to_front_office_task"
    ) as mock_task:
        stats = sync_service.import_released_datasets(max_pages=1)

    assert stats["processed"] == 3
    assert stats["created"] == 3
    assert stats["updated"] == 0
    assert stats["failed"] == 0

    assert mock_task.delay.call_count == 3
