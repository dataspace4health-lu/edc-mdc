import pytest
import csv
from unittest.mock import Mock, AsyncMock, MagicMock
from models.data_dictionary import DataDictionaryEntry
from models.identity_context import IdentityContext
from schemas.data_dictionary import (
    AddDataDictionaryEntry,
    BulkUpdateAuthenticSourceDto,
    UpdateAuthenticSourceDto,
    BulkUpdatePositionDto,
    UpdatePositionDto,
)
from repositories.data_dictionary import DataDictionaryRepository
from services.data_dictionary import DataDictionaryService
from services.database_session_manager import DatabaseSessionManager
from services.activity_logs.dataset_activity_log import DatasetActivityLogService
from services.activity_logs.data_dictionary_activity_log import (
    DataDictionaryActivityLogService,
)
from services.dataset_permissions_service import DatasetPermissionsService
from schemas.data_dictionary import (
    data_dictionary_entity_to_resource,
)
from deepdiff import DeepDiff
from fastapi import UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from io import StringIO
from factories.data_dictionary_entry import create_sample_data_dictionary_entry


@pytest.fixture
def data_dictionary_service() -> DataDictionaryService:
    return DataDictionaryService(
        repository=Mock(spec=DataDictionaryRepository),
        database_session_manager=Mock(spec=DatabaseSessionManager),
        activity_log_service=Mock(spec=DatasetActivityLogService),
        dataset_permissions_service=Mock(spec=DatasetPermissionsService),
        data_dictionary_activity_log_service=Mock(
            spec=DataDictionaryActivityLogService
        ),
    )


@pytest.fixture
def expected_data_dictionary() -> DataDictionaryEntry:
    entry = create_sample_data_dictionary_entry(dataset_id=1)
    entry.id = 1
    return entry


@pytest.fixture
def authentic_source_entry() -> DataDictionaryEntry:
    entry = create_sample_data_dictionary_entry(
        dataset_id=1, field_name="authentic_field"
    )
    entry.id = 2
    entry.is_authentic_source = True
    return entry


def test_get_data_dictionaries_by_dataset_id(
    expected_data_dictionary: DataDictionaryEntry,
    data_dictionary_service: DataDictionaryService,
):
    dataset_id = 1
    data_dictionaries = [expected_data_dictionary]
    data_dictionary_service._repository.get_data_dictionaries_by_dataset_id.return_value = (
        data_dictionaries
    )

    expected_resources = [
        data_dictionary_entity_to_resource(dd) for dd in data_dictionaries
    ]

    actual = data_dictionary_service.get_data_dictionaries_by_dataset_id(
        dataset_id, None
    )

    assert not DeepDiff(expected_resources, actual, ignore_order=True)

    data_dictionary_service._repository.get_data_dictionaries_by_dataset_id.assert_called_once_with(
        dataset_id
    )


