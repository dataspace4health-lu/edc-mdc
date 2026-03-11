from models.dataset import (
    Dataset,
    DatasetVersionNote,
    DatasetStatus,
    DatasetGroupManagers,
    DatasetVersionChangeType,
)
from models.identity_context import IdentityContext
from fastapi import HTTPException
from unittest.mock import Mock, patch
from datetime import date, datetime
from services.dataset_status import DatasetStatusService
from services.database_session_manager import DatabaseSessionManager
from services.email_service import EmailService
from services.activity_logs.dataset_activity_log import DatasetActivityLogService
from services.config import ConfigService
from repositories.dataset import DatasetRepository
import pytest
from test_factory import sample_dataset
from services.emails.dataset_versioning_email import DatasetVersioningEmailService


@pytest.fixture
def identity() -> IdentityContext:
    return IdentityContext(user_id=1, permissions=[])


@pytest.fixture
def config_service():
    mock_config = Mock(spec=ConfigService)
    mock_config.get_enable_multi_tenants.return_value = False
    return mock_config


@pytest.fixture
def dataset_repository(sample_dataset):
    repository = Mock(spec=DatasetRepository)
    repository.get_dataset.return_value = sample_dataset
    repository.has_published_newer_version.return_value = False
    return repository


@pytest.fixture
def database_session_manager():
    return Mock(spec=DatabaseSessionManager)


@pytest.fixture
def email_service():
    return Mock(spec=EmailService)


@pytest.fixture
def dataset_versioning_email_service():
    return Mock(spec=DatasetVersioningEmailService)


@pytest.fixture
def activity_log_service():
    return Mock(spec=DatasetActivityLogService)


@pytest.fixture
def dataset_permissions_service():
    svc = Mock()
    svc.validate_status_change_permissions.return_value = None
    return svc


@pytest.mark.parametrize(
    "initial_status, trigger, permissions, expected_status",
    [
        (
            DatasetStatus.DRAFT.value,
            "complete",
            ["datasets:status-change:complete"],
            DatasetStatus.COMPLETED.value,
        ),
        (
            DatasetStatus.COMPLETED.value,
            "validate",
            ["datasets:status-change:validate"],
            DatasetStatus.VALIDATED.value,
        ),
        (
            DatasetStatus.VALIDATED.value,
            "approve",
            ["datasets:status-change:approve"],
            DatasetStatus.APPROVED.value,
        ),
        (
            DatasetStatus.APPROVED.value,
            "mark_internal",
            ["datasets:status-change:internal-only"],
            DatasetStatus.INTERNAL_ONLY.value,
        ),
        (
            DatasetStatus.APPROVED.value,
            "publish",
            ["datasets:status-change:publish"],
            DatasetStatus.PUBLISHED.value,
        ),
        (
            DatasetStatus.VALIDATED.value,
            "back_to_draft",
            ["datasets:status-change:draft"],
            DatasetStatus.DRAFT.value,
        ),
        (
            DatasetStatus.INTERNAL_ONLY.value,
            "deprecate",
            ["datasets:status-change:deprecate"],
            DatasetStatus.DEPRECATED.value,
        ),
        (
            DatasetStatus.PUBLISHED.value,
            "deprecate",
            ["datasets:status-change:deprecate"],
            DatasetStatus.DEPRECATED.value,
        ),
        (
            DatasetStatus.PUBLISHED.value,
            "unpublish",
            ["datasets:status-change:publish"],
            DatasetStatus.APPROVED.value,
        ),
    ],
)
def test_update_status_valid_transitions(
    initial_status,
    trigger,
    permissions,
    expected_status,
    sample_dataset,
    dataset_repository,
    database_session_manager,
    identity,
    email_service,
    activity_log_service,
    config_service,
    dataset_permissions_service,
):
    sample_dataset.status = initial_status
    identity.permissions = permissions

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset_id=1,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        email_service=email_service,
        activity_log_service=activity_log_service,
        config_service=config_service,
        dataset_permissions_service=dataset_permissions_service,
    )

    updated_dataset = dataset_status_service.update_status(trigger)

    assert dataset_status_service._dataset.status == expected_status
    assert updated_dataset.status == expected_status
    dataset_status_service._dataset_repository.merge.assert_called_once_with(
        dataset_status_service._dataset
    )
    if trigger == "validate":
        email_service.notify_dataset_validated.assert_called_once()
    elif trigger == "approve":
        email_service.notify_dataset_approved.assert_called_once()
    elif trigger == "complete":
        email_service.notify_dataset_completed.assert_called_once()
    elif trigger == "back_to_draft":
        email_service.notify_dataset_back_to_draft.assert_called_once()
    elif trigger == "publish":
        email_service.notify_dataset_published.assert_called_once()
    elif trigger == "mark_internal":
        email_service.notify_dataset_marked_as_internal.assert_called_once()
    elif trigger == "deprecate":
        email_service.notify_dataset_deprecated.assert_called_once()

    dataset_status_service._database_session_manager.commit.assert_called_once()
    activity_log_service.log_dataset_status_change.assert_called_once()


