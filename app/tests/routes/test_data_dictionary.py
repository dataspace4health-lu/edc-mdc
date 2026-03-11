import pytest
from unittest.mock import Mock
import io
from test_factory import client_with_logged_in_user, sample_dataset
from conftest import db_session
from sqlalchemy.orm import Session
from models.dataset import Dataset
from models.data_dictionary import DataDictionaryEntry
from fastapi import status, UploadFile


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    yield
    db_session.query(DataDictionaryEntry).delete()
    db_session.query(Dataset).delete()
    db_session.commit()


@pytest.fixture
def default_data_dictionary_entry():
    return {
        "field_name": "test_field",
        "description": "Test description",
        "data_type": "string",
        "personally_identifiable_variable": True,
        "required": False,
        "max_allowed_value": 100,
        "min_allowed_value": 1,
        "variable_unit": "kg",
        "allowed_values": "[1, 2, 3]",
        "allowed_values_description": "[1=One, 2=Two, 3=Three]",
        "table_name": "test_table",
        "privacy_risk_type": "Quasi-identifiant",
    }


def test_create_data_dictionary_entry(
    client_with_logged_in_user, sample_dataset, default_data_dictionary_entry
):
    dataset_id = sample_dataset.id
    default_data_dictionary_entry["field_name"] = "unique_test_field"

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries",
        json=default_data_dictionary_entry,
    )

    assert response.status_code == 201, response.text
    data_dictionary_entry = response.json()

    assert (
        data_dictionary_entry["field_name"]
        == default_data_dictionary_entry["field_name"]
    )
    assert (
        data_dictionary_entry["description"]
        == default_data_dictionary_entry["description"]
    )
    assert (
        data_dictionary_entry["data_type"] == default_data_dictionary_entry["data_type"]
    )
    assert (
        data_dictionary_entry["personally_identifiable_variable"]
        == default_data_dictionary_entry["personally_identifiable_variable"]
    )
    assert (
        data_dictionary_entry["required"] == default_data_dictionary_entry["required"]
    )
    assert (
        data_dictionary_entry["max_allowed_value"]
        == default_data_dictionary_entry["max_allowed_value"]
    )
    assert (
        data_dictionary_entry["min_allowed_value"]
        == default_data_dictionary_entry["min_allowed_value"]
    )
    assert (
        data_dictionary_entry["variable_unit"]
        == default_data_dictionary_entry["variable_unit"]
    )
    assert (
        data_dictionary_entry["allowed_values"]
        == default_data_dictionary_entry["allowed_values"]
    )
    assert (
        data_dictionary_entry["allowed_values_description"]
        == default_data_dictionary_entry["allowed_values_description"]
    )
    assert (
        data_dictionary_entry["table_name"]
        == default_data_dictionary_entry["table_name"]
    )
    assert "dataset_id" in data_dictionary_entry
    assert data_dictionary_entry["dataset_id"] == dataset_id


def test_get_data_dictionaries(
    client_with_logged_in_user, sample_dataset, default_data_dictionary_entry
):
    dataset_id = sample_dataset.id

    client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries",
        json=default_data_dictionary_entry,
    )

    response = client_with_logged_in_user.get(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries"
    )

    assert response.status_code == 200
    result = response.json()
    assert len(result) == 1

    data_dictionary_entry = result[0]
    assert (
        data_dictionary_entry["field_name"]
        == default_data_dictionary_entry["field_name"]
    )
    assert (
        data_dictionary_entry["description"]
        == default_data_dictionary_entry["description"]
    )
    assert (
        data_dictionary_entry["data_type"] == default_data_dictionary_entry["data_type"]
    )
    assert (
        data_dictionary_entry["personally_identifiable_variable"]
        == default_data_dictionary_entry["personally_identifiable_variable"]
    )
    assert (
        data_dictionary_entry["required"] == default_data_dictionary_entry["required"]
    )
    assert (
        data_dictionary_entry["max_allowed_value"]
        == default_data_dictionary_entry["max_allowed_value"]
    )
    assert (
        data_dictionary_entry["min_allowed_value"]
        == default_data_dictionary_entry["min_allowed_value"]
    )
    assert (
        data_dictionary_entry["variable_unit"]
        == default_data_dictionary_entry["variable_unit"]
    )
    assert (
        data_dictionary_entry["allowed_values"]
        == default_data_dictionary_entry["allowed_values"]
    )
    assert (
        data_dictionary_entry["allowed_values_description"]
        == default_data_dictionary_entry["allowed_values_description"]
    )

    assert (
        data_dictionary_entry["table_name"]
        == default_data_dictionary_entry["table_name"]
    )
    assert data_dictionary_entry["is_authentic_source"] == False
    assert "dataset_id" in data_dictionary_entry
    assert data_dictionary_entry["dataset_id"] == dataset_id


