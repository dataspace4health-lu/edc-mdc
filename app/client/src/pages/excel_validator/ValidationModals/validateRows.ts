import { validateField } from "./validateField.ts";
import { extractRows } from "../Utils.ts";
import * as XLSX from "xlsx";

export const validateRows = (
  sheet: XLSX.WorkSheet,
  normalizedHeaders: string[],
  requiredFields: string[],
  sheetName: string,
  dataErrors: Record<string, string[]>,
) => {
  const rows = extractRows(sheet);
  const headerIndex: Record<string, number> = {};
  normalizedHeaders.forEach((h, i) => (headerIndex[h] = i));

  rows.forEach((row, rowIdx) => {
    requiredFields.forEach((field) => {
      const colIdx = headerIndex[field];
      if (colIdx == null || !row[colIdx]?.trim()) {
        if (!dataErrors[sheetName]) dataErrors[sheetName] = [];
        dataErrors[sheetName].push(`Row ${rowIdx + 2} - Missing value for: "${field}"`);
      }
    });
    normalizedHeaders.forEach((field) => {
      const colIdx = headerIndex[field];
      if (colIdx != null && row[colIdx]?.trim()) {
        validateField(sheetName, field, row, colIdx, rowIdx, dataErrors);
      }
    });
  });
};
