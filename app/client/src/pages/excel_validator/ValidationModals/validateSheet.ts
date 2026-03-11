import { extractHeaders, cleanHeader } from "../Utils.ts";
import { requiredHeadersMap, requiredFieldsMap } from "../Configs.ts";
import { validateRows } from "./validateRows.ts";
import { validateHeaders } from "./validateHeaders.ts";
import { validateDropdownFields, DropdownOptions } from "./validateDropdown.ts";
import * as XLSX from "xlsx";

export const validateSheet = (
  sheet: XLSX.WorkSheet,
  sheetName: string,
  missingHeaders: Record<string, string[]>,
  dataErrors: Record<string, string[]>,
  dropdownOptions: DropdownOptions,
) => {
  const rawHeaders = extractHeaders(sheet);
  const normalizedHeaders = rawHeaders.map(cleanHeader);
  const requiredHeaders = requiredHeadersMap[sheetName].map((headerObj) =>
    cleanHeader(headerObj.header),
  );
  const requiredFields = requiredFieldsMap[sheetName].map(cleanHeader);

  const missing = validateHeaders(normalizedHeaders, requiredHeaders);
  if (missing.length) {
    missingHeaders[sheetName] = missing;
    return;
  }

  validateRows(sheet, normalizedHeaders, requiredFields, sheetName, dataErrors);
  validateDropdownFields(sheet, sheetName, normalizedHeaders, dropdownOptions, dataErrors);
};
