import json
from unittest.mock import Mock
import pytest
from repositories.activity_log import ActivityLogRepository
from services.activity_logs.authentic_source_label_activity_log import (
    AuthenticSourceLabelActivityLogService,
)
from schemas.activity_logs import ResourceActivityLog


@pytest.fixture(autouse=True)
def reset_mocks(authentic_source_label_activity_log_service):
    yield
    authentic_source_label_activity_log_service._repository.reset_mock()


@pytest.fixture
def authentic_source_label_activity_log_service() -> (
    AuthenticSourceLabelActivityLogService
):
    return AuthenticSourceLabelActivityLogService(
        repository=Mock(spec=ActivityLogRepository),
    )


def test_log_label_created(authentic_source_label_activity_log_service):
    user_id = 1
    label_id = 123
    label_name = "Test Label"
    label_description = "Test Description"

    authentic_source_label_activity_log_service.log_label_created(
        user_id=user_id,
        label_id=label_id,
        label_name=label_name,
        label_description=label_description,
    )

    log_entry = (
        authentic_source_label_activity_log_service._repository.add.call_args.args[0]
    )

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "authentic_source_label"
    assert log_entry.entity_id == str(label_id)
    assert log_entry.action_type == "create"

    expected_diff = [
        {
            "field": "authentic_source_label",
            "old_value": None,
            "new_value": {
                "id": label_id,
                "name": label_name,
                "description": label_description,
            },
            "change_type": "created",
        }
    ]

    actual_diff = json.loads(log_entry.changes)
    assert (
        actual_diff == expected_diff
    ), f"Expected {expected_diff} but got {actual_diff}"

    authentic_source_label_activity_log_service._repository.add.assert_called_once_with(
        log_entry
    )
    authentic_source_label_activity_log_service._repository.commit.assert_called_once()


def test_get_all_activity_logs(authentic_source_label_activity_log_service):
    page = 1
    page_size = 10

    # Create mock logs
    mock_log_1 = Mock()
    mock_log_2 = Mock()
    mock_logs = [mock_log_1, mock_log_2]

    authentic_source_label_activity_log_service._repository.get_all_activity_logs_for_entity.return_value = (
        mock_logs
    )

    result = authentic_source_label_activity_log_service.get_all_activity_logs(
        page=page, page_size=page_size
    )

    # Verify the repository was called correctly
    authentic_source_label_activity_log_service._repository.get_all_activity_logs_for_entity.assert_called_once_with(
        "authentic_source_label", page, page_size
    )

    # Verify that the result contains the expected number of logs
    assert len(result) == 2


def test_log_label_assigned_with_dataset_info(
    authentic_source_label_activity_log_service,
):
    user_id = 1
    label_id = 123
    label_name = "Test Label"
    entry_id = 456
    dataset_id = 789
    old_entry_id = 321
    old_dataset_id = 654

    authentic_source_label_activity_log_service.log_label_assigned(
        user_id=user_id,
        label_id=label_id,
        label_name=label_name,
        entry_id=entry_id,
        old_entry_id=old_entry_id,
        dataset_id=dataset_id,
        old_dataset_id=old_dataset_id,
    )

    # Should be called twice now - once for label, once for dataset
    assert authentic_source_label_activity_log_service._repository.add.call_count == 2
    assert (
        authentic_source_label_activity_log_service._repository.commit.call_count == 2
    )

    # Get all call arguments
    call_args = (
        authentic_source_label_activity_log_service._repository.add.call_args_list
    )

    # First call should be for the label entity
    label_log_entry = call_args[0].args[0]
    assert label_log_entry.user_id == user_id
    assert label_log_entry.entity_type == "authentic_source_label"
    assert label_log_entry.entity_id == str(label_id)
    assert label_log_entry.action_type == "update"

    expected_label_diff = [
        {
            "field": "authentic_source_label",
            "old_value": {
                "entry_id": old_entry_id,
                "dataset_id": old_dataset_id,
            },
            "new_value": {
                "id": label_id,
                "name": label_name,
                "entry_id": entry_id,
                "dataset_id": dataset_id,
            },
            "change_type": "assigned",
        }
    ]

    actual_label_diff = json.loads(label_log_entry.changes)
    assert actual_label_diff == expected_label_diff

    # Second call should be for the dataset entity
    dataset_log_entry = call_args[1].args[0]
    assert dataset_log_entry.user_id == user_id
    assert dataset_log_entry.entity_type == "dataset"
    assert dataset_log_entry.entity_id == str(dataset_id)
    assert dataset_log_entry.action_type == "update"

    expected_dataset_diff = [
        {
            "field": "authentic_source_label",
            "old_value": {
                "entry_id": old_entry_id,
            },
            "new_value": {
                "id": label_id,
                "name": label_name,
                "entry_id": entry_id,
            },
            "change_type": "label_assigned",
        }
    ]

    actual_dataset_diff = json.loads(dataset_log_entry.changes)
    assert actual_dataset_diff == expected_dataset_diff


