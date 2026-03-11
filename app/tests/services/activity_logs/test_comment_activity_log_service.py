import json
from unittest.mock import Mock
import pytest
from repositories.activity_log import ActivityLogRepository
from services.activity_logs.comment_activity_log import CommentActivityLogService


@pytest.fixture(autouse=True)
def reset_mocks(activity_log_service_comment):
    yield
    # Reset mock here after each test function
    activity_log_service_comment._repository.reset_mock()


@pytest.fixture
def activity_log_service_comment() -> CommentActivityLogService:
    return CommentActivityLogService(
        repository=Mock(spec=ActivityLogRepository),
    )


def test_log_dataset_comment(activity_log_service_comment):
    user_id = 1
    dataset_id = 1
    comment = "This is a test comment"

    activity_log_service_comment.log_dataset_comment(
        user_id, dataset_id, comment, action_type="add_comment"
    )

    log_entry = activity_log_service_comment._repository.add.call_args.args[0]

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "dataset"
    assert log_entry.entity_id == str(dataset_id)
    assert log_entry.action_type == "add_comment"

    expected_diff = [
        {
            "field": "comment",
            "old_value": None,
            "new_value": comment,
            "change_type": "created",
        }
    ]

    actual_diff = json.loads(log_entry.changes)
    assert (
        actual_diff == expected_diff
    ), f"Expected {expected_diff} but got {actual_diff}"

    activity_log_service_comment._repository.add.assert_called_once_with(log_entry)
    activity_log_service_comment._repository.commit.assert_called_once()


def test_log_dataset_comment_delete(activity_log_service_comment):
    user_id = 1
    dataset_id = 1
    comment = "This is a deleted comment"

    activity_log_service_comment.log_dataset_comment(
        user_id, dataset_id, comment, action_type="delete_comment"
    )

    log_entry = activity_log_service_comment._repository.add.call_args.args[0]

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "dataset"
    assert log_entry.entity_id == str(dataset_id)
    assert log_entry.action_type == "delete_comment"

    expected_diff = [
        {
            "field": "comment",
            "old_value": comment,
            "new_value": None,
            "change_type": "deleted",
        }
    ]

    actual_diff = json.loads(log_entry.changes)
    assert (
        actual_diff == expected_diff
    ), f"Expected {expected_diff} but got {actual_diff}"

    activity_log_service_comment._repository.add.assert_called_once_with(log_entry)
    activity_log_service_comment._repository.commit.assert_called_once()
