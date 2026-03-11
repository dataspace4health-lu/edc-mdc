import { describe, it, expect, vi, beforeEach } from "vitest";
import * as XLSX from "xlsx";
import { extractDatasetsFromWorkbook } from "../BuildDatasets";
import { fetchFormFields } from "../Loader";

vi.mock("../../../zodiosClient/client", () => ({
  default: {},
}));

vi.mock("../Loader", () => ({
  fetchFormFields: vi.fn(),
}));

const createTestWorkbook = (
  datasetData: Record<string, string>[],
  distributionData?: Record<string, string>[],
) => {
  const workbook: XLSX.WorkBook = { Sheets: {}, SheetNames: [] };

  // Create DatasetTemplate sheet
  const datasetHeaders = [
    "title",
    "description",
    "publisher",
    "contact point name",
    "contact point email",
    "themes",
    "dataset types",
    "keywords",
    "start date",
    "end date",
    "frequency",
    "access rights",
    "applicable legislations",
    "language",
    "data protection types",
    "geographical coverage",
    "creator",
    "landing page",
    "documentation",
    "purpose",
  ];

  const datasetSheet: XLSX.WorkSheet = {};

  // Add headers
  datasetHeaders.forEach((header, colIdx) => {
    const cellRef = XLSX.utils.encode_cell({ r: 0, c: colIdx });
    datasetSheet[cellRef] = { t: "s", v: header };
  });

  // Add data rows
  datasetData.forEach((rowData, rowIdx) => {
    datasetHeaders.forEach((header, colIdx) => {
      const cellValue = rowData[header] || "";
      const cellRef = XLSX.utils.encode_cell({ r: rowIdx + 1, c: colIdx });
      datasetSheet[cellRef] = { t: "s", v: cellValue };
    });
  });

  datasetSheet["!ref"] = XLSX.utils.encode_range({
    s: { r: 0, c: 0 },
    e: { r: datasetData.length, c: datasetHeaders.length - 1 },
  });

  workbook.Sheets["DatasetTemplate"] = datasetSheet;
  workbook.SheetNames.push("DatasetTemplate");

  // Create DistributionTemplate sheet if provided
  if (distributionData && distributionData.length > 0) {
    const distHeaders = [
      "dataset title",
      "distribution title",
      "description",
      "access url",
      "format",
      "license",
      "language",
      "rights",
      "availability",
      "applicable legislations",
      "spatial restrictions",
      "media type/compression format/packaging format",
    ];

    const distSheet: XLSX.WorkSheet = {};

    distHeaders.forEach((header, colIdx) => {
      const cellRef = XLSX.utils.encode_cell({ r: 0, c: colIdx });
      distSheet[cellRef] = { t: "s", v: header };
    });

    distributionData.forEach((rowData, rowIdx) => {
      distHeaders.forEach((header, colIdx) => {
        const cellValue = rowData[header] || "";
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
  dataset: {
    themes: [
      {
        value: "http://publications.europa.eu/resource/authority/data-theme/ENVI",
        eng_label: "Environment",
      },
    ],
    dataset_types: [
      {
        value: "http://publications.europa.eu/resource/authority/dataset-type/TEST_DATA",
        eng_label: "Test Data",
      },
    ],
    keywords: [{ value: "water", eng_label: "Water", organisation_ids: [] }],
    periodicities: [
      {
        value: "http://publications.europa.eu/resource/authority/frequency/ANNUAL",
        eng_label: "Annual",
      },
    ],
    languages: [
      {
        value: "http://publications.europa.eu/resource/authority/language/ENG",
        eng_label: "English",
      },
    ],
    spatial_coverages: [
      {
        value: "http://publications.europa.eu/resource/authority/country/LUX",
        eng_label: "Luxembourg",
      },
    ],
    applicable_legislations: [
      {
        value: "directive_2000_60_ec",
        eng_label: "Water Framework Directive",
        link: "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32000L0060",
        organisation_ids: [],
      },
    ],
  },
  organisation: {
    organisations: [{ id: 1, value: "1", eng_label: "Test Organization", is_deprecated: false }],
  },
  contact: {
    contacts: [{ value: "1", eng_label: "John Doe (john.doe@example.com)" }],
  },
  distribution: {
    file_types: [{ value: "CSV", eng_label: "CSV" }],
    languages: [
      {
        value: "http://publications.europa.eu/resource/authority/language/ENG",
        eng_label: "English",
      },
    ],
    spatial_restrictions: [],
  },
});

describe("extractDatasetsFromWorkbook", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(fetchFormFields).mockResolvedValue(createMockFormFields());
  });

  it("should extract dataset with landing page and documentation fields", async () => {
    const workbook = createTestWorkbook(
      [
        {
          title: "Water Quality Dataset",
          description: "This is a comprehensive dataset about water quality",
          publisher: "Test Organization",
          "contact point name": "John Doe",
          "contact point email": "john.doe@example.com",
          themes: "ENVI",
          "dataset types": "Test Data",
          keywords: "Water",
          "start date": "01/01/2022",
          "end date": "31/12/2023",
          frequency: "Annual",
          "access rights": "public",
          "applicable legislations": "Water Framework Directive",
          language: "English",
          "data protection types": "",
          "geographical coverage": "Luxembourg",
          creator: "",
          "landing page": "https://example.com/water-quality",
          documentation: "https://example.com/docs/water-quality",
          purpose: "Research and public health monitoring",
        },
      ],
      [
        {
          "dataset title": "Water Quality Dataset",
          "distribution title": "CSV Distribution",
          description: "CSV file of water quality measurements",
          "access url": "https://example.com/data.csv",
          format: "CSV",
          license: "no_license",
          language: "English",
          rights: "public",
          availability: "",
          "applicable legislations": "",
          "spatial restrictions": "",
          "media type/compression format/packaging format": "",
        },
      ],
    );

    const result = await extractDatasetsFromWorkbook(workbook);

    expect(result).toHaveLength(1);

    const dataset = result[0];

    // Basic fields
    expect(dataset.title).toBe("Water Quality Dataset");
    expect(dataset.description).toBe("This is a comprehensive dataset about water quality");

    // Organization and contact
    expect(dataset.publisherId).toBe("1");
    expect(dataset.contactIds).toEqual([1]);
    expect(dataset.creatorId).toEqual([]);

    // Multi-select fields
    expect(dataset.themes).toEqual([
      "http://publications.europa.eu/resource/authority/data-theme/ENVI",
    ]);
    expect(dataset.datasetTypes).toEqual([
      "http://publications.europa.eu/resource/authority/dataset-type/TEST_DATA",
    ]);
    expect(dataset.keywords).toEqual(["water"]);
    expect(dataset.languages).toEqual([
      "http://publications.europa.eu/resource/authority/language/ENG",
    ]);
    expect(dataset.spatial_coverages).toEqual([
      "http://publications.europa.eu/resource/authority/country/LUX",
    ]);
    expect(dataset.applicableLegislations).toEqual(["directive_2000_60_ec"]);
    expect(dataset.dataProtectionTypes).toEqual([]);

    // Single select fields
    expect(dataset.periodicity).toBe(
      "http://publications.europa.eu/resource/authority/frequency/ANNUAL",
    );
    expect(dataset.rightsStatement).toBe(
      "http://publications.europa.eu/resource/authority/access-right/PUBLIC",
    );

    // Date fields
    expect(dataset.timePeriodStart).toBeInstanceOf(Date);
    expect(dataset.timePeriodStart?.toISOString()).toContain("2022-01-01");
    expect(dataset.timePeriodEnd).toBeInstanceOf(Date);
    expect(dataset.timePeriodEnd?.toISOString()).toContain("2023-12-31");

    // New fields being tested
    expect(dataset.landingPages).toEqual(["https://example.com/water-quality"]);
    expect(dataset.documentation).toEqual(["https://example.com/docs/water-quality"]);
    expect(dataset.purpose).toEqual(["Research and public health monitoring"]);

    // Distributions
    expect(dataset.distributions ?? []).toHaveLength(1);

    const distribution = (dataset.distributions ?? [])[0];
    expect(distribution.title).toBe("CSV Distribution");
    expect(distribution.description).toBe("CSV file of water quality measurements");
    expect(distribution.accessURLs).toEqual(["https://example.com/data.csv"]);
    expect(distribution.fileFormat).toBe("CSV");
    expect(distribution.license).toBe("no_license");
    expect(distribution.languages).toEqual([
      "http://publications.europa.eu/resource/authority/language/ENG",
    ]);
    expect(distribution.distributionRightsStatement).toBe(
      "http://publications.europa.eu/resource/authority/access-right/PUBLIC",
    );
    expect(distribution.applicableLegislations).toEqual([]);
    expect(distribution.spatialRestrictions).toEqual([]);
  });
});