def test_log_label_unassigned_with_dataset(authentic_source_label_activity_log_service):
    user_id = 1
    label_id = 123
    label_name = "Test Label"
    old_entry_id = 456
    old_dataset_id = 789

    authentic_source_label_activity_log_service.log_label_unassigned(
        user_id=user_id,
        label_id=label_id,
        label_name=label_name,
        old_entry_id=old_entry_id,
        old_dataset_id=old_dataset_id,
    )

    # Should be called twice now - once for label, once for dataset
    assert authentic_source_label_activity_log_service._repository.add.call_count == 2
    assert (
        authentic_source_label_activity_log_service._repository.commit.call_count == 2
    )

    # Get all call arguments
    call_args = (
        authentic_source_label_activity_log_service._repository.add.call_args_list
    )

    # First call should be for the label entity
    label_log_entry = call_args[0].args[0]
    expected_label_diff = [
        {
            "field": "authentic_source_label",
            "old_value": {
                "id": label_id,
                "name": label_name,
                "entry_id": old_entry_id,
                "dataset_id": old_dataset_id,
            },
            "new_value": None,
            "change_type": "unassigned",
        }
    ]

    actual_label_diff = json.loads(label_log_entry.changes)
    assert actual_label_diff == expected_label_diff

    # Second call should be for the dataset entity
    dataset_log_entry = call_args[1].args[0]
    assert dataset_log_entry.entity_type == "dataset"
    assert dataset_log_entry.entity_id == str(old_dataset_id)

    expected_dataset_diff = [
        {
            "field": "authentic_source_label",
            "old_value": {
                "id": label_id,
                "name": label_name,
                "entry_id": old_entry_id,
            },
            "new_value": None,
            "change_type": "label_unassigned",
        }
    ]

    actual_dataset_diff = json.loads(dataset_log_entry.changes)
    assert actual_dataset_diff == expected_dataset_diff


