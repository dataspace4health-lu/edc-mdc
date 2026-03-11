from typing import Annotated, List
from fastapi import Depends, HTTPException, status, UploadFile
from models.data_dictionary import DataDictionaryEntry
from models.identity_context import IdentityContext
from repositories.data_dictionary import DataDictionaryRepository
from schemas.data_dictionary import (
    AddDataDictionaryEntry,
    ResourceDataDictionaryEntry,
    data_dictionary_entity_to_resource,
    BulkUpdateAuthenticSourceDto,
    BulkUpdatePositionDto,
)
from services.database_session_manager import DatabaseSessionManager
from services.activity_logs.dataset_activity_log import DatasetActivityLogService
from services.activity_logs.data_dictionary_activity_log import (
    DataDictionaryActivityLogService,
)
from services.dataset_permissions_service import DatasetPermissionsService
from utils.csv_parser import CSVParser
import csv
from io import StringIO
from fastapi.responses import StreamingResponse


class DataDictionaryService:
    def __init__(
        self,
        repository: Annotated[
            DataDictionaryRepository, Depends(DataDictionaryRepository)
        ],
        database_session_manager: Annotated[
            DatabaseSessionManager, Depends(DatabaseSessionManager)
        ],
        activity_log_service: Annotated[
            DatasetActivityLogService, Depends(DatasetActivityLogService)
        ],
        dataset_permissions_service: Annotated[
            DatasetPermissionsService, Depends(DatasetPermissionsService)
        ],
        data_dictionary_activity_log_service: Annotated[
            DataDictionaryActivityLogService, Depends(DataDictionaryActivityLogService)
        ],
    ):
        self._repository = repository
        self._database_session_manager = database_session_manager
        self._activity_log_service = activity_log_service
        self._dataset_permissions_service = dataset_permissions_service
        self._data_dictionary_activity_log_service = (
            data_dictionary_activity_log_service
        )
        self._csv_parser = CSVParser()

    def get_data_dictionaries_by_dataset_id(
        self, dataset_id: int, identity: IdentityContext
    ) -> List[ResourceDataDictionaryEntry]:
        self._dataset_permissions_service.validate_read_permissions(
            dataset_id, identity
        )
        data_dictionaries = self._repository.get_data_dictionaries_by_dataset_id(
            dataset_id
        )
        return [data_dictionary_entity_to_resource(dd) for dd in data_dictionaries]

    def add_data_dictionary(
        self, dataset_id: int, data: AddDataDictionaryEntry, identity: IdentityContext
    ) -> ResourceDataDictionaryEntry:
        try:
            self._dataset_permissions_service.validate_edit_permissions(
                dataset_id, identity
            )
            existing_entry = self._repository.get_existing_entry(
                data.field_name, dataset_id
            )
            if existing_entry:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"DataDictionaryEntry with field name '{data.field_name}' already exists.",
                )

            entry = DataDictionaryEntry(
                field_name=data.field_name,
                description=data.description,
                data_type=data.data_type,
                personally_identifiable_variable=data.personally_identifiable_variable,
                required=data.required,
                max_allowed_value=data.max_allowed_value,
                min_allowed_value=data.min_allowed_value,
                variable_unit=data.variable_unit,
                allowed_values=data.allowed_values,
                allowed_values_description=data.allowed_values_description,
                table_name=data.table_name,
                dataset_id=dataset_id,
                is_authentic_source=False,
                privacy_risk_type=data.privacy_risk_type,
                position=None,
            )
            self._repository.add(entry)

            self._log_activity(identity.user_id, dataset_id, None, entry)

            self._database_session_manager.commit()
            self._database_session_manager.refresh(entry)

            return data_dictionary_entity_to_resource(entry)
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

    def update_data_dictionary(
        self,
        dataset_id: int,
        entry_id: int,
        data: AddDataDictionaryEntry,
        identity: IdentityContext,
    ) -> ResourceDataDictionaryEntry:
        try:
            self._dataset_permissions_service.validate_edit_permissions(
                dataset_id, identity
            )

            existing_entry = self._repository.get_data_dictionary_entry(entry_id)

            if existing_entry.dataset_id != dataset_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Data dictionary entry does not belong to this dataset",
                )

            if existing_entry.field_name != data.field_name:
                duplicate_entry = self._repository.get_existing_entry(
                    data.field_name, dataset_id
                )
                if duplicate_entry and duplicate_entry.id != entry_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"DataDictionaryEntry with field name '{data.field_name}' already exists.",
                    )

            old_entry_dict = existing_entry.to_dict_for_diff()

            self._repository.update(
                existing_entry,
                field_name=data.field_name,
                description=data.description,
                data_type=data.data_type,
                personally_identifiable_variable=data.personally_identifiable_variable,
                required=data.required,
                max_allowed_value=data.max_allowed_value,
                min_allowed_value=data.min_allowed_value,
                variable_unit=data.variable_unit,
                allowed_values=data.allowed_values,
                allowed_values_description=data.allowed_values_description,
                table_name=data.table_name,
                privacy_risk_type=data.privacy_risk_type,
            )

            self._database_session_manager.commit()
            self._database_session_manager.refresh(existing_entry)

            old_entry = DataDictionaryEntry()
            old_entry.__dict__.update(old_entry_dict)
            self._log_activity(identity.user_id, dataset_id, old_entry, existing_entry)

            return data_dictionary_entity_to_resource(existing_entry)
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

    def delete_data_dictionary_entry(
        self, dataset_id: int, entry_id: int, identity: IdentityContext
    ) -> None:
        self._dataset_permissions_service.validate_edit_permissions(
            dataset_id, identity
        )
        entry_to_delete = self._repository.get_data_dictionary_entry(entry_id)

        if not entry_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"DataDictionary Entry with id {entry_id} not found",
            )
        self._log_activity(identity.user_id, dataset_id, entry_to_delete, None)
        self._repository.delete_entry_by_id(entry_id)

        self._database_session_manager.commit()

    def _log_activity(
        self,
        user_id: int,
        dataset_id: int,
        old_entry: DataDictionaryEntry,
        new_entry: DataDictionaryEntry,
    ) -> None:
        old_value = old_entry.to_dict_for_diff() if old_entry else None
        new_value = new_entry.to_dict_for_diff() if new_entry else None
        field_name = old_entry.field_name if old_entry else new_entry.field_name
        field = f"data_dictionaries.{field_name}"

        self._activity_log_service.log_dictionary_item_activities(
            user_id, dataset_id, field, old_value, new_value
        )

    async def _parse_csv_file(self, file: UploadFile) -> csv.DictReader:
        required_headers = [
            "field_name**",
            "description**",
            "data_type**",
        ]

        try:
            return await self._csv_parser.parse_csv_file(file, required_headers)
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An unexpected error occurred: {str(e)}",
            )

    def _validate_csv_row(self, row: dict, row_num: int) -> dict:
        validation_errors = []

        # Check for column mismatch issues first
        for key, value in row.items():
            if isinstance(value, list):
                validation_errors.append(
                    f"Row {row_num}: Column mismatch detected. Extra values found: {', '.join(map(str, value))}. "
                    f"This row has more columns than the header row."
                )

        required_fields = ["field_name**", "description**", "data_type**"]
        for field in required_fields:
            if not row.get(field):
                validation_errors.append(
                    f"Row {row_num}, Column '{field}': Required field is missing or empty."
                )

        # Validate data type is allowed
        if row.get("data_type**"):
            data_type = row["data_type**"]
            if isinstance(data_type, str):
                # Define allowed types (same as in schema)
                type_mapping = {
                    "string": "String",
                    "integer": "Integer",
                    "int": "Integer",
                    "boolean": "Boolean",
                    "bool": "Boolean",
                    "float": "Float",
                    "character": "Character",
                    "char": "Character",
                    "byte": "Byte",
                    "short": "Short",
                    "long": "Long",
                    "double": "Double",
                    "date": "Date",
                }

                normalized_type = type_mapping.get(data_type.lower(), data_type)
                allowed_types = {
                    "String",
                    "Integer",
                    "Boolean",
                    "Float",
                    "Character",
                    "Byte",
                    "Short",
                    "Long",
                    "Double",
                    "Date",
                }

                if normalized_type not in allowed_types:
                    validation_errors.append(
                        f"Row {row_num}, Column 'data_type**': Invalid data type '{data_type}'. "
                        f"Allowed types are: {', '.join(sorted(allowed_types))} "
                        f"(case insensitive, also accepts: string, int, bool, char, date)"
                    )

        boolean_fields = [
            "personally_identifiable_variable",
            "required",
        ]
        for field in boolean_fields:
            if field in row and row[field]:
                # Handle case where value might be a list due to column mismatch
                value = row[field]
                if isinstance(value, list):
                    continue  # Skip validation, already reported as column mismatch
                if value.strip().lower() not in ["true", "false"]:
                    validation_errors.append(
                        f"Row {row_num}, Column '{field}': Value must be 'true' or 'false', but got '{value}'."
                    )

        float_fields = ["max_allowed_value", "min_allowed_value"]
        for field in float_fields:
            if field in row and row[field]:
                # Handle case where value might be a list due to column mismatch
                value = row[field]
                if isinstance(value, list):
                    continue  # Skip validation, already reported as column mismatch
                try:
                    float(value)
                except ValueError:
                    validation_errors.append(
                        f"Row {row_num}, Column '{field}': Value must be a valid number, but got '{value}'."
                    )

        if validation_errors:
            raise ValueError(validation_errors)

        return {
            key: (
                row.get(key, "").strip()
                if row.get(key) and isinstance(row.get(key), str)
                else str(row.get(key)) if row.get(key) else None
            )
            for key in row.keys()
        }

    def _process_csv_rows(
        self, reader: csv.DictReader, dataset_id: int, existing_field_names: set
    ) -> tuple:
        entries = []
        skipped_entries = []
        validation_errors = []

        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            try:
                row_data = self._validate_csv_row(row, row_num)

                if row_data["field_name**"] in existing_field_names:
                    skipped_entries.append(
                        {"row": row_num, "field_name": row_data["field_name**"]}
                    )
                    continue

                existing_field_names.add(row_data["field_name**"])

                row_data["personally_identifiable_variable"] = (
                    row_data["personally_identifiable_variable"].lower() == "true"
                    if row_data.get("personally_identifiable_variable")
                    else None
                )
                row_data["required"] = (
                    row_data["required"].lower() == "true"
                    if row_data.get("required")
                    else None
                )
                row_data["max_allowed_value"] = (
                    float(row_data["max_allowed_value"])
                    if row_data.get("max_allowed_value")
                    else None
                )
                row_data["min_allowed_value"] = (
                    float(row_data["min_allowed_value"])
                    if row_data.get("min_allowed_value")
                    else None
                )

                # temporary, till we put back this feature
                row_data["privacy_risk_type"] = ""

                validated_entry = AddDataDictionaryEntry(
                    field_name=row_data["field_name**"],
                    description=row_data["description**"],
                    data_type=row_data["data_type**"],
                    personally_identifiable_variable=row_data[
                        "personally_identifiable_variable"
                    ],
                    required=row_data["required"],
                    max_allowed_value=row_data["max_allowed_value"],
                    min_allowed_value=row_data["min_allowed_value"],
                    variable_unit=row_data["variable_unit"],
                    allowed_values=row_data["allowed_values"],
                    allowed_values_description=row_data["allowed_values_description"],
                    privacy_risk_type=row_data["privacy_risk_type"],
                    table_name="",
                )
                entry = DataDictionaryEntry(
                    **validated_entry.dict(), dataset_id=dataset_id, position=None
                )
                entries.append(entry)

            except ValueError as e:
                errors = (
                    e.args[0] if e.args and isinstance(e.args[0], list) else [str(e)]
                )
                validation_errors.append({"row": row_num, "errors": errors})
            except Exception as e:
                validation_errors.append({"row": row_num, "errors": [str(e)]})

        return entries, skipped_entries, validation_errors

    async def bulk_upload_data_dictionaries(
        self, dataset_id: int, file: UploadFile, identity: IdentityContext
    ) -> dict:
        try:
            self._dataset_permissions_service.validate_edit_permissions(
                dataset_id, identity
            )

            reader = await self._parse_csv_file(file)
            if not reader.fieldnames:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The uploaded CSV file is empty or does not have valid headers.",
                )

            existing_entries = self._repository.get_data_dictionaries_by_dataset_id(
                dataset_id
            )
            existing_field_names = {entry.field_name for entry in existing_entries}

            entries, skipped_entries, validation_errors = self._process_csv_rows(
                reader, dataset_id, existing_field_names
            )

            # If there are validation errors, provide detailed feedback
            if validation_errors:
                error_details = []
                for error in validation_errors:
                    if isinstance(error.get("errors"), list):
                        error_details.extend(error["errors"])
                    else:
                        error_details.append(
                            f"Row {error['row']}: {error.get('errors', 'Unknown error')}"
                        )

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"CSV validation failed with {len(validation_errors)} errors:\n"
                    + "\n".join(error_details[:10])  # Show first 10 errors
                    + (
                        f"\n...and {len(error_details) - 10} more errors"
                        if len(error_details) > 10
                        else ""
                    ),
                )

            if entries:
                for entry in entries:
                    self._log_activity(identity.user_id, dataset_id, None, entry)
                self._repository.add_bulk(entries)
                self._database_session_manager.commit()

            message = f"{len(entries)} dictionary entries created successfully."
            if skipped_entries:
                message += f" Skipped {len(skipped_entries)} duplicate entries."

            return {
                "message": message,
                "entries": [
                    data_dictionary_entity_to_resource(entry) for entry in entries
                ],
                "skipped_entries": skipped_entries,
                "validation_errors": [],  # Empty since we throw errors above
            }

        except Exception as e:
            self._database_session_manager.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error processing CSV file: {str(e)}",
            )

    def generate_csv(
        self, dataset_id: int, identity: IdentityContext
    ) -> StreamingResponse:
        self._dataset_permissions_service.validate_read_permissions(
            dataset_id, identity
        )

        data_dictionaries = self._repository.get_data_dictionaries_by_dataset_id(
            dataset_id
        )

        output = StringIO()
        fieldnames = [
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

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for entry in data_dictionaries:
            is_authentic_source_value = "false"

            if entry.is_authentic_source:
                # Get active assignment for this data dictionary entry
                active_assignment = (
                    self._repository.get_active_authentic_source_assignment(entry.id)
                )
                if active_assignment and active_assignment.label:
                    label_name = active_assignment.label.name
                    label_description = active_assignment.label.description or ""
                    is_authentic_source_value = f"{label_name} - {label_description}"
                else:
                    is_authentic_source_value = "true"

            row = {
                "field_name**": entry.field_name,
                "description**": entry.description,
                "data_type**": entry.data_type,
                "personally_identifiable_variable": (
                    str(entry.personally_identifiable_variable).lower()
                    if entry.personally_identifiable_variable is not None
                    else ""
                ),
                "required": (
                    str(entry.required).lower() if entry.required is not None else ""
                ),
                "max_allowed_value": (
                    str(entry.max_allowed_value)
                    if entry.max_allowed_value is not None
                    else ""
                ),
                "min_allowed_value": (
                    str(entry.min_allowed_value)
                    if entry.min_allowed_value is not None
                    else ""
                ),
                "variable_unit": entry.variable_unit or "",
                "allowed_values": entry.allowed_values or "",
                "allowed_values_description": entry.allowed_values_description or "",
                "is_authentic_source": is_authentic_source_value,
            }
            writer.writerow(row)

        output.seek(0)
        filename = f"data_dictionary_dataset_{dataset_id}.csv"
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    def bulk_update_authentic_source(
        self,
        dataset_id: int,
        update_data: BulkUpdateAuthenticSourceDto,
        identity: IdentityContext,
    ) -> List[ResourceDataDictionaryEntry]:
        self._dataset_permissions_service.validate_bulk_update_authentic_source_permissions(
            dataset_id, identity
        )

        data_dictionaries = self._repository.get_data_dictionaries_by_dataset_id(
            dataset_id
        )

        entry_updates = []
        for entry in update_data.entries:
            if entry.entry_id not in [dd.id for dd in data_dictionaries]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"DataDictionary Entry with id {entry.entry_id} not found",
                )

            entry_updates.append((entry.entry_id, entry.is_authentic_source))

        self._repository.bulk_update_authentic_source(entry_updates)

        self._database_session_manager.commit()

        return self.get_data_dictionaries_by_dataset_id(dataset_id, identity)

    def copy_data_dictionaries(
        self,
        source_dataset_id: int,
        target_dataset_id: int,
        identity: IdentityContext,
        preserve_authentic_source: bool = False,
    ) -> None:
        self._dataset_permissions_service.validate_edit_permissions(
            target_dataset_id, identity
        )

        source_data_dictionaries = self._repository.get_data_dictionaries_by_dataset_id(
            source_dataset_id
        )

        for entry in source_data_dictionaries:
            new_entry = DataDictionaryEntry(
                field_name=entry.field_name,
                description=entry.description,
                data_type=entry.data_type,
                personally_identifiable_variable=entry.personally_identifiable_variable,
                required=entry.required,
                max_allowed_value=entry.max_allowed_value,
                min_allowed_value=entry.min_allowed_value,
                variable_unit=entry.variable_unit,
                allowed_values=entry.allowed_values,
                allowed_values_description=entry.allowed_values_description,
                table_name=entry.table_name,
                dataset_id=target_dataset_id,
                is_authentic_source=(
                    entry.is_authentic_source if preserve_authentic_source else False
                ),
                privacy_risk_type=entry.privacy_risk_type,
                position=entry.position,
            )
            self._repository.add(new_entry)

            self._log_activity(
                user_id=identity.user_id,
                dataset_id=target_dataset_id,
                old_entry=None,
                new_entry=new_entry,
            )

        self._database_session_manager.commit()

    def bulk_update_positions(
        self,
        dataset_id: int,
        update_data: BulkUpdatePositionDto,
        identity: IdentityContext,
    ) -> List[ResourceDataDictionaryEntry]:
        self._dataset_permissions_service.validate_edit_permissions(
            dataset_id, identity
        )

        # Get all entries for this dataset
        entries = self._repository.get_data_dictionaries_by_dataset_id(dataset_id)
        entry_dict = {entry.id: entry for entry in entries}

        # Validate that all entry_ids belong to this dataset
        for update in update_data.updates:
            if update.entry_id not in entry_dict:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Entry {update.entry_id} not found in dataset {dataset_id}",
                )

        # Update positions
        for update in update_data.updates:
            entry = entry_dict[update.entry_id]
            entry.position = update.position

        # Log the order change
        self._data_dictionary_activity_log_service.log_order_change(
            identity.user_id, dataset_id
        )

        self._database_session_manager.commit()

        # Return updated entries in order
        updated_entries = self._repository.get_data_dictionaries_by_dataset_id(
            dataset_id
        )
        return [data_dictionary_entity_to_resource(entry) for entry in updated_entries]
