import { describe, it, expect, vi } from "vitest";
import * as XLSX from "xlsx";
import { extractDataDictionariesFromWorkbook } from "../BuildDataDictionary";

vi.mock("../../../zodiosClient/client", () => ({
  default: {},
}));

const createTestWorkbook = (dataDictionaryData: Record<string, string>[]) => {
  const workbook: XLSX.WorkBook = { Sheets: {}, SheetNames: [] };

  const headers = [
    "dataset title",
    "field_name",
    "description",
    "data_type",
    "personally_identifiable_variable",
    "required",
    "max_allowed_value",
    "min_allowed_value",
    "variable_unit",
    "allowed_values",
    "allowed_values_description",
  ];

  const sheet: XLSX.WorkSheet = {};

  // Add headers
  headers.forEach((header, colIdx) => {
    const cellRef = XLSX.utils.encode_cell({ r: 0, c: colIdx });
    sheet[cellRef] = { t: "s", v: header };
  });

  // Add data rows
  dataDictionaryData.forEach((rowData, rowIdx) => {
    headers.forEach((header, colIdx) => {
      const cellValue = rowData[header] || "";
      const cellRef = XLSX.utils.encode_cell({ r: rowIdx + 1, c: colIdx });
      sheet[cellRef] = { t: "s", v: cellValue };
    });
  });

  sheet["!ref"] = XLSX.utils.encode_range({
    s: { r: 0, c: 0 },
    e: { r: dataDictionaryData.length, c: headers.length - 1 },
  });

  workbook.Sheets["DataDictionaryTemplate"] = sheet;
  workbook.SheetNames.push("DataDictionaryTemplate");

  return workbook;
};

