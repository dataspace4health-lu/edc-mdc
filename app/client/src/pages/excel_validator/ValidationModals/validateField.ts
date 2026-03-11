import {
  validateEmail,
  validateUrl,
  validateNumber,
  validateDate,
  validateString,
  splitValues,
} from "../Utils";
import { requiredHeadersMap, multiValueFieldsMap } from "../Configs";

export const validateField = (
  sheetName: string,
  field: string,
  row: string[],
  colIdx: number,
  rowIdx: number,
  dataErrors: Record<string, string[]>,
) => {
  const headerConfig = requiredHeadersMap[sheetName].find((h) => h.header === field);
  if (!headerConfig) return;

  const validationType = headerConfig.validationType;
  const rawValue = row[colIdx]?.trim();
  if (!rawValue) return;

  const multiValueFields = multiValueFieldsMap[sheetName] || [];
  const isMultiValue = multiValueFields.includes(field);

  const values = isMultiValue ? splitValues(rawValue) : [rawValue];

  values.forEach((value) => {
    let isValid = false;

    switch (validationType) {
      case "email":
        isValid = validateEmail(value);
        break;
      case "url":
        isValid = validateUrl(value);
        break;
      case "number":
        isValid = validateNumber(value);
        break;
      case "date":
        isValid = validateDate(value);
        break;
      case "string":
        isValid = validateString(value);
        break;
      default:
        isValid = true;
        break;
    }

    if (!isValid) {
      if (!dataErrors[sheetName]) dataErrors[sheetName] = [];
      dataErrors[sheetName].push(`Row ${rowIdx + 2} - Invalid value for "${field}": "${value}"`);
    }
  });
};