def test_add_data_dictionary(data_dictionary_service: DataDictionaryService):
    data_dictionary_service._repository.get_existing_entry = Mock(return_value=None)
    data_dictionary_service._repository.add = Mock()

    identity = IdentityContext(user_id=1, permissions=[])
    dataset_id = 1
    add_data_dictionary_entry = AddDataDictionaryEntry(
        field_name="test_field",
        description="Test description",
        data_type="string",
        personally_identifiable_variable=True,
        required=False,
        max_allowed_value=100,
        min_allowed_value=1,
        variable_unit="kg",
        allowed_values="[1, 2, 3]",
        allowed_values_description="[1=One, 2=Two, 3=Three]",
        table_name="test_table",
        privacy_risk_type="Quasi-identifiant",
    )

    data_dictionary_service.add_data_dictionary(
        dataset_id, add_data_dictionary_entry, identity
    )

    added_entry = data_dictionary_service._repository.add.call_args[0][0]

    assert add_data_dictionary_entry.field_name == added_entry.field_name
    assert add_data_dictionary_entry.description == added_entry.description
    assert add_data_dictionary_entry.data_type == added_entry.data_type
    assert (
        add_data_dictionary_entry.personally_identifiable_variable
        == added_entry.personally_identifiable_variable
    )
    assert add_data_dictionary_entry.required == added_entry.required
    assert add_data_dictionary_entry.max_allowed_value == added_entry.max_allowed_value
    assert add_data_dictionary_entry.min_allowed_value == added_entry.min_allowed_value
    assert add_data_dictionary_entry.variable_unit == added_entry.variable_unit
    assert add_data_dictionary_entry.allowed_values == added_entry.allowed_values
    assert (
        add_data_dictionary_entry.allowed_values_description
        == added_entry.allowed_values_description
    )
    assert add_data_dictionary_entry.table_name == added_entry.table_name
    assert False == added_entry.is_authentic_source
    assert dataset_id == added_entry.dataset_id

    data_dictionary_service._repository.add.assert_called_once()

    data_dictionary_service._activity_log_service.log_dictionary_item_activities.assert_called_once_with(
        identity.user_id,
        dataset_id,
        "data_dictionaries.test_field",
        None,
        {
            "field_name": "test_field",
            "description": "Test description",
            "data_type": "String",
            "personally_identifiable_variable": True,
            "required": False,
            "max_allowed_value": 100.0,
            "min_allowed_value": 1.0,
            "variable_unit": "kg",
            "allowed_values": "[1, 2, 3]",
            "allowed_values_description": "[1=One, 2=Two, 3=Three]",
            "table_name": "test_table",
            "is_authentic_source": False,
            "privacy_risk_type": "Quasi-identifiant",
        },
    )


def test_delete_data_dictionaries_by_dataset_id(
    expected_data_dictionary: DataDictionaryEntry,
    data_dictionary_service: DataDictionaryService,
):
    identity = IdentityContext(user_id=1, permissions=[])
    dataset_id = 2
    entry_id = 1

    data_dictionary_service._repository.get_data_dictionary_entry.return_value = (
        expected_data_dictionary
    )

    data_dictionary_service.delete_data_dictionary_entry(dataset_id, entry_id, identity)

    data_dictionary_service._repository.delete_entry_by_id.assert_called_once_with(
        entry_id
    )
    data_dictionary_service._activity_log_service.log_dictionary_item_activities.assert_called_once_with(
        identity.user_id,
        dataset_id,
        "data_dictionaries.test_field",
        {
            "field_name": "test_field",
            "description": "Test description",
            "data_type": "string",
            "personally_identifiable_variable": True,
            "required": False,
            "max_allowed_value": 100.0,
            "min_allowed_value": 1.0,
            "variable_unit": "kg",
            "allowed_values": "[1, 2, 3]",
            "allowed_values_description": "[1=One, 2=Two, 3=Three]",
            "table_name": "test_table",
            "is_authentic_source": False,
            "privacy_risk_type": "low",
        },
        None,
    )


@pytest.mark.asyncio
async def test_bulk_upload_data_dictionaries(
    data_dictionary_service: DataDictionaryService,
):
    identity = IdentityContext(user_id=1, permissions=[])
    dataset_id = 1

    data_dictionary_service._repository.get_data_dictionaries_by_dataset_id.return_value = (
        []
    )
    data_dictionary_service._repository.add_bulk = Mock()
    data_dictionary_service._database_session_manager.commit = Mock()

    csv_content = """field_name**,description**,data_type**,personally_identifiable_variable,required,max_allowed_value,min_allowed_value,variable_unit,allowed_values,allowed_values_description,
test_field_2,Description for field,string,true,false,200,10,kg,"[1,2]","[1=Low, 2=High]"
"""
    file_mock = Mock(spec=UploadFile)
    file_mock.filename = "test.csv"
    file_mock.read = AsyncMock(return_value=csv_content.encode("utf-8"))

    response = await data_dictionary_service.bulk_upload_data_dictionaries(
        dataset_id, file_mock, identity
    )

    data_dictionary_service._repository.add_bulk.assert_called_once()
    data_dictionary_service._database_session_manager.commit.assert_called_once()

    assert response["message"] == "1 dictionary entries created successfully."
    assert len(response["entries"]) == 1
    assert response["entries"][0].field_name == "test_field_2"
    assert response["entries"][0].description == "Description for field"
    assert response["entries"][0].data_type == "String"
    assert response["entries"][0].personally_identifiable_variable is True
    assert response["entries"][0].required is False
    assert response["entries"][0].max_allowed_value == 200
    assert response["entries"][0].min_allowed_value == 10
    assert response["entries"][0].variable_unit == "kg"
    assert response["entries"][0].allowed_values == "[1,2]"
    assert response["entries"][0].allowed_values_description == "[1=Low, 2=High]"
    assert response["entries"][0].is_authentic_source is None

    assert response["skipped_entries"] == []
    assert response["validation_errors"] == []


