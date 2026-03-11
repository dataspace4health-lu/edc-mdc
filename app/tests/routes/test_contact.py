import pytest
from test_factory import client_with_logged_in_user, sample_organisation
from fastapi.testclient import TestClient
from models.contact import Contact
from models.dataset import Dataset
from models.organisation import Organisation
from conftest import db_session
import uuid


@pytest.fixture
def reset_database(db_session):
    db_session.query(Dataset).delete()
    db_session.query(Contact).delete()
    db_session.commit()


@pytest.fixture
def unique_contact():
    return {
        "name": f"John Doe {uuid.uuid4()}",
        "email": f"john.doe.{uuid.uuid4()}@example.com",
        "role": "Manager",
    }


def test_create_contact(
    client_with_logged_in_user, unique_contact, sample_organisation, reset_database
):
    organisation_id = sample_organisation.id
    response = client_with_logged_in_user.post(
        f"/api/v1/organisations/{organisation_id}/contacts", json=unique_contact
    )
    assert response.status_code == 201, response.text

    created_contact = response.json()
    assert "id" in created_contact
    assert created_contact["name"] == unique_contact["name"]
    assert created_contact["email"] == unique_contact["email"]


def test_update_contact(
    client_with_logged_in_user, unique_contact, sample_organisation, reset_database
):
    organisation_id = sample_organisation.id
    create_response = client_with_logged_in_user.post(
        f"/api/v1/organisations/{organisation_id}/contacts", json=unique_contact
    )
    assert create_response.status_code == 201, create_response.text

    created_contact = create_response.json()
    contact_id = created_contact["id"]
    updated_contact = unique_contact.copy()
    updated_contact["name"] = "Updated Contact Name"

    response = client_with_logged_in_user.put(
        f"/api/v1/organisations/{organisation_id}/contacts/{contact_id}",
        json=updated_contact,
    )
    assert response.status_code == 200, response.text

    contact = response.json()
    assert contact["name"] == "Updated Contact Name"
    assert contact["email"] == unique_contact["email"]


def test_delete_contact_success(
    client_with_logged_in_user,
    unique_contact,
    db_session,
):

    clean_org = Organisation(
        name="Clean Test Org",
        email="clean@test.com",
        type="Company",
        is_deprecated=False,
    )
    db_session.add(clean_org)
    db_session.commit()
    db_session.refresh(clean_org)
    organisation_id = clean_org.id

    # Create a contact
    create_response = client_with_logged_in_user.post(
        f"/api/v1/organisations/{organisation_id}/contacts", json=unique_contact
    )
    assert create_response.status_code == 201, create_response.text
    created_contact = create_response.json()
    contact_id = created_contact["id"]

    contact_exists = db_session.query(Contact).filter_by(id=contact_id).first()

    assert contact_exists is not None, "Contact should exist before deletion"

    # Delete the contact
    response = client_with_logged_in_user.delete(
        f"/api/v1/organisations/{organisation_id}/contacts/{contact_id}"
    )
    assert response.status_code == 204, response.text

    contact_exists_after_delete = (
        db_session.query(Contact).filter_by(id=contact_id).first()
    )

    assert (
        contact_exists_after_delete is None
    ), "Contact should not exist after deletion"


def test_toggle_contact_deprecation_deprecate(
    client_with_logged_in_user,
    unique_contact,
    sample_organisation,
    reset_database,
    db_session,
):
    organisation_id = sample_organisation.id

    create_response = client_with_logged_in_user.post(
        f"/api/v1/organisations/{organisation_id}/contacts", json=unique_contact
    )
    assert create_response.status_code == 201, create_response.text
    created_contact = create_response.json()
    contact_id = created_contact["id"]

    response = client_with_logged_in_user.patch(
        f"/api/v1/organisations/{organisation_id}/contacts/{contact_id}/toggle-deprecation"
    )
    assert response.status_code == 200, response.text

    contact = db_session.query(Contact).filter_by(id=contact_id).first()
    assert contact.is_deprecated is True


def test_toggle_contact_deprecation_restore(
    client_with_logged_in_user,
    unique_contact,
    sample_organisation,
    reset_database,
    db_session,
):
    organisation_id = sample_organisation.id

    create_response = client_with_logged_in_user.post(
        f"/api/v1/organisations/{organisation_id}/contacts", json=unique_contact
    )
    created_contact = create_response.json()
    contact_id = created_contact["id"]

    contact = db_session.query(Contact).filter_by(id=contact_id).first()
    contact.is_deprecated = True
    db_session.commit()

    response = client_with_logged_in_user.patch(
        f"/api/v1/organisations/{organisation_id}/contacts/{contact_id}/toggle-deprecation"
    )
    assert response.status_code == 200, response.text

    db_session.refresh(contact)
    assert contact.is_deprecated is False
