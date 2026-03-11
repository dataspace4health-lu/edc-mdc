import { describe, it, expect, vi, beforeEach } from "vitest";
import * as XLSX from "xlsx";
import {
  fetchFormFields,
  processAndAddMissingKeywords,
  processAndAddMissingApplicableLegislation,
} from "../Loader";
import { ResourceUserType } from "../../../types";
import { processMissingFormFields } from "../BuildFormFields";

vi.mock("../../../zodiosClient/client", () => ({
  default: {
    get: vi.fn(),
  },
}));

// Only mock the external dependencies (API calls and imports we can't control)
vi.mock("../Loader", () => ({
  fetchFormFields: vi.fn(),
  processAndAddMissingKeywords: vi.fn(),
  processAndAddMissingApplicableLegislation: vi.fn(),
}));

const mockUser = {
  feature_options: {
    enable_multi_tenants: true, // or false to test different behavior
  },
} as ResourceUserType;

const createTestWorkbook = (datasetData: string[][], distributionData?: string[][]) => {
  const workbook: XLSX.WorkBook = { Sheets: {}, SheetNames: [] };

  // Create DatasetTemplate sheet
  const datasetSheet: XLSX.WorkSheet = {};
  const datasetHeaders = ["Title", "Publisher", "Keywords", "Applicable Legislations"];

  // Add headers
  datasetHeaders.forEach((header, colIdx) => {
    const cellRef = XLSX.utils.encode_cell({ r: 0, c: colIdx });
    datasetSheet[cellRef] = { t: "s", v: header };
  });

  // Add data rows
  datasetData.forEach((row, rowIdx) => {
    row.forEach((cellValue, colIdx) => {
      const cellRef = XLSX.utils.encode_cell({ r: rowIdx + 1, c: colIdx });
      datasetSheet[cellRef] = { t: "s", v: cellValue };
    });
  });

  // Set sheet range
  datasetSheet["!ref"] = XLSX.utils.encode_range({
    s: { r: 0, c: 0 },
    e: { r: datasetData.length, c: datasetHeaders.length - 1 },
  });

  workbook.Sheets["DatasetTemplate"] = datasetSheet;
  workbook.SheetNames.push("DatasetTemplate");

  // Create DistributionTemplate sheet if provided
  if (distributionData) {
    const distSheet: XLSX.WorkSheet = {};
    const distHeaders = ["Dataset Title", "Applicable Legislations"];

    distHeaders.forEach((header, colIdx) => {
      const cellRef = XLSX.utils.encode_cell({ r: 0, c: colIdx });
      distSheet[cellRef] = { t: "s", v: header };
    });

    distributionData.forEach((row, rowIdx) => {
      row.forEach((cellValue, colIdx) => {
        const cellRef = XLSX.utils.encode_cell({ r: rowIdx + 1, c: colIdx });
        distSheet[cellRef] = { t: "s", v: cellValue };
      });
    });

    distSheet["!ref"] = XLSX.utils.encode_range({
      s: { r: 0, c: 0 },
      e: { r: distributionData.length, c: distHeaders.length - 1 },
    });

    workbook.Sheets["DistributionTemplate"] = distSheet;
    workbook.SheetNames.push("DistributionTemplate");
  }

  return workbook;
};

const createMockFormFields = () => ({
  // This structure matches what your function expects
  dataset: {
    // Keywords that exist in the system
    keywords: [
      { value: "existing_keyword_1", eng_label: "existing keyword", organisation_id: "1" },
      { value: "existing_keyword_2", eng_label: "all existing keyword", organisation_id: "2" },
    ] as Array<{
      value: string;
      eng_label: string;
      organisation_id?: string;
    }>,
    // Applicable legislations that exist in the system
    applicable_legislations: [{ value: "existing_law_1", eng_label: "existing law" }],
  },
  // Organization data for getOrganisationMap
  organisation: {
    organisations: [
      { value: "1", eng_label: "Organization One" },
      { value: "2", eng_label: "Organization Two" },
    ],
  },
});