def test_update_status_invalid_transition(
    dataset_repository,
    database_session_manager,
    identity,
    email_service,
    activity_log_service,
    dataset_permissions_service,
):
    identity.permissions = ["datasets:status-change:complete"]
    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset_id=1,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        email_service=email_service,
        activity_log_service=activity_log_service,
        dataset_permissions_service=dataset_permissions_service,
    )

    dataset_status_service._dataset.status = DatasetStatus.COMPLETED.value
    with pytest.raises(HTTPException):
        dataset_status_service.update_status("complete")


def test_update_status_rejects_imported_dataset(
    dataset_repository,
    database_session_manager,
    identity,
    email_service,
    activity_log_service,
    sample_dataset,
    dataset_permissions_service,
):
    identity.permissions = ["datasets:status-change:complete"]
    sample_dataset.status = DatasetStatus.DRAFT.value
    sample_dataset.source = "external-mdc"

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        email_service=email_service,
        activity_log_service=activity_log_service,
        dataset_permissions_service=dataset_permissions_service,
    )

    with pytest.raises(HTTPException) as excinfo:
        dataset_status_service.update_status("complete")

    assert (
        excinfo.value.detail == "Status transitions are disabled for imported datasets."
    )


def test_update_status_complete_by_some_other_user(
    dataset_repository,
    database_session_manager,
    identity,
    email_service,
    activity_log_service,
    dataset_permissions_service,
):
    identity.permissions = ["datasets:status-change:complete:my"]
    identity.user_id = 2
    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset_id=1,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        email_service=email_service,
        activity_log_service=activity_log_service,
        dataset_permissions_service=dataset_permissions_service,
    )

    with pytest.raises(HTTPException):
        dataset_status_service.update_status("complete")


def test_get_triggers(
    dataset_repository, database_session_manager, identity, dataset_permissions_service
):
    identity.permissions = ["datasets:status-change:complete"]
    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset_id=1,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        dataset_permissions_service=dataset_permissions_service,
    )
    triggers = dataset_status_service.get_triggers()

    assert triggers == ["complete"]


def test_update_status_complete_requires_at_least_one_distribution(
    dataset_repository,
    database_session_manager,
    identity,
    sample_dataset,
    dataset_permissions_service,
):
    identity.permissions = ["datasets:status-change:complete"]
    sample_dataset.status = DatasetStatus.DRAFT.value
    sample_dataset.distributions = set()

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        dataset_permissions_service=dataset_permissions_service,
    )

    with pytest.raises(HTTPException) as exc_info:
        dataset_status_service.update_status("complete")

    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail
        == "At least one distribution is required before submitting the dataset."
    )


def test_update_status_complete_requires_version_and_notes_for_underlying_data_versions(
    dataset_repository,
    database_session_manager,
    identity,
    sample_dataset,
    dataset_permissions_service,
):
    identity.permissions = ["datasets:status-change:complete"]
    sample_dataset.status = DatasetStatus.DRAFT.value
    sample_dataset.version_change_type = DatasetVersionChangeType.UNDERLYING_DATA.value
    sample_dataset.version_notes = []

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        dataset_permissions_service=dataset_permissions_service,
    )

    with pytest.raises(HTTPException) as exc_info:
        dataset_status_service.update_status("complete")

    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail
        == "This version is marked as an underlying data change. Please fill in the 'version' field and add at least one 'version note' before submitting."
    )


