import pytest
from fastapi.testclient import TestClient
from main import app
from models.user import User
from models.dataset import Keyword
from test_factory import (
    client_with_logged_in_user,
    client_with_logged_in_catalogue_manager_user,
)

client = TestClient(app)


@pytest.fixture
def setup_users(db_session):
    user1 = User(
        name="Jean Dupont", email="jean@example.com", iam_roles="ADMIN", external_id="1"
    )
    user2 = User(
        name="Marie Curie", email="marie@example.com", iam_roles="USER", external_id="2"
    )
    db_session.add_all([user1, user2])
    db_session.commit()


@pytest.fixture(autouse=True)
def clean_users(db_session):
    yield
    db_session.query(User).delete()
    db_session.commit()


def test_users_with_matching_query(client_with_logged_in_user, setup_users, clean_db):
    response = client_with_logged_in_user.post(
        "/api/v1/users",
        json={
            "page": 1,
            "page_size": 10,
            "query": "jean",
        },
    )

    assert response.status_code == 200
    result = response.json()

    assert "meta" in result
    assert "total_items" in result["meta"]
    assert "page" in result["meta"]
    assert "page_size" in result["meta"]
    assert "total_pages" in result["meta"]

    assert isinstance(result["items"], list)
    user_names = [user["name"].lower() for user in result["items"]]
    assert any("jean" in name for name in user_names)
    assert any(user["name"].lower() == "jean dupont" for user in result["items"])


def test_users_with_no_matching_query(client_with_logged_in_user, db_session):
    user = User(
        name="Alice Martin",
        email="alice@example.com",
        iam_roles="USER",
        external_id="3",
    )
    db_session.add(user)
    db_session.commit()

    response = client_with_logged_in_user.post(
        "/api/v1/users",
        json={"page": 1, "page_size": 10, "query": "nomatch"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total_items"] == 0
    assert data["items"] == []


def test_users_meta_structure(client_with_logged_in_user, db_session):
    for i in range(15):
        db_session.add(
            User(
                name=f"User {i}",
                email=f"user{i}@example.com",
                iam_roles="USER",
                external_id=str(i + 50),
            )
        )
    db_session.commit()

    response = client_with_logged_in_user.post(
        "/api/v1/users",
        json={"page": 1, "page_size": 10},
    )

    assert response.status_code == 200
    data = response.json()
    meta = data["meta"]
    assert meta["page"] == 1
    assert meta["page_size"] == 10
    assert meta["total_items"] == 15
    assert meta["total_pages"] == 2


def test_users_empty_db(client_with_logged_in_user):
    response = client_with_logged_in_user.post(
        "/api/v1/users",
        json={"page": 1, "page_size": 10},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total_items"] == 0
    assert data["items"] == []


def test_users_multiple_pages(client_with_logged_in_user, db_session):
    for i in range(25):
        db_session.add(
            User(
                name=f"User {i}",
                email=f"user{i}@example.com",
                iam_roles="USER",
                external_id=str(i + 100),
            )
        )
    db_session.commit()

    response = client_with_logged_in_user.post(
        "/api/v1/users",
        json={"page": 2, "page_size": 10},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["meta"]["page"] == 2


def test_delete_unassigned_users(
    client_with_logged_in_catalogue_manager_user, db_session
):
    user = User(
        name="Unassigned User",
        email="unassigned@email.com",
        iam_roles="",
        external_id="11",
    )
    keyword = Keyword(
        key="keyword_created_by_user_to_test_unassigned_user_deletion",
        eng_label="Keyword for Unassigned User Deletion",
        created_by=user,
    )
    db_session.add(keyword)
    db_session.add(user)
    db_session.commit()

    assert db_session.query(User).filter_by(id=user.id).first() is not None

    response = client_with_logged_in_catalogue_manager_user.delete(
        f"/api/v1/users/{user.id}"
    )
    assert response.status_code == 400
    assert db_session.query(User).filter_by(id=user.id).first() is not None


def test_deprecate_user(client_with_logged_in_catalogue_manager_user, db_session):
    user = User(
        name="unknown user",
        email="unknown@email.com",
        iam_roles="whatever",
        external_id="15",
        is_deprecated=False,
    )
    db_session.add(user)
    db_session.commit()
    usr = db_session.query(User).filter_by(id=user.id).first()
    assert usr is not None
    assert usr.is_deprecated is False
    db_session.commit()
    db_session.refresh(user)

    response = client_with_logged_in_catalogue_manager_user.patch(
        f"/api/v1/users/{user.id}/toggle-deprecation",
    )
    assert response.status_code == 200

    usr1 = db_session.query(User).filter_by(id=user.id).first()
    db_session.refresh(usr1)

    assert usr1.is_deprecated == True


def test_remove_user_iam_roles(db_session):
    from unittest.mock import patch
    from fastapi import Request
    from fastapi.testclient import TestClient
    from main import app
    from services.config import ConfigService

    # Create catalogue manager for authentication
    cm = User(
        name="Catalogue Manager",
        email="cm_remove_roles@example.com",
        iam_roles="CATALOGUE_MANAGER",
        external_id="cm-remove-123",
    )
    db_session.add(cm)
    db_session.commit()

    # Create target user
    user = User(
        name="Test User",
        email="testuser@email.com",
        iam_roles="ADMIN,USER,CATALOGUE_MANAGER",
        external_id="16",
    )
    db_session.add(user)
    db_session.commit()

    # Setup client with authentication as catalogue manager
    session_prop = property(lambda self: {"user_id": cm.id})
    with patch.object(Request, "session", session_prop):
        config_service = ConfigService("./config.json")
        config_service.get_enable_multi_tenants = lambda: False
        config_service.get_roles_path_in_access_token = (
            lambda: "resource_access.test.roles"
        )
        app.state.config_service = config_service

        client = TestClient(app)
        response = client.delete(f"/api/v1/users/{user.id}/iam-roles")

    assert response.status_code == 204
    db_session.refresh(user)
    assert user.iam_roles == ""