describe("extractDataDictionariesFromWorkbook", () => {
  it("should return empty object when DataDictionaryTemplate sheet is missing", () => {
    const workbook: XLSX.WorkBook = { Sheets: {}, SheetNames: [] };
    const result = extractDataDictionariesFromWorkbook(workbook);
    expect(result).toEqual({});
  });

  it("should extract data dictionary entries with valid data types", () => {
    const workbook = createTestWorkbook([
      {
        "dataset title": "Test Dataset",
        field_name: "user_id",
        description: "Unique identifier for user",
        data_type: "String",
        personally_identifiable_variable: "true",
        required: "true",
        max_allowed_value: "",
        min_allowed_value: "",
        variable_unit: "",
        allowed_values: "",
        allowed_values_description: "",
      },
      {
        "dataset title": "Test Dataset",
        field_name: "age",
        description: "User age",
        data_type: "Integer",
        personally_identifiable_variable: "false",
        required: "false",
        max_allowed_value: "120",
        min_allowed_value: "0",
        variable_unit: "years",
        allowed_values: "",
        allowed_values_description: "",
      },
    ]);

    const result = extractDataDictionariesFromWorkbook(workbook);

    expect(result).toHaveProperty("Test Dataset");
    expect(result["Test Dataset"]).toHaveLength(2);

    const firstEntry = result["Test Dataset"][0];
    expect(firstEntry.field_name).toBe("user_id");
    expect(firstEntry.description).toBe("Unique identifier for user");
    expect(firstEntry.data_type).toBe("String");
    expect(firstEntry.personally_identifiable_variable).toBe(true);
    expect(firstEntry.required).toBe(true);

    const secondEntry = result["Test Dataset"][1];
    expect(secondEntry.field_name).toBe("age");
    expect(secondEntry.description).toBe("User age");
    expect(secondEntry.data_type).toBe("Integer");
    expect(secondEntry.personally_identifiable_variable).toBe(false);
    expect(secondEntry.required).toBe(false);
    expect(secondEntry.max_allowed_value).toBe(120);
    expect(secondEntry.min_allowed_value).toBe(0);
    expect(secondEntry.variable_unit).toBe("years");
  });

  it("should handle case-insensitive data types and normalize them", () => {
    const workbook = createTestWorkbook([
      {
        "dataset title": "Test Dataset",
        field_name: "field1",
        description: "Test field with lowercase type",
        data_type: "string",
        personally_identifiable_variable: "false",
        required: "false",
        max_allowed_value: "",
        min_allowed_value: "",
        variable_unit: "",
        allowed_values: "",
        allowed_values_description: "",
      },
      {
        "dataset title": "Test Dataset",
        field_name: "field2",
        description: "Test field with uppercase type",
        data_type: "INTEGER",
        personally_identifiable_variable: "false",
        required: "false",
        max_allowed_value: "",
        min_allowed_value: "",
        variable_unit: "",
        allowed_values: "",
        allowed_values_description: "",
      },
      {
        "dataset title": "Test Dataset",
        field_name: "field3",
        description: "Test field with mixed case type",
        data_type: "BoOlEaN",
        personally_identifiable_variable: "false",
        required: "false",
        max_allowed_value: "",
        min_allowed_value: "",
        variable_unit: "",
        allowed_values: "",
        allowed_values_description: "",
      },
    ]);

    const result = extractDataDictionariesFromWorkbook(workbook);

    expect(result["Test Dataset"]).toHaveLength(3);
    expect(result["Test Dataset"][0].data_type).toBe("String");
    expect(result["Test Dataset"][1].data_type).toBe("Integer");
    expect(result["Test Dataset"][2].data_type).toBe("Boolean");
  });

  it("should throw error for invalid data type", () => {
    const workbook = createTestWorkbook([
      {
        "dataset title": "Test Dataset",
        field_name: "invalid_field",
        description: "Field with invalid type",
        data_type: "InvalidType",
        personally_identifiable_variable: "false",
        required: "false",
        max_allowed_value: "",
        min_allowed_value: "",
        variable_unit: "",
        allowed_values: "",
        allowed_values_description: "",
      },
    ]);

    expect(() => extractDataDictionariesFromWorkbook(workbook)).toThrow(
      'Invalid data_type "InvalidType" for field "invalid_field" in dataset "Test Dataset". Must be one of: String, Integer, Boolean, Float, Character, Byte, Short, Long, Double, Date',
    );
  });

  it("should accept all valid data types", () => {
    const validTypes = [
      "String",
      "Integer",
      "Boolean",
      "Float",
      "Character",
      "Byte",
      "Short",
      "Long",
      "Double",
      "Date",
    ];

    const workbook = createTestWorkbook(
      validTypes.map((type, index) => ({
        "dataset title": "Test Dataset",
        field_name: `field_${index}`,
        description: `Field with ${type} type`,
        data_type: type,
        personally_identifiable_variable: "false",
        required: "false",
        max_allowed_value: "",
        min_allowed_value: "",
        variable_unit: "",
        allowed_values: "",
        allowed_values_description: "",
      })),
    );

    const result = extractDataDictionariesFromWorkbook(workbook);

    expect(result["Test Dataset"]).toHaveLength(validTypes.length);
    validTypes.forEach((type, index) => {
      expect(result["Test Dataset"][index].data_type).toBe(type);
    });
  });

  it("should handle multiple datasets", () => {
    const workbook = createTestWorkbook([
      {
        "dataset title": "Dataset 1",
        field_name: "field1",
        description: "Field in dataset 1",
        data_type: "String",
        personally_identifiable_variable: "false",
        required: "false",
        max_allowed_value: "",
        min_allowed_value: "",
        variable_unit: "",
        allowed_values: "",
        allowed_values_description: "",
      },
      {
        "dataset title": "Dataset 2",
        field_name: "field2",
        description: "Field in dataset 2",
        data_type: "Integer",
        personally_identifiable_variable: "false",
        required: "false",
        max_allowed_value: "",
        min_allowed_value: "",
        variable_unit: "",
        allowed_values: "",
        allowed_values_description: "",
      },
      {
        "dataset title": "Dataset 1",
        field_name: "field3",
        description: "Another field in dataset 1",
        data_type: "Boolean",
        personally_identifiable_variable: "false",
        required: "false",
        max_allowed_value: "",
        min_allowed_value: "",
        variable_unit: "",
        allowed_values: "",
        allowed_values_description: "",
      },
    ]);

    const result = extractDataDictionariesFromWorkbook(workbook);

    expect(result).toHaveProperty("Dataset 1");
    expect(result).toHaveProperty("Dataset 2");
    expect(result["Dataset 1"]).toHaveLength(2);
    expect(result["Dataset 2"]).toHaveLength(1);
  });

  it("should handle optional fields correctly", () => {
    const workbook = createTestWorkbook([
      {
        "dataset title": "Test Dataset",
        field_name: "test_field",
        description: "Test field",
        data_type: "Float",
        personally_identifiable_variable: "",
        required: "",
        max_allowed_value: "",
        min_allowed_value: "",
        variable_unit: "",
        allowed_values: "value1,value2,value3",
        allowed_values_description: "Possible values",
      },
    ]);

    const result = extractDataDictionariesFromWorkbook(workbook);

    expect(result["Test Dataset"][0].personally_identifiable_variable).toBeNull();
    expect(result["Test Dataset"][0].required).toBeNull();
    expect(result["Test Dataset"][0].max_allowed_value).toBeNull();
    expect(result["Test Dataset"][0].min_allowed_value).toBeNull();
    expect(result["Test Dataset"][0].variable_unit).toBeNull();
    expect(result["Test Dataset"][0].allowed_values).toBe("value1,value2,value3");
    expect(result["Test Dataset"][0].allowed_values_description).toBe("Possible values");
  });
});
