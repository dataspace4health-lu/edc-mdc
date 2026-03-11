import * as XLSX from "xlsx";
import {
  extractRows,
  extractHeaders,
  cleanHeader,
  parseContactLabel,
} from "../excel_validator/Utils";
import { fetchFormFields, addContactToOrganisation } from "./Loader";
import { RawContact } from "../excel_validator/Types";

export const processMissingContacts = async (
  workbook: XLSX.WorkBook,
  logCallback?: (message: string) => void,
): Promise<string[]> => {
  const errors: string[] = [];

  try {
    const formFields = await fetchFormFields();
    const rawOrgs = formFields.organisation?.organisations || [];
    const rawContacts = (formFields.contact?.contacts as RawContact[]) || [];

    const orgContactsMap: Record<string, { id: number; name: string; contactsSet: Set<string> }> =
      {};

    rawOrgs.forEach((org) => {
      orgContactsMap[org.value] = {
        id: Number(org.value),
        name: org.eng_label.trim(),
        contactsSet: new Set(),
      };
    });

    rawContacts.forEach((contact) => {
      const parentValue = contact.parent_value;
      if (parentValue && orgContactsMap[parentValue]) {
        const { name, email } = parseContactLabel(contact.eng_label);

        if (name) orgContactsMap[parentValue].contactsSet.add(name);
        if (email) orgContactsMap[parentValue].contactsSet.add(email);
      }
    });

    const sheetName = "DatasetTemplate";
    const sheet = workbook.Sheets[sheetName];
    if (!sheet) return errors;

    const rawHeaders = extractHeaders(sheet);
    const normalizedHeaders = rawHeaders.map(cleanHeader);

    const contactNameIdx = normalizedHeaders.indexOf(cleanHeader("contact point name"));
    const contactEmailIdx = normalizedHeaders.indexOf(cleanHeader("contact point email"));
    const publisherIdx = normalizedHeaders.indexOf(cleanHeader("publisher"));

    if (contactNameIdx === -1 || contactEmailIdx === -1 || publisherIdx === -1) return errors;

    const rows = extractRows(sheet);

    for (let i = 0; i < rows.length; i++) {
      const row = rows[i];
      const contactName = row[contactNameIdx]?.trim() ?? "";
      const contactEmail = row[contactEmailIdx]?.trim() ?? "";
      const publisherRaw = row[publisherIdx]?.trim() ?? "";

      if (!publisherRaw) continue;

      const orgEntry = Object.values(orgContactsMap).find((org) => org.name === publisherRaw);

      if (!orgEntry) {
        errors.push(`Row ${i + 2} - Publisher "${publisherRaw}" not found.`);
        continue;
      }

      if (contactName && contactEmail) {
        if (!orgEntry.contactsSet.has(contactName) && !orgEntry.contactsSet.has(contactEmail)) {
          try {
            await addContactToOrganisation(orgEntry.id, contactName, contactEmail);
            orgEntry.contactsSet.add(contactName);
            orgEntry.contactsSet.add(contactEmail);
            if (logCallback) {
              logCallback(
                `  ✓ Added contact: "${contactName}" <${contactEmail}> for "${publisherRaw}"`,
              );
            }
          } catch (error) {
            const errorMsg = `Row ${i + 2} - Failed to create contact "${contactName}" for publisher "${publisherRaw}": ${(error as Error).message || error}`;
            errors.push(errorMsg);
            if (logCallback) {
              logCallback(`  ✗ ${errorMsg}`);
            }
          }
        } else if (logCallback) {
          logCallback(
            `  ⓘ Contact "${contactName}" <${contactEmail}> already exists for "${publisherRaw}"`,
          );
        }
      }
    }
  } catch (e) {
    errors.push(`Unexpected error: ${(e as Error).message || e}`);
  }

  return errors;
};
