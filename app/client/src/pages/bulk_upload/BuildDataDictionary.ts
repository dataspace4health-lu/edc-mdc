import * as XLSX from "xlsx";
import { extractHeaders, extractRows, cleanHeader } from "../excel_validator/Utils";
import { ResourceDataDictionaryEntry } from "../../types";
import { parseBoolean, emptyToNull, parseNumber } from "./Utils";
import { allowedDataTypes } from "../DataDictionary/dto";

export const extractDataDictionariesFromWorkbook = (
  workbook: XLSX.WorkBook,
): Record<string, ResourceDataDictionaryEntry[]> => {
  const sheet = workbook.Sheets["DataDictionaryTemplate"];
  if (!sheet) return {};

  const headers = extractHeaders(sheet).map(cleanHeader);
  const rows = extractRows(sheet);

  const rowAtIndex = (row: string[], key: string): string =>
    headers.indexOf(key) >= 0 && row[headers.indexOf(key)] ? row[headers.indexOf(key)].trim() : "";

  const dictionaryMap: Record<string, ResourceDataDictionaryEntry[]> = {};

  for (const row of rows) {
    const datasetTitle = rowAtIndex(row, "dataset title");
    const dataType = rowAtIndex(row, "data_type");

    const normalizedDataType = allowedDataTypes.find(
      (type) => type.toLowerCase() === dataType.toLowerCase(),
    );

    if (!normalizedDataType) {
      throw new Error(
        `Invalid data_type "${dataType}" for field "${rowAtIndex(row, "field_name")}" in dataset "${datasetTitle}". Must be one of: ${allowedDataTypes.join(", ")}`,
      );
    }

    const entry = {
      field_name: rowAtIndex(row, "field_name"),
      description: rowAtIndex(row, "description"),
      data_type: normalizedDataType,
      personally_identifiable_variable: parseBoolean(
        rowAtIndex(row, "personally_identifiable_variable"),
      ),
      required: parseBoolean(rowAtIndex(row, "required")),
      max_allowed_value: parseNumber(rowAtIndex(row, "max_allowed_value")),
      min_allowed_value: parseNumber(rowAtIndex(row, "min_allowed_value")),
      variable_unit: emptyToNull(rowAtIndex(row, "variable_unit")),
      allowed_values: emptyToNull(rowAtIndex(row, "allowed_values")),
      allowed_values_description: emptyToNull(rowAtIndex(row, "allowed_values_description")),
    };

    if (!dictionaryMap[datasetTitle]) {
      dictionaryMap[datasetTitle] = [];
    }

    dictionaryMap[datasetTitle].push(entry);
  }

  return dictionaryMap;
};
