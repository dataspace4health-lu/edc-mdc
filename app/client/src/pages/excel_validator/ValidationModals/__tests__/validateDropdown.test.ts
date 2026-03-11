import { describe, it, expect, vi, beforeEach } from "vitest";
import * as XLSX from "xlsx";
import { validateDropdownFields } from "../validateDropdown";

vi.mock("../../../../zodiosClient/client", () => ({
  default: {
    retrieve_form_fields_api_v1_form_fields_get: vi.fn(),
  },
}));

const createTestWorksheet = (headers: string[], rows: string[][]): XLSX.WorkSheet => {
  const sheet: XLSX.WorkSheet = {};

  headers.forEach((header, colIdx) => {
    const cellRef = XLSX.utils.encode_cell({ r: 0, c: colIdx });
    sheet[cellRef] = { t: "s", v: header };
  });

  rows.forEach((row, rowIdx) => {
    row.forEach((cellValue, colIdx) => {
      const cellRef = XLSX.utils.encode_cell({ r: rowIdx + 1, c: colIdx });
      sheet[cellRef] = { t: "s", v: cellValue };
    });
  });

  sheet["!ref"] = XLSX.utils.encode_range({
    s: { r: 0, c: 0 },
    e: { r: rows.length, c: headers.length - 1 },
  });

  return sheet;
};

