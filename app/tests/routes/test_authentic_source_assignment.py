import pytest
from datetime import datetime, timezone
from test_factory import (
    client_with_logged_in_catalogue_manager_user,
    sample_dataset,
    client_with_logged_in_user,
)
from fastapi.testclient import TestClient
from models.authentic_source_label import AuthenticSourceLabel
from models.authentic_source_assignment import AuthenticSourceAssignment
from models.data_dictionary import DataDictionaryEntry
from factories.data_dictionary_entry import create_sample_data_dictionary_entry
from factories.authentic_source_label import create_sample_authentic_source_label
from models.dataset import Dataset
from conftest import db_session


@pytest.fixture(autouse=True)
def clean_db(db_session):
    db_session.query(AuthenticSourceAssignment).delete()
    db_session.query(AuthenticSourceLabel).delete()
    db_session.query(DataDictionaryEntry).delete()
    db_session.query(Dataset).delete()
    db_session.commit()


@pytest.fixture
def sample_data_dictionary_entry(db_session, sample_dataset):
    entry = create_sample_data_dictionary_entry(dataset_id=sample_dataset.id)
    db_session.add(entry)
    db_session.commit()
    db_session.refresh(entry)
    return entry


@pytest.fixture
def sample_authentic_source_label(db_session):
    label = create_sample_authentic_source_label()
    db_session.add(label)
    db_session.commit()
    db_session.refresh(label)
    return label


@pytest.fixture
def valid_bulk_assignment_payload(
    sample_data_dictionary_entry, sample_authentic_source_label
):
    return {
        "label_assignments": [
            {
                "label_id": sample_authentic_source_label.id,
                "assigned_entry_id": sample_data_dictionary_entry.id,
            }
        ]
    }


def test_bulk_assign_authentic_source_labels_success(
    client_with_logged_in_catalogue_manager_user: TestClient,
    valid_bulk_assignment_payload: dict,
    sample_dataset,
    sample_authentic_source_label,
):
    response = client_with_logged_in_catalogue_manager_user.post(
        "/api/v1/authentic-source-assignments", json=valid_bulk_assignment_payload
    )

    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.text}"
    result = response.json()

    # Verify response is a list
    assert isinstance(result, list)
    assert len(result) >= 1

    # Find the label we assigned
    assigned_label = next(
        (label for label in result if label["id"] == sample_authentic_source_label.id),
        None,
    )
    assert assigned_label is not None
    assert assigned_label["name"] == sample_authentic_source_label.name


def test_complete_authentic_source_review_api_success(
    client_with_logged_in_catalogue_manager_user: TestClient,
    sample_dataset: Dataset,
    db_session,
):
    db_session.add(sample_dataset)
    db_session.commit()

    response = client_with_logged_in_catalogue_manager_user.post(
        f"/api/v1/datasets/{sample_dataset.id}/authentic-source/complete-review"
    )

    assert response.status_code == 204

    db_session.refresh(sample_dataset)
    assert sample_dataset.authentic_source_reviewed_at is not None


def test_get_assignment_history_for_label(
    client_with_logged_in_user,
    sample_authentic_source_label,
    sample_data_dictionary_entry,
    sample_dataset,
    db_session,
):
    db_session.add(sample_dataset)
    assignment1 = AuthenticSourceAssignment(
        data_dictionary_entry_id=sample_data_dictionary_entry.id,
        authentic_source_label_id=sample_authentic_source_label.id,
    )
    assignment1.is_active = False
    db_session.add(assignment1)
    db_session.commit()
    response = client_with_logged_in_user.get(
        f"/api/v1/authentic-source-labels/{sample_authentic_source_label.id}/history"
    )
    data = response.json()
    assert data[0]["dataset_title"] == sample_dataset.title
    assert data[0]["dataset_description"] == sample_dataset.description
    assert response.status_code == 200