def test_update_status_complete_requires_changed_version_and_new_notes_for_underlying_data_versions(
    dataset_repository,
    database_session_manager,
    identity,
    sample_dataset,
    dataset_permissions_service,
):
    identity.permissions = ["datasets:status-change:complete"]
    sample_dataset.status = DatasetStatus.DRAFT.value
    sample_dataset.version_change_type = DatasetVersionChangeType.UNDERLYING_DATA.value
    sample_dataset.previous_version_dataset_id = 2
    sample_dataset.version = "1.0"
    sample_dataset.version_notes = [
        DatasetVersionNote(value="Initial release"),
    ]

    previous_dataset = Dataset(
        id=2,
        status=DatasetStatus.PUBLISHED.value,
        version="1.0",
        previous_version_dataset_id=None,
        user_id=identity.user_id,
    )
    previous_dataset.version_notes = [
        DatasetVersionNote(value="Initial release"),
    ]

    dataset_repository.get_dataset.side_effect = lambda dataset_id: (
        previous_dataset if dataset_id == 2 else sample_dataset
    )

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        dataset_permissions_service=dataset_permissions_service,
    )

    with pytest.raises(HTTPException) as exc_info:
        dataset_status_service.update_status("complete")

    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail
        == "This version is marked as an underlying data change. Please update the 'version' field and add at least one new 'version note' compared to the previous version."
    )


def test_get_triggers_returns_empty_for_imported_dataset(
    dataset_repository,
    database_session_manager,
    identity,
    sample_dataset,
    dataset_permissions_service,
):
    identity.permissions = ["datasets:status-change:complete"]
    sample_dataset.source = "external-mdc"

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        dataset_permissions_service=dataset_permissions_service,
    )

    assert dataset_status_service.get_triggers() == []


def test_get_triggers_when_not_correct_permission(
    dataset_repository, database_session_manager, identity, dataset_permissions_service
):
    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset_id=1,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        dataset_permissions_service=dataset_permissions_service,
    )
    triggers = dataset_status_service.get_triggers()

    assert triggers == []


def test_can_draft_as_group_manager(
    dataset_repository, database_session_manager, identity, dataset_permissions_service
):
    identity.user_id = 2
    identity.permissions = ["datasets:status-change:draft:group"]
    group_manager = DatasetGroupManagers(user_id=2)
    dataset = Dataset(
        id=1, status=DatasetStatus.COMPLETED.value, group_managers={group_manager}
    )

    dataset_status_service = DatasetStatusService(
        dataset=dataset,
        identity=identity,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        email_service=email_service,
        dataset_permissions_service=dataset_permissions_service,
    )

    triggers = dataset_status_service.get_triggers()

    assert "back_to_draft" in triggers


def test_can_draft_with_validate_permission_from_completed_status(
    dataset_repository,
    database_session_manager,
    identity,
    sample_dataset,
    dataset_permissions_service,
):
    identity.permissions = ["datasets:status-change:validate"]
    sample_dataset.status = DatasetStatus.COMPLETED.value

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        dataset_permissions_service=dataset_permissions_service,
    )

    triggers = dataset_status_service.get_triggers()
    assert "back_to_draft" in triggers


def test_cannot_draft_with_validate_permission_from_validated_status(
    dataset_repository,
    database_session_manager,
    identity,
    sample_dataset,
    dataset_permissions_service,
):
    identity.permissions = ["datasets:status-change:validate"]
    sample_dataset.status = DatasetStatus.VALIDATED.value
    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        dataset_permissions_service=dataset_permissions_service,
    )

    triggers = dataset_status_service.get_triggers()
    assert "back_to_draft" not in triggers


def test_can_draft_with_approve_permission_from_validated_status(
    dataset_repository,
    database_session_manager,
    identity,
    sample_dataset,
    dataset_permissions_service,
):
    identity.permissions = ["datasets:status-change:approve"]
    sample_dataset.status = DatasetStatus.VALIDATED.value

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        dataset_permissions_service=dataset_permissions_service,
    )

    triggers = dataset_status_service.get_triggers()
    assert "back_to_draft" in triggers


