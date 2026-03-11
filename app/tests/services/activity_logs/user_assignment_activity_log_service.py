import json
from unittest.mock import Mock
import pytest
from repositories.activity_log import ActivityLogRepository
from services.activity_logs.user_assignment_activity_log import (
    UserAssignmentActivityLogService,
)
from schemas.activity_logs import ResourceActivityLog


@pytest.fixture(autouse=True)
def reset_mocks(user_assignment_activity_log_service):
    yield
    # Reset mock here after each test function
    user_assignment_activity_log_service._repository.reset_mock()


@pytest.fixture
def user_assignment_activity_log_service() -> UserAssignmentActivityLogService:
    return UserAssignmentActivityLogService(
        repository=Mock(spec=ActivityLogRepository),
    )


def test_log_user_assignment_created(user_assignment_activity_log_service):
    user_id = 1
    organisation_id = 2
    target_user_id = 3
    target_user_email = "target.user@example.com"
    role_id = 5

    user_assignment_activity_log_service.log_user_assignment_created(
        user_id=user_id,
        organisation_id=organisation_id,
        target_user_id=target_user_id,
        target_user_email=target_user_email,
        role_id=role_id,
    )

    log_entry = user_assignment_activity_log_service._repository.add.call_args.args[0]

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "user_assignment"
    assert log_entry.entity_id == f"{target_user_id}:{organisation_id}"
    assert log_entry.action_type == "create"

    expected_diff = [
        {
            "field": "user_assignment",
            "old_value": None,
            "new_value": {
                "target_user_id": target_user_id,
                "target_user_email": target_user_email,
                "organisation_id": organisation_id,
                "role_id": role_id,
            },
            "change_type": "created",
        }
    ]

    actual_diff = json.loads(log_entry.changes)
    assert (
        actual_diff == expected_diff
    ), f"Expected {expected_diff} but got {actual_diff}"

    user_assignment_activity_log_service._repository.add.assert_called_once_with(
        log_entry
    )
    user_assignment_activity_log_service._repository.commit.assert_called_once()


def test_log_user_assignment_deleted(user_assignment_activity_log_service):
    user_id = 1
    organisation_id = 2
    target_user_id = 3
    target_user_email = "target.user@example.com"
    role_ids = [5, 6]

    user_assignment_activity_log_service.log_user_assignment_deleted(
        user_id=user_id,
        organisation_id=organisation_id,
        target_user_id=target_user_id,
        target_user_email=target_user_email,
        role_ids=role_ids,
    )

    log_entry = user_assignment_activity_log_service._repository.add.call_args.args[0]

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "user_assignment"
    assert log_entry.entity_id == f"{target_user_id}:{organisation_id}"
    assert log_entry.action_type == "delete"

    expected_diff = [
        {
            "field": "user_assignment",
            "old_value": {
                "target_user_id": target_user_id,
                "target_user_email": target_user_email,
                "organisation_id": organisation_id,
                "role_ids": role_ids,
            },
            "new_value": None,
            "change_type": "deleted",
        }
    ]

    actual_diff = json.loads(log_entry.changes)
    assert (
        actual_diff == expected_diff
    ), f"Expected {expected_diff} but got {actual_diff}"

    user_assignment_activity_log_service._repository.add.assert_called_once_with(
        log_entry
    )
    user_assignment_activity_log_service._repository.commit.assert_called_once()


def test_log_user_assignment_role_added(user_assignment_activity_log_service):
    user_id = 1
    organisation_id = 2
    target_user_id = 3
    target_user_email = "target.user@example.com"
    role_id = 5

    user_assignment_activity_log_service.log_user_assignment_role_added(
        user_id=user_id,
        organisation_id=organisation_id,
        target_user_id=target_user_id,
        target_user_email=target_user_email,
        role_id=role_id,
    )

    log_entry = user_assignment_activity_log_service._repository.add.call_args.args[0]

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "user_assignment"
    assert log_entry.entity_id == f"{target_user_id}:{organisation_id}"
    assert log_entry.action_type == "update"

    expected_diff = [
        {
            "field": "roles",
            "old_value": None,
            "new_value": {
                "target_user_id": target_user_id,
                "target_user_email": target_user_email,
                "organisation_id": organisation_id,
                "role_id": role_id,
            },
            "change_type": "role_added",
        }
    ]

    actual_diff = json.loads(log_entry.changes)
    assert (
        actual_diff == expected_diff
    ), f"Expected {expected_diff} but got {actual_diff}"

    user_assignment_activity_log_service._repository.add.assert_called_once_with(
        log_entry
    )
    user_assignment_activity_log_service._repository.commit.assert_called_once()


