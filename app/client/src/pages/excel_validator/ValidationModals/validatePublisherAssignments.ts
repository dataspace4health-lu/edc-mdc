import * as XLSX from "xlsx";
import { extractRows, extractHeaders, cleanHeader } from "../Utils";
import { addValidationError, validateCTIEOrgAccess } from "./validateContacts";
import client from "../../../zodiosClient/client";
import type { FormFields } from "../Types";

interface UserResponse {
  current_organisation?: { name?: string };
  permissions?: string[];
  feature_options?: { enable_multi_tenants?: boolean; enable_dual_instance?: boolean };
}

interface UIConfigResponse {
  is_ctie_instance?: boolean;
}

export const validatePublisherAssignments = async (
  workbook: XLSX.WorkBook,
  dataErrors: Record<string, string[]>,
  sheetName: string,
  formFields: FormFields,
  publisherHeader = "publisher",
) => {
  const sheet = workbook.Sheets[sheetName];
  if (!sheet) return;

  const rawHeaders = extractHeaders(sheet);
  const normalizedHeaders = rawHeaders.map(cleanHeader);

  const publisherIdx = normalizedHeaders.indexOf(cleanHeader(publisherHeader));
  if (publisherIdx === -1) return;

  const rows = extractRows(sheet);

  const userResponse = await client.get("/api/v1/user", { withCredentials: true });
  const user = userResponse as unknown as UserResponse;
  const uiConfigResponse = await client.get("/api/v1/ui_config", {
    withCredentials: true,
  });
  const uiConfig = uiConfigResponse as unknown as UIConfigResponse;

  const userOrgName = user.current_organisation?.name?.trim() || null;
  const isCTIEInstance = uiConfig.is_ctie_instance || false;
  const enableMultiTenants = user?.feature_options?.enable_multi_tenants ?? false;
  const enableDualInstance = user?.feature_options?.enable_dual_instance ?? false;

  const orgAccessMap: Record<string, boolean | null | undefined> = {};
  const rawOrgs = formFields.organisation?.organisations || [];
  for (const org of rawOrgs) {
    orgAccessMap[org.eng_label.trim()] = org.accessible_within_ctie;
  }

  for (let rowIndex = 0; rowIndex < rows.length; rowIndex++) {
    const row = rows[rowIndex];
    const publisherRaw = row[publisherIdx];
    const publisher = publisherRaw?.trim() || "";

    if (!publisher) continue;

    const orgAccessibility = orgAccessMap[publisher];
    const ctieError = validateCTIEOrgAccess(
      enableMultiTenants,
      isCTIEInstance,
      orgAccessibility,
      enableDualInstance,
    );
    if (ctieError) {
      addValidationError(
        dataErrors,
        sheetName,
        rowIndex,
        `Organisation "${publisher}" ${ctieError}`,
      );
      continue;
    }

    if (user?.permissions?.includes("organisations:edit")) {
      continue;
    }

    if (userOrgName !== publisher) {
      addValidationError(
        dataErrors,
        sheetName,
        rowIndex,
        `Your current organisation ("${userOrgName || "none"}") does not match the specified organisation "${publisher}".`,
      );
    }
  }
};