def test_cannot_draft_with_approve_permission_from_approved_status(
    dataset_repository,
    database_session_manager,
    identity,
    sample_dataset,
    dataset_permissions_service,
):
    identity.permissions = ["datasets:status-change:approve"]
    sample_dataset.status = DatasetStatus.APPROVED.value

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        dataset_permissions_service=dataset_permissions_service,
    )

    triggers = dataset_status_service.get_triggers()
    assert "back_to_draft" not in triggers


def test_can_draft_with_publish_permission_from_approved_status(
    dataset_repository,
    database_session_manager,
    identity,
    sample_dataset,
    dataset_permissions_service,
):
    identity.permissions = ["datasets:status-change:publish"]
    sample_dataset.status = DatasetStatus.APPROVED.value

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        dataset_permissions_service=dataset_permissions_service,
    )

    triggers = dataset_status_service.get_triggers()
    assert "back_to_draft" in triggers


def test_cannot_draft_with_publish_permission_from_published_status_when_multi_tenants_enabled(
    dataset_repository,
    database_session_manager,
    identity,
    sample_dataset,
    config_service,
    dataset_permissions_service,
):
    config_service.get_enable_multi_tenants.return_value = True

    identity.permissions = ["datasets:status-change:publish"]
    sample_dataset.status = DatasetStatus.PUBLISHED.value
    sample_dataset.released_at = datetime(2025, 1, 1)

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        config_service=config_service,
        dataset_permissions_service=dataset_permissions_service,
    )

    triggers = dataset_status_service.get_triggers()
    assert "back_to_draft" not in triggers


def test_can_draft_with_publish_permission_from_published_status_when_multi_tenants_disabled(
    dataset_repository,
    database_session_manager,
    identity,
    sample_dataset,
    config_service,
    dataset_permissions_service,
):
    config_service.get_enable_multi_tenants.return_value = False

    identity.permissions = ["datasets:status-change:publish"]
    sample_dataset.status = DatasetStatus.PUBLISHED.value
    sample_dataset.released_at = datetime(2025, 1, 1)

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        config_service=config_service,
        dataset_permissions_service=dataset_permissions_service,
    )

    triggers = dataset_status_service.get_triggers()
    assert "back_to_draft" in triggers


def test_release_date_is_set_when_published(
    dataset_repository,
    database_session_manager,
    identity,
    email_service,
    sample_dataset,
    activity_log_service,
    config_service,
    dataset_permissions_service,
):
    # Set up permissions
    identity.permissions = ["datasets:status-change:publish"]

    # Create the repository mock that returns our dataset
    repository = Mock(spec=DatasetRepository)
    repository.get_dataset.return_value = sample_dataset
    repository.has_published_newer_version.return_value = False
    sample_dataset.status = DatasetStatus.APPROVED.value
    sample_dataset.released_at = None
    # Create service
    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=repository,
        database_session_manager=database_session_manager,
        email_service=email_service,
        activity_log_service=activity_log_service,
        config_service=config_service,
        dataset_permissions_service=dataset_permissions_service,
    )

    # Mock datetime.now to return a fixed value
    with patch("services.dataset_status.datetime") as mock_datetime:
        mock_now = date(2025, 5, 12)
        mock_datetime.now.return_value = mock_now

        # Perform the status update
        result = dataset_status_service.update_status("publish")

        # Verify the release date was set
        assert sample_dataset.released_at == mock_now
        assert sample_dataset.status == DatasetStatus.PUBLISHED.value

        # Verify the correct methods were called
        repository.merge.assert_called_once()
        database_session_manager.commit.assert_called_once()
        activity_log_service.log_dataset_status_change.assert_called_once()
        email_service.notify_dataset_published.assert_called_once()


