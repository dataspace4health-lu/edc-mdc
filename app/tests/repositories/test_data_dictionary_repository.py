from sqlalchemy.orm import Session
from repositories.data_dictionary import DataDictionaryRepository
from factories.data_dictionary_entry import create_sample_data_dictionary_entry
import pytest
from models.dataset import Dataset
from fastapi import HTTPException
from test_factory import sample_dataset


@pytest.fixture
def data_dictionary_repository(db_session: Session) -> DataDictionaryRepository:
    return DataDictionaryRepository(db_session)


def test_get_data_dictionaries_by_dataset_id(
    data_dictionary_repository: DataDictionaryRepository,
    db_session: Session,
    sample_dataset: Dataset,
):
    # Create another sample dataset
    sample_dataset2 = sample_dataset
    db_session.add(sample_dataset2)
    db_session.flush()

    data_dictionary_entry = create_sample_data_dictionary_entry(
        dataset_id=sample_dataset2.id
    )
    db_session.add(data_dictionary_entry)
    db_session.commit()

    actual = data_dictionary_repository.get_data_dictionaries_by_dataset_id(
        sample_dataset2.id
    )

    assert len(actual) == 1
    assert actual[0].field_name == "test_field"
    assert actual[0].personally_identifiable_variable is True
    assert actual[0].max_allowed_value == 100
    assert actual[0].min_allowed_value == 1
    assert actual[0].variable_unit == "kg"
    assert actual[0].allowed_values_description == "[1=One, 2=Two, 3=Three]"
    assert actual[0].allowed_values == "[1, 2, 3]"
    assert actual[0].table_name == "test_table"
    assert actual[0].dataset_id == sample_dataset2.id
    assert actual[0].is_authentic_source is False


def test_get_data_dictionary_entry_exists(
    data_dictionary_repository: DataDictionaryRepository,
    db_session: Session,
    sample_dataset: Dataset,
):
    # Create another sample dataset
    sample_dataset2 = sample_dataset
    db_session.add(sample_dataset2)
    db_session.flush()

    data_dictionary_entry = create_sample_data_dictionary_entry(
        dataset_id=sample_dataset2.id
    )
    db_session.add(data_dictionary_entry)
    db_session.commit()

    actual = data_dictionary_repository.get_data_dictionary_entry(
        data_dictionary_entry.id
    )
    assert actual.field_name == "test_field"
    assert actual.description == "Test description"
    assert actual.data_type == "string"
    assert actual.personally_identifiable_variable is True
    assert actual.max_allowed_value == 100
    assert actual.allowed_values == "[1, 2, 3]"
    assert actual.table_name == "test_table"
    assert actual.dataset_id == sample_dataset2.id
    assert actual.is_authentic_source is False


def test_get_data_dictionary_entry_not_found(
    data_dictionary_repository: DataDictionaryRepository,
):
    entry_id = -1

    with pytest.raises(HTTPException) as excinfo:
        data_dictionary_repository.get_data_dictionary_entry(entry_id)
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == f"DataDictionaryEntry[{entry_id}] not found"


def test_delete_data_dictionaries_by_dataset_id(
    data_dictionary_repository: DataDictionaryRepository,
    db_session: Session,
    sample_dataset: Dataset,
):
    # Create another sample dataset
    sample_dataset2 = sample_dataset
    db_session.add(sample_dataset2)
    db_session.flush()

    data_dictionary_entry = create_sample_data_dictionary_entry(
        dataset_id=sample_dataset2.id
    )
    db_session.add(data_dictionary_entry)
    db_session.commit()

    actual = data_dictionary_repository.get_data_dictionary_entry(
        data_dictionary_entry.id
    )
    assert actual.field_name == "test_field"

    data_dictionary_repository.delete_entry_by_id(actual.id)
    db_session.commit()

    with pytest.raises(HTTPException) as excinfo:
        data_dictionary_repository.get_data_dictionary_entry(actual.id)
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == f"DataDictionaryEntry[{actual.id}] not found"


