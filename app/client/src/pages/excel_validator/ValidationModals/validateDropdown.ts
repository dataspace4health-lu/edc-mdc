import { dropdownFieldsMap, multiValueFieldsMap } from "../Configs";
import { extractRows, splitValues } from "../Utils";
import * as XLSX from "xlsx";
import client from "../../../zodiosClient/client";
import { availabilityOptions } from "../../../schemas/distributionSchema";
import { mediaTypes } from "../../../utils/mediaTypeLabels";
import { dataProtectionTypeOptions } from "../../../utils/dataProtectionLabels";
import { rightStatementsValues } from "../../bulk_upload/Utils";
import { allowedDataTypes } from "../../DataDictionary/dto";

export type DropdownOptions = Record<string, Set<string>>;

export const validateDropdownFields = (
  sheet: XLSX.WorkSheet,
  sheetName: string,
  normalizedHeaders: string[],
  dropdownOptions: DropdownOptions,
  dataErrors: Record<string, string[]>,
) => {
  const dropdownFields = dropdownFieldsMap[sheetName] || [];
  if (dropdownFields.length === 0) return;

  const multiValueFields = multiValueFieldsMap[sheetName] || [];

  const rows = extractRows(sheet);

  const headerIndex: Record<string, number> = {};
  normalizedHeaders.forEach((header, idx) => {
    headerIndex[header] = idx;
  });

  const fieldMappings: Record<string, string> = {
    themes: "themes",
    // keywords: auto-created, not validated
    "geographical coverage": "spatial_coverages",
    language: "languages",
    format: "file_types",
    license: "licenses",
    availability: "availability",
    "dataset types": "dataset_types",
    frequency: "periodicities",
    "access rights": "access_rights",
    rights: "rights",
    "data protection types": "data_protection_types",
    "media type/compression format/packaging format":
      "media_type_compression_format_packaging_format",
    data_type: "data_type",
    personally_identifiable_variable: "personally_identifiable_variable",
    required: "required",
  };

  const combinedOptions: DropdownOptions = { ...dropdownOptions };

  if (sheetName === "DataDictionaryTemplate") {
    combinedOptions["data_type"] = new Set(allowedDataTypes);

    combinedOptions["personally_identifiable_variable"] = new Set(["true", "false"]);
    combinedOptions["required"] = new Set(["true", "false"]);
  }

  if (sheetName === "DatasetTemplate") {
    combinedOptions["access_rights"] = new Set(Object.keys(rightStatementsValues));
    combinedOptions["data_protection_types"] = new Set(
      dataProtectionTypeOptions.map((opt) => opt.label),
    );
  }

  if (sheetName === "DistributionTemplate") {
    combinedOptions["availability"] = new Set(availabilityOptions.map((opt) => opt.label));
    combinedOptions["rights"] = new Set(Object.keys(rightStatementsValues));
    combinedOptions["media_type_compression_format_packaging_format"] = new Set(mediaTypes);
  }

  rows.forEach((row, rowIdx) => {
    dropdownFields.forEach((field) => {
      const colIdx = headerIndex[field];
      const cellValue = row[colIdx]?.trim();

      if (!cellValue) return;

      const dbField = fieldMappings[field];
      if (!dbField) return;
      const validValues = combinedOptions[dbField];
      if (!validValues) return;

      const isMulti = multiValueFields.includes(field);
      const values = isMulti ? splitValues(cellValue) : [cellValue];

      values.forEach((v) => {
        // Case-insensitive comparison by checking if any valid value matches (ignoring case)
        const isValid = Array.from(validValues).some(
          (validValue) => validValue.toLowerCase() === v.toLowerCase(),
        );

        if (!isValid) {
          if (!dataErrors[sheetName]) dataErrors[sheetName] = [];
          dataErrors[sheetName].push(
            `Row ${rowIdx + 2} - Invalid dropdown value for "${field}": "${v}"`,
          );
        }
      });
    });
  });
};

export const fetchDropdownOptions = async (): Promise<DropdownOptions> => {
  const rawData = (await client.retrieve_form_fields_api_v1_form_fields_get({
    withCredentials: true,
  })) as Record<string, Record<string, Array<{ value: string; eng_label: string }>>>;

  const dropdownOptions: DropdownOptions = {};

  for (const groupName in rawData) {
    const group = rawData[groupName];
    for (const fieldName in group) {
      const fieldArray = group[fieldName];
      for (const item of fieldArray) {
        const key = fieldName.toLowerCase();
        const valueToAdd = key === "licenses" ? item.value : item.eng_label;

        if (!dropdownOptions[key]) {
          dropdownOptions[key] = new Set();
        }

        dropdownOptions[key].add(valueToAdd);

        if (key === "themes") {
          const code = item.value.split("/").pop();
          if (code) dropdownOptions[key].add(code);
        }
      }
    }
  }

  return dropdownOptions;
};
