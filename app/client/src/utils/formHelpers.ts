import { z } from "zod";
import groupBy from "just-group-by";
import { Utils } from "./helpers";

export type JSONFormValues = string | Array<string>;
export type JSONForm = { [key: string]: JSONFormValues };

const hasStringValue = (x: [string, FormDataEntryValue]): x is [string, string] =>
  typeof x[1] === "string" || x[1] instanceof String;

const mapFormDataValues = (current: JSONForm, next: [key: string, value: string]) => {
  const [key, value] = next;

  // checkbox keys (spotted by the '-ck#-' in the middle of their key) need special treatment
  const checkboxRegex = /-chkBox#-.*$/;
  if (checkboxRegex.test(key)) {
    if (value !== "") {
      const cleanKey = key.replace(checkboxRegex, "");
      return { ...current, [cleanKey]: [...(current[cleanKey] ?? []), value] };
    } else {
      return current;
    }
  }

  // 'array' keys (spotted by their arbitrary '[]' suffix) need special treatment
  if (key.endsWith("[]")) {
    if (value !== "") {
      const arraySuffixRegex = /\[\]$/;
      const cleanKey = key.replace(arraySuffixRegex, "");
      return { ...current, [cleanKey]: [...(current[cleanKey] ?? []), value] };
    } else {
      return current;
    }
  }

  return { ...current, [key]: value };
};

const gatherPrefixedKeys = (
  obj: { [key: string]: string | Array<string> },
  prefixRegex: RegExp,
  mainGroupKey: string,
) => {
  const keysToGroup = Object.keys(obj).filter((key: string) => prefixRegex.test(key));

  const groupedKeys = groupBy(keysToGroup, (x) => (prefixRegex.exec(x) ?? ["unmatched"])[0]);

  const groupedKeysWithValues = Object.keys(groupedKeys).map((groupKey) => {
    return groupedKeys[groupKey].reduce(
      (c, n) => {
        const cleanName = n.replace(groupKey, "");
        c[cleanName] = obj[n];
        return c;
      },
      {} as { [key: string]: string | Array<string> },
    );
  });

  const newObjWithGroups = {
    ...Utils.removeKeysFromObj(obj, keysToGroup),
    [mainGroupKey]: groupedKeysWithValues,
  };

  return newObjWithGroups;
};

export function reformatArrayFieldnamesForDisplay(
  arrayFieldNames: string[],
  errList: { [key: string]: string },
) {
  return Object.entries(errList).reduce(
    (curr, next) => {
      const [key, val] = next;
      return {
        ...curr,
        [arrayFieldNames.includes(key + "[]") ? key + "[]" : key]: val,
      };
    },
    {} as { [key: string]: string },
  );
}

export function parseErrorsForDisplay(itemIds: Array<string>, groupKey: string, err: z.ZodError) {
  const issues = err.issues;
  return issues
    .map((issue) => {
      const fullPath = issue.path;
      const rootPath = fullPath[0];
      if (rootPath === groupKey) {
        const idxInObj = parseInt(String(fullPath[1]));
        if (!isNaN(idxInObj)) {
          const nestedItemId = itemIds[idxInObj];
          const nameInForm = nestedItemId + "-" + String(fullPath[2]);
          return { name: nameInForm, message: issue.message };
        }
        // TODO Potential place to signal error if idx not found
      }
      return { name: String(rootPath), message: issue.message };
    })
    .reduce((current, next) => ({ ...current, [next.name]: next.message }), {});
}

export const FormHelpers = {
  hasStringValue,
  mapFormDataValues,
  gatherPrefixedKeys,
  parseErrorsForDisplay,
  reformatArrayFieldnamesForDisplay,
};