def test_release_date_is_not_set_when_marked_internal(
    dataset_repository,
    database_session_manager,
    identity,
    email_service,
    sample_dataset,
    activity_log_service,
    config_service,
    dataset_permissions_service,
):
    # Set up permissions
    identity.permissions = ["datasets:status-change:internal-only"]

    # Create the repository mock that returns our dataset
    repository = Mock(spec=DatasetRepository)
    repository.get_dataset.return_value = sample_dataset
    repository.has_published_newer_version.return_value = False
    sample_dataset.status = DatasetStatus.APPROVED.value
    sample_dataset.released_at = None
    # Create service
    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=repository,
        database_session_manager=database_session_manager,
        email_service=email_service,
        activity_log_service=activity_log_service,
        config_service=config_service,
        dataset_permissions_service=dataset_permissions_service,
    )

    # Perform the status update
    result = dataset_status_service.update_status("mark_internal")

    # Verify the release date was NOT set
    assert sample_dataset.released_at is None
    assert sample_dataset.status == DatasetStatus.INTERNAL_ONLY.value

    # Verify the correct methods were called
    repository.merge.assert_called_once()
    database_session_manager.commit.assert_called_once()
    activity_log_service.log_dataset_status_change.assert_called_once()
    email_service.notify_dataset_marked_as_internal.assert_called_once()


def test_set_release_date_method(
    dataset_repository,
    database_session_manager,
    sample_dataset,
    dataset_permissions_service,
):
    # Create service with minimum dependencies
    dataset_status_service = DatasetStatusService(
        identity=Mock(),
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        dataset_permissions_service=dataset_permissions_service,
    )

    # Mock datetime.now to return a fixed value
    with patch("services.dataset_status.datetime") as mock_datetime:
        mock_now = datetime(2025, 5, 12)
        mock_datetime.now.return_value = mock_now

        # Call the method directly
        dataset_status_service._set_release_date()

        # Verify the release date was set
        assert sample_dataset.released_at == mock_now


def test_set_deprecate_date_method(
    dataset_repository,
    database_session_manager,
    sample_dataset,
    dataset_permissions_service,
):
    dataset_status_service = DatasetStatusService(
        identity=Mock(),
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        dataset_permissions_service=dataset_permissions_service,
    )

    with patch("services.dataset_status.datetime") as mock_datetime:
        mock_now = datetime(2025, 5, 16, 15, 0)
        mock_datetime.now.return_value = mock_now

        dataset_status_service._set_deprecate_date()

        assert sample_dataset.deprecated_at == mock_now


def test_multiple_after_callbacks_execution_order(
    dataset_repository,
    database_session_manager,
    identity,
    email_service,
    activity_log_service,
    sample_dataset,
    dataset_permissions_service,
):
    # Set permissions
    identity.permissions = ["datasets:status-change:publish"]

    sample_dataset.status = DatasetStatus.APPROVED.value

    # Set up repository mock
    repository = Mock(spec=DatasetRepository)
    repository.get_dataset.return_value = sample_dataset
    repository.has_published_newer_version.return_value = False

    # Create service and patch the methods we want to test for execution order
    with patch(
        "services.dataset_status.DatasetStatusService._set_release_date"
    ) as mock_set_release_date, patch(
        "services.dataset_status.DatasetStatusService._commit_status_change"
    ) as mock_commit_status_change:

        dataset_status_service = DatasetStatusService(
            identity=identity,
            dataset=sample_dataset,
            dataset_repository=repository,
            database_session_manager=database_session_manager,
            email_service=email_service,
            activity_log_service=activity_log_service,
            dataset_permissions_service=dataset_permissions_service,
        )

        # Perform the status update
        dataset_status_service.update_status("publish")

        # Verify both callbacks were called
        mock_set_release_date.assert_called_once()
        mock_commit_status_change.assert_called_once()


