import { describe, expect, it } from "vitest";
import { ResourceDatasetType, ResourceDistributionType } from "../../types";
import { validateDatasetForCompletion } from "./completionValidation";

const PUBLIC_RIGHTS = "http://publications.europa.eu/resource/authority/access-right/PUBLIC";
const THEME_ENVI = "http://publications.europa.eu/resource/authority/data-theme/ENVI";
const DATASET_TYPE = "http://publications.europa.eu/resource/authority/dataset-type/TEST_DATA";
const LANG_EN = "http://publications.europa.eu/resource/authority/language/ENG";

const buildDistribution = (
  overrides: Partial<ResourceDistributionType> = {},
): ResourceDistributionType =>
  ({
    id: 11,
    title: "Main Distribution",
    description: null,
    dataset_id: 1,
    distribution_dcat_status: null,
    download_urls: [],
    access_urls: ["https://example.com/distribution.csv"],
    file_type: null,
    rights_statement: PUBLIC_RIGHTS,
    languages: [],
    internal_only: false,
    is_analytics: false,
    applicable_legislations: [],
    notes: null,
    license: null,
    distribution_path: null,
    availability: null,
    linked_schemas: [],
    access_services: [],
    modification_date: null,
    release_date: null,
    documentation: [],
    byte_size: null,
    checksum: null,
    policy_actions: [],
    media_type: null,
    compression_format: null,
    packaging_format: null,
    spatial_resolution: null,
    temporal_resolution: null,
    ...overrides,
  }) as ResourceDistributionType;

const buildDataset = (overrides: Partial<ResourceDatasetType> = {}): ResourceDatasetType =>
  ({
    id: 1,
    status: "DRAFT",
    status_triggers: ["complete"],
    title: "Dataset Title",
    description: "Dataset Description",
    contact_ids: [],
    contact_names: [],
    contact_emails: [],
    user_id: 99,
    publisher_name: "Publisher",
    publisher_id: 10,
    identifier: "dataset-identifier",
    submitted_at: "2026-02-10T00:00:00Z",
    time_period_start: null,
    dataset_types: [{ value: DATASET_TYPE, eng_label: "Test Data" }],
    themes: [{ value: THEME_ENVI, eng_label: "Environment" }],
    keywords: [{ value: "water", eng_label: "Water", parent_value: null }],
    health_categories: [],
    health_themes: [],
    spatial_coverages: [],
    conventions: [],
    areas_of_work: [],
    areas_of_competence: [],
    applicable_legislations: [],
    languages: [{ value: LANG_EN, eng_label: "English" }],
    distributions: [buildDistribution()],
    group_manager_ids: [],
    group_manager_names: [],
    data_protection_types: [],
    creator_names: [],
    creator_ids: [],
    release_date: null,
    released_at: null,
    modified_at: null,
    deprecated_at: null,
    time_period_end: null,
    retention_period_start: null,
    retention_period_end: null,
    rights_statement: PUBLIC_RIGHTS,
    periodicity: null,
    version: null,
    notes: null,
    conforms_to: [],
    duration_of_administrative_utility: null,
    max_typical_age: null,
    min_typical_age: null,
    number_of_records: null,
    number_of_unique_individuals: null,
    is_any_dictionary_authentic_source: null,
    final_disposition: null,
    ...overrides,
  }) as ResourceDatasetType;

describe("validateDatasetForCompletion", () => {
  it("returns no errors for a valid dataset with one valid distribution", () => {
    const dataset = buildDataset();

    const errors = validateDatasetForCompletion(dataset);

    expect(errors).toEqual([]);
  });

  it("returns required error when there are no distributions", () => {
    const dataset = buildDataset({ distributions: [] });

    const errors = validateDatasetForCompletion(dataset);

    expect(errors).toContain(
      "At least one distribution is required before submitting the dataset.",
    );
  });

  it("returns distribution-level error when a distribution is invalid", () => {
    const dataset = buildDataset({
      distributions: [buildDistribution({ title: "CSV Export", access_urls: ["not-a-url"] })],
    });

    const errors = validateDatasetForCompletion(dataset);

    expect(errors.some((error) => error.includes("Distribution 1 (CSV Export)"))).toBe(true);
    expect(errors.some((error) => error.includes("Access URL"))).toBe(true);
  });

  it("ignores invalid distribution date strings via normalization", () => {
    const dataset = buildDataset({
      distributions: [
        buildDistribution({
          release_date: "not-a-date",
          modification_date: "also-not-a-date",
        }),
      ],
    });

    const errors = validateDatasetForCompletion(dataset);

    expect(errors).toEqual([]);
  });

  it("normalizes placeholder empty values in distribution arrays", () => {
    const dataset = buildDataset({
      distributions: [
        buildDistribution({
          applicable_legislations: [""],
        }),
      ],
    });

    const errors = validateDatasetForCompletion(dataset);

    expect(errors).toEqual([]);
  });

  it("returns distribution-level errors when duplicate manual URL values are provided", () => {
    const dataset = buildDataset({
      distributions: [
        buildDistribution({
          title: "CSV Export",
          access_urls: [
            "https://example.com/distribution.csv",
            "https://example.com/distribution.csv",
          ],
          download_urls: ["https://example.com/download.csv", "https://example.com/download.csv"],
        }),
      ],
    });

    const errors = validateDatasetForCompletion(dataset);

    expect(errors.some((error) => error.includes("Duplicate access URLs are not allowed."))).toBe(
      true,
    );
    expect(errors.some((error) => error.includes("Duplicate download URLs are not allowed."))).toBe(
      true,
    );
  });

  it("returns dataset-level errors when duplicate spatial resolutions are provided", () => {
    const dataset = buildDataset({
      spatial_resolutions: [10, 10],
    });

    const errors = validateDatasetForCompletion(dataset);

    expect(
      errors.some((error) => error.includes("Duplicate spatial resolutions are not allowed.")),
    ).toBe(true);
  });
});
