import json
from unittest.mock import Mock
import pytest
from repositories.activity_log import ActivityLogRepository
from services.activity_logs.organisation_activity_log import (
    OrganisationActivityLogService,
)
from models.contact import Contact
from factories.contact import create_sample_contact


@pytest.fixture
def service() -> OrganisationActivityLogService:
    return OrganisationActivityLogService(
        repository=Mock(spec=ActivityLogRepository),
    )


def test_log_contact_added_to_organisation(service):
    user_id = 1
    organisation_id = 1
    contact = create_sample_contact(organisation_id=organisation_id)

    service.log_contact_added_to_organisation(user_id, organisation_id, contact)

    log_entry = service._repository.add.call_args.args[0]

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "organisation"
    assert log_entry.entity_id == str(organisation_id)
    assert log_entry.action_type == "add_contact"

    expected_diff = [
        {
            "field": "contact",
            "new_value": {
                "id": contact.id,
                "name": contact.name,
                "email": contact.email,
                "role": contact.role,
                "is_deprecated": contact.is_deprecated,
            },
            "change_type": "values_changed",
        }
    ]

    actual_diff = json.loads(log_entry.changes)

    assert (
        actual_diff == expected_diff
    ), f"Expected {expected_diff} but got {actual_diff}"

    service._repository.add.assert_called_once_with(log_entry)
    service._repository.commit.assert_called_once()


def test_log_contact_updated_in_organisation(service):
    user_id = 1
    organisation_id = 1
    contact_before = create_sample_contact(
        id=101,
        name="Jane Doe",
        email="jane.doe@example.com",
        role="Developer",
        organisation_id=organisation_id,
    )

    contact_after = create_sample_contact(
        id=101,
        name="Jane Doe",
        email="jane.doe@example2.com",
        role="Lead Developer",
        organisation_id=organisation_id,
    )

    service.log_contact_updated_in_organisation(
        user_id, organisation_id, contact_before.to_dict(), contact_after
    )

    log_entry = service._repository.add.call_args.args[0]

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "organisation"
    assert log_entry.entity_id == str(organisation_id)
    assert log_entry.action_type == "update_contact"

    expected_diff = [
        {
            "field": "email",
            "old_value": "jane.doe@example.com",
            "new_value": "jane.doe@example2.com",
            "change_type": "values_changed",
        },
        {
            "field": "role",
            "old_value": "Developer",
            "new_value": "Lead Developer",
            "change_type": "values_changed",
        },
    ]

    actual_diff = json.loads(log_entry.changes)
    assert (
        actual_diff == expected_diff
    ), f"Expected {expected_diff} but got {actual_diff}"

    service._repository.add.assert_called_once_with(log_entry)
    service._repository.commit.assert_called_once()


def test_log_contact_deleted_from_organisation(service):
    user_id = 1
    organisation_id = 1

    # Create a contact that will be "deleted"
    contact = create_sample_contact(
        id=202,
        name="John Smith",
        email="john.smith@example.com",
        role="Manager",
        organisation_id=organisation_id,
    )

    # Get the contact data as it would be before deletion
    contact_data = contact.to_dict()

    service.log_contact_deleted_from_organisation(
        user_id, organisation_id, contact_data
    )

    log_entry = service._repository.add.call_args.args[0]
    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "organisation"
    assert log_entry.entity_id == str(organisation_id)
    assert log_entry.action_type == "delete_contact"

    expected_diff = [
        {
            "field": "contact",
            "old_value": {
                "id": contact.id,
                "name": contact.name,
                "email": contact.email,
                "role": contact.role,
                "is_deprecated": contact.is_deprecated,
            },
            "change_type": "values_changed",
        }
    ]
    actual_diff = json.loads(log_entry.changes)
    assert (
        actual_diff == expected_diff
    ), f"Expected {expected_diff} but got {actual_diff}"

    service._repository.add.assert_called_once_with(log_entry)
    service._repository.commit.assert_called_once()
