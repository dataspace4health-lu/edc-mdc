import csv
import re
from typing import List, Optional
from io import StringIO
from fastapi import HTTPException, status, UploadFile


class CSVParser:
    def __init__(self):
        self.encodings_to_try = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]

    async def parse_csv_file(
        self, file: UploadFile, required_headers: Optional[List[str]] = None
    ) -> csv.DictReader:
        try:
            # Validate file extension
            if not file.filename.endswith(".csv"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The uploaded file is not a valid CSV file.",
                )

            # Read file content
            content = await file.read()
            if not content.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The uploaded CSV file is empty.",
                )

            # Decode content with multiple encoding attempts
            decoded_content = self._decode_content(content)

            # Clean and normalize content
            cleaned_content = self._clean_csv_content(decoded_content)

            # Try to create CSV reader first
            try:
                csv_data = StringIO(cleaned_content)
                reader = csv.DictReader(csv_data)

                # Test if CSV can be parsed by reading the fieldnames
                if not reader.fieldnames:
                    raise csv.Error("No headers found")

                # Validate headers if required
                if required_headers:
                    self._validate_headers(reader, required_headers)

                return reader

            except (csv.Error, Exception) as parse_error:
                # Only if CSV parsing fails, provide detailed structure errors
                structure_errors = self._validate_csv_structure_detailed(
                    cleaned_content
                )
                if structure_errors:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"CSV structure errors found:\n"
                        + "\n".join(structure_errors),
                    )
                else:
                    # If no specific errors found, show the original parse error
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"CSV parsing failed: {str(parse_error)}",
                    )

        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unexpected error parsing CSV file: {str(e)}",
            )

    def _decode_content(self, content: bytes) -> str:
        decoded_content = None

        for encoding in self.encodings_to_try:
            try:
                decoded_content = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        if decoded_content is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to decode the CSV file. Please ensure it uses UTF-8, Latin-1, or Windows-1252 encoding.",
            )

        return decoded_content

    def _clean_csv_content(self, content: str) -> str:
        # Remove BOM (Byte Order Mark) characters
        content = self._remove_bom(content)

        # Fix line breaks within quoted fields
        content = self._normalize_line_breaks(content)

        # Remove empty lines that might cause parsing issues
        content = self._remove_empty_lines(content)

        return content

    def _remove_bom(self, content: str) -> str:
        # UTF-8 BOM
        content = content.lstrip("\ufeff")
        # UTF-16 BOM (little endian)
        content = content.lstrip("\ufffe")
        # UTF-16 BOM (big endian)
        content = content.lstrip("\ufeff")

        return content

    def _normalize_line_breaks(self, content: str) -> str:
        """
        Fix line breaks within quoted CSV fields by converting them to spaces.
        This handles cases where users paste multi-line text into Excel cells.
        """
        lines = content.split("\n")
        fixed_lines = []
        current_row = ""
        in_quotes = False
        quote_char = '"'

        for line in lines:
            if not current_row:
                current_row = line
            else:
                # We're continuing a row that was split by a line break
                current_row += " " + line.strip()

            # Count quotes to determine if we're inside a quoted field
            quote_count = current_row.count(quote_char)

            # Simple heuristic: if we have an even number of quotes, the row is likely complete
            # This handles most cases but may not work with escaped quotes
            if quote_count % 2 == 0:
                fixed_lines.append(current_row)
                current_row = ""
            # If odd number of quotes, we're likely inside a quoted field with line breaks

        # Add any remaining content
        if current_row.strip():
            fixed_lines.append(current_row)

        return "\n".join(fixed_lines)

    def _remove_empty_lines(self, content: str) -> str:
        lines = [line for line in content.split("\n") if line.strip()]
        return "\n".join(lines)

    def _validate_headers(
        self, reader: csv.DictReader, required_headers: List[str]
    ) -> None:
        if not reader.fieldnames:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded CSV file is empty or does not have valid headers.",
            )

        missing_headers = set(required_headers) - set(reader.fieldnames)
        if missing_headers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The uploaded CSV file is missing required headers: {', '.join(missing_headers)}. "
                f"Required headers are: {', '.join(required_headers)}",
            )

    def validate_csv_structure(self, reader: csv.DictReader) -> dict:
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "row_count": 0,
            "column_count": len(reader.fieldnames) if reader.fieldnames else 0,
        }

        try:
            for row_num, row in enumerate(reader, start=1):
                validation_result["row_count"] = row_num

                # Check for rows with wrong number of columns
                expected_columns = validation_result["column_count"]
                actual_columns = len([v for v in row.values() if v is not None])

                if len(row) != expected_columns:
                    validation_result["warnings"].append(
                        f"Row {row_num} has {len(row)} values but expected {expected_columns} columns"
                    )

        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"CSV structure error: {str(e)}")

        return validation_result

    def _validate_csv_structure_detailed(self, content: str) -> List[str]:
        """
        Validate CSV structure and return detailed error messages.

        Returns:
            List of error messages with row/column details
        """
        errors = []

        try:
            csv_data = StringIO(content)
            reader = csv.DictReader(csv_data)

            if not reader.fieldnames:
                errors.append("CSV file has no headers or is malformed")
                return errors

            expected_column_count = len(reader.fieldnames)

            for row_num, row in enumerate(
                reader, start=2
            ):  # Start at 2 (header is row 1)
                try:
                    # Check for missing columns
                    actual_values = [v for v in row.values() if v is not None]
                    if len(row) != expected_column_count:
                        errors.append(
                            f"Row {row_num}: Expected {expected_column_count} columns, "
                            f"but found {len(row)}. Missing or extra values detected."
                        )

                    # Check for specific column issues
                    for col_name, value in row.items():
                        if col_name is None:
                            errors.append(
                                f"Row {row_num}: Found value '{value}' without a corresponding column header. "
                                f"This may indicate misaligned data or extra commas."
                            )

                        # Check for unescaped quotes or malformed fields
                        if value and isinstance(value, str):
                            if value.count('"') % 2 != 0:
                                errors.append(
                                    f"Row {row_num}, Column '{col_name}': Contains unmatched quotes. "
                                    f"Value: '{value[:50]}{'...' if len(value) > 50 else ''}'"
                                )

                except Exception as row_error:
                    errors.append(
                        f"Row {row_num}: Error parsing row - {str(row_error)}"
                    )

            # Additional structure checks
            if row_num == 1:  # Only header found
                errors.append("CSV file contains only headers, no data rows found")

        except csv.Error as csv_error:
            errors.append(f"CSV parsing error: {str(csv_error)}")
        except Exception as e:
            errors.append(f"Unexpected error validating CSV structure: {str(e)}")

        return errors

    def validate_csv_content_detailed(
        self, reader: csv.DictReader, row_validators: dict = None
    ) -> dict:
        """
        Validate CSV content with detailed row/column error reporting.

        Args:
            reader: CSV reader object
            row_validators: Dict of column_name -> validation_function

        Returns:
            Dict with validation results and detailed errors
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "row_count": 0,
            "column_count": len(reader.fieldnames) if reader.fieldnames else 0,
        }

        if not reader.fieldnames:
            result["valid"] = False
            result["errors"].append("No headers found in CSV file")
            return result

        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            result["row_count"] = row_num - 1

            try:
                # Validate each cell if validators are provided
                if row_validators:
                    for col_name, validator_func in row_validators.items():
                        if col_name in row:
                            cell_value = row[col_name]
                            try:
                                if not validator_func(cell_value):
                                    result["errors"].append(
                                        f"Row {row_num}, Column '{col_name}': "
                                        f"Invalid value '{cell_value}'"
                                    )
                                    result["valid"] = False
                            except Exception as validation_error:
                                result["errors"].append(
                                    f"Row {row_num}, Column '{col_name}': "
                                    f"Validation error - {str(validation_error)}"
                                )
                                result["valid"] = False

                # Check for empty required fields (if you want to add this logic)
                for col_name, value in row.items():
                    if col_name and col_name.endswith("**") and not value:
                        result["warnings"].append(
                            f"Row {row_num}, Column '{col_name}': Required field is empty"
                        )

            except Exception as row_error:
                result["errors"].append(
                    f"Row {row_num}: Error processing row - {str(row_error)}"
                )
                result["valid"] = False

        return result
