import * as XLSX from "xlsx";
import client from "../../zodiosClient/client";
import { toDatasetDTO } from "../DatasetForm/datasetDTO";
import { ResourceDataDictionaryEntry } from "../../types";
import { rightStatementsLabelsUpload } from "../excel_validator/Configs";
import { submitDistributions } from "./BuildDistributions";
import { DatasetWithDistributions } from "./BuildDatasets";

export async function submitDatasets(
  datasets: DatasetWithDistributions[],
  dictionariesByDatasetTitle: Record<string, ResourceDataDictionaryEntry[]>,
  logCallback?: (message: string) => void,
): Promise<{ errors: string[]; successCount: number }> {
  const errors: string[] = [];
  let successCount = 0;

  for (const dataset of datasets) {
    try {
      if (logCallback) {
        logCallback(`  Creating dataset: "${dataset.title}"`);
      }

      // Extract distributions before converting to DTO
      const distributions = dataset.distributions || [];

      // Create dataset without distributions
      const { distributions: _distributions, ...datasetWithoutDistributions } = dataset;
      const dto = toDatasetDTO(datasetWithoutDistributions);
      const createdDataset = await client.create_dataset_api_v1_datasets_post(dto, {
        withCredentials: true,
      });

      const datasetId = createdDataset.id;

      // Add distributions using dedicated endpoint
      if (distributions.length > 0) {
        const distributionErrors = await submitDistributions(
          datasetId,
          distributions,
          dataset.title,
          logCallback,
        );
        errors.push(...distributionErrors);
      }

      const dictionaries = dictionariesByDatasetTitle[dataset.title];
      if (dictionaries && dictionaries.length > 0) {
        if (logCallback) {
          logCallback(`    Adding ${dictionaries.length} data dictionary entries`);
        }
        for (const entry of dictionaries) {
          try {
            await client.add_data_dictionary_api_v1_datasets__dataset_id__data_dictionaries_post(
              {
                field_name: entry.field_name,
                data_type: entry.data_type,
                description: entry.description,
                personally_identifiable_variable: entry.personally_identifiable_variable ?? false,
                required: entry.required ?? false,
                max_allowed_value: entry.max_allowed_value ?? null,
                min_allowed_value: entry.min_allowed_value ?? null,
                variable_unit: entry.variable_unit ?? "",
                allowed_values: entry.allowed_values ?? "",
                allowed_values_description: entry.allowed_values_description ?? "",
                table_name: entry.table_name ?? "",
                dataset_id: datasetId,
                privacy_risk_type: entry.privacy_risk_type ?? null,
              },
              {
                params: { dataset_id: datasetId },
                withCredentials: true,
              },
            );
          } catch (err) {
            const errorMsg = `Error occurred while adding data dictionary entry to dataset "${dataset.title}" for field "${entry.field_name}"`;
            errors.push(errorMsg);
            if (logCallback) {
              logCallback(`    ✗ ${errorMsg}`);
            }
          }
        }
      }

      successCount += 1;
      if (logCallback) {
        logCallback(`  ✓ Successfully created dataset: "${dataset.title}"`);
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      let errorMessage = `Error while submitting the dataset "${dataset.title}".`;
      if (err?.response?.status === 409 && err?.response?.data?.detail) {
        errorMessage = `Duplicate detected: "${dataset.title}" matches an existing dataset by title, description, and publisher.`;
      }
      errors.push(errorMessage);
      if (logCallback) {
        logCallback(`  ✗ ${errorMessage}`);
      }
    }
  }

  return { errors, successCount };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const parseExcelDate = (value: any): string | null => {
  if (typeof value === "number") {
    const excelDate = XLSX.SSF.parse_date_code(value);
    if (!excelDate) return null;
    const { y, m, d } = excelDate;
    if (y < 1900) return null;
    return `${y.toString().padStart(4, "0")}-${m.toString().padStart(2, "0")}-${d.toString().padStart(2, "0")}`;
  }

  if (typeof value === "string" && value.trim()) {
    const trimmed = value.trim();
    const numericValue = Number(trimmed);
    if (!isNaN(numericValue)) {
      return parseExcelDate(numericValue);
    }

    const parts = trimmed.split("/");
    if (parts.length === 3) {
      const [day, month, yearRawRaw] = parts;
      let yearRaw = yearRawRaw;
      if (yearRaw.length === 2) {
        const yearNum = Number(yearRaw);
        yearRaw = yearNum < 30 ? `20${yearRaw}` : `19${yearRaw}`;
      }

      const isoDate = `${yearRaw}-${month.padStart(2, "0")}-${day.padStart(2, "0")}`;
      if (!isValidDateString(isoDate)) {
        console.warn(`⚠️ Invalid date string detected: ${isoDate}`);
        return null;
      }

      return isoDate;
    } else {
      console.warn(`⚠️ Unexpected string format for date: ${value}`);
    }
  }

  return null;
};

const isValidDateString = (date: string | null): boolean => {
  if (!date) return false;
  const parsed = new Date(date);
  return !isNaN(parsed.getTime());
};

export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}
export const parseBoolean = (v: string): boolean | null =>
  v.toLowerCase() === "true" ? true : v.toLowerCase() === "false" ? false : null;

export const parseNumber = (v: string): number | null => {
  if (v === "" || v.trim() === "") return null;
  const n = Number(v);
  return isNaN(n) ? null : n;
};

export const emptyToNull = (v: string): string | null => (v === "" ? null : v);

export function notNull<T>(val: T | null): val is T {
  return val !== null;
}

export const parseDate = (v: string): Date | undefined => {
  const s = parseExcelDate(v);
  return s ? new Date(s) : undefined;
};

export const rightStatementsValues = Object.fromEntries(
  Object.entries(rightStatementsLabelsUpload).map(([key, label]) => [label, key]),
);

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const getValueFromLabel = (field: string, label: string, rawData: any): string | null => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const found = rawData.dataset[field]?.find((item: any) => item.eng_label === label);
  return found ? found.value : null;
};