@pytest.mark.asyncio
async def test_bulk_upload_empty_csv(data_dictionary_service: DataDictionaryService):
    identity = IdentityContext(user_id=1, permissions=[])
    dataset_id = 1

    csv_content = ""
    file_mock = Mock(spec=UploadFile)
    file_mock.filename = "empty.csv"
    file_mock.read = AsyncMock(return_value=csv_content.encode("utf-8"))

    with pytest.raises(HTTPException) as excinfo:
        await data_dictionary_service.bulk_upload_data_dictionaries(
            dataset_id, file_mock, identity
        )

    assert excinfo.value.status_code == 400
    assert "The uploaded CSV file is empty." in excinfo.value.detail


@pytest.mark.asyncio
async def test_generate_csv(
    data_dictionary_service: DataDictionaryService,
    expected_data_dictionary: DataDictionaryEntry,
):
    dataset_id = 1
    identity = IdentityContext(user_id=1, permissions=[])

    data_dictionary_service._repository.get_data_dictionaries_by_dataset_id.return_value = [
        expected_data_dictionary
    ]

    response = data_dictionary_service.generate_csv(dataset_id, identity)

    data_dictionary_service._dataset_permissions_service.validate_read_permissions.assert_called_once_with(
        dataset_id, identity
    )

    data_dictionary_service._repository.get_data_dictionaries_by_dataset_id.assert_called_once_with(
        dataset_id
    )

    assert isinstance(response, StreamingResponse)
    assert response.media_type == "text/csv"
    assert (
        response.headers["Content-Disposition"]
        == f"attachment; filename=data_dictionary_dataset_{dataset_id}.csv"
    )

    content = ""
    async for chunk in response.body_iterator:
        content += chunk

    csv_reader = csv.DictReader(StringIO(content))

    rows = list(csv_reader)
    assert len(rows) == 1

    row = rows[0]
    expected_headers = [
        "field_name**",
        "description**",
        "data_type**",
        "personally_identifiable_variable",
        "required",
        "max_allowed_value",
        "min_allowed_value",
        "variable_unit",
        "allowed_values",
        "allowed_values_description",
        "is_authentic_source",
    ]
    for header in expected_headers:
        assert header in row

    assert row["field_name**"] == expected_data_dictionary.field_name
    assert row["description**"] == expected_data_dictionary.description
    assert row["data_type**"] == expected_data_dictionary.data_type
    assert row["personally_identifiable_variable"] == "true"  # Boolean to string
    assert row["required"] == "false"  # Boolean to string
    assert row["max_allowed_value"] == str(expected_data_dictionary.max_allowed_value)
    assert row["min_allowed_value"] == str(expected_data_dictionary.min_allowed_value)
    assert row["variable_unit"] == expected_data_dictionary.variable_unit
    assert row["allowed_values"] == expected_data_dictionary.allowed_values
    assert (
        row["allowed_values_description"]
        == expected_data_dictionary.allowed_values_description
    )
    assert row["is_authentic_source"] == "false"