def test_delete_data_dictionaries(
    client_with_logged_in_user, sample_dataset, default_data_dictionary_entry
):
    dataset_id = sample_dataset.id

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries",
        json=default_data_dictionary_entry,
    )
    assert response.status_code == 201
    data_dictionary_entry = response.json()
    entry_id = data_dictionary_entry["id"]

    response = client_with_logged_in_user.delete(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries/{entry_id}"
    )
    assert response.status_code == 204

    response = client_with_logged_in_user.get(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries"
    )
    result = response.json()
    assert len(result) == 0


@pytest.mark.asyncio
async def test_bulk_upload_data_dictionaries(
    client_with_logged_in_user, sample_dataset
):
    dataset_id = sample_dataset.id

    csv_content = """field_name**,description**,data_type**,personally_identifiable_variable,required,max_allowed_value,min_allowed_value,variable_unit,allowed_values,allowed_values_description
test_field_1,Description for field 1,string,true,false,200,10,kg,"[1,2,3]","[1=Low, 2=Medium, 3=High]"
test_field_2,Description for field 2,string,false,true,150,5,m,"[4,5]","[4=Low, 5=High]"
"""
    file_mock = Mock(spec=UploadFile)
    file_mock.filename = "data_dictionary.csv"
    file_mock.file = io.BytesIO(csv_content.encode("utf-8"))

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries/bulk-upload",
        files={"file": ("data_dictionary.csv", file_mock.file, "text/csv")},
    )

    assert response.status_code == status.HTTP_201_CREATED, response.text
    result = response.json()

    assert "entries" in result
    assert len(result["entries"]) == 2
    assert result["message"] == "2 dictionary entries created successfully."

    entry_1 = result["entries"][0]
    assert entry_1["field_name"] == "test_field_1"
    assert entry_1["description"] == "Description for field 1"
    assert entry_1["data_type"] == "String"
    assert entry_1["personally_identifiable_variable"] is True
    assert entry_1["required"] is False
    assert entry_1["max_allowed_value"] == 200
    assert entry_1["min_allowed_value"] == 10
    assert entry_1["variable_unit"] == "kg"
    assert entry_1["allowed_values"] == "[1,2,3]"
    assert entry_1["allowed_values_description"] == "[1=Low, 2=Medium, 3=High]"
    assert entry_1["is_authentic_source"] is False


@pytest.mark.asyncio
async def test_bulk_upload_empty_file(client_with_logged_in_user, sample_dataset):
    dataset_id = sample_dataset.id

    file_mock = Mock(spec=UploadFile)
    file_mock.filename = "empty.csv"
    file_mock.file = io.BytesIO(b"")

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries/bulk-upload",
        files={"file": ("empty.csv", file_mock.file, "text/csv")},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.text
    result = response.json()
    assert "The uploaded CSV file is empty." in result["detail"]


@pytest.mark.asyncio
async def test_bulk_upload_invalid_headers(client_with_logged_in_user, sample_dataset):
    dataset_id = sample_dataset.id

    csv_content = "invalid_header1,invalid_header2\nvalue1,value2"
    file_mock = Mock(spec=UploadFile)
    file_mock.filename = "invalid_headers.csv"
    file_mock.file = io.BytesIO(csv_content.encode("utf-8"))

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries/bulk-upload",
        files={"file": ("invalid_headers.csv", file_mock.file, "text/csv")},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.text
    result = response.json()
    assert "The uploaded CSV file is missing required headers" in result["detail"]