export function splitPrinciplesAndLegislation(values: string[]): {
  principles: string[];
  legislations: string[];
} {
  const PRINCIPLE_CODES = ["ARDNP", "ARDP", "TUDP"];
  const principles: string[] = [];
  const legislations: string[] = [];

  for (const v of values) {
    const match = PRINCIPLE_CODES.find((code) => v.toUpperCase().includes(code));
    if (match) {
      principles.push(match);
    } else {
      legislations.push(v);
    }
  }

  return { principles, legislations };
}

export function addToMapSet(map: Record<string, Set<string>>, key: string, value: string) {
  if (!map[key]) {
    map[key] = new Set();
  }
  map[key].add(value);
}

export type ApplicableLegislations = {
  eng_label?: string;
  value?: string;
  description?: string;
  link?: string;
  organisation_ids?: number[];
};

/**
 * Normalize URL for comparison by removing protocol and 'data.' subdomain
 */
const normalizeUrl = (url: string): string => {
  if (!url) return url;

  // Remove http://, https:// protocols
  let normalized = url.replace(/^https?:\/\//, "");

  // Remove 'data.' subdomain if present
  if (normalized.startsWith("data.")) {
    normalized = normalized.substring(5);
  }

  return normalized;
};

/**
 * Extract CELEX code from EUR-Lex URL (both ELI and CELEX formats)
 * Examples:
 *   https://eur-lex.europa.eu/eli/dir/2000/60/oj -> 32000L0060
 *   https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32000L0060 -> 32000L0060
 */
const extractCelexCode = (url: string): string | null => {
  if (!url) return null;

  // CELEX format: ?uri=CELEX:32000L0060
  const celexMatch = url.match(/CELEX:([A-Z0-9]+)/i);
  if (celexMatch) {
    return celexMatch[1].toUpperCase();
  }

  // ELI format: /eli/dir/2000/60/oj or /eli/dir/2007/60/oj?locale=fr
  const eliMatch = url.match(/\/eli\/(dir|reg|dec)\/(\d{4})\/(\d+)/i);
  if (eliMatch) {
    const [, docType, year, number] = eliMatch;
    const typeCode =
      docType.toUpperCase() === "DIR" ? "L" : docType.toUpperCase() === "REG" ? "R" : "D";
    return `3${year}${typeCode}${number.padStart(4, "0")}`;
  }

  return null;
};

export const getApplicableLegislationValueFromLabel = (
  label: string,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  rawData: any,
  field: string = "applicable_legislations",
): string | null => {
  const normalizedLabel = label.trim().toLowerCase();

  // Return null for empty or whitespace-only labels
  if (!normalizedLabel) {
    return null;
  }

  const normalizedLabelUrl = normalizeUrl(normalizedLabel);
  const labelCelexCode = extractCelexCode(label);

  const found = rawData.dataset[field]?.find((item: ApplicableLegislations) => {
    const itemLink = item.link?.toLowerCase() || "";
    const normalizedItemLink = normalizeUrl(itemLink);
    const itemCelexCode = extractCelexCode(item.link || "");

    // Match by CELEX code if both URLs contain one
    if (labelCelexCode && itemCelexCode && labelCelexCode === itemCelexCode) {
      return true;
    }

    return (
      item.eng_label?.toLowerCase().includes(normalizedLabel) ||
      item.value?.toLowerCase() === normalizedLabel ||
      item.description?.toLowerCase().includes(normalizedLabel) ||
      itemLink === normalizedLabel ||
      normalizedItemLink === normalizedLabelUrl
    );
  });

  return found ? found.value || null : null;
};
