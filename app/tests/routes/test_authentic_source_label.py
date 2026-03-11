import pytest
from test_factory import (
    client_with_logged_in_catalogue_manager_user,
    sample_organisation,
)
from fastapi.testclient import TestClient
from models.authentic_source_label import AuthenticSourceLabel
from conftest import db_session
import uuid
from factories.authentic_source_label import create_sample_authentic_source_label


@pytest.fixture
def reset_database(db_session):
    db_session.query(AuthenticSourceLabel).delete()
    db_session.commit()


@pytest.fixture
def unique_authentic_source_label():
    unique_id = str(uuid.uuid4())[:8]
    return {
        "name": f"Test Label {unique_id}",
        "description": f"Test description for label {unique_id}",
    }


def test_create_authentic_source_label_success(
    client_with_logged_in_catalogue_manager_user: TestClient,
    unique_authentic_source_label: dict,
    reset_database,
):
    response = client_with_logged_in_catalogue_manager_user.post(
        "/api/v1/authentic-source-labels", json=unique_authentic_source_label
    )

    assert response.status_code == 201, response.text
    created_label = response.json()

    assert "id" in created_label
    assert created_label["name"] == unique_authentic_source_label["name"]
    assert created_label["description"] == unique_authentic_source_label["description"]
    assert "created_at" in created_label
    assert "created_by" in created_label


def test_get_authentic_source_labels_single_label(
    client_with_logged_in_catalogue_manager_user: TestClient,
    db_session,
    reset_database,
):
    expected_label = create_sample_authentic_source_label(id=None)
    db_session.add(expected_label)
    db_session.commit()
    db_session.refresh(expected_label)

    response = client_with_logged_in_catalogue_manager_user.get(
        "/api/v1/authentic-source-labels"
    )

    assert response.status_code == 200, response.text
    labels = response.json()

    assert len(labels) == 1
    label = labels[0]
    assert label["id"] == expected_label.id
    assert label["name"] == expected_label.name
    assert label["description"] == expected_label.description


def test_update_authentic_source_label_success(
    client_with_logged_in_catalogue_manager_user: TestClient,
    db_session,
    reset_database,
):
    # Create a label first
    original_label = create_sample_authentic_source_label(id=None)
    db_session.add(original_label)
    db_session.commit()
    db_session.refresh(original_label)

    # Prepare update data
    unique_id = str(uuid.uuid4())[:8]
    update_data = {
        "name": f"Updated Label {unique_id}",
        "description": f"Updated description {unique_id}",
    }
    # Update the label
    response = client_with_logged_in_catalogue_manager_user.put(
        f"/api/v1/authentic-source-labels/{original_label.id}", json=update_data
    )

    assert response.status_code == 200, response.text
    updated_label = response.json()

    assert updated_label["id"] == original_label.id
    assert updated_label["name"] == update_data["name"]
    assert updated_label["description"] == update_data["description"]
    assert "created_at" in updated_label
    assert "created_by" in updated_label


def test_delete_authentic_source_label_success(
    client_with_logged_in_catalogue_manager_user: TestClient,
    db_session,
    reset_database,
):
    label_to_delete = create_sample_authentic_source_label(id=101)
    db_session.add(label_to_delete)
    db_session.commit()
    db_session.refresh(label_to_delete)

    response = client_with_logged_in_catalogue_manager_user.delete(
        f"/api/v1/authentic-source-labels/{label_to_delete.id}"
    )

    assert response.status_code == 204, response.text

    get_response = client_with_logged_in_catalogue_manager_user.get(
        "/api/v1/authentic-source-labels"
    )
    assert get_response.status_code == 200
    labels = get_response.json()
    assert len(labels) == 0


def test_toggle_deprecation_authentic_source_label_deprecate(
    client_with_logged_in_catalogue_manager_user: TestClient,
    db_session,
    reset_database,
):
    label = create_sample_authentic_source_label(id=None, is_deprecated=False)
    db_session.add(label)
    db_session.commit()
    db_session.refresh(label)

    response = client_with_logged_in_catalogue_manager_user.patch(
        f"/api/v1/authentic-source-labels/{label.id}/toggle-deprecation"
    )

    assert response.status_code == 200, response.text
    response_data = response.json()
    assert response_data["id"] == label.id
    assert response_data["is_deprecated"] is True


def test_toggle_deprecation_authentic_source_label_restore(
    client_with_logged_in_catalogue_manager_user: TestClient,
    db_session,
    reset_database,
):
    label = create_sample_authentic_source_label(id=None, is_deprecated=True)
    db_session.add(label)
    db_session.commit()
    db_session.refresh(label)

    response = client_with_logged_in_catalogue_manager_user.patch(
        f"/api/v1/authentic-source-labels/{label.id}/toggle-deprecation"
    )

    assert response.status_code == 200, response.text
    response_data = response.json()
    assert response_data["id"] == label.id
    assert response_data["is_deprecated"] is False