def test_log_label_reassigned_with_different_datasets(
    authentic_source_label_activity_log_service,
):
    """Test reassignment between different datasets"""
    user_id = 1
    label_id = 123
    label_name = "Test Label"
    old_entry_id = 456
    new_entry_id = 789
    old_dataset_id = 111
    new_dataset_id = 222

    authentic_source_label_activity_log_service.log_label_reassigned(
        user_id=user_id,
        label_id=label_id,
        label_name=label_name,
        old_entry_id=old_entry_id,
        new_entry_id=new_entry_id,
        old_dataset_id=old_dataset_id,
        new_dataset_id=new_dataset_id,
    )

    # Should be called 3 times: once for label, once for old dataset unassign, once for new dataset assign
    assert authentic_source_label_activity_log_service._repository.add.call_count == 3
    assert (
        authentic_source_label_activity_log_service._repository.commit.call_count == 3
    )

    call_args = (
        authentic_source_label_activity_log_service._repository.add.call_args_list
    )

    # First call: label entity
    label_log_entry = call_args[0].args[0]
    assert label_log_entry.entity_type == "authentic_source_label"

    expected_label_diff = [
        {
            "field": "authentic_source_label",
            "old_value": {
                "id": label_id,
                "name": label_name,
                "entry_id": old_entry_id,
                "dataset_id": old_dataset_id,
            },
            "new_value": {
                "id": label_id,
                "name": label_name,
                "entry_id": new_entry_id,
                "dataset_id": new_dataset_id,
            },
            "change_type": "reassigned",
        }
    ]

    actual_label_diff = json.loads(label_log_entry.changes)
    assert actual_label_diff == expected_label_diff

    # Second call: old dataset unassign
    old_dataset_log_entry = call_args[1].args[0]
    assert old_dataset_log_entry.entity_type == "dataset"
    assert old_dataset_log_entry.entity_id == str(old_dataset_id)

    # Third call: new dataset assign
    new_dataset_log_entry = call_args[2].args[0]
    assert new_dataset_log_entry.entity_type == "dataset"
    assert new_dataset_log_entry.entity_id == str(new_dataset_id)


def test_log_label_updated(authentic_source_label_activity_log_service):
    user_id = 1
    label_id = 123
    old_name = "Old Label Name"
    new_name = "New Label Name"
    old_description = "Old description"
    new_description = "New description"

    authentic_source_label_activity_log_service.log_label_updated(
        user_id=user_id,
        label_id=label_id,
        old_name=old_name,
        new_name=new_name,
        old_description=old_description,
        new_description=new_description,
    )

    log_entry = (
        authentic_source_label_activity_log_service._repository.add.call_args.args[0]
    )

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "authentic_source_label"
    assert log_entry.entity_id == str(label_id)
    assert log_entry.action_type == "update"

    expected_diff = [
        {
            "field": "name",
            "old_value": old_name,
            "new_value": new_name,
            "change_type": "updated",
        },
        {
            "field": "description",
            "old_value": old_description,
            "new_value": new_description,
            "change_type": "updated",
        },
        {
            "field": "authentic_source_label",
            "old_value": {
                "id": label_id,
                "name": old_name,
                "description": old_description,
            },
            "new_value": {
                "id": label_id,
                "name": new_name,
                "description": new_description,
            },
            "change_type": "updated",
        },
    ]

    actual_diff = json.loads(log_entry.changes)
    assert (
        actual_diff == expected_diff
    ), f"Expected {expected_diff} but got {actual_diff}"

    authentic_source_label_activity_log_service._repository.add.assert_called_once_with(
        log_entry
    )
    authentic_source_label_activity_log_service._repository.commit.assert_called_once()


def test_log_label_deleted(authentic_source_label_activity_log_service):
    user_id = 1
    label_id = 123
    label_name = "Test Label to Delete"
    label_description = "Test Description to Delete"

    authentic_source_label_activity_log_service.log_label_deleted(
        user_id=user_id,
        label_id=label_id,
        label_name=label_name,
        label_description=label_description,
    )

    log_entry = (
        authentic_source_label_activity_log_service._repository.add.call_args.args[0]
    )

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "authentic_source_label"
    assert log_entry.entity_id == str(label_id)
    assert log_entry.action_type == "delete"

    expected_diff = [
        {
            "field": "authentic_source_label",
            "old_value": {
                "id": label_id,
                "name": label_name,
                "description": label_description,
            },
            "new_value": None,
            "change_type": "deleted",
        }
    ]

    actual_diff = json.loads(log_entry.changes)
    assert (
        actual_diff == expected_diff
    ), f"Expected {expected_diff} but got {actual_diff}"

    authentic_source_label_activity_log_service._repository.add.assert_called_once_with(
        log_entry
    )
    authentic_source_label_activity_log_service._repository.commit.assert_called_once()
