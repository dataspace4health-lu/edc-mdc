import { describe, it, expect, beforeEach, vi } from "vitest";
import * as XLSX from "xlsx";
import { validateDropdownFields } from "../validateDropdown";
import { extractRows } from "../../Utils";
import { availabilityOptions } from "../../../../schemas/distributionSchema";
import { mediaTypes } from "../../../../utils/mediaTypeLabels";

// Mock Utils
vi.mock("../../Utils", () => ({
  extractRows: vi.fn(),
  splitValues: (val: string) => val.split("|"),
}));

vi.mock("../../../../zodiosClient/client", () => ({
  default: {
    retrieve_form_fields_api_v1_form_fields_get: vi.fn().mockResolvedValue({
      themes: {
        themes: [
          { value: "theme/HEAL", eng_label: "Health" },
          { value: "theme/GOVE", eng_label: "Government" },
        ],
      },
      availability: {
        availability: [
          { value: "available", eng_label: "Available" },
          { value: "temporary", eng_label: "Temporary" },
        ],
      },
      licenses: {
        licenses: [{ value: "cc0-1.0", eng_label: "CC0-1.0" }],
      },
      format: {
        format: [{ value: "csv", eng_label: "CSV" }],
      },
      "media type / compression format / packaging format": {
        "media type / compression format / packaging format": [
          { value: "application/zip", eng_label: "ZIP" },
          { value: "application/json", eng_label: "JSON" },
        ],
      },
    }),
  },
}));

describe("validateDropdownFields", () => {
  const sheetName = "DistributionTemplate";
  const mockSheet = {} as XLSX.WorkSheet;
  let dataErrors: Record<string, string[]>;

  const normalizedHeaders = [
    "dataset title",
    "distribution title",
    "description",
    "access url",
    "format",
    "license",
    "rights",
    "language",
    "media type/compression format/packaging format",
    "applicable legislations",
    "availability",
  ];

  beforeEach(() => {
    dataErrors = {};
    vi.clearAllMocks();
  });

  it("should not return errors for valid dropdown values", () => {
    const validRow = [
      "Dataset 1",
      "Dist 1",
      "desc",
      "https://url.com",
      "CSV",
      "CC0-1.0",
      "public",
      "English",
      mediaTypes[0],
      "legislation",
      "Available",
    ];

    vi.mocked(extractRows).mockReturnValue([validRow]);

    const dropdownOptions = {
      file_types: new Set(["CSV"]),
      licenses: new Set(["CC0-1.0"]),
      availability: new Set(availabilityOptions.map((o) => o.label)),
      languages: new Set(["English"]),
      media_type_compression_format_packaging_format: new Set(mediaTypes),
    };

    validateDropdownFields(mockSheet, sheetName, normalizedHeaders, dropdownOptions, dataErrors);

    expect(dataErrors[sheetName]).toBeUndefined();
  });

  it("should return errors for invalid dropdown values", () => {
    const invalidRow = [
      "Dataset 1",
      "Dist 1",
      "desc",
      "https://url.com",
      "BAD_FORMAT",
      "INVALID_LICENSE",
      "rights",
      "Martian",
      "bad/media",
      "legislation",
      "UnknownAvailability",
    ];

    vi.mocked(extractRows).mockReturnValue([invalidRow]);

    const dropdownOptions = {
      file_types: new Set(["CSV"]),
      licenses: new Set(["CC0-1.0"]),
      availability: new Set(availabilityOptions.map((o) => o.label)),
      languages: new Set(["English"]),
      media_type_compression_format_packaging_format: new Set(mediaTypes),
    };

    validateDropdownFields(mockSheet, sheetName, normalizedHeaders, dropdownOptions, dataErrors);

    expect(dataErrors[sheetName]).toEqual(
      expect.arrayContaining([
        'Row 2 - Invalid dropdown value for "format": "BAD_FORMAT"',
        'Row 2 - Invalid dropdown value for "license": "INVALID_LICENSE"',
        'Row 2 - Invalid dropdown value for "language": "Martian"',
        'Row 2 - Invalid dropdown value for "media type/compression format/packaging format": "bad/media"',
        'Row 2 - Invalid dropdown value for "availability": "UnknownAvailability"',
      ]),
    );
  });
});
