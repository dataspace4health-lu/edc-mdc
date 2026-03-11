import * as XLSX from "xlsx";

// clean the header fields
export const cleanHeader = (header: string): string =>
  header
    .replace(/\*/g, "")
    .toLowerCase()
    .trim()
    .replace(/\s+/g, " ")
    .replace(/ {0,5}\/ {0,5}/g, "/");

// Extraction of headers
export const extractHeaders = (sheet: XLSX.WorkSheet): string[] => {
  const range = XLSX.utils.decode_range(sheet["!ref"] || "");
  return Array.from({ length: range.e.c - range.s.c + 1 }, (_, colIdx) => {
    const cell = sheet[XLSX.utils.encode_cell({ r: range.s.r, c: range.s.c + colIdx })];
    return cell?.v?.toString() ?? "";
  });
};

// Extraction non empty line
export const extractRows = (sheet: XLSX.WorkSheet): string[][] => {
  const range = XLSX.utils.decode_range(sheet["!ref"] || "");
  const rows: string[][] = [];

  for (let R = range.s.r + 1; R <= range.e.r; R++) {
    const row = Array.from({ length: range.e.c - range.s.c + 1 }, (_, C) => {
      const cell = sheet[XLSX.utils.encode_cell({ r: R, c: range.s.c + C })];
      return cell?.v?.toString() ?? "";
    });

    if (row.some((val) => val.trim() !== "")) {
      rows.push(row);
    }
  }
  return rows;
};

export const splitValues = (value: string): string[] => {
  return value
    .split(/[|;]/)
    .map((v) => v.trim())
    .filter(Boolean);
};

export const validateEmail = (value: string): boolean => {
  return /^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]{2,7}$/.test(value);
};

export const validateUrl = (value: string): boolean => {
  return /^(https?:\/\/)?([\w-]+\.)+[a-zA-Z]{2,6}(:\d+)?(\/[^\s]*)?$/.test(value);
};

export const validateNumber = (value: string): boolean => {
  return !isNaN(Number(value)) && value.trim() !== "";
};

export const validateDate = (value: string): boolean => {
  return !isNaN(Date.parse(value)) && value.trim() !== "";
};

export const validateString = (value: string): boolean => {
  return typeof value === "string" && value.trim().length > 0;
};

// Optimized function: finds the index of a column by reading only the first row
// assuming that "dataset title" is not always in column 0
export const findColumnIndex = (sheet: XLSX.WorkSheet, targetHeader: string): number => {
  const range = XLSX.utils.decode_range(sheet["!ref"] || "");
  const cleanTarget = cleanHeader(targetHeader);

  for (let colIdx = range.s.c; colIdx <= range.e.c; colIdx++) {
    const cell = sheet[XLSX.utils.encode_cell({ r: range.s.r, c: colIdx })];
    const cellValue = cell?.v?.toString() ?? "";
    if (cleanHeader(cellValue) === cleanTarget) {
      return colIdx;
    }
  }
  return -1;
};

export interface ContactInfo {
  name: string;
  email: string;
}

export const parseContactLabel = (engLabel: string): ContactInfo => {
  if (!engLabel) {
    return { name: "", email: "" };
  }

  const trimmedLabel = engLabel.trim();

  // Match pattern: "Name (email)" - fixed ReDoS vulnerability by using * instead of +
  const match = trimmedLabel.match(/^(.{1,250}?)\s*\(([^)]*)\)$/);

  if (match) {
    const name = match[1].trim();
    const email = match[2].trim();
    return { name, email };
  }

  // If no match, treat entire label as name with empty email
  return {
    name: trimmedLabel,
    email: "",
  };
};
