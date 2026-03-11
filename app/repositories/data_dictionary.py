from fastapi import Depends, HTTPException
from dependencies.database import get_db_session
from sqlalchemy.orm import Session
from models.data_dictionary import DataDictionaryEntry
from models.authentic_source_assignment import AuthenticSourceAssignment
from models.authentic_source_label import AuthenticSourceLabel
from typing import List, Annotated


class DataDictionaryRepository:
    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def get_data_dictionaries_by_dataset_id(
        self, dataset_id: int
    ) -> List[DataDictionaryEntry]:
        return (
            self._db_session.query(DataDictionaryEntry)
            .filter(DataDictionaryEntry.dataset_id == dataset_id)
            .order_by(
                DataDictionaryEntry.position.asc().nulls_last(),
                DataDictionaryEntry.id.asc(),
            )
            .all()
        )

    def get_data_dictionary_entry(self, entry_id: int) -> DataDictionaryEntry:
        entry = (
            self._db_session.query(DataDictionaryEntry)
            .filter(DataDictionaryEntry.id == entry_id)
            .first()
        )
        if not entry:
            raise HTTPException(
                status_code=404, detail=f"DataDictionaryEntry[{entry_id}] not found"
            )
        return entry

    def add(self, data_dictionary: DataDictionaryEntry) -> None:
        self._db_session.add(data_dictionary)

    def update(
        self,
        entry: DataDictionaryEntry,
        field_name: str = None,
        description: str = None,
        data_type: str = None,
        personally_identifiable_variable: bool = None,
        required: bool = None,
        max_allowed_value: float = None,
        min_allowed_value: float = None,
        variable_unit: str = None,
        allowed_values: str = None,
        allowed_values_description: str = None,
        table_name: str = None,
        privacy_risk_type: str = None,
    ) -> DataDictionaryEntry:
        if field_name is not None:
            entry.field_name = field_name
        if description is not None:
            entry.description = description
        if data_type is not None:
            entry.data_type = data_type
        if personally_identifiable_variable is not None:
            entry.personally_identifiable_variable = personally_identifiable_variable
        if required is not None:
            entry.required = required
        if max_allowed_value is not None:
            entry.max_allowed_value = max_allowed_value
        if min_allowed_value is not None:
            entry.min_allowed_value = min_allowed_value
        if variable_unit is not None:
            entry.variable_unit = variable_unit
        if allowed_values is not None:
            entry.allowed_values = allowed_values
        if allowed_values_description is not None:
            entry.allowed_values_description = allowed_values_description
        if table_name is not None:
            entry.table_name = table_name
        if privacy_risk_type is not None:
            entry.privacy_risk_type = privacy_risk_type

        self._db_session.add(entry)
        return entry

    def delete_entry_by_id(self, entry_id: int):
        self._db_session.query(DataDictionaryEntry).filter(
            DataDictionaryEntry.id == entry_id
        ).delete()

    def add_bulk(self, entries: List[DataDictionaryEntry]) -> None:
        self._db_session.add_all(entries)

    def get_existing_entry(
        self, field_name: str, dataset_id: int
    ) -> DataDictionaryEntry:
        return (
            self._db_session.query(DataDictionaryEntry)
            .filter(
                DataDictionaryEntry.field_name == field_name,
                DataDictionaryEntry.dataset_id == dataset_id,
            )
            .first()
        )

    def bulk_update_authentic_source(
        self, entry_updates: List[tuple[int, bool]]
    ) -> int:
        updated_count = 0
        for entry_id, is_authentic_source in entry_updates:
            updated_rows = (
                self._db_session.query(DataDictionaryEntry)
                .filter(DataDictionaryEntry.id == entry_id)
                .update({"is_authentic_source": is_authentic_source})
            )
            updated_count += updated_rows
        return updated_count

    def get_active_authentic_source_assignment(self, data_dictionary_entry_id: int):
        return (
            self._db_session.query(AuthenticSourceAssignment)
            .join(AuthenticSourceLabel)
            .filter(
                AuthenticSourceAssignment.data_dictionary_entry_id
                == data_dictionary_entry_id,
                AuthenticSourceAssignment.is_active == True,
            )
            .first()
        )