@pytest.mark.asyncio
async def test_generate_csv_with_authentic_source_labels(
    data_dictionary_service: DataDictionaryService,
    expected_data_dictionary: DataDictionaryEntry,
    authentic_source_entry: DataDictionaryEntry,
):

    class MockLabel:
        def __init__(self, name, description=None):
            self.name = name
            self.description = description

    class MockAuthenticSourceAssignment:
        def __init__(self, label):
            self.label = label

    dataset_id = 1
    identity = IdentityContext(user_id=1, permissions=[])

    # Create mock label and assignment
    mock_label = MockLabel("Primary Source", "Official government database")
    mock_assignment = MockAuthenticSourceAssignment(mock_label)

    # Setup repository mocks
    data_dictionary_service._repository.get_data_dictionaries_by_dataset_id.return_value = [
        expected_data_dictionary,  # Regular entry (not authentic source)
        authentic_source_entry,  # Authentic source entry
    ]

    # Mock the get_active_authentic_source_assignment method
    def mock_get_active_assignment(entry_id):
        if entry_id == authentic_source_entry.id:
            return mock_assignment
        return None

    data_dictionary_service._repository.get_active_authentic_source_assignment = Mock(
        side_effect=mock_get_active_assignment
    )

    # Generate CSV
    response = data_dictionary_service.generate_csv(dataset_id, identity)

    # Verify permissions were checked
    data_dictionary_service._dataset_permissions_service.validate_read_permissions.assert_called_once_with(
        dataset_id, identity
    )

    # Verify repository was called
    data_dictionary_service._repository.get_data_dictionaries_by_dataset_id.assert_called_once_with(
        dataset_id
    )

    # Verify the assignment lookup was called for the authentic source entry
    data_dictionary_service._repository.get_active_authentic_source_assignment.assert_called_once_with(
        authentic_source_entry.id
    )

    # Verify response properties
    assert isinstance(response, StreamingResponse)
    assert response.media_type == "text/csv"
    assert (
        response.headers["Content-Disposition"]
        == f"attachment; filename=data_dictionary_dataset_{dataset_id}.csv"
    )

    # Read and parse the CSV content
    content = ""
    async for chunk in response.body_iterator:
        content += chunk

    csv_reader = csv.DictReader(StringIO(content))
    rows = list(csv_reader)
    assert len(rows) == 2

    # Check regular entry (not authentic source)
    regular_row = next(
        row
        for row in rows
        if row["field_name**"] == expected_data_dictionary.field_name
    )
    assert regular_row["is_authentic_source"] == "false"

    # Check authentic source entry with label
    authentic_row = next(
        row for row in rows if row["field_name**"] == authentic_source_entry.field_name
    )
    assert (
        authentic_row["is_authentic_source"]
        == "Primary Source - Official government database"
    )


def test_bulk_update_authentic_source_success(
    data_dictionary_service: DataDictionaryService,
    expected_data_dictionary: DataDictionaryEntry,
):
    identity = IdentityContext(user_id=1, permissions=[])
    dataset_id = 1

    second_entry = create_sample_data_dictionary_entry(
        dataset_id=dataset_id, field_name="second_field"
    )
    second_entry.id = 2

    data_dictionary_service._repository.get_data_dictionaries_by_dataset_id.return_value = [
        expected_data_dictionary,
        second_entry,
    ]
    data_dictionary_service._repository.bulk_update_authentic_source = Mock()

    update_data = BulkUpdateAuthenticSourceDto(
        entries=[
            UpdateAuthenticSourceDto(entry_id=1, is_authentic_source=True),
            UpdateAuthenticSourceDto(entry_id=2, is_authentic_source=False),
        ]
    )
    # Call the method
    result = data_dictionary_service.bulk_update_authentic_source(
        dataset_id, update_data, identity
    )

    data_dictionary_service._repository.bulk_update_authentic_source.assert_called_once_with(
        [(1, True), (2, False)]
    )
    data_dictionary_service._database_session_manager.commit.assert_called_once()
    # Verify the method returns updated entries (through get_data_dictionaries_by_dataset_id)
    assert len(result) == 2