def test_publish_new_version_deprecates_original_dataset(
    dataset_repository,
    database_session_manager,
    identity,
    email_service,
    activity_log_service,
    sample_dataset,
    dataset_versioning_email_service,
    config_service,
    dataset_permissions_service,
):
    original_dataset = Dataset(
        id=2,
        status=DatasetStatus.PUBLISHED.value,
        deprecated_at=None,
        previous_version_dataset_id=None,
        user_id=identity.user_id,
    )

    sample_dataset.status = DatasetStatus.APPROVED.value
    sample_dataset.previous_version_dataset_id = 2

    dataset_repository.get_dataset.side_effect = lambda dataset_id: (
        original_dataset if dataset_id == 2 else sample_dataset
    )

    identity.permissions = ["datasets:status-change:publish"]

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        email_service=email_service,
        activity_log_service=activity_log_service,
        dataset_versioning_email_service=dataset_versioning_email_service,
        config_service=config_service,
        dataset_permissions_service=dataset_permissions_service,
    )

    updated_dataset = dataset_status_service.update_status("publish")

    assert updated_dataset.status == DatasetStatus.PUBLISHED.value

    assert original_dataset.status == DatasetStatus.DEPRECATED.value
    assert original_dataset.deprecated_at is not None

    dataset_repository.merge.assert_any_call(sample_dataset)
    dataset_repository.merge.assert_any_call(original_dataset)

    database_session_manager.commit.assert_called()

    activity_log_service.log_dataset_status_change.assert_called()
    dataset_versioning_email_service.notify_old_dataset_deprecated.assert_called_once_with(
        original_dataset, sample_dataset
    )


def test_publish_new_version_deprecates_approved_dataset(
    dataset_repository,
    database_session_manager,
    identity,
    email_service,
    activity_log_service,
    sample_dataset,
    dataset_versioning_email_service,
    config_service,
    dataset_permissions_service,
):
    previous_dataset = Dataset(
        id=2,
        status=DatasetStatus.APPROVED.value,
        deprecated_at=None,
        previous_version_dataset_id=None,
        user_id=identity.user_id,
    )

    sample_dataset.status = DatasetStatus.APPROVED.value
    sample_dataset.previous_version_dataset_id = 2

    dataset_repository.get_dataset.side_effect = lambda dataset_id: (
        previous_dataset if dataset_id == 2 else sample_dataset
    )

    identity.permissions = ["datasets:status-change:publish"]

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        email_service=email_service,
        activity_log_service=activity_log_service,
        dataset_versioning_email_service=dataset_versioning_email_service,
        config_service=config_service,
        dataset_permissions_service=dataset_permissions_service,
    )

    dataset_status_service.update_status("publish")

    assert previous_dataset.status == DatasetStatus.DEPRECATED.value
    assert previous_dataset.deprecated_at is not None


def test_complete_authentic_source_review_when_publishing_with_no_data_dictionaries(
    dataset_repository,
    database_session_manager,
    identity,
    email_service,
    activity_log_service,
    sample_dataset,
    config_service,
    dataset_permissions_service,
):
    # Set up permissions
    identity.permissions = ["datasets:status-change:publish"]

    # Set up dataset with no data dictionaries
    sample_dataset.status = DatasetStatus.APPROVED.value
    sample_dataset.data_dictionaries = set()

    # Create service
    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        email_service=email_service,
        activity_log_service=activity_log_service,
        config_service=config_service,
        dataset_permissions_service=dataset_permissions_service,
    )
    # Perform the publish action
    updated_dataset = dataset_status_service.update_status("publish")

    # Verify the dataset was published
    assert updated_dataset.status == DatasetStatus.PUBLISHED.value

    # Verify that complete_authentic_source_review was called
    dataset_repository.complete_authentic_source_review.assert_called_once_with(
        sample_dataset.id
    )

    # Verify standard publish flow still works
    dataset_repository.merge.assert_called_with(sample_dataset)
    database_session_manager.commit.assert_called()
    email_service.notify_dataset_published.assert_called_once()
    activity_log_service.log_dataset_status_change.assert_called_once()


def test_cannot_publish_if_newer_version_already_published(
    dataset_repository,
    database_session_manager,
    identity,
    sample_dataset,
    dataset_permissions_service,
):
    identity.permissions = ["datasets:status-change:publish"]
    sample_dataset.status = DatasetStatus.APPROVED.value

    # Mock the repository method to return True (newer version exists and is published)
    dataset_repository.has_published_newer_version.return_value = True

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        dataset_permissions_service=dataset_permissions_service,
    )

    triggers = dataset_status_service.get_triggers()
    assert "publish" not in triggers