describe("validateDropdownFields - DataDictionaryTemplate", () => {
  let dataErrors: Record<string, string[]>;

  beforeEach(() => {
    dataErrors = {};
  });

  it("should validate valid data types", () => {
    const sheet = createTestWorksheet(
      ["dataset title", "field_name", "description", "data_type"],
      [
        ["Test Dataset", "field1", "Description", "String"],
        ["Test Dataset", "field2", "Description", "Integer"],
        ["Test Dataset", "field3", "Description", "Boolean"],
        ["Test Dataset", "field4", "Description", "Float"],
        ["Test Dataset", "field5", "Description", "Date"],
      ],
    );

    validateDropdownFields(
      sheet,
      "DataDictionaryTemplate",
      ["dataset title", "field_name", "description", "data_type"],
      {},
      dataErrors,
    );

    expect(dataErrors["DataDictionaryTemplate"]).toBeUndefined();
  });

  it("should validate data types case-insensitively", () => {
    const sheet = createTestWorksheet(
      ["dataset title", "field_name", "description", "data_type"],
      [
        ["Test Dataset", "field1", "Description", "string"],
        ["Test Dataset", "field2", "Description", "INTEGER"],
        ["Test Dataset", "field3", "Description", "BoOlEaN"],
        ["Test Dataset", "field4", "Description", "FLOAT"],
        ["Test Dataset", "field5", "Description", "date"],
      ],
    );

    validateDropdownFields(
      sheet,
      "DataDictionaryTemplate",
      ["dataset title", "field_name", "description", "data_type"],
      {},
      dataErrors,
    );

    expect(dataErrors["DataDictionaryTemplate"]).toBeUndefined();
  });

  it("should reject invalid data types", () => {
    const sheet = createTestWorksheet(
      ["dataset title", "field_name", "description", "data_type"],
      [
        ["Test Dataset", "field1", "Description", "number"],
        ["Test Dataset", "field2", "Description", "text"],
        ["Test Dataset", "field3", "Description", "InvalidType"],
      ],
    );

    validateDropdownFields(
      sheet,
      "DataDictionaryTemplate",
      ["dataset title", "field_name", "description", "data_type"],
      {},
      dataErrors,
    );

    expect(dataErrors["DataDictionaryTemplate"]).toBeDefined();
    expect(dataErrors["DataDictionaryTemplate"]).toHaveLength(3);
    expect(dataErrors["DataDictionaryTemplate"][0]).toContain(
      'Invalid dropdown value for "data_type": "number"',
    );
    expect(dataErrors["DataDictionaryTemplate"][1]).toContain(
      'Invalid dropdown value for "data_type": "text"',
    );
    expect(dataErrors["DataDictionaryTemplate"][2]).toContain(
      'Invalid dropdown value for "data_type": "InvalidType"',
    );
  });

  it("should validate all allowed data types", () => {
    const sheet = createTestWorksheet(
      ["dataset title", "field_name", "description", "data_type"],
      [
        ["Test Dataset", "field1", "Description", "String"],
        ["Test Dataset", "field2", "Description", "Integer"],
        ["Test Dataset", "field3", "Description", "Boolean"],
        ["Test Dataset", "field4", "Description", "Float"],
        ["Test Dataset", "field5", "Description", "Character"],
        ["Test Dataset", "field6", "Description", "Byte"],
        ["Test Dataset", "field7", "Description", "Short"],
        ["Test Dataset", "field8", "Description", "Long"],
        ["Test Dataset", "field9", "Description", "Double"],
        ["Test Dataset", "field10", "Description", "Date"],
      ],
    );

    validateDropdownFields(
      sheet,
      "DataDictionaryTemplate",
      ["dataset title", "field_name", "description", "data_type"],
      {},
      dataErrors,
    );

    expect(dataErrors["DataDictionaryTemplate"]).toBeUndefined();
  });

  it("should validate boolean fields (personally_identifiable_variable and required)", () => {
    const sheet = createTestWorksheet(
      [
        "dataset title",
        "field_name",
        "description",
        "data_type",
        "personally_identifiable_variable",
        "required",
      ],
      [
        ["Test Dataset", "field1", "Description", "String", "true", "false"],
        ["Test Dataset", "field2", "Description", "Integer", "false", "true"],
      ],
    );

    validateDropdownFields(
      sheet,
      "DataDictionaryTemplate",
      [
        "dataset title",
        "field_name",
        "description",
        "data_type",
        "personally_identifiable_variable",
        "required",
      ],
      {},
      dataErrors,
    );

    expect(dataErrors["DataDictionaryTemplate"]).toBeUndefined();
  });

  it("should reject invalid boolean values", () => {
    const sheet = createTestWorksheet(
      [
        "dataset title",
        "field_name",
        "description",
        "data_type",
        "personally_identifiable_variable",
        "required",
      ],
      [
        ["Test Dataset", "field1", "Description", "String", "yes", "no"],
        ["Test Dataset", "field2", "Description", "Integer", "1", "0"],
      ],
    );

    validateDropdownFields(
      sheet,
      "DataDictionaryTemplate",
      [
        "dataset title",
        "field_name",
        "description",
        "data_type",
        "personally_identifiable_variable",
        "required",
      ],
      {},
      dataErrors,
    );

    expect(dataErrors["DataDictionaryTemplate"]).toBeDefined();
    expect(dataErrors["DataDictionaryTemplate"].length).toBeGreaterThan(0);
    expect(
      dataErrors["DataDictionaryTemplate"].some((err) =>
        err.includes('Invalid dropdown value for "personally_identifiable_variable"'),
      ),
    ).toBe(true);
    expect(
      dataErrors["DataDictionaryTemplate"].some((err) =>
        err.includes('Invalid dropdown value for "required"'),
      ),
    ).toBe(true);
  });

  it("should skip validation for empty cells", () => {
    const sheet = createTestWorksheet(
      ["dataset title", "field_name", "description", "data_type"],
      [
        ["Test Dataset", "field1", "Description", ""],
        ["Test Dataset", "field2", "Description", "   "],
      ],
    );

    validateDropdownFields(
      sheet,
      "DataDictionaryTemplate",
      ["dataset title", "field_name", "description", "data_type"],
      {},
      dataErrors,
    );

    expect(dataErrors["DataDictionaryTemplate"]).toBeUndefined();
  });

  it("should handle mixed valid and invalid data types", () => {
    const sheet = createTestWorksheet(
      ["dataset title", "field_name", "description", "data_type"],
      [
        ["Test Dataset", "field1", "Description", "String"],
        ["Test Dataset", "field2", "Description", "number"],
        ["Test Dataset", "field3", "Description", "Integer"],
        ["Test Dataset", "field4", "Description", "InvalidType"],
      ],
    );

    validateDropdownFields(
      sheet,
      "DataDictionaryTemplate",
      ["dataset title", "field_name", "description", "data_type"],
      {},
      dataErrors,
    );

    expect(dataErrors["DataDictionaryTemplate"]).toBeDefined();
    expect(dataErrors["DataDictionaryTemplate"]).toHaveLength(2);
    expect(dataErrors["DataDictionaryTemplate"][0]).toContain("Row 3");
    expect(dataErrors["DataDictionaryTemplate"][0]).toContain('"number"');
    expect(dataErrors["DataDictionaryTemplate"][1]).toContain("Row 5");
    expect(dataErrors["DataDictionaryTemplate"][1]).toContain('"InvalidType"');
  });

  it("should report correct row numbers in error messages", () => {
    const sheet = createTestWorksheet(
      ["dataset title", "field_name", "description", "data_type"],
      [
        ["Test Dataset", "field1", "Description", "String"],
        ["Test Dataset", "field2", "Description", "String"],
        ["Test Dataset", "field3", "Description", "number"],
      ],
    );

    validateDropdownFields(
      sheet,
      "DataDictionaryTemplate",
      ["dataset title", "field_name", "description", "data_type"],
      {},
      dataErrors,
    );

    expect(dataErrors["DataDictionaryTemplate"]).toBeDefined();
    expect(dataErrors["DataDictionaryTemplate"][0]).toContain("Row 4");
  });
});