@pytest.mark.asyncio
async def test_bulk_upload_invalid_row_data(client_with_logged_in_user, sample_dataset):
    dataset_id = sample_dataset.id

    # CSV with invalid boolean value - should now be caught by enhanced validation
    csv_content = """field_name**,description**,data_type**,table_name,personally_identifiable_variable,required,max_allowed_value,min_allowed_value,variable_unit,allowed_values,allowed_values_description
test_field,Description for field,string,test_table,invalid_boolean,true,100,10,kg,"[1,2,3]","[1=Low, 2=Medium, 3=High]"
"""
    file_mock = Mock(spec=UploadFile)
    file_mock.filename = "invalid_row_data.csv"
    file_mock.file = io.BytesIO(csv_content.encode("utf-8"))

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries/bulk-upload",
        files={"file": ("invalid_row_data.csv", file_mock.file, "text/csv")},
    )

    # Should now return 400 with detailed validation error
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    error_response = response.json()
    assert "CSV validation failed" in error_response["detail"]
    assert "invalid_boolean" in error_response["detail"]
    assert "must be 'true' or 'false'" in error_response["detail"]


@pytest.mark.asyncio
async def test_bulk_upload_duplicate_entries(
    client_with_logged_in_user, sample_dataset
):
    dataset_id = sample_dataset.id

    csv_content = """field_name**,description**,data_type**,personally_identifiable_variable,required,max_allowed_value,min_allowed_value,variable_unit,allowed_values,allowed_values_description
duplicate_field,Description 1,string,true,true,100,10,kg,"[1,2,3]","[1=Low, 2=Medium, 3=High]"
duplicate_field,Description 2,string,true,true,200,20,kg,"[4,5]","[4=Low, 5=High]"
"""
    file_mock = Mock(spec=UploadFile)
    file_mock.filename = "duplicate_entries.csv"
    file_mock.file = io.BytesIO(csv_content.encode("utf-8"))

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries/bulk-upload",
        files={"file": ("duplicate_entries.csv", file_mock.file, "text/csv")},
    )

    assert response.status_code == status.HTTP_201_CREATED, response.text
    result = response.json()
    assert len(result["entries"]) == 1
    assert len(result["skipped_entries"]) == 1


@pytest.mark.asyncio
async def test_bulk_upload_non_csv_file(client_with_logged_in_user, sample_dataset):
    dataset_id = sample_dataset.id

    file_mock = Mock(spec=UploadFile)
    file_mock.filename = "not_a_csv.txt"
    file_mock.file = io.BytesIO(b"This is not a CSV file.")

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries/bulk-upload",
        files={"file": ("not_a_csv.txt", file_mock.file, "text/plain")},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.text
    result = response.json()
    assert "The uploaded file is not a valid CSV file." in result["detail"]


def test_bulk_update_authentic_source_route_success(
    client_with_logged_in_user,
    sample_dataset,
    default_data_dictionary_entry,
    db_session,
):
    dataset_id = sample_dataset.id

    # Create some data dictionary entries first
    entry1_data = default_data_dictionary_entry.copy()
    entry1_data["field_name"] = "test_field_1"
    response1 = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries",
        json=entry1_data,
    )
    assert response1.status_code == 201
    entry1 = response1.json()

    entry2_data = default_data_dictionary_entry.copy()
    entry2_data["field_name"] = "test_field_2"
    response2 = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries",
        json=entry2_data,
    )
    assert response2.status_code == 201
    entry2 = response2.json()

    sample_dataset.status = "PUBLISHED"
    db_session.add(sample_dataset)
    db_session.commit()

    update_data = {
        "entries": [
            {"entry_id": entry1["id"], "is_authentic_source": True},
            {"entry_id": entry2["id"], "is_authentic_source": False},
        ]
    }
    # Make the bulk update request
    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries/bulk-update-authentic-source",
        json=update_data,
    )

    assert response.status_code == 200
    result = response.json()

    # Verify response contains updated entries
    assert len(result) == 2
    # Find entries by ID and verify their authentic source flags
    updated_entry1 = next(e for e in result if e["id"] == entry1["id"])
    updated_entry2 = next(e for e in result if e["id"] == entry2["id"])
    assert updated_entry1["is_authentic_source"] is True
    assert updated_entry2["is_authentic_source"] is False