def test_copy_data_dictionaries(data_dictionary_service: DataDictionaryService):
    source_id, target_id = 1, 2
    identity = IdentityContext(user_id=1, permissions=[])
    src1 = create_sample_data_dictionary_entry(dataset_id=source_id, field_name="a")
    src1.id = 10
    src2 = create_sample_data_dictionary_entry(dataset_id=source_id, field_name="b")
    src2.id = 11

    data_dictionary_service._repository.get_data_dictionaries_by_dataset_id.return_value = [
        src1,
        src2,
    ]
    data_dictionary_service._repository.add = Mock()
    data_dictionary_service._database_session_manager.commit = Mock()
    data_dictionary_service._dataset_permissions_service.validate_edit_permissions = (
        Mock()
    )

    result = data_dictionary_service.copy_data_dictionaries(
        source_dataset_id=source_id,
        target_dataset_id=target_id,
        identity=identity,
        preserve_authentic_source=True,
    )

    data_dictionary_service._dataset_permissions_service.validate_edit_permissions.assert_called_once_with(
        target_id, identity
    )
    data_dictionary_service._repository.get_data_dictionaries_by_dataset_id.assert_called_once_with(
        source_id
    )
    assert data_dictionary_service._repository.add.call_count == 2
    added = [
        args[0] for args, _ in data_dictionary_service._repository.add.call_args_list
    ]
    assert {e.field_name for e in added} == {"a", "b"}
    assert all(e.dataset_id == target_id for e in added)
    data_dictionary_service._database_session_manager.commit.assert_called_once()
    assert result is None


@pytest.mark.asyncio
async def test_bulk_upload_data_dictionaries_full_flow(
    data_dictionary_service: DataDictionaryService,
):
    identity = IdentityContext(user_id=1, permissions=[])
    dataset_id = 1

    # Example of a valid CSV content
    csv_content = (
        "field_name**,description**,data_type**,personally_identifiable_variable,required,"
        "max_allowed_value,min_allowed_value,variable_unit,allowed_values,allowed_values_description\n"
        'field1,desc1,string,true,false,100,10,kg,"[1,2]","desc allowed"\n'
        'field2,desc2,integer,false,true,200,20,m,"[3,4]","desc allowed 2"\n'
    )

    file_mock = MagicMock(spec=UploadFile)
    file_mock.filename = "upload.csv"
    file_mock.read = AsyncMock(return_value=csv_content.encode("utf-8"))

    # Mock permission validation method
    data_dictionary_service._dataset_permissions_service.validate_edit_permissions = (
        MagicMock()
    )

    # We assume _parse_csv_file is used as is or mocked if needed

    # Simulate no existing entries in dataset
    data_dictionary_service._repository.get_data_dictionaries_by_dataset_id = MagicMock(
        return_value=[]
    )

    # Mock _process_csv_rows to return two new entries, no skipped entries or validation errors
    entry1 = create_sample_data_dictionary_entry(
        dataset_id=dataset_id, field_name="field1"
    )
    entry2 = create_sample_data_dictionary_entry(
        dataset_id=dataset_id, field_name="field2"
    )
    entries = [entry1, entry2]
    skipped_entries = []
    validation_errors = []
    data_dictionary_service._process_csv_rows = MagicMock(
        return_value=(entries, skipped_entries, validation_errors)
    )

    # Mock add_bulk and commit methods
    data_dictionary_service._repository.add_bulk = MagicMock()
    data_dictionary_service._database_session_manager.commit = MagicMock()
    data_dictionary_service._database_session_manager.rollback = MagicMock()

    # Mock _log_activity to track calls
    data_dictionary_service._log_activity = MagicMock()

    # Call the method under test
    result = await data_dictionary_service.bulk_upload_data_dictionaries(
        dataset_id, file_mock, identity
    )

    # Permission validation called once with correct parameters
    data_dictionary_service._dataset_permissions_service.validate_edit_permissions.assert_called_once_with(
        dataset_id, identity
    )

    # add_bulk called once with the entries returned by _process_csv_rows
    data_dictionary_service._repository.add_bulk.assert_called_once_with(entries)

    # commit called once after successful insert
    data_dictionary_service._database_session_manager.commit.assert_called_once()

    # rollback never called since no error occurred
    data_dictionary_service._database_session_manager.rollback.assert_not_called()

    # _log_activity called once per entry
    assert data_dictionary_service._log_activity.call_count == len(entries)
    for call_args in data_dictionary_service._log_activity.call_args_list:
        user_id, ds_id, old_val, new_val = call_args[0]
        assert user_id == identity.user_id
        assert ds_id == dataset_id
        assert old_val is None
        assert new_val in entries

    # Result contains the correct success message
    assert (
        result["message"] == f"{len(entries)} dictionary entries created successfully."
    )
    assert len(result["entries"]) == len(entries)
    assert result["skipped_entries"] == skipped_entries
    assert result["validation_errors"] == validation_errors

    # Verify the returned entries have the expected field_names
    for res_entry, orig_entry in zip(result["entries"], entries):
        assert res_entry.field_name == orig_entry.field_name


