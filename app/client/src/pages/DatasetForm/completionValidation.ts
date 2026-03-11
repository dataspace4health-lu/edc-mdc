import datasetSchema from "../../schemas/datasetSchema";
import distributionSchema from "../../schemas/distributionSchema";
import { ResourceDatasetType, ResourceDistributionType } from "../../types";
import { DistributionFormInputs, getDistributionFormInputSchema } from "../distributions/dto";
import { DatasetFormInputs, getDatasetFormInputsSchema, toFormInputs } from "./datasetDTO";

const removePlaceholderEmptyValues = (value: unknown): unknown => {
  if (value instanceof Date) {
    return value;
  }

  if (Array.isArray(value)) {
    const filtered = value.filter((item) => item !== "");
    return filtered.map(removePlaceholderEmptyValues);
  }

  if (value && typeof value === "object") {
    const normalized: Record<string, unknown> = {};
    for (const [key, nested] of Object.entries(value)) {
      if (nested === null) {
        normalized[key] = undefined;
      } else {
        normalized[key] = removePlaceholderEmptyValues(nested);
      }
    }
    return normalized;
  }

  return value === null ? undefined : value;
};

const buildCompletionValidationMessage = (path: string, message: string): string => {
  const normalizedPath = path.replace(/\.\d+\./g, ".").replace(/\.\d+$/g, "");
  const fieldKey = normalizedPath.split(".").pop() || normalizedPath;
  const schemaField = datasetSchema.find(
    (field) => field.name === fieldKey || field.apiFieldName === fieldKey,
  );
  const fallbackLabel = fieldKey
    .replace(/_/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/^./, (s) => s.toUpperCase());
  const fieldLabel = schemaField?.shortLabel || fallbackLabel || "Field";
  return `${fieldLabel}: ${message}`;
};

const toDateOrUndefined = (value: string | null | undefined): Date | undefined => {
  if (!value) {
    return undefined;
  }

  const parsedDate = new Date(value);
  if (Number.isNaN(parsedDate.getTime())) {
    return undefined;
  }

  return parsedDate;
};

const toDistributionFormInputs = (
  distribution: ResourceDistributionType,
): DistributionFormInputs => ({
  title: distribution.title,
  description: distribution.description ?? undefined,
  downloadURLs: distribution.download_urls ?? [],
  accessURLs: distribution.access_urls,
  fileFormat: distribution.file_type?.value ?? undefined,
  distributionRightsStatement: distribution.rights_statement,
  languages: distribution.languages?.map((language) => language.value) ?? [],
  internalOnly: distribution.internal_only ?? undefined,
  isAnalytics: distribution.is_analytics ?? undefined,
  applicableLegislations: distribution.applicable_legislations ?? [],
  notes: distribution.notes ?? undefined,
  license: distribution.license?.value ?? undefined,
  distributionPath: distribution.distribution_path ?? undefined,
  availability: distribution.availability ?? undefined,
  documentation: Array.isArray(distribution.documentation) ? distribution.documentation : [],
  releaseDate: toDateOrUndefined(distribution.release_date),
  modificationDate: toDateOrUndefined(distribution.modification_date),
  linkedSchemas: distribution.linked_schemas ?? [],
  byteSize: distribution.byte_size ?? undefined,
  checksum: distribution.checksum ?? undefined,
  policyActions:
    distribution.policy_actions?.map((action) => ({
      policyActionType: action.policy_action_type,
      policyConstraintType: action.policy_constraint_type ?? undefined,
      policyConstraintValue: action.policy_constraint_value ?? undefined,
      temporalRestrictionStart: toDateOrUndefined(action.temporal_restriction_start),
      temporalRestrictionEnd: toDateOrUndefined(action.temporal_restriction_end),
      spatialRestrictions:
        action.spatial_restrictions?.map((restriction) => restriction.value) ?? [],
    })) ?? [],
  mediaType: distribution.media_type ?? undefined,
  compressionFormat: distribution.compression_format ?? undefined,
  packagingFormat: distribution.packaging_format ?? undefined,
  distributionDCATStatus: distribution.distribution_dcat_status ?? undefined,
  spatialResolution: distribution.spatial_resolution ?? undefined,
  temporalResolution: distribution.temporal_resolution ?? undefined,
  accessServices: distribution.access_services?.map((service) => Number(service.id)) ?? [],
});

const buildDistributionCompletionValidationMessage = (
  distributionIndex: number,
  distribution: ResourceDistributionType,
  path: string,
  message: string,
): string => {
  const normalizedPath = path.replace(/\.\d+\./g, ".").replace(/\.\d+$/g, "");
  const fieldKey = normalizedPath.split(".").pop() || normalizedPath;
  const schemaField = distributionSchema.find(
    (field) => field.name === fieldKey || field.apiFieldName === fieldKey,
  );
  const fallbackLabel = fieldKey
    .replace(/_/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/^./, (s) => s.toUpperCase());
  const fieldLabel = schemaField?.shortLabel || fallbackLabel || "Field";
  const distributionLabel = distribution.title
    ? `Distribution ${distributionIndex + 1} (${distribution.title})`
    : `Distribution ${distributionIndex + 1}`;
  return `${distributionLabel} - ${fieldLabel}: ${message}`;
};

const distributionCompletionValidationSchema = getDistributionFormInputSchema({
  requireByteSize: true,
});

const validateDistributionForCompletion = (
  distribution: ResourceDistributionType,
  distributionIndex: number,
): string[] => {
  const normalizedDistributionForm = removePlaceholderEmptyValues(
    toDistributionFormInputs(distribution),
  ) as DistributionFormInputs;
  const parsedDistribution = distributionCompletionValidationSchema.safeParse(
    normalizedDistributionForm,
  );

  if (parsedDistribution.success) {
    return [];
  }

  return parsedDistribution.error.issues.map((issue) =>
    buildDistributionCompletionValidationMessage(
      distributionIndex,
      distribution,
      issue.path.join("."),
      issue.message,
    ),
  );
};

export function validateDatasetForCompletion(
  datasetDto: ResourceDatasetType,
  options: { enableHealthDcat?: boolean } = {},
): string[] {
  const rawFormInputs = toFormInputs(datasetDto);
  const normalizedFormInputs = removePlaceholderEmptyValues(rawFormInputs) as DatasetFormInputs;
  const schema = getDatasetFormInputsSchema({
    enableHealthDcat: options.enableHealthDcat ?? false,
  });
  const parsed = schema.safeParse(normalizedFormInputs);
  const errors = new Set<string>();

  if (!Array.isArray(datasetDto.distributions) || datasetDto.distributions.length === 0) {
    errors.add("At least one distribution is required before submitting the dataset.");
  }

  if (Array.isArray(datasetDto.distributions)) {
    datasetDto.distributions.forEach((distribution, index) => {
      const distributionErrors = validateDistributionForCompletion(distribution, index);
      distributionErrors.forEach((distributionError) => errors.add(distributionError));
    });
  }

  if (!parsed.success) {
    parsed.error.issues.forEach((issue) => {
      errors.add(buildCompletionValidationMessage(issue.path.join("."), issue.message));
    });
  }

  return Array.from(errors);
}
