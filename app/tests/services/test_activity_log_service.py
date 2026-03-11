import json
from unittest.mock import Mock

import pytest
from models.organisation import Organisation
from repositories.activity_log import ActivityLogRepository
from schemas.organisation import OrganisationDto
from services.activity_log import ActivityLogService
from schemas.form_field import (
    ApplicableLegislationFormFieldDto,
    FormFieldDto,
)


@pytest.fixture(autouse=True)
def reset_mocks(activity_log_service):
    yield
    activity_log_service._repository.reset_mock()


@pytest.fixture
def activity_log_service() -> ActivityLogService:
    return ActivityLogService(
        repository=Mock(spec=ActivityLogRepository),
    )


def test_log_organisation_create(activity_log_service):
    user_id = 1
    organisation = Organisation(id=1, name=None, type=None, email=None)
    organisation_dto = OrganisationDto(
        name="New Organisation",
        type="Organisation",
        email="new@organisation.com",
        category=None,
        accessible_within_ctie=None,
        contacts=[],
    )

    activity_log_service.log_organisation_activities(
        user_id, organisation.id, {}, organisation_dto, "create"
    )

    log_entry = activity_log_service._repository.add.call_args.args[0]

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "organisation"
    assert log_entry.action_type == "create"

    expected_diff = [
        {
            "field": "root",
            "old_value": {},
            "new_value": {
                "name": "New Organisation",
                "type": "Organisation",
                "email": "new@organisation.com",
                "category": None,
                "accessible_within_ctie": None,
                "contacts": [],
            },
            "change_type": "values_changed",
        }
    ]

    actual_diff = json.loads(log_entry.changes)
    assert (
        actual_diff == expected_diff
    ), f"Expected {expected_diff} but got {actual_diff}"


def test_log_applicable_legislation_create(activity_log_service):
    user_id = 1
    key = "lb-key"
    dto = ApplicableLegislationFormFieldDto(
        key=key,
        eng_label="GDPR",
        description="General Data Protection Regulation",
        link="https://gdpr-info.eu/",
        organisation_ids=[1],
    )
    activity_log_service.log_applicable_legislation_activities(
        user_id=user_id,
        applicable_legislation_key=key,
        applicable_legislation_data={},
        updated_applicable_legislation_data=dto,
        action_type="create",
    )

    log_entry = activity_log_service._repository.add.call_args.args[0]
    assert log_entry.entity_type == "applicable_legislation"
    assert log_entry.entity_id == key
    assert log_entry.action_type == "create"
    assert log_entry.user_id == user_id

    changes = json.loads(log_entry.changes)
    assert any(change["field"] == "eng_label" for change in changes)


def test_log_applicable_legislation_update(activity_log_service):
    user_id = 1
    key = "lb-key"
    original = {
        "eng_label": "GDPR",
        "description": "Old description",
        "link": "https://old-link.com",
        "organisation_ids": [1],
    }
    updated_dto = ApplicableLegislationFormFieldDto(
        key=key,
        eng_label="GDPR",
        description="New description",
        link="https://new-link.com",
        organisation_ids=[1],
    )

    activity_log_service.log_applicable_legislation_activities(
        user_id=user_id,
        applicable_legislation_key=key,
        applicable_legislation_data=original,
        updated_applicable_legislation_data=updated_dto,
        action_type="update",
    )

    log_entry = activity_log_service._repository.add.call_args.args[0]
    assert log_entry.entity_type == "applicable_legislation"
    assert log_entry.action_type == "update"
    changes = json.loads(log_entry.changes)
    assert {
        "field": "description",
        "old_value": "Old description",
        "new_value": "New description",
        "change_type": "values_changed",
    } in changes
    assert {
        "field": "link",
        "old_value": "https://old-link.com",
        "new_value": "https://new-link.com",
        "change_type": "values_changed",
    } in changes


def test_log_applicable_legislation_delete(activity_log_service):
    user_id = 1
    key = "lb-key"
    original = {
        "eng_label": "Label",
        "description": "Description",
        "link": "https://link.com",
        "organisation_ids": [1],
    }
    updated_dto = ApplicableLegislationFormFieldDto(
        key=key, eng_label="", description="", link="", organisation_ids=[1]
    )

    activity_log_service.log_applicable_legislation_activities(
        user_id=user_id,
        applicable_legislation_key=key,
        applicable_legislation_data=original,
        updated_applicable_legislation_data=updated_dto,
        action_type="delete",
    )

    log_entry = activity_log_service._repository.add.call_args.args[0]
    changes = json.loads(log_entry.changes)
    assert log_entry.entity_type == "applicable_legislation"
    assert log_entry.action_type == "delete"
    assert any(change["field"] == "eng_label" for change in changes)


def test_log_keyword_create(activity_log_service):
    user_id = 1
    key = "kw-key"
    updated_dto = FormFieldDto(key=key, eng_label="Security", organisation_ids=[1])

    activity_log_service.log_keyword_activities(
        user_id=user_id,
        keyword_key=key,
        keyword_data={},
        updated_keyword_data=updated_dto.model_dump(),
        action_type="create",
    )

    log_entry = activity_log_service._repository.add.call_args.args[0]
    changes = json.loads(log_entry.changes)

    assert log_entry.entity_type == "keyword"
    assert log_entry.entity_id == key
    assert log_entry.action_type == "create"
    assert log_entry.user_id == user_id
    assert any(
        change["field"] == "eng_label"
        and change["new_value"] == "Security"
        and change["change_type"] == "created"
        for change in changes
    )


def test_log_keyword_update(activity_log_service):
    user_id = 1
    key = "kw-key"
    original_data = {"eng_label": "Security"}
    updated_dto = FormFieldDto(
        key=key, eng_label="Updated Security", organisation_ids=[1]
    )

    activity_log_service.log_keyword_activities(
        user_id=user_id,
        keyword_key=key,
        keyword_data=original_data,
        updated_keyword_data=updated_dto.model_dump(),
        action_type="update",
    )

    log_entry = activity_log_service._repository.add.call_args.args[0]
    changes = json.loads(log_entry.changes)

    assert log_entry.entity_type == "keyword"
    assert log_entry.entity_id == key
    assert log_entry.action_type == "update"
    assert log_entry.user_id == user_id

    assert {
        "field": "eng_label",
        "old_value": "Security",
        "new_value": "Updated Security",
        "change_type": "values_changed",
    } in changes


def test_log_keyword_delete(activity_log_service):
    user_id = 1
    key = "kw-key"
    original_data = {"eng_label": "Security"}
    updated_dto = FormFieldDto(key=key, eng_label="", organisation_ids=[1])

    activity_log_service.log_keyword_activities(
        user_id=user_id,
        keyword_key=key,
        keyword_data=original_data,
        updated_keyword_data=updated_dto.model_dump(),
        action_type="delete",
    )

    log_entry = activity_log_service._repository.add.call_args.args[0]
    changes = json.loads(log_entry.changes)

    assert log_entry.entity_type == "keyword"
    assert log_entry.entity_id == key
    assert log_entry.action_type == "delete"
    assert log_entry.user_id == user_id

    assert {
        "field": "eng_label",
        "old_value": "Security",
        "new_value": "",
        "change_type": "values_changed",
    } in changes