@pytest.mark.asyncio
async def test_bulk_upload_data_dictionaries_raises_and_rollbacks(
    data_dictionary_service: DataDictionaryService,
):
    identity = IdentityContext(user_id=1, permissions=[])
    dataset_id = 1

    # Mock an empty or invalid CSV file causing parsing failure
    file_mock = MagicMock(spec=UploadFile)
    file_mock.filename = "empty.csv"
    file_mock.read = AsyncMock(return_value=b"")

    # Mock permission validation method
    data_dictionary_service._dataset_permissions_service.validate_edit_permissions = (
        MagicMock()
    )

    # Mock _parse_csv_file to raise an exception simulating parse error
    data_dictionary_service._parse_csv_file = AsyncMock(
        side_effect=Exception("parse error")
    )

    # Mock rollback method to verify it is called on error
    data_dictionary_service._database_session_manager.rollback = MagicMock()

    # Expect HTTPException with status 400 on error
    with pytest.raises(HTTPException) as exc_info:
        await data_dictionary_service.bulk_upload_data_dictionaries(
            dataset_id, file_mock, identity
        )

    # Verify rollback was called after error
    data_dictionary_service._database_session_manager.rollback.assert_called_once()

    # Verify HTTPException status code and message content
    assert exc_info.value.status_code == 400
    assert "Error processing CSV file" in exc_info.value.detail


@pytest.mark.asyncio
async def test_parse_csv_file_with_special_characters(
    data_dictionary_service: DataDictionaryService,
):
    # CSV content with special characters (e.g., accented letters)
    csv_content = """field_name**,description**,data_type**
café,Description with é,string
niño,Description with ñ,integer"""

    file_mock = Mock(spec=UploadFile)
    file_mock.filename = "test_special_chars.csv"

    # Test with Latin-1 encoding (which contains the special characters)
    file_mock.read = AsyncMock(return_value=csv_content.encode("latin-1"))

    reader = await data_dictionary_service._parse_csv_file(file_mock)

    # Verify the reader was created successfully and can read the content
    rows = list(reader)
    assert len(rows) == 2
    assert rows[0]["field_name**"] == "café"
    assert rows[0]["description**"] == "Description with é"
    assert rows[1]["field_name**"] == "niño"
    assert rows[1]["description**"] == "Description with ñ"


