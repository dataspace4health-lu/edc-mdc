import { requiredSheets } from "../Configs";
import { fetchDropdownOptions } from "./validateDropdown";
import { validateSheet } from "./validateSheet";
import { validateCrossReferences } from "./validateCrossReferences";
import { validateContacts } from "./validateContacts";
import { validatePublisherAssignments } from "./validatePublisherAssignments";
import { fetchFormFields } from "../../bulk_upload/Loader";

import * as XLSX from "xlsx";

export const validateWorkbook = async (workbook: XLSX.WorkBook) => {
  const missingSheets: string[] = [];
  const missingHeaders: Record<string, string[]> = {};
  const dataErrors: Record<string, string[]> = {};

  const dropdownOptions = await fetchDropdownOptions();
  const formFields = await fetchFormFields();

  for (const sheetName of requiredSheets) {
    const sheet = workbook.Sheets[sheetName];
    if (!sheet) {
      missingSheets.push(sheetName);
      continue;
    }

    validateSheet(sheet, sheetName, missingHeaders, dataErrors, dropdownOptions);
    await validateContacts(workbook, dataErrors, sheetName, formFields);
  }

  await validatePublisherAssignments(workbook, dataErrors, "DatasetTemplate", formFields);
  validateCrossReferences(workbook, dataErrors);

  return { missingSheets, missingHeaders, dataErrors };
};
