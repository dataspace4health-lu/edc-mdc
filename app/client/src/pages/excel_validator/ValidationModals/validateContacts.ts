import * as XLSX from "xlsx";
import { extractRows, extractHeaders, cleanHeader, parseContactLabel } from "../Utils";
import type { ResourceOrganisation } from "../../../types";
import { RawContact, FormFields } from "../Types";

const shouldSkipContactValidation = () =>
  typeof window !== "undefined" && window.location.pathname.includes("bulk-upload");

export const validateContacts = async (
  workbook: XLSX.WorkBook,
  dataErrors: Record<string, string[]>,
  sheetName: string,
  formFields: FormFields,
  contactNameHeader = "contact point name",
  contactEmailHeader = "contact point email",
  publisherHeader = "publisher",
) => {
  const rawOrgs = formFields.organisation?.organisations || [];
  const rawContacts = (formFields.contact?.contacts as RawContact[]) || [];

  const orgContactsMap: Record<
    string,
    {
      name: string;
      contactsNameSet: Set<string>;
      contactsEmailMap: Map<string, string>;
    }
  > = {};

  rawOrgs.forEach((org) => {
    orgContactsMap[org.value] = {
      name: org.eng_label.trim(),
      contactsNameSet: new Set(),
      contactsEmailMap: new Map(),
    };
  });

  rawContacts.forEach((contact) => {
    const parentValue = contact.parent_value;
    if (parentValue && orgContactsMap[parentValue]) {
      const { name, email } = parseContactLabel(contact.eng_label);

      if (name) orgContactsMap[parentValue].contactsNameSet.add(name);
      if (email) orgContactsMap[parentValue].contactsEmailMap.set(email, name);
    }
  });

  const sheet = workbook.Sheets[sheetName];
  if (!sheet) return;

  const rawHeaders = extractHeaders(sheet);
  const normalizedHeaders = rawHeaders.map(cleanHeader);

  const contactNameKey = cleanHeader(contactNameHeader);
  const contactEmailKey = cleanHeader(contactEmailHeader);
  const publisherKey = cleanHeader(publisherHeader);

  const contactNameIdx = normalizedHeaders.indexOf(contactNameKey);
  const contactEmailIdx = normalizedHeaders.indexOf(contactEmailKey);
  const publisherIdx = normalizedHeaders.indexOf(publisherKey);

  if (contactNameIdx === -1 || contactEmailIdx === -1 || publisherIdx === -1) return;

  const rows = extractRows(sheet);

  rows.forEach((row, rowIdx) => {
    const contactName = row[contactNameIdx]?.trim() ?? "";
    const contactEmail = row[contactEmailIdx]?.trim() ?? "";
    const publisherRaw = row[publisherIdx]?.trim() ?? "";

    if (!publisherRaw) return;

    const orgEntry = Object.values(orgContactsMap).find((org) => org.name === publisherRaw);

    if (!orgEntry) {
      if (!dataErrors[sheetName]) dataErrors[sheetName] = [];
      dataErrors[sheetName].push(
        `Row ${rowIdx + 2} - Publisher "${publisherRaw}" not found in organisation list.`,
      );
      return;
    }

    const rawOrg = formFields.organisation?.organisations.find(
      (org) => org.eng_label.trim() === publisherRaw,
    );
    if (rawOrg?.is_deprecated) {
      if (!dataErrors[sheetName]) dataErrors[sheetName] = [];
      dataErrors[sheetName].push(`Row ${rowIdx + 2} - Publisher "${publisherRaw}" is deprecated.`);
      return;
    }

    if (contactName && contactEmail) {
      const emailOwnerName = orgEntry.contactsEmailMap.get(contactEmail);

      if (emailOwnerName && emailOwnerName !== contactName) {
        if (!dataErrors[sheetName]) dataErrors[sheetName] = [];
        dataErrors[sheetName].push(
          `Row ${rowIdx + 2} - Email "${contactEmail}" already exists with a different name "${emailOwnerName}".`,
        );
        return;
      }

      const isKnownContact =
        orgEntry.contactsNameSet.has(contactName) || orgEntry.contactsEmailMap.has(contactEmail);

      if (!isKnownContact && !shouldSkipContactValidation()) {
        if (!dataErrors[sheetName]) dataErrors[sheetName] = [];
        dataErrors[sheetName].push(
          `Row ${rowIdx + 2} - Contact (name: "${contactName}", email: "${contactEmail}") does not belong to publisher "${publisherRaw}".`,
        );
      }
    }
  });
};

export const getOrganisationMap = (
  formFields: FormFields,
): Record<string, ResourceOrganisation> => {
  const rawOrgs = formFields.organisation?.organisations || [];

  const map: Record<string, ResourceOrganisation> = {};

  rawOrgs.forEach((rawOrg) => {
    map[rawOrg.eng_label.trim()] = {
      name: rawOrg.eng_label.trim(),
      id: Number(rawOrg.value),
      type: null,
      email: null,
      is_deprecated: false,
      category: null,
      accessible_within_ctie: null,
      contacts: [],
    };
  });

  return map;
};

export const addValidationError = (
  dataErrors: Record<string, string[]>,
  sheetName: string,
  rowIndex: number,
  message: string,
): void => {
  if (!dataErrors[sheetName]) dataErrors[sheetName] = [];
  dataErrors[sheetName].push(`Row ${rowIndex + 2} - ${message}`);
};

export const validateCTIEOrgAccess = (
  enableMultiTenants: boolean,
  isCTIEInstance: boolean,
  orgAccessibility: boolean | null | undefined,
  enableDualInstance: boolean,
): string | null => {
  if (!enableDualInstance) {
    return null;
  }

  if (!enableMultiTenants) {
    return null;
  }

  if (isCTIEInstance && orgAccessibility !== true) {
    return "Organisation cannot be used in CTIE instance.";
  }

  if (!isCTIEInstance && orgAccessibility === true) {
    return "Organisation is CTIE-only and cannot be used here.";
  }

  return null;
};