def test_get_data_dictionaries_ordered_by_position(
    data_dictionary_service: DataDictionaryService,
):
    """Test that entries are returned ordered by position (nulls last), then by id"""
    dataset_id = 1

    # Create entries with mixed positions
    entry1 = create_sample_data_dictionary_entry(
        dataset_id=dataset_id, field_name="field1", position=2
    )
    entry1.id = 1
    entry2 = create_sample_data_dictionary_entry(
        dataset_id=dataset_id, field_name="field2", position=0
    )
    entry2.id = 2
    entry3 = create_sample_data_dictionary_entry(
        dataset_id=dataset_id, field_name="field3", position=None
    )
    entry3.id = 3
    entry4 = create_sample_data_dictionary_entry(
        dataset_id=dataset_id, field_name="field4", position=1
    )
    entry4.id = 4
    entry5 = create_sample_data_dictionary_entry(
        dataset_id=dataset_id, field_name="field5", position=None
    )
    entry5.id = 5

    # Mock repository to return entries in the expected order
    # Order should be: position 0, 1, 2, then null (by id: 3, 5)
    expected_order = [entry2, entry4, entry1, entry3, entry5]
    data_dictionary_service._repository.get_data_dictionaries_by_dataset_id.return_value = (
        expected_order
    )

    result = data_dictionary_service.get_data_dictionaries_by_dataset_id(
        dataset_id, None
    )

    # Verify the order is maintained
    assert len(result) == 5
    assert result[0].field_name == "field2"  # position 0
    assert result[1].field_name == "field4"  # position 1
    assert result[2].field_name == "field1"  # position 2
    assert result[3].field_name == "field3"  # position None, id 3
    assert result[4].field_name == "field5"  # position None, id 5


def test_add_data_dictionary_sets_position_to_none(
    data_dictionary_service: DataDictionaryService,
):
    data_dictionary_service._repository.get_existing_entry = Mock(return_value=None)
    data_dictionary_service._repository.add = Mock()

    identity = IdentityContext(user_id=1, permissions=[])
    dataset_id = 1
    add_data_dictionary_entry = AddDataDictionaryEntry(
        field_name="new_field",
        description="New field description",
        data_type="string",
        personally_identifiable_variable=False,
        required=True,
        max_allowed_value=None,
        min_allowed_value=None,
        variable_unit=None,
        allowed_values=None,
        allowed_values_description=None,
        table_name="test_table",
        privacy_risk_type="",
    )

    data_dictionary_service.add_data_dictionary(
        dataset_id, add_data_dictionary_entry, identity
    )

    # Verify the added entry has position=None
    added_entry = data_dictionary_service._repository.add.call_args[0][0]
    assert added_entry.position is None


def test_bulk_update_positions_success(
    data_dictionary_service: DataDictionaryService,
):
    identity = IdentityContext(user_id=1, permissions=[])
    dataset_id = 1

    entry1 = create_sample_data_dictionary_entry(
        dataset_id=dataset_id, field_name="field1", position=None
    )
    entry1.id = 1
    entry2 = create_sample_data_dictionary_entry(
        dataset_id=dataset_id, field_name="field2", position=None
    )
    entry2.id = 2
    entry3 = create_sample_data_dictionary_entry(
        dataset_id=dataset_id, field_name="field3", position=None
    )
    entry3.id = 3

    # Mock repository to return entries
    data_dictionary_service._repository.get_data_dictionaries_by_dataset_id.return_value = [
        entry1,
        entry2,
        entry3,
    ]

    update_data = BulkUpdatePositionDto(
        updates=[
            UpdatePositionDto(entry_id=1, position=2),
            UpdatePositionDto(entry_id=2, position=0),
            UpdatePositionDto(entry_id=3, position=1),
        ]
    )

    result = data_dictionary_service.bulk_update_positions(
        dataset_id, update_data, identity
    )

    # Verify permissions were validated
    data_dictionary_service._dataset_permissions_service.validate_edit_permissions.assert_called_once_with(
        dataset_id, identity
    )

    # Verify entries were updated
    assert entry1.position == 2
    assert entry2.position == 0
    assert entry3.position == 1

    # Verify activity log was called
    data_dictionary_service._data_dictionary_activity_log_service.log_order_change.assert_called_once_with(
        identity.user_id, dataset_id
    )

    # Verify commit was called
    data_dictionary_service._database_session_manager.commit.assert_called_once()

    # Verify result is returned
    assert len(result) == 3


