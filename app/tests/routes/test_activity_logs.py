from test_factory import (
    client_with_logged_in_user,
    client_with_logged_in_catalogue_manager_user,
    default_dataset_json,
    sample_dataset,
    default_organisation_json,
    sample_organisation,
)
import json
from unittest.mock import MagicMock, patch
import pytest
from conftest import db_session
from sqlalchemy.orm import Session
from models.keyword_assignment import KeywordAssignment
from models.applicable_legislation_assignment import ApplicableLegislationAssignment
from models.dataset import Keyword, ApplicableLegislation


@pytest.fixture(autouse=True)
def clean_form_fields(db_session: Session):
    try:
        db_session.rollback()
    except:
        pass

    db_session.query(KeywordAssignment).delete()
    db_session.query(ApplicableLegislationAssignment).delete()
    db_session.query(Keyword).delete()
    db_session.query(ApplicableLegislation).delete()
    db_session.commit()

    yield

    try:
        db_session.rollback()
    except:
        pass

    db_session.query(KeywordAssignment).delete()
    db_session.query(ApplicableLegislationAssignment).delete()
    db_session.query(Keyword).delete()
    db_session.query(ApplicableLegislation).delete()
    db_session.commit()


def test_create_dataset_activity_log(client_with_logged_in_user, default_dataset_json):
    created_dataset_response = client_with_logged_in_user.post(
        "/api/v1/datasets",
        json=default_dataset_json,
    )

    dataset_id = created_dataset_response.json()["id"]

    response = client_with_logged_in_user.get(
        f"/api/v1/datasets/{dataset_id}/activity-logs"
    )

    assert response.status_code == 200

    activity_logs = response.json()

    assert len(activity_logs) == 1
    actual = activity_logs[0]

    assert actual["action_type"] == "create"
    assert actual["entity_type"] == "dataset"
    assert actual["entity_id"] == str(dataset_id)


def test_update_dataset_activity_log(client_with_logged_in_user, default_dataset_json):
    created_dataset_response = client_with_logged_in_user.post(
        "/api/v1/datasets",
        json=default_dataset_json,
    )

    assert created_dataset_response.status_code == 200
    created_dataset = created_dataset_response.json()
    dataset_id = created_dataset["id"]

    updated_dataset = default_dataset_json.copy()
    updated_dataset["title"] = "Updated Title"

    updated_dataset_response = client_with_logged_in_user.put(
        f"/api/v1/datasets/{dataset_id}",
        json=updated_dataset,
    )

    assert updated_dataset_response.status_code == 200

    response = client_with_logged_in_user.get(
        f"/api/v1/datasets/{dataset_id}/activity-logs"
    )

    assert response.status_code == 200

    activity_logs = response.json()

    assert len(activity_logs) == 2

    create_log = next(it for it in activity_logs if it["action_type"] == "create")
    assert create_log["action_type"] == "create"
    assert create_log["entity_type"] == "dataset"
    assert create_log["entity_id"] == str(dataset_id)

    update_log = next(it for it in activity_logs if it["action_type"] == "update")
    assert update_log["action_type"] == "update"
    assert update_log["entity_type"] == "dataset"
    assert update_log["entity_id"] == str(dataset_id)

    update_changes = json.loads(update_log["changes"])
    assert any(
        change["field"] == "title" and change["new_value"] == "Updated Title"
        for change in update_changes
    )
    assert not any(change["field"] == "identifier" for change in update_changes)


@pytest.mark.parametrize(
    "field_type, create_payload, update_payload, endpoint",
    [
        (
            "keyword",
            {
                "eng_label": "Initial Label",
                "organisation_ids": [1],
            },
            {
                "key": "initial_label",
                "eng_label": "Updated Label",
                "organisation_ids": [1],
            },
            "/api/v1/keyword/activity-logs",
        ),
        (
            "applicable_legislation",
            {
                "eng_label": "Initial Applicable Legislation",
                "description": "desc",
                "link": "https://link",
                "organisation_ids": [1],
            },
            {
                "key": "initial_applicable_legislation",
                "eng_label": "Updated Applicable Legislation",
                "description": "updated",
                "link": "https://updated-link",
                "organisation_ids": [1],
            },
            "/api/v1/applicable_legislation/activity-logs",
        ),
    ],
)
def test_form_field_activity_logs(
    client_with_logged_in_user, field_type, create_payload, update_payload, endpoint
):
    create_response = client_with_logged_in_user.post(
        f"/api/v1/form-fields/{field_type}",
        json=create_payload,
    )
    assert create_response.status_code == 201
    created_field = create_response.json()

    # Update the update_payload with the actual key from the created field
    update_payload_with_key = update_payload.copy()
    update_payload_with_key["key"] = created_field["key"]

    update_response = client_with_logged_in_user.put(
        f"/api/v1/form-fields/{field_type}",
        json=update_payload_with_key,
    )
    assert update_response.status_code == 200

    logs_response = client_with_logged_in_user.get(endpoint)
    assert logs_response.status_code == 200

    logs = logs_response.json()

    target_logs = [log for log in logs if log["entity_id"] == created_field["key"]]
    actions = [log["action_type"] for log in target_logs]

    assert "create" in actions
    assert "update" in actions

    for log in target_logs:
        assert log["entity_type"] == field_type
        assert isinstance(json.loads(log["changes"]), list)


def test_retrieve_all_organisations_activity_logs_as_catalogue_manager(
    client_with_logged_in_catalogue_manager_user, default_organisation_json
):
    # first org
    r1 = client_with_logged_in_catalogue_manager_user.post(
        "/api/v1/organisations", json=default_organisation_json
    )
    assert r1.status_code == 201
    id1 = r1.json()["id"]

    payload2 = default_organisation_json.copy()
    payload2["name"] = payload2["name"] + "-2"
    payload2["email"] = payload2["email"].replace("@", "+2@")

    r2 = client_with_logged_in_catalogue_manager_user.post(
        "/api/v1/organisations", json=payload2
    )
    assert r2.status_code == 201
    id2 = r2.json()["id"]

    resp = client_with_logged_in_catalogue_manager_user.get(
        "/api/v1/organisations/activity-logs"
    )
    assert resp.status_code == 200

    logs = resp.json()
    ids = {l["entity_id"] for l in logs}
    assert ids == {str(id1), str(id2)}

    for l in logs:
        assert l["entity_type"] == "organisation"
        assert l["action_type"] == "create"