def test_add_bulk(
    data_dictionary_repository: DataDictionaryRepository,
    db_session: Session,
    sample_dataset: Dataset,
):
    sample_dataset_id = sample_dataset.id
    entries = [
        create_sample_data_dictionary_entry(
            dataset_id=sample_dataset_id, field_name="field_1"
        ),
        create_sample_data_dictionary_entry(
            dataset_id=sample_dataset_id, field_name="field_2"
        ),
    ]

    data_dictionary_repository.add_bulk(entries)
    db_session.commit()

    actual = data_dictionary_repository.get_data_dictionaries_by_dataset_id(
        sample_dataset_id
    )
    assert len(actual) == 2
    assert actual[0].field_name == "field_1"
    assert actual[1].field_name == "field_2"


def test_bulk_update_authentic_source(
    data_dictionary_repository: DataDictionaryRepository,
    db_session: Session,
    sample_dataset: Dataset,
):

    sample_dataset2 = sample_dataset
    db_session.add(sample_dataset2)
    db_session.flush()

    dict1 = create_sample_data_dictionary_entry(
        dataset_id=sample_dataset2.id, field_name="test_field_1"
    )
    dict2 = create_sample_data_dictionary_entry(
        dataset_id=sample_dataset2.id, field_name="test_field_2"
    )

    db_session.add(dict1)
    db_session.add(dict2)
    db_session.commit()

    entry_updates = [
        (dict1.id, True),
        (dict2.id, True),
    ]

    updated_count = data_dictionary_repository.bulk_update_authentic_source(
        entry_updates
    )

    db_session.commit()
    assert updated_count == 2

    actual_entries = data_dictionary_repository.get_data_dictionaries_by_dataset_id(
        sample_dataset2.id
    )

    assert len(actual_entries) == 2
    assert actual_entries[0].is_authentic_source is True
    assert actual_entries[1].is_authentic_source is True


def test_get_active_authentic_source_assignment(
    data_dictionary_repository: DataDictionaryRepository,
    db_session: Session,
    sample_dataset: Dataset,
):
    sample_dataset2 = sample_dataset
    db_session.add(sample_dataset2)
    db_session.flush()

    # Create data dictionary entry
    data_dictionary_entry = create_sample_data_dictionary_entry(
        dataset_id=sample_dataset2.id
    )
    data_dictionary_entry.is_authentic_source = True
    db_session.add(data_dictionary_entry)
    db_session.flush()

    # Create authentic source label
    from models.authentic_source_label import AuthenticSourceLabel

    label = AuthenticSourceLabel(
        name="Primary Source", description="Official government database"
    )
    db_session.add(label)
    db_session.flush()

    # Create authentic source assignment
    from models.authentic_source_assignment import AuthenticSourceAssignment

    assignment = AuthenticSourceAssignment(
        data_dictionary_entry_id=data_dictionary_entry.id,
        authentic_source_label_id=label.id,
        is_active=True,
    )
    db_session.add(assignment)
    db_session.commit()

    # Test the method
    result = data_dictionary_repository.get_active_authentic_source_assignment(
        data_dictionary_entry.id
    )

    # Assertions
    assert result is not None
    assert result.data_dictionary_entry_id == data_dictionary_entry.id
    assert result.authentic_source_label_id == label.id
    assert result.is_active is True
    assert result.label.name == "Primary Source"
    assert result.label.description == "Official government database"