def test_log_user_assignment_role_removed(user_assignment_activity_log_service):
    user_id = 1
    organisation_id = 2
    target_user_id = 3
    target_user_email = "target.user@example.com"
    role_id = 5

    user_assignment_activity_log_service.log_user_assignment_role_removed(
        user_id=user_id,
        organisation_id=organisation_id,
        target_user_id=target_user_id,
        target_user_email=target_user_email,
        role_id=role_id,
    )

    log_entry = user_assignment_activity_log_service._repository.add.call_args.args[0]

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "user_assignment"
    assert log_entry.entity_id == f"{target_user_id}:{organisation_id}"
    assert log_entry.action_type == "update"

    expected_diff = [
        {
            "field": "roles",
            "old_value": {
                "target_user_id": target_user_id,
                "target_user_email": target_user_email,
                "organisation_id": organisation_id,
                "role_id": role_id,
            },
            "new_value": None,
            "change_type": "role_removed",
        }
    ]

    actual_diff = json.loads(log_entry.changes)
    assert (
        actual_diff == expected_diff
    ), f"Expected {expected_diff} but got {actual_diff}"

    user_assignment_activity_log_service._repository.add.assert_called_once_with(
        log_entry
    )
    user_assignment_activity_log_service._repository.commit.assert_called_once()


def test_get_activity_logs_for_organisations(user_assignment_activity_log_service):
    organisation_ids = [2, 5]

    # Create mock logs with different entity_ids
    mock_log_1 = Mock()
    mock_log_1.entity_id = "1:2"  # user 1 in org 2
    mock_log_2 = Mock()
    mock_log_2.entity_id = "3:5"  # user 3 in org 5
    mock_log_3 = Mock()
    mock_log_3.entity_id = "4:8"  # user 4 in org 8 (should be filtered out)
    mock_log_4 = Mock()
    mock_log_4.entity_id = (
        "2:25"  # user 2 in org 25 (should be filtered out - contains "2" but not ":2")
    )
    mock_log_5 = Mock()
    mock_log_5.entity_id = "6:2"  # user 6 in org 2

    all_mock_logs = [mock_log_1, mock_log_2, mock_log_3, mock_log_4, mock_log_5]
    user_assignment_activity_log_service._repository.get_all_activity_logs_for_entity.return_value = (
        all_mock_logs
    )

    result = user_assignment_activity_log_service.get_activity_logs_for_organisations(
        organisation_ids=organisation_ids
    )

    # Verify the repository was called correctly
    user_assignment_activity_log_service._repository.get_all_activity_logs_for_entity.assert_called_once_with(
        "user_assignment"
    )

    # Verify only logs for organisations 2 and 5 are returned
    assert len(result) == 3  # Should include mock_log_1, mock_log_2, and mock_log_5


def test_get_activity_logs_for_organisations_when_no_org_ids_are_provided(
    user_assignment_activity_log_service,
):
    organisation_ids = []

    mock_log_1 = Mock()
    mock_log_1.entity_id = "1:2"  # user 1 in org 2
    mock_log_2 = Mock()
    mock_log_2.entity_id = "3:5"  # user 3 in org 5
    mock_log_3 = Mock()
    mock_log_3.entity_id = "4:8"  # user 4 in org 8 (should be filtered out)
    mock_log_4 = Mock()
    mock_log_4.entity_id = (
        "2:25"  # user 2 in org 25 (should be filtered out - contains "2" but not ":2")
    )
    mock_log_5 = Mock()
    mock_log_5.entity_id = "6:2"  # user 6 in org 2

    all_mock_logs = [mock_log_1, mock_log_2, mock_log_3, mock_log_4, mock_log_5]

    user_assignment_activity_log_service._repository.get_all_activity_logs_for_entity.return_value = (
        all_mock_logs
    )

    result = user_assignment_activity_log_service.get_activity_logs_for_organisations(
        organisation_ids=organisation_ids
    )

    user_assignment_activity_log_service._repository.get_all_activity_logs_for_entity.assert_called_once_with(
        "user_assignment"
    )

    assert (
        len(result) == 5
    )  # Should include all mock logs since no org IDs were provided


def test_log_user_deprecation_status_change_deprecated(
    user_assignment_activity_log_service,
):
    user_id = 1
    target_user_id = 123
    target_user_email = "test@example.com"
    target_user_name = "Test User"
    change_type = "deprecated"

    user_assignment_activity_log_service.log_user_deprecation_status_change(
        user_id=user_id,
        target_user_id=target_user_id,
        target_user_email=target_user_email,
        target_user_name=target_user_name,
        change_type=change_type,
    )

    log_entry = user_assignment_activity_log_service._repository.add.call_args.args[0]

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "user_assignment"
    assert log_entry.entity_id == str(target_user_id)
    assert log_entry.action_type == "update"

    expected_diff = [
        {
            "field": "is_deprecated",
            "old_value": {
                "target_user_id": target_user_id,
                "target_user_email": target_user_email,
                "target_user_name": target_user_name,
                "is_deprecated": False,
            },
            "new_value": {
                "target_user_id": target_user_id,
                "target_user_email": target_user_email,
                "target_user_name": target_user_name,
                "is_deprecated": True,
            },
            "change_type": change_type,
        }
    ]

    actual_diff = json.loads(log_entry.changes)
    assert (
        actual_diff == expected_diff
    ), f"Expected {expected_diff} but got {actual_diff}"

    user_assignment_activity_log_service._repository.add.assert_called_once_with(
        log_entry
    )
    user_assignment_activity_log_service._repository.commit.assert_called_once()