def test_bulk_update_positions_route_success(
    client_with_logged_in_user,
    sample_dataset,
    default_data_dictionary_entry,
):
    dataset_id = sample_dataset.id

    # Create some data dictionary entries first
    entry1_data = default_data_dictionary_entry.copy()
    entry1_data["field_name"] = "test_field_1"
    response1 = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries",
        json=entry1_data,
    )
    assert response1.status_code == 201
    entry1 = response1.json()

    entry2_data = default_data_dictionary_entry.copy()
    entry2_data["field_name"] = "test_field_2"
    response2 = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries",
        json=entry2_data,
    )
    assert response2.status_code == 201
    entry2 = response2.json()

    entry3_data = default_data_dictionary_entry.copy()
    entry3_data["field_name"] = "test_field_3"
    response3 = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries",
        json=entry3_data,
    )
    assert response3.status_code == 201
    entry3 = response3.json()

    # Update positions
    update_data = {
        "updates": [
            {"entry_id": entry1["id"], "position": 2},
            {"entry_id": entry2["id"], "position": 0},
            {"entry_id": entry3["id"], "position": 1},
        ]
    }

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries/bulk-update-positions",
        json=update_data,
    )

    assert response.status_code == 200
    result = response.json()

    # Verify response contains updated entries
    assert len(result) == 3

    # Find entries by ID and verify their positions
    updated_entry1 = next(e for e in result if e["id"] == entry1["id"])
    updated_entry2 = next(e for e in result if e["id"] == entry2["id"])
    updated_entry3 = next(e for e in result if e["id"] == entry3["id"])

    assert updated_entry1["position"] == 2
    assert updated_entry2["position"] == 0
    assert updated_entry3["position"] == 1

    # Verify entries are returned in correct order (by position)
    assert result[0]["position"] == 0
    assert result[1]["position"] == 1
    assert result[2]["position"] == 2


def test_bulk_update_positions_entry_not_in_dataset(
    client_with_logged_in_user,
    sample_dataset,
    default_data_dictionary_entry,
):
    dataset_id = sample_dataset.id

    # Create one data dictionary entry
    entry1_data = default_data_dictionary_entry.copy()
    entry1_data["field_name"] = "test_field_1"
    response1 = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries",
        json=entry1_data,
    )
    assert response1.status_code == 201
    entry1 = response1.json()

    # Try to update a non-existent entry
    update_data = {
        "updates": [
            {"entry_id": entry1["id"], "position": 0},
            {"entry_id": 999999, "position": 1},  # Non-existent entry
        ]
    }

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries/bulk-update-positions",
        json=update_data,
    )

    assert response.status_code == 404
    assert "Entry 999999 not found" in response.json()["detail"]


def test_bulk_update_positions_invalid_position(
    client_with_logged_in_user,
    sample_dataset,
    default_data_dictionary_entry,
):
    dataset_id = sample_dataset.id

    # Create one data dictionary entry
    entry1_data = default_data_dictionary_entry.copy()
    entry1_data["field_name"] = "test_field_1"
    response1 = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries",
        json=entry1_data,
    )
    assert response1.status_code == 201
    entry1 = response1.json()

    # Try to update with negative position
    update_data = {
        "updates": [
            {"entry_id": entry1["id"], "position": -1},  # Invalid negative position
        ]
    }

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries/bulk-update-positions",
        json=update_data,
    )

    assert response.status_code == 422  # Validation error


