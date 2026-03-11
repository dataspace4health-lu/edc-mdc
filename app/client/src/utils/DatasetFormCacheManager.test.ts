import { expect, test } from "vitest";
import DatasetFormCacheManager from "./DatasetFormCacheManager";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type StoreType = { [key: string]: any };
const localStorageMock = (() => {
  let store: StoreType = {};
  return {
    getItem(key: string): string | null {
      return store[key] || null;
    },
    setItem(key: string, value: string): void {
      store[key] = value;
    },
    removeItem(key: string): void {
      delete store[key];
    },
    clear(): void {
      store = {};
    },
  };
})();

Object.defineProperty(window, "localStorage", { value: localStorageMock });

test("DatasetFormCacheManager saves and retrieves form data", () => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const formData: Record<string, any> = {
    contactName: "John Doe",
    publisherName: "John Doe publisher",
    contactEmail: "johndoe@example.com",
    title: "Sample Dataset Title",
    description: "This is a sample description for the dataset.",
    keywords: "AIR",
    themes: "ENVI",
    qualified_attributions: 1,
    spatial_coverage: "LUX",
    applicable_legislations: ["GDPR"],
    datasetType: "OFFICIAL",
    datasetTypeOtherValue: "",
    rightsStatement: "PUBLIC",
    timePeriodStart: "2021-12-31",
    timePeriodEnd: "2022-12-31",
    periodicity: "ANNUAL",
    distributionPath: "INSIPRE",
    notes: "",
    duration_of_administrative_utility: 3,
    final_disposition: null,
    conventions: ["CONVENTION"],
    areas_of_work: ["autorisations_certificats_subventions"],
    areas_of_competence: ["bruit"],
    dataProtectionTypes: ["commercial_confidentiality"],
    version: "0.0.1",
    creator: "John Doe",
    provenance: "Official records",
  };

  DatasetFormCacheManager.save(formData);

  const expected = {
    contactName: "John Doe",
    publisherName: "John Doe publisher",
    contactEmail: "johndoe@example.com",
    title: "Sample Dataset Title",
    description: "This is a sample description for the dataset.",
    keywords: "AIR",
    themes: "ENVI",
    qualified_attributions: 1,
    spatial_coverage: "LUX",
    applicable_legislations: ["GDPR"],
    datasetType: "OFFICIAL",
    datasetTypeOtherValue: "",
    rightsStatement: "PUBLIC",
    timePeriodStart: "2021-12-31",
    timePeriodEnd: "2022-12-31",
    periodicity: "ANNUAL",
    distributionPath: "INSIPRE",
    notes: "",
    duration_of_administrative_utility: 3,
    version: "0.0.1",
    creator: "John Doe",
    provenance: "Official records",
    dataProtectionTypes: ["commercial_confidentiality"],
    areas_of_competence: ["bruit"],
    areas_of_work: ["autorisations_certificats_subventions"],
    conventions: ["CONVENTION"],
    final_disposition: null,
  };

  expect(DatasetFormCacheManager.getFormData()).toStrictEqual(expected);
});
