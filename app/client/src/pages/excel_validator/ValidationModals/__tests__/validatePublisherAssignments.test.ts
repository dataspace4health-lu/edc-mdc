/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, vi, beforeEach } from "vitest";
import * as XLSX from "xlsx";
import { validatePublisherAssignments } from "../validatePublisherAssignments";
import { extractRows, extractHeaders } from "../../Utils";
import client from "../../../../zodiosClient/client";

// Mock the Utils module
vi.mock("../../Utils", () => ({
  extractRows: vi.fn(),
  extractHeaders: vi.fn(),
  cleanHeader: vi.fn((header: string) => header.toLowerCase().replace(/\s+/g, " ").trim()),
}));

// Mock the client
vi.mock("../../../../zodiosClient/client", () => ({
  default: {
    get: vi.fn(),
  },
}));

describe("validatePublisherAssignments", () => {
  const mockWorkbook: XLSX.WorkBook = {
    Sheets: {
      "test-sheet": {} as XLSX.WorkSheet,
    },
    SheetNames: ["test-sheet"],
  };

  let dataErrors: Record<string, string[]>;

  beforeEach(() => {
    dataErrors = {};
    vi.clearAllMocks();

    vi.mocked(extractHeaders).mockReturnValue(["Publisher", "Other Header"]);
    vi.mocked(extractRows).mockReturnValue([
      ["Organization One", "data1"],
      ["Organization Two", "data2"],
    ]);
  });

  const mockFormFields = {
    organisation: {
      organisations: [
        {
          value: "1",
          eng_label: "Different Organization",
          is_deprecated: null,
          accessible_within_ctie: false,
        },
      ],
    },
  };

  it("should pass validation when user has organisations:edit permission feature", async () => {
    (vi.mocked(client.get).mockResolvedValue as any)({
      current_organisation: { name: "User Organization" },
      permissions: ["organisations:edit"],
    } as any);

    vi.mocked(extractRows).mockReturnValue([["Different Organization"]]);

    await validatePublisherAssignments(mockWorkbook, dataErrors, "test-sheet", mockFormFields);

    expect(dataErrors["test-sheet"]).toBeUndefined();
  });

  it("should fail validation when user without organisations:edit permission", async () => {
    (vi.mocked(client.get).mockResolvedValue as any)({
      current_organisation: { name: "User Organization" },
      permissions: [],
    } as any);

    vi.mocked(extractRows).mockReturnValue([["Different Organization"]]);

    await validatePublisherAssignments(mockWorkbook, dataErrors, "test-sheet", mockFormFields);

    expect(dataErrors["test-sheet"]).toContain(
      'Row 2 - Your current organisation ("User Organization") does not match the specified organisation "Different Organization".',
    );
  });

  it("should pass validation when user organization matches publisher", async () => {
    (vi.mocked(client.get).mockResolvedValue as any)({
      current_organisation: { name: "Organization One" },
      permissions: [],
      feature_options: {},
    } as any);

    vi.mocked(extractRows).mockReturnValue([["Organization One"]]);

    await validatePublisherAssignments(mockWorkbook, dataErrors, "test-sheet", mockFormFields);

    expect(dataErrors["test-sheet"]).toBeUndefined();
  });

  it("should add error when user organization does not match publisher", async () => {
    (vi.mocked(client.get).mockResolvedValue as any)({
      current_organisation: { name: "User Organization" },
      permissions: [],
      feature_options: {},
    } as any);

    vi.mocked(extractRows).mockReturnValue([["Different Organization"]]);

    await validatePublisherAssignments(mockWorkbook, dataErrors, "test-sheet", mockFormFields);

    expect(dataErrors["test-sheet"]).toContain(
      'Row 2 - Your current organisation ("User Organization") does not match the specified organisation "Different Organization".',
    );
  });

  it("should handle user with no current organization", async () => {
    (vi.mocked(client.get).mockResolvedValue as any)({
      current_organisation: null,
      permissions: [],
      feature_options: {},
    } as any);

    vi.mocked(extractRows).mockReturnValue([["Some Organization"]]);

    await validatePublisherAssignments(mockWorkbook, dataErrors, "test-sheet", mockFormFields);

    expect(dataErrors["test-sheet"]).toContain(
      'Row 2 - Your current organisation ("none") does not match the specified organisation "Some Organization".',
    );
  });

  it("should handle user with organization name having extra whitespace", async () => {
    (vi.mocked(client.get).mockResolvedValue as any)({
      current_organisation: { name: "  Organization One  " },
      permissions: [],
      feature_options: {},
    } as any);

    vi.mocked(extractRows).mockReturnValue([["Organization One"]]);

    await validatePublisherAssignments(mockWorkbook, dataErrors, "test-sheet", mockFormFields);

    expect(dataErrors["test-sheet"]).toBeUndefined();
  });

  it("should skip validation for empty publisher values", async () => {
    (vi.mocked(client.get).mockResolvedValue as any)({
      current_organisation: { name: "User Organization" },
      permissions: [],
      feature_options: {},
    } as any);

    vi.mocked(extractRows).mockReturnValue([[""], ["   "], [""], [""]]);

    await validatePublisherAssignments(mockWorkbook, dataErrors, "test-sheet", mockFormFields);

    expect(dataErrors["test-sheet"]).toBeUndefined();
  });

  it("should handle missing sheet gracefully", async () => {
    const workbookWithoutSheet = {
      Sheets: {},
      SheetNames: [],
    };

    await validatePublisherAssignments(
      workbookWithoutSheet,
      dataErrors,
      "non-existent-sheet",
      mockFormFields,
    );

    expect(dataErrors["non-existent-sheet"]).toBeUndefined();
  });

  it("should handle missing publisher header", async () => {
    vi.mocked(extractHeaders).mockReturnValue(["Other Header"]);

    await validatePublisherAssignments(mockWorkbook, dataErrors, "test-sheet", mockFormFields);

    expect(dataErrors["test-sheet"]).toBeUndefined();
  });

  it("should handle multiple rows with mixed valid/invalid publishers", async () => {
    (vi.mocked(client.get).mockResolvedValue as any)({
      current_organisation: { name: "User Organization" },
      permissions: [],
      feature_options: {},
    } as any);

    vi.mocked(extractRows).mockReturnValue([
      ["User Organization"], // Valid
      ["Different Organization"], // Invalid
      ["User Organization"], // Valid
      ["Another Organization"], // Invalid
    ]);

    await validatePublisherAssignments(mockWorkbook, dataErrors, "test-sheet", mockFormFields);

    expect(dataErrors["test-sheet"]).toHaveLength(2);
    expect(dataErrors["test-sheet"]).toContain(
      'Row 3 - Your current organisation ("User Organization") does not match the specified organisation "Different Organization".',
    );
    expect(dataErrors["test-sheet"]).toContain(
      'Row 5 - Your current organisation ("User Organization") does not match the specified organisation "Another Organization".',
    );
  });

  it("should skip CTIE validation when enable_multi_tenants feature flag is disabled", async () => {
    (vi.mocked(client.get).mockResolvedValue as any)({
      current_organisation: { name: "LNDS-Only Org" },
      permissions: [],
      feature_options: { enable_multi_tenants: false },
      is_ctie_instance: true,
    } as any);

    vi.mocked(extractRows).mockReturnValue([["LNDS-Only Org"]]);

    const lndsOnlyFormFields = {
      organisation: {
        organisations: [
          {
            value: "1",
            eng_label: "LNDS-Only Org",
            is_deprecated: null,
            accessible_within_ctie: false,
          },
        ],
      },
    };

    await validatePublisherAssignments(mockWorkbook, dataErrors, "test-sheet", lndsOnlyFormFields);

    expect(dataErrors["test-sheet"]).toBeUndefined();
  });

  it("should validate CTIE-only orgs cannot be used in LNDS instance when feature enabled", async () => {
    (vi.mocked(client.get).mockResolvedValue as any)({
      current_organisation: { name: "User Organization" },
      permissions: [],
      feature_options: { enable_multi_tenants: true, enable_dual_instance: true },
      is_ctie_instance: false,
    } as any);

    vi.mocked(extractRows).mockReturnValue([["CTIEOnlyOrg"]]);

    const formFields = {
      organisation: {
        organisations: [
          {
            value: "1",
            eng_label: "CTIEOnlyOrg",
            is_deprecated: null,
            accessible_within_ctie: true,
          },
        ],
      },
    };

    await validatePublisherAssignments(mockWorkbook, dataErrors, "test-sheet", formFields);

    expect(dataErrors["test-sheet"]).toBeDefined();
    expect(dataErrors["test-sheet"]?.[0]).toContain("CTIE-only");
  });

  it("should validate LNDS-only orgs cannot be used in CTIE instance when feature enabled", async () => {
    (vi.mocked(client.get).mockResolvedValue as any)({
      current_organisation: { name: "User Organization" },
      permissions: [],
      feature_options: { enable_multi_tenants: true, enable_dual_instance: true },
      is_ctie_instance: true,
    } as any);

    vi.mocked(extractRows).mockReturnValue([["LNDSOnlyOrg"]]);

    const formFields = {
      organisation: {
        organisations: [
          {
            value: "1",
            eng_label: "LNDSOnlyOrg",
            is_deprecated: null,
            accessible_within_ctie: false,
          },
        ],
      },
    };

    await validatePublisherAssignments(mockWorkbook, dataErrors, "test-sheet", formFields);

    expect(dataErrors["test-sheet"]).toBeDefined();
    expect(dataErrors["test-sheet"]?.[0]).toContain("cannot be used in CTIE instance");
  });
});