describe("processMissingFormFields", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Setup default mock returns
    vi.mocked(fetchFormFields).mockResolvedValue(createMockFormFields());
    vi.mocked(processAndAddMissingKeywords).mockResolvedValue(undefined);
    vi.mocked(processAndAddMissingApplicableLegislation).mockResolvedValue(undefined);
  });

  it("should process missing keywords from dataset", async () => {
    const workbook = createTestWorkbook([
      // 'existing keyword' will be found in the mock data, others won't
      ["Dataset 1", "Organization One", "existing keyword|missing keyword|another missing", ""],
      ["Dataset 2", "Organization Two", "all existing keyword", ""], // This exists in mock data
    ]);

    await processMissingFormFields(workbook, mockUser);

    // Should only process the keywords that are NOT found in the mock data
    expect(processAndAddMissingKeywords).toHaveBeenCalledWith(
      "1",
      ["missing keyword", "another missing"],
      undefined,
    );
    expect(processAndAddMissingKeywords).not.toHaveBeenCalledWith(
      "2",
      expect.anything(),
      expect.anything(),
    );
  });

  it("should process missing applicable legislations from dataset", async () => {
    const workbook = createTestWorkbook([
      ["Dataset 1", "Organization One", "", "existing law|missing legislation"],
      ["Dataset 2", "Organization Two", "", "another missing law"],
    ]);

    await processMissingFormFields(workbook, mockUser);

    expect(processAndAddMissingApplicableLegislation).toHaveBeenCalledWith(
      "1",
      ["missing legislation"],
      undefined,
    );
    expect(processAndAddMissingApplicableLegislation).toHaveBeenCalledWith(
      "2",
      ["another missing law"],
      undefined,
    );
  });

  it("should process missing legislations from distribution sheet", async () => {
    const workbook = createTestWorkbook(
      [["Dataset 1", "Organization One", "", ""]],
      [["Dataset 1", "distribution missing law"]],
    );

    await processMissingFormFields(workbook, mockUser);

    expect(processAndAddMissingApplicableLegislation).toHaveBeenCalledWith(
      "1",
      ["distribution missing law"],
      undefined,
    );
  });

  it("should handle publishers not found in organization map", async () => {
    const workbook = createTestWorkbook([
      ["Dataset 1", "Unknown Publisher", "missing keyword", "missing law"],
    ]);

    await processMissingFormFields(workbook, mockUser);

    // Should not process keywords/laws for unknown publishers
    expect(processAndAddMissingKeywords).not.toHaveBeenCalled();
    expect(processAndAddMissingApplicableLegislation).not.toHaveBeenCalled();
  });

  it("should handle empty keyword and legislation values", async () => {
    const workbook = createTestWorkbook([
      ["Dataset 1", "Organization One", "", ""],
      ["Dataset 2", "Organization One", "   ", "   "],
    ]);

    await processMissingFormFields(workbook, mockUser);

    expect(processAndAddMissingKeywords).not.toHaveBeenCalled();
    expect(processAndAddMissingApplicableLegislation).not.toHaveBeenCalled();
  });

  it("should collect unique missing items per publisher", async () => {
    const workbook = createTestWorkbook([
      ["Dataset 1", "Organization One", "missing keyword|duplicate keyword", "missing law"],
      [
        "Dataset 2",
        "Organization One",
        "duplicate keyword|another missing",
        "missing law|another law",
      ],
    ]);

    await processMissingFormFields(workbook, mockUser);

    // Should deduplicate keywords
    expect(processAndAddMissingKeywords).toHaveBeenCalledWith(
      "1",
      expect.arrayContaining(["missing keyword", "duplicate keyword", "another missing"]),
      undefined,
    );
    expect(processAndAddMissingKeywords).toHaveBeenCalledTimes(1);

    // Should batch all unique legislations in a single call
    expect(processAndAddMissingApplicableLegislation).toHaveBeenCalledWith(
      "1",
      ["missing law", "another law"],
      undefined,
    );
    expect(processAndAddMissingApplicableLegislation).toHaveBeenCalledTimes(1);
  });

  it("should send null publisherId when enable_multi_tenants is false", async () => {
    const mockUser = {
      feature_options: {
        enable_multi_tenants: false,
      },
    } as ResourceUserType;

    const workbook = createTestWorkbook([
      ["Dataset 1", "Organization One", "missing keyword", "missing law"],
    ]);

    await processMissingFormFields(workbook, mockUser);

    expect(processAndAddMissingKeywords).toHaveBeenCalledWith(null, ["missing keyword"], undefined);
    expect(processAndAddMissingApplicableLegislation).toHaveBeenCalledWith(
      null,
      ["missing law"],
      undefined,
    );
  });
});