def test_bulk_update_positions_entry_not_found(
    data_dictionary_service: DataDictionaryService,
):
    identity = IdentityContext(user_id=1, permissions=[])
    dataset_id = 1

    entry1 = create_sample_data_dictionary_entry(
        dataset_id=dataset_id, field_name="field1", position=None
    )
    entry1.id = 1

    # Mock repository to return only one entry
    data_dictionary_service._repository.get_data_dictionaries_by_dataset_id.return_value = [
        entry1
    ]

    # Try to update an entry that doesn't exist in this dataset
    update_data = BulkUpdatePositionDto(
        updates=[
            UpdatePositionDto(entry_id=1, position=0),
            UpdatePositionDto(entry_id=999, position=1),  # Non-existent entry
        ]
    )

    with pytest.raises(HTTPException) as excinfo:
        data_dictionary_service.bulk_update_positions(dataset_id, update_data, identity)

    assert excinfo.value.status_code == 404
    assert "Entry 999 not found in dataset 1" in excinfo.value.detail


def test_bulk_update_positions_partial_update(
    data_dictionary_service: DataDictionaryService,
):
    identity = IdentityContext(user_id=1, permissions=[])
    dataset_id = 1

    entry1 = create_sample_data_dictionary_entry(
        dataset_id=dataset_id, field_name="field1", position=5
    )
    entry1.id = 1
    entry2 = create_sample_data_dictionary_entry(
        dataset_id=dataset_id, field_name="field2", position=10
    )
    entry2.id = 2

    data_dictionary_service._repository.get_data_dictionaries_by_dataset_id.return_value = [
        entry1,
        entry2,
    ]

    # Only update entry1
    update_data = BulkUpdatePositionDto(
        updates=[
            UpdatePositionDto(entry_id=1, position=0),
        ]
    )

    data_dictionary_service.bulk_update_positions(dataset_id, update_data, identity)

    # Verify only entry1 was updated
    assert entry1.position == 0
    assert entry2.position == 10  # Unchanged


def test_update_data_dictionary(
    data_dictionary_service: DataDictionaryService,
    expected_data_dictionary: DataDictionaryEntry,
):
    identity = IdentityContext(user_id=1, permissions=[])
    dataset_id = 1
    entry_id = 1

    updated_data = AddDataDictionaryEntry(
        field_name="updated_field_name",
        description="Updated description",
        data_type="Integer",
        personally_identifiable_variable=False,
        required=True,
        max_allowed_value=200,
        min_allowed_value=5,
        variable_unit="meters",
        allowed_values="[4, 5, 6]",
        allowed_values_description="[4=Four, 5=Five, 6=Six]",
        table_name="updated_table",
        privacy_risk_type="Identifiant direct",
    )

    data_dictionary_service._repository.get_data_dictionary_entry.return_value = (
        expected_data_dictionary
    )
    data_dictionary_service._repository.get_existing_entry.return_value = None
    data_dictionary_service._repository.update = Mock(
        return_value=expected_data_dictionary
    )
    result = data_dictionary_service.update_data_dictionary(
        dataset_id, entry_id, updated_data, identity
    )

    data_dictionary_service._repository.update.assert_called_once_with(
        expected_data_dictionary,
        field_name="updated_field_name",
        description="Updated description",
        data_type="Integer",
        personally_identifiable_variable=False,
        required=True,
        max_allowed_value=200.0,
        min_allowed_value=5.0,
        variable_unit="meters",
        allowed_values="[4, 5, 6]",
        allowed_values_description="[4=Four, 5=Five, 6=Six]",
        table_name="updated_table",
        privacy_risk_type="Identifiant direct",
    )

    data_dictionary_service._database_session_manager.commit.assert_called_once()

    data_dictionary_service._activity_log_service.log_dictionary_item_activities.assert_called_once()

    assert result is not None
