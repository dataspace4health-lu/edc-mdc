import pytest
from sqlalchemy.orm import Session
from factories.data_dictionary_entry import create_sample_data_dictionary_entry
from models.data_dictionary import DataDictionaryEntry
from models.dataset import Dataset
from test_factory import sample_dataset


def test_create_and_get_data_dictionary_entry(
    db_session: Session, sample_dataset: Dataset
):
    db_session.add(sample_dataset)
    db_session.flush()

    data_dictionary_entry = create_sample_data_dictionary_entry(
        dataset_id=sample_dataset.id
    )
    db_session.add(data_dictionary_entry)
    db_session.commit()

    db_data_dictionary_entry = (
        db_session.query(DataDictionaryEntry).filter_by(field_name="test_field").first()
    )
    assert db_data_dictionary_entry is not None
    assert db_data_dictionary_entry.description == "Test description"
    assert db_data_dictionary_entry.personally_identifiable_variable is True
    assert db_data_dictionary_entry.required is False
    assert db_data_dictionary_entry.max_allowed_value == 100
    assert db_data_dictionary_entry.min_allowed_value == 1
    assert db_data_dictionary_entry.variable_unit == "kg"
    assert db_data_dictionary_entry.allowed_values == "[1, 2, 3]"
    assert db_data_dictionary_entry.table_name == "test_table"
    assert db_data_dictionary_entry.dataset_id == sample_dataset.id
    assert db_data_dictionary_entry.is_authentic_source is False
    assert (
        db_data_dictionary_entry.allowed_values_description == "[1=One, 2=Two, 3=Three]"
    )
