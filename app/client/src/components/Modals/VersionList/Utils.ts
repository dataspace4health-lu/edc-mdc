import client from "../../../zodiosClient/client";
import { ResourceDatasetType } from "../../../types";
import { toReadableFormat } from "../../../utils/dataProtectionLabels";

export type DatasetVersionsProps = {
  datasetId: number;
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type Distribution = Record<string, any>;

export type Diff = {
  path: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  oldValue: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  newValue: any;
};

export const formatDateTime = (dateString: string | undefined | null) => {
  if (!dateString) return "";
  const date = new Date(dateString);
  return (
    date.toLocaleDateString(undefined, {
      year: "numeric",
      month: "long",
      day: "numeric",
    }) +
    " at " +
    date.toLocaleTimeString(undefined, {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    })
  );
};

export const fetchDatasetVersions = async (datasetId: number): Promise<ResourceDatasetType[]> => {
  const response =
    await client.get_dataset_versions_chain_api_v1_datasets__dataset_id__versions_chain_get({
      params: { dataset_id: datasetId },
      withCredentials: true,
    });
  return response;
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function deepDiff(obj1: any, obj2: any, path = ""): Diff[] {
  let diffs: Diff[] = [];

  const keys = new Set([...Object.keys(obj1 || {}), ...Object.keys(obj2 || {})]);

  keys.forEach((key) => {
    const val1 = obj1 ? obj1[key] : undefined;
    const val2 = obj2 ? obj2[key] : undefined;
    const currentPath = path ? `${path}.${key}` : key;

    if (
      typeof val1 === "object" &&
      val1 !== null &&
      !Array.isArray(val1) &&
      typeof val2 === "object" &&
      val2 !== null &&
      !Array.isArray(val2)
    ) {
      diffs = diffs.concat(deepDiff(val1, val2, currentPath));
    } else if (Array.isArray(val1) && Array.isArray(val2)) {
      if (!arraysHaveSameContent(val1, val2)) {
        diffs.push({ path: currentPath, oldValue: val1, newValue: val2 });
      }
    } else if (val1 !== val2) {
      diffs.push({
        path: currentPath,
        oldValue: val1,
        newValue: val2,
      });
    }
  });

  return diffs;
}

export const getTimeDiffText = (oldDateStr: string, newDateStr: string) => {
  const oldDate = new Date(oldDateStr);
  const newDate = new Date(newDateStr);

  // Met à minuit pour éviter les décalages horaires et heure dans le calcul
  const oldDateMidnight = new Date(oldDate.getFullYear(), oldDate.getMonth(), oldDate.getDate());
  const newDateMidnight = new Date(newDate.getFullYear(), newDate.getMonth(), newDate.getDate());
  const diffMs = newDateMidnight.getTime() - oldDateMidnight.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays < 1) return "Modified: today";
  if (diffDays < 30) return `Modified: ${diffDays} day${diffDays > 1 ? "s" : ""} ago`;
  const diffMonths = Math.floor(diffDays / 30);
  return `Modified: ${diffMonths} month${diffMonths > 1 ? "s" : ""} ago`;
};

export const searchParams = (version: ResourceDatasetType) =>
  new URLSearchParams({
    status: version.status,
    page: "1",
    datasetId: version.id.toString(),
  }).toString();

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function formatDataProtectionTypes(value: any) {
  let items: string[] = [];

  if (typeof value === "string") {
    items = value.split(",");
  } else if (Array.isArray(value)) {
    items = value;
  } else if (value) {
    items = [String(value)];
  }

  // Ici on applique toReadableFormat pour chaque élément
  return items.map((item) => toReadableFormat(item.trim())).join(", ");
}

export const getEngLabelFromFormFields = (
  value: string,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  formFields: Record<string, any>,
  path: string,
): string | undefined => {
  if (!path) return undefined;

  const field = formFields[path];
  if (!field) return undefined;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const option = field.options?.find((opt: any) => opt.value === value);
  if (option) return option.eng_label;
  return undefined;
};

export const formatValueWithLabels = (
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  val: any,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  formFields: Record<string, any>,
  path: string,
): string => {
  if (Array.isArray(val)) {
    return val
      .map((v) =>
        typeof v === "object" && v?.eng_label
          ? v.eng_label
          : typeof v === "string"
            ? getEngLabelFromFormFields(v, formFields, path) || v
            : v,
      )
      .join(", ");
  }

  if (typeof val === "object" && val?.eng_label) return val.eng_label;
  if (typeof val === "string") return getEngLabelFromFormFields(val, formFields, path) || val;

  return val?.toString() ?? "N/A";
};

export const getDistributionKey = (d: Distribution): string =>
  `${d.title ?? ""}||${d.description ?? ""}||${d.access_url ?? ""}`;

export const diffDistributions = (
  oldDists: Distribution[] = [],
  newDists: Distribution[] = [],
): Diff[] => {
  const diffs: Diff[] = [];

  const oldMap = Object.fromEntries(oldDists.map((d) => [getDistributionKey(d), d]));
  const newMap = Object.fromEntries(newDists.map((d) => [getDistributionKey(d), d]));

  const allKeys = Array.from(new Set([...Object.keys(oldMap), ...Object.keys(newMap)]));

  for (const key of allKeys) {
    const oldDist = oldMap[key];
    const newDist = newMap[key];

    if (!oldDist) {
      diffs.push({
        path: `distributions[${key}]`,
        oldValue: undefined,
        newValue: newDist,
      });
      continue;
    }

    if (!newDist) {
      diffs.push({
        path: `distributions[${key}]`,
        oldValue: oldDist,
        newValue: undefined,
      });
      continue;
    }

    for (const field of Object.keys({ ...oldDist, ...newDist })) {
      const oldVal = oldDist[field];
      const newVal = newDist[field];

      if (JSON.stringify(oldVal) !== JSON.stringify(newVal)) {
        diffs.push({
          path: `distributions[${key}].${field}`,
          oldValue: oldVal,
          newValue: newVal,
        });
      }
    }
  }

  return diffs;
};

export const diffDataDictionaries = (
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  oldDicts: any[] = [],
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  newDicts: any[] = [],
): Diff[] => {
  const diffs: Diff[] = [];

  const oldMap = Object.fromEntries(oldDicts.map((d) => [d.field_name, d]));
  const newMap = Object.fromEntries(newDicts.map((d) => [d.field_name, d]));

  const allFieldNames = Array.from(new Set([...Object.keys(oldMap), ...Object.keys(newMap)]));

  for (const fieldName of allFieldNames) {
    const oldDict = oldMap[fieldName];
    const newDict = newMap[fieldName];

    if (!oldDict) {
      diffs.push({
        path: `data_dictionaries[${fieldName}]`,
        oldValue: undefined,
        newValue: newDict,
      });
      continue;
    }

    if (!newDict) {
      diffs.push({
        path: `data_dictionaries[${fieldName}]`,
        oldValue: oldDict,
        newValue: undefined,
      });
      continue;
    }

    for (const field of Object.keys({ ...oldDict, ...newDict })) {
      const oldVal = oldDict[field];
      const newVal = newDict[field];

      if (JSON.stringify(oldVal) !== JSON.stringify(newVal)) {
        diffs.push({
          path: `data_dictionaries[${fieldName}].${field}`,
          oldValue: oldVal,
          newValue: newVal,
        });
      }
    }
  }

  return diffs;
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type Relation = Record<string, any>;

export const getRelationKey = (r: Relation): string => {
  if (r.relation_kind === "dataset") {
    return `dataset|${r.relation_type ?? ""}|${r.dataset_id ?? ""}`;
  }
  return `external|${r.external_url ?? ""}`;
};

export const diffRelations = (
  oldRelations: Relation[] = [],
  newRelations: Relation[] = [],
): Diff[] => {
  const diffs: Diff[] = [];

  const oldMap = Object.fromEntries(oldRelations.map((r) => [getRelationKey(r), r]));
  const newMap = Object.fromEntries(newRelations.map((r) => [getRelationKey(r), r]));

  const allKeys = Array.from(new Set([...Object.keys(oldMap), ...Object.keys(newMap)]));

  for (const key of allKeys) {
    const oldRel = oldMap[key];
    const newRel = newMap[key];

    if (!oldRel) {
      diffs.push({ path: `relations[${key}]`, oldValue: undefined, newValue: newRel });
      continue;
    }

    if (!newRel) {
      diffs.push({ path: `relations[${key}]`, oldValue: oldRel, newValue: undefined });
      continue;
    }

    for (const field of Object.keys({ ...oldRel, ...newRel })) {
      const oldVal = oldRel[field];
      const newVal = newRel[field];

      if (JSON.stringify(oldVal) !== JSON.stringify(newVal)) {
        diffs.push({ path: `relations[${key}].${field}`, oldValue: oldVal, newValue: newVal });
      }
    }
  }

  return diffs;
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type QualifiedAttribution = Record<string, any>;

export const getQualifiedAttributionKey = (qa: QualifiedAttribution): string =>
  `${qa.organisation_id ?? ""}|${qa.role ?? ""}`;

export const diffQualifiedAttributions = (
  oldQAs: QualifiedAttribution[] = [],
  newQAs: QualifiedAttribution[] = [],
): Diff[] => {
  const diffs: Diff[] = [];

  const oldMap = Object.fromEntries(oldQAs.map((qa) => [getQualifiedAttributionKey(qa), qa]));
  const newMap = Object.fromEntries(newQAs.map((qa) => [getQualifiedAttributionKey(qa), qa]));

  const allKeys = Array.from(new Set([...Object.keys(oldMap), ...Object.keys(newMap)]));

  for (const key of allKeys) {
    const oldQA = oldMap[key];
    const newQA = newMap[key];

    if (!oldQA) {
      diffs.push({
        path: `qualified_attributions[${key}]`,
        oldValue: undefined,
        newValue: newQA,
      });
      continue;
    }

    if (!newQA) {
      diffs.push({
        path: `qualified_attributions[${key}]`,
        oldValue: oldQA,
        newValue: undefined,
      });
      continue;
    }

    for (const field of Object.keys({ ...oldQA, ...newQA })) {
      const oldVal = oldQA[field];
      const newVal = newQA[field];

      if (JSON.stringify(oldVal) !== JSON.stringify(newVal)) {
        diffs.push({
          path: `qualified_attributions[${key}].${field}`,
          oldValue: oldVal,
          newValue: newVal,
        });
      }
    }
  }

  return diffs;
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function arraysHaveSameContent(arr1: any[], arr2: any[]): boolean {
  if (arr1.length !== arr2.length) return false;

  return arr1.every((item1) =>
    arr2.some((item2) => {
      if (
        typeof item1 === "object" &&
        item1 !== null &&
        typeof item2 === "object" &&
        item2 !== null
      ) {
        return areObjectsEqual(item1, item2);
      }
      if (typeof item1 === "string" && typeof item2 === "string") {
        return item1.trim().toLowerCase() === item2.trim().toLowerCase();
      }
      return item1 === item2;
    }),
  );
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function areObjectsEqual(o1: any, o2: any): boolean {
  const keys1 = Object.keys(o1).sort((a, b) => a.localeCompare(b));
  const keys2 = Object.keys(o2).sort((a, b) => a.localeCompare(b));
  if (keys1.length !== keys2.length) return false;
  for (let i = 0; i < keys1.length; i++) {
    if (keys1[i] !== keys2[i]) return false;
    const val1 = o1[keys1[i]];
    const val2 = o2[keys2[i]];

    if (typeof val1 === "string" && typeof val2 === "string") {
      if (val1.trim().toLowerCase() !== val2.trim().toLowerCase()) {
        return false;
      }
    } else if (val1 !== val2) {
      return false;
    }
  }
  return true;
}
