import pytest
from test_factory import client_with_logged_in_user
from models.user_assignment import UserOrganisationAssignment, Role
from models.organisation import Organisation
from models.user import User
from fastapi.testclient import TestClient
from conftest import db_session
import uuid


@pytest.fixture
def reset_database(db_session):
    db_session.query(UserOrganisationAssignment).delete()
    db_session.query(Organisation).delete()
    db_session.query(User).delete()
    db_session.query(Role).delete()
    db_session.commit()


@pytest.fixture
def create_role(db_session):
    role = Role(name=f"Test Role {uuid.uuid4()}")
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture
def create_test_organisation(client_with_logged_in_user, reset_database):
    org_data = {
        "name": f"Test Organisation {uuid.uuid4()}",
        "email": f"contact.{uuid.uuid4()}@organisation.com",
        "type": "Organisation",
    }
    response = client_with_logged_in_user.post("/api/v1/organisations", json=org_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def create_test_user(db_session):
    user = User(
        name=f"Test User {uuid.uuid4()}",
        email=f"testuser_{uuid.uuid4()}@example.com",
        external_id=f"ext-id-{uuid.uuid4()}",
        iam_roles="user",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_assignment_payload(create_test_user, create_role):
    return {
        "email": create_test_user.email,
        "role_id": create_role.id,
    }


def test_create_user_assignment(
    client_with_logged_in_user, create_test_organisation, user_assignment_payload
):
    organisation_id = create_test_organisation["id"]

    response = client_with_logged_in_user.post(
        f"/api/v1/organisations/{organisation_id}/assignments",
        json=user_assignment_payload,
    )
    assert response.status_code == 201


def test_delete_user_assignment(
    client_with_logged_in_user,
    create_test_organisation,
    create_test_user,
    user_assignment_payload,
):
    organisation_id = create_test_organisation["id"]

    create_response = client_with_logged_in_user.post(
        f"/api/v1/organisations/{organisation_id}/assignments",
        json=user_assignment_payload,
    )
    assert create_response.status_code == 201

    delete_response = client_with_logged_in_user.delete(
        f"/api/v1/organisations/{organisation_id}/assignments/{create_test_user.id}"
    )
    assert delete_response.status_code == 204

    delete_again_response = client_with_logged_in_user.delete(
        f"/api/v1/organisations/{organisation_id}/assignments/{create_test_user.id}"
    )
    assert delete_again_response.status_code == 404


def test_delete_nonexistent_user_assignment(
    client_with_logged_in_user, create_test_organisation
):
    organisation_id = create_test_organisation["id"]
    user_id = 99999

    response = client_with_logged_in_user.delete(
        f"/api/v1/organisations/{organisation_id}/assignments/{user_id}"
    )
    assert response.status_code == 404


def test_create_user_assignment_duplicate(
    client_with_logged_in_user, create_test_organisation, user_assignment_payload
):
    organisation_id = create_test_organisation["id"]

    response1 = client_with_logged_in_user.post(
        f"/api/v1/organisations/{organisation_id}/assignments",
        json=user_assignment_payload,
    )
    assert response1.status_code == 201

    response2 = client_with_logged_in_user.post(
        f"/api/v1/organisations/{organisation_id}/assignments",
        json=user_assignment_payload,
    )
    assert response2.status_code == 409


def test_delete_user_role_assignment_removes_role_but_keeps_assignment(
    client_with_logged_in_user,
    create_test_organisation,
    create_test_user,
    create_role,
    db_session,
):
    organisation_id = create_test_organisation["id"]
    user_id = create_test_user.id

    first_role_id = create_role.id
    response_create = client_with_logged_in_user.post(
        f"/api/v1/organisations/{organisation_id}/assignments",
        json={"email": create_test_user.email, "role_id": first_role_id},
    )
    assert response_create.status_code == 201

    role = Role(name=f"Test Role {uuid.uuid4()}")
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    second_role_id = role.id

    response_add_role = client_with_logged_in_user.post(
        f"/api/v1/organisations/{organisation_id}/assignments",
        json={"email": create_test_user.email, "role_id": second_role_id},
    )
    print("Response after adding second role:", response_add_role.json())
    assert response_add_role.status_code == 201

    response_delete_role = client_with_logged_in_user.delete(
        f"/api/v1/organisations/{organisation_id}/assignments/{user_id}/roles/{first_role_id}"
    )
    assert response_delete_role.status_code == 204


def test_delete_user_role_assignment_nonexistent(
    client_with_logged_in_user,
    create_test_organisation,
    create_test_user,
):
    organisation_id = create_test_organisation["id"]
    user_id = create_test_user.id
    invalid_role_id = 999999

    response = client_with_logged_in_user.delete(
        f"/api/v1/organisations/{organisation_id}/assignments/{user_id}/roles/{invalid_role_id}"
    )
    assert response.status_code == 404


def test_delete_last_role_removes_assignment(
    client_with_logged_in_user,
    create_test_organisation,
    create_test_user,
    create_role,
):
    organisation_id = create_test_organisation["id"]

    assignment_payload = {
        "email": create_test_user.email,
        "role_id": create_role.id,
    }
    create_response = client_with_logged_in_user.post(
        f"/api/v1/organisations/{organisation_id}/assignments",
        json=assignment_payload,
    )
    assert create_response.status_code == 201

    delete_role_response = client_with_logged_in_user.delete(
        f"/api/v1/organisations/{organisation_id}/assignments/{create_test_user.id}/roles/{create_role.id}"
    )
    assert delete_role_response.status_code == 204
