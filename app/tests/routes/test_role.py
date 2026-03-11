import pytest
from fastapi.testclient import TestClient
from main import app
from models.user_assignment import Role

from test_factory import client_with_logged_in_user

client = TestClient(app)


@pytest.fixture
def setup_roles(db_session):
    role1 = Role(name="Role 1")
    role2 = Role(name="Role 2")
    role3 = Role(name="Test")
    db_session.add_all([role1, role2, role3])
    db_session.commit()


@pytest.fixture(autouse=True)
def clean_roles(db_session):
    db_session.query(Role).delete()
    db_session.commit()
    yield


def test_get_roles_success(client_with_logged_in_user, setup_roles):
    response = client_with_logged_in_user.post("/api/v1/roles")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert any(role["name"] == "Role 1" for role in data)
    assert any(role["name"] == "Role 2" for role in data)
    assert any(role["name"] == "Test" for role in data)


def test_get_roles_not_found(client_with_logged_in_user):
    response = client_with_logged_in_user.post("/api/v1/roles")
    assert response.status_code == 404
    assert response.json() == {"detail": "No roles found"}
