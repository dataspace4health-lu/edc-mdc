import * as XLSX from "xlsx";
import { extractRows, findColumnIndex } from "../Utils";

export const validateCrossReferences = (
  workbook: XLSX.WorkBook,
  dataErrors: Record<string, string[]>,
) => {
  const datasetSheet = workbook.Sheets["DatasetTemplate"];
  const distributionSheet = workbook.Sheets["DistributionTemplate"];
  const dictionarySheet = workbook.Sheets["DataDictionaryTemplate"];

  if (!datasetSheet) return;

  const datasetTitleIdx = findColumnIndex(datasetSheet, "title");
  if (datasetTitleIdx === -1) return;

  const datasetRows = extractRows(datasetSheet);
  const datasetTitles = new Set(
    datasetRows.map((row) => row[datasetTitleIdx]?.trim()).filter(Boolean),
  );

  const validateSheetDatasetLink = (
    sheet: XLSX.WorkSheet,
    sheetName: string,
    targetHeader: string,
  ) => {
    const colIdx = findColumnIndex(sheet, targetHeader);
    if (colIdx === -1) return;

    const rows = extractRows(sheet);
    rows.forEach((row, rowIdx) => {
      const datasetTitle = row[colIdx]?.trim();
      if (datasetTitle && !datasetTitles.has(datasetTitle)) {
        if (!dataErrors[sheetName]) dataErrors[sheetName] = [];
        dataErrors[sheetName].push(
          `Row ${rowIdx + 2} - Dataset title "${datasetTitle}" not found in DatasetTemplate`,
        );
      }
    });
  };

  if (distributionSheet) {
    validateSheetDatasetLink(distributionSheet, "DistributionTemplate", "dataset title");
  }

  if (dictionarySheet) {
    validateSheetDatasetLink(dictionarySheet, "DataDictionaryTemplate", "dataset title");
  }
};
