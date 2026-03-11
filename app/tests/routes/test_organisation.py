import pytest
from test_factory import client_with_logged_in_user
from models.organisation import Organisation
from fastapi.testclient import TestClient
from conftest import db_session
import uuid


@pytest.fixture
def reset_database(db_session):
    db_session.query(Organisation).delete()
    db_session.commit()


@pytest.fixture
def unique_organisation():
    return {
        "name": f"Test Organisation {uuid.uuid4()}",
        "email": f"contact.{uuid.uuid4()}@organisation.com",
        "type": "Organisation",
        "category": "EP",
        "accessible_within_ctie": True,
    }


def test_create_organisation(
    client_with_logged_in_user, unique_organisation, reset_database
):
    response = client_with_logged_in_user.post(
        "/api/v1/organisations", json=unique_organisation
    )
    assert (
        response.status_code == 201
    ), f"Unexpected status code: {response.status_code}, Response: {response.text}"

    created_organisation = response.json()
    assert "id" in created_organisation
    assert created_organisation["name"] == unique_organisation["name"]
    assert created_organisation["email"] == unique_organisation["email"]
    assert created_organisation["category"] == unique_organisation["category"]
    assert (
        created_organisation["accessible_within_ctie"]
        == unique_organisation["accessible_within_ctie"]
    )


def test_get_organisations(
    client_with_logged_in_user, unique_organisation, reset_database
):
    client_with_logged_in_user.post("/api/v1/organisations", json=unique_organisation)
    response = client_with_logged_in_user.get("/api/v1/organisations")
    assert response.status_code == 200, response.text

    organisations = response.json()
    assert len(organisations) > 0
    assert any(
        organisation["name"] == unique_organisation["name"]
        for organisation in organisations
    )


def test_get_organisation_by_id(
    client_with_logged_in_user, unique_organisation, reset_database
):
    create_response = client_with_logged_in_user.post(
        "/api/v1/organisations", json=unique_organisation
    )
    assert create_response.status_code == 201, create_response.text

    created_organisation = create_response.json()
    organisation_id = created_organisation["id"]
    response = client_with_logged_in_user.get(
        f"/api/v1/organisations/{organisation_id}"
    )
    assert response.status_code == 200, response.text

    organisation = response.json()
    assert organisation["name"] == unique_organisation["name"]
    assert organisation["email"] == unique_organisation["email"]


def test_update_organisation(
    client_with_logged_in_user, unique_organisation, reset_database
):
    create_response = client_with_logged_in_user.post(
        "/api/v1/organisations", json=unique_organisation
    )
    assert create_response.status_code == 201, create_response.text

    created_organisation = create_response.json()
    organisation_id = created_organisation["id"]
    updated_organisation = unique_organisation.copy()
    updated_organisation["name"] = "Updated Organisation Name"

    response = client_with_logged_in_user.put(
        f"/api/v1/organisations/{organisation_id}", json=updated_organisation
    )
    assert response.status_code == 200, response.text

    organisation = response.json()
    assert organisation["name"] == updated_organisation["name"]
    assert organisation["email"] == unique_organisation["email"]


def test_toggle_organisation_deprecation(
    client_with_logged_in_user, unique_organisation, reset_database
):
    # Create an organisation first
    create_response = client_with_logged_in_user.post(
        "/api/v1/organisations", json=unique_organisation
    )
    assert create_response.status_code == 201, create_response.text

    created_organisation = create_response.json()
    organisation_id = created_organisation["id"]

    # Verify organisation is not deprecated initially
    assert created_organisation["is_deprecated"] is False

    # Toggle deprecation - deprecate
    response = client_with_logged_in_user.patch(
        f"/api/v1/organisations/{organisation_id}/toggle-deprecation"
    )
    assert response.status_code == 200, response.text

    deprecated_organisation = response.json()
    assert deprecated_organisation["is_deprecated"] is True

    # Toggle deprecation again - restore
    response = client_with_logged_in_user.patch(
        f"/api/v1/organisations/{organisation_id}/toggle-deprecation"
    )
    assert response.status_code == 200, response.text

    restored_organisation = response.json()
    assert restored_organisation["is_deprecated"] is False