def test_get_data_dictionaries_ordered_by_position(
    client_with_logged_in_user,
    sample_dataset,
    default_data_dictionary_entry,
):
    dataset_id = sample_dataset.id

    # Create entries
    entry1_data = default_data_dictionary_entry.copy()
    entry1_data["field_name"] = "field_c"
    response1 = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries",
        json=entry1_data,
    )
    entry1 = response1.json()

    entry2_data = default_data_dictionary_entry.copy()
    entry2_data["field_name"] = "field_a"
    response2 = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries",
        json=entry2_data,
    )
    entry2 = response2.json()

    entry3_data = default_data_dictionary_entry.copy()
    entry3_data["field_name"] = "field_b"
    response3 = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries",
        json=entry3_data,
    )
    entry3 = response3.json()

    # Set positions
    update_data = {
        "updates": [
            {"entry_id": entry1["id"], "position": 2},
            {"entry_id": entry2["id"], "position": 0},
            {"entry_id": entry3["id"], "position": 1},
        ]
    }

    client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries/bulk-update-positions",
        json=update_data,
    )

    # Get entries and verify order
    response = client_with_logged_in_user.get(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries"
    )

    assert response.status_code == 200
    result = response.json()

    # Entries should be ordered by position
    assert result[0]["field_name"] == "field_a"  # position 0
    assert result[1]["field_name"] == "field_b"  # position 1
    assert result[2]["field_name"] == "field_c"  # position 2


def test_update_data_dictionary_entry(
    client_with_logged_in_user, sample_dataset, default_data_dictionary_entry
):
    dataset_id = sample_dataset.id

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries",
        json=default_data_dictionary_entry,
    )
    assert response.status_code == 201
    created_entry = response.json()
    entry_id = created_entry["id"]

    updated_data = {
        "field_name": "updated_field_name",
        "description": "Updated description",
        "data_type": "Integer",
        "personally_identifiable_variable": False,
        "required": True,
        "max_allowed_value": 200,
        "min_allowed_value": 5,
        "variable_unit": "meters",
        "allowed_values": "[4, 5, 6]",
        "allowed_values_description": "[4=Four, 5=Five, 6=Six]",
        "table_name": "updated_table",
        "privacy_risk_type": "Identifiant direct",
    }

    response = client_with_logged_in_user.put(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries/{entry_id}",
        json=updated_data,
    )

    assert response.status_code == 200, response.text
    updated_entry = response.json()

    assert updated_entry["field_name"] == updated_data["field_name"]
    assert updated_entry["description"] == updated_data["description"]
    assert updated_entry["data_type"] == updated_data["data_type"]
    assert (
        updated_entry["personally_identifiable_variable"]
        == updated_data["personally_identifiable_variable"]
    )
    assert updated_entry["required"] == updated_data["required"]
    assert updated_entry["max_allowed_value"] == updated_data["max_allowed_value"]
    assert updated_entry["min_allowed_value"] == updated_data["min_allowed_value"]
    assert updated_entry["variable_unit"] == updated_data["variable_unit"]
    assert updated_entry["allowed_values"] == updated_data["allowed_values"]
    assert (
        updated_entry["allowed_values_description"]
        == updated_data["allowed_values_description"]
    )
    assert updated_entry["table_name"] == updated_data["table_name"]
    assert updated_entry["dataset_id"] == dataset_id
    assert updated_entry["id"] == entry_id


def test_update_data_dictionary_entry_duplicate_field_name(
    client_with_logged_in_user, sample_dataset, default_data_dictionary_entry
):
    dataset_id = sample_dataset.id

    entry1_data = default_data_dictionary_entry.copy()
    entry1_data["field_name"] = "first_field"
    response1 = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries",
        json=entry1_data,
    )
    assert response1.status_code == 201
    entry1 = response1.json()

    entry2_data = default_data_dictionary_entry.copy()
    entry2_data["field_name"] = "second_field"
    response2 = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries",
        json=entry2_data,
    )
    assert response2.status_code == 201
    entry2 = response2.json()

    updated_data = entry2_data.copy()
    updated_data["field_name"] = "first_field"

    response = client_with_logged_in_user.put(
        f"/api/v1/datasets/{dataset_id}/data-dictionaries/{entry2['id']}",
        json=updated_data,
    )

    assert response.status_code == 400, response.text
    error_response = response.json()
    assert "already exists" in error_response["detail"].lower()