def test_update_status_complete_by_organisation_user(
    dataset_repository,
    database_session_manager,
    identity,
    email_service,
    activity_log_service,
    sample_dataset,
    dataset_permissions_service,
):
    identity.permissions = ["datasets:status-change:complete:organisation"]
    identity.user_id = 2
    identity.current_organisation_id = 123
    sample_dataset.publisher_id = 123
    sample_dataset.user_id = 999  # different user

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        email_service=email_service,
        activity_log_service=activity_log_service,
        dataset_permissions_service=dataset_permissions_service,
    )

    updated_dataset = dataset_status_service.update_status("complete")
    assert updated_dataset.status == DatasetStatus.COMPLETED.value


def test_update_status_complete_by_organisation_user_wrong_org(
    dataset_repository,
    database_session_manager,
    identity,
    email_service,
    activity_log_service,
    sample_dataset,
    dataset_permissions_service,
):
    identity.permissions = ["datasets:status-change:complete:organisation"]
    identity.user_id = 2
    identity.current_organisation_id = 456
    sample_dataset.publisher_id = 123
    sample_dataset.user_id = 999  # different user

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        email_service=email_service,
        activity_log_service=activity_log_service,
        dataset_permissions_service=dataset_permissions_service,
    )

    with pytest.raises(HTTPException):
        dataset_status_service.update_status("complete")


def test_restore_approved_from_internal_only(
    dataset_repository,
    database_session_manager,
    identity,
    email_service,
    activity_log_service,
    sample_dataset,
    config_service,
    dataset_permissions_service,
):
    identity.permissions = ["datasets:status-change:internal-only"]
    sample_dataset.status = DatasetStatus.INTERNAL_ONLY.value

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        email_service=email_service,
        activity_log_service=activity_log_service,
        config_service=config_service,
        dataset_permissions_service=dataset_permissions_service,
    )

    updated_dataset = dataset_status_service.update_status("restore_approved")
    assert updated_dataset.status == DatasetStatus.APPROVED.value
    dataset_repository.merge.assert_called_once()
    database_session_manager.commit.assert_called_once()
    activity_log_service.log_dataset_status_change.assert_called_once()


def test_cannot_restore_approved_without_permission(
    dataset_repository,
    database_session_manager,
    identity,
    sample_dataset,
    dataset_permissions_service,
):
    identity.permissions = ["datasets:status-change:publish"]
    sample_dataset.status = DatasetStatus.INTERNAL_ONLY.value

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        dataset_permissions_service=dataset_permissions_service,
    )

    triggers = dataset_status_service.get_triggers()
    assert "restore_approved" not in triggers


def test_cannot_move_internal_only_to_draft(
    dataset_repository,
    database_session_manager,
    identity,
    sample_dataset,
    dataset_permissions_service,
):
    identity.permissions = ["datasets:status-change:draft"]
    sample_dataset.status = DatasetStatus.INTERNAL_ONLY.value

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        dataset_permissions_service=dataset_permissions_service,
    )

    triggers = dataset_status_service.get_triggers()
    assert "back_to_draft" not in triggers


def test_mark_internal_requires_internal_only_permission(
    dataset_repository,
    database_session_manager,
    identity,
    sample_dataset,
    dataset_permissions_service,
):
    identity.permissions = ["datasets:status-change:publish"]
    sample_dataset.status = DatasetStatus.APPROVED.value

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        dataset_permissions_service=dataset_permissions_service,
    )

    triggers = dataset_status_service.get_triggers()
    assert "mark_internal" not in triggers


def test_mark_internal_with_correct_permission(
    dataset_repository,
    database_session_manager,
    identity,
    sample_dataset,
    dataset_permissions_service,
):
    identity.permissions = ["datasets:status-change:internal-only"]
    sample_dataset.status = DatasetStatus.APPROVED.value

    dataset_status_service = DatasetStatusService(
        identity=identity,
        dataset=sample_dataset,
        dataset_repository=dataset_repository,
        database_session_manager=database_session_manager,
        dataset_permissions_service=dataset_permissions_service,
    )

    triggers = dataset_status_service.get_triggers()
    assert "mark_internal" in triggers