def test_get_data_dictionaries_ordered_by_position(
    data_dictionary_repository: DataDictionaryRepository,
    db_session: Session,
    sample_dataset: Dataset,
):
    sample_dataset2 = sample_dataset
    db_session.add(sample_dataset2)
    db_session.flush()

    # Create entries with various positions
    entry1 = create_sample_data_dictionary_entry(
        dataset_id=sample_dataset2.id, field_name="field_with_position_2"
    )
    entry1.position = 2
    db_session.add(entry1)

    entry2 = create_sample_data_dictionary_entry(
        dataset_id=sample_dataset2.id, field_name="field_with_position_0"
    )
    entry2.position = 0
    db_session.add(entry2)

    entry3 = create_sample_data_dictionary_entry(
        dataset_id=sample_dataset2.id, field_name="field_with_no_position_1"
    )
    entry3.position = None
    db_session.add(entry3)

    entry4 = create_sample_data_dictionary_entry(
        dataset_id=sample_dataset2.id, field_name="field_with_position_1"
    )
    entry4.position = 1
    db_session.add(entry4)

    entry5 = create_sample_data_dictionary_entry(
        dataset_id=sample_dataset2.id, field_name="field_with_no_position_2"
    )
    entry5.position = None
    db_session.add(entry5)

    db_session.commit()

    # Get entries from repository
    actual = data_dictionary_repository.get_data_dictionaries_by_dataset_id(
        sample_dataset2.id
    )

    # Verify order: position 0, 1, 2, then nulls (by id)
    assert len(actual) == 5
    assert actual[0].field_name == "field_with_position_0"  # position 0
    assert actual[1].field_name == "field_with_position_1"  # position 1
    assert actual[2].field_name == "field_with_position_2"  # position 2
    # Entries with null positions should come after, ordered by id
    assert actual[3].field_name == "field_with_no_position_1"  # position None
    assert actual[4].field_name == "field_with_no_position_2"  # position None


def test_get_data_dictionaries_all_null_positions(
    data_dictionary_repository: DataDictionaryRepository,
    db_session: Session,
    sample_dataset: Dataset,
):
    sample_dataset2 = sample_dataset
    db_session.add(sample_dataset2)
    db_session.flush()

    entry1 = create_sample_data_dictionary_entry(
        dataset_id=sample_dataset2.id, field_name="field_z"
    )
    entry1.position = None
    db_session.add(entry1)

    entry2 = create_sample_data_dictionary_entry(
        dataset_id=sample_dataset2.id, field_name="field_a"
    )
    entry2.position = None
    db_session.add(entry2)

    entry3 = create_sample_data_dictionary_entry(
        dataset_id=sample_dataset2.id, field_name="field_m"
    )
    entry3.position = None
    db_session.add(entry3)

    db_session.commit()

    actual = data_dictionary_repository.get_data_dictionaries_by_dataset_id(
        sample_dataset2.id
    )

    # All have null positions, so should be ordered by id (creation order)
    assert len(actual) == 3
    assert actual[0].field_name == "field_z"
    assert actual[1].field_name == "field_a"
    assert actual[2].field_name == "field_m"


def test_update_data_dictionary_entry(
    data_dictionary_repository: DataDictionaryRepository,
    db_session: Session,
    sample_dataset: Dataset,
):
    sample_dataset2 = sample_dataset
    db_session.add(sample_dataset2)
    db_session.flush()

    data_dictionary_entry = create_sample_data_dictionary_entry(
        dataset_id=sample_dataset2.id
    )
    db_session.add(data_dictionary_entry)
    db_session.commit()

    updated_entry = data_dictionary_repository.update(
        data_dictionary_entry,
        field_name="updated_field",
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
    db_session.commit()

    actual = data_dictionary_repository.get_data_dictionary_entry(updated_entry.id)
    assert actual.field_name == "updated_field"
    assert actual.description == "Updated description"
    assert actual.data_type == "Integer"
    assert actual.personally_identifiable_variable is False
    assert actual.required is True
    assert actual.max_allowed_value == 200.0
    assert actual.min_allowed_value == 5.0
    assert actual.variable_unit == "meters"
    assert actual.allowed_values == "[4, 5, 6]"
    assert actual.allowed_values_description == "[4=Four, 5=Five, 6=Six]"
    assert actual.table_name == "updated_table"
    assert actual.privacy_risk_type == "Identifiant direct"
    assert actual.dataset_id == sample_dataset2.id
