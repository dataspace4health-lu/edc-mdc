import { z } from "zod";
import { NON_PUBLIC_RIGHTS_STATEMENT } from "../../schemas/distributionSchema";
import { DateUtils } from "../../utils/dateTimeHelpers";
import { getDuplicateStringValue } from "../../utils/duplicateValidation";

const policyActionSchema = z
  .object({
    policyActionType: z.string(),
    policyConstraintType: z.string().optional(),
    policyConstraintValue: z.string().optional(),
    temporalRestrictionStart: z.preprocess(
      (v) => (v === "" || v === null ? undefined : v),
      z.date().optional(),
    ),
    temporalRestrictionEnd: z.preprocess(
      (v) => (v === "" || v === null ? undefined : v),
      z.date().optional(),
    ),
    spatialRestrictions: z.array(z.string().nonempty()).optional(),
  })
  .superRefine((a, ctx) => {
    switch (a.policyConstraintType) {
      case "purpose":
      case "industry":
        if (!a.policyConstraintValue?.trim()) {
          ctx.addIssue({
            path: ["policyConstraintValue"],
            code: z.ZodIssueCode.custom,
            message: "Required",
          });
        }
        break;

      case "temporal": {
        const hasStart = !!a.temporalRestrictionStart;
        const hasEnd = !!a.temporalRestrictionEnd;

        if (!hasStart && !hasEnd) {
          ctx.addIssue({
            path: ["temporalRestrictionStart"],
            code: z.ZodIssueCode.custom,
            message: "At least one of the temporal restriction constraints must be set.",
          });
          ctx.addIssue({
            path: ["temporalRestrictionEnd"],
            code: z.ZodIssueCode.custom,
            message: "At least one of the temporal restriction constraints must be set.",
          });
        }
        if (hasStart && hasEnd && a.temporalRestrictionEnd! < a.temporalRestrictionStart!) {
          ctx.addIssue({
            path: ["temporalRestrictionEnd"],
            code: z.ZodIssueCode.custom,
            message: "End date cannot be earlier than start date.",
          });
        }
        break;
      }

      case "spatial":
        if (!a.spatialRestrictions || a.spatialRestrictions.length === 0) {
          ctx.addIssue({
            path: ["spatialRestrictions"],
            code: z.ZodIssueCode.custom,
            message:
              "At least one spatial restriction must be selected when constraint type is spatial.",
          });
        }
        break;
    }
  });

export const getDistributionFormInputSchema = ({
  requireByteSize = true,
}: { requireByteSize?: boolean } = {}) =>
  z
    .object({
      title: z.preprocess(
        (value) => (typeof value === "string" && value.trim().length === 0 ? undefined : value),
        z.string().min(1).optional(),
      ),
      description: z.string().min(8, "Description must be at least 8 characters long").optional(),
      downloadURLs: z.array(z.string().url()).optional(),
      accessURLs: z.array(z.string().url()).min(1, "At least one access URL is required"),
      fileFormat: z.string().optional(),
      distributionRightsStatement: z.string().nonempty(),
      otherFileFormatValue: z
        .string()
        .regex(/^[a-zA-Z0-9_\-.\s]+$/)
        .optional(),
      languages: z.array(z.string().nonempty()).optional(),
      internalOnly: z.boolean().optional(),
      isAnalytics: z.boolean().optional(),
      applicableLegislations: z.array(z.string().nonempty()).optional(),
      notes: z.string().optional(),
      license: z.string().optional(),
      distributionPath: z.string().nullable().optional(),
      availability: z.string().optional(),
      documentation: z.array(z.string().nonempty()).optional(),
      releaseDate: z.preprocess((value) => (value === "" ? undefined : value), z.date().optional()),
      modificationDate: z.preprocess(
        (value) => (value === "" || value === null ? undefined : value),
        z.date().optional(),
      ),
      linkedSchemas: z.array(z.string()).optional(),
      byteSize: z.number().min(0, "Must be a positive number").optional(),
      checksum: z.string().optional(),
      policyActions: z.array(policyActionSchema).optional(),
      spatialRestrictions: z.array(z.string().nonempty()).optional(),
      mediaType: z.string().optional(),
      compressionFormat: z.string().optional(),
      packagingFormat: z.string().optional(),
      distributionDCATStatus: z.string().optional(),
      spatialResolution: z.number().int().min(0, "Must be a positive number").optional(),
      temporalResolution: z.string().optional(),
      accessServices: z.array(z.number()).optional(),
    })
    .refine((data) => data.fileFormat !== "OTHER" || !!data.otherFileFormatValue, {
      message: "Required",
      path: ["otherFileFormatValue"],
    })
    .refine(
      (data) =>
        data.distributionRightsStatement !== NON_PUBLIC_RIGHTS_STATEMENT ||
        (data.fileFormat !== undefined && data.fileFormat !== null && data.fileFormat !== ""),
      {
        message: "File format is required when Rights are non-public.",
        path: ["fileFormat"],
      },
    )
    .refine(
      (data) =>
        !requireByteSize ||
        data.distributionRightsStatement !== NON_PUBLIC_RIGHTS_STATEMENT ||
        (data.byteSize !== undefined && data.byteSize !== null),
      {
        message: "Byte size is required when Rights are non-public.",
        path: ["byteSize"],
      },
    )
    .superRefine((data, ctx) => {
      if (getDuplicateStringValue(data.accessURLs)) {
        ctx.addIssue({
          path: ["accessURLs"],
          code: z.ZodIssueCode.custom,
          message: "Duplicate access URLs are not allowed.",
        });
      }

      if (getDuplicateStringValue(data.downloadURLs)) {
        ctx.addIssue({
          path: ["downloadURLs"],
          code: z.ZodIssueCode.custom,
          message: "Duplicate download URLs are not allowed.",
        });
      }

      if (getDuplicateStringValue(data.linkedSchemas, (value) => value.trim().toLowerCase())) {
        ctx.addIssue({
          path: ["linkedSchemas"],
          code: z.ZodIssueCode.custom,
          message: "Duplicate linked schemas are not allowed.",
        });
      }

      if (getDuplicateStringValue(data.documentation, (value) => value.trim().toLowerCase())) {
        ctx.addIssue({
          path: ["documentation"],
          code: z.ZodIssueCode.custom,
          message: "Duplicate documentation entries are not allowed.",
        });
      }
    });

export const distributionSchema = getDistributionFormInputSchema();

export type DistributionFormInputs = z.infer<typeof distributionSchema>;

export function toDistributionDTO(distributionItem: DistributionFormInputs) {
  const {
    fileFormat,
    downloadURLs,
    accessURLs,
    internalOnly,
    isAnalytics,
    applicableLegislations,
    distributionRightsStatement,
    notes,
    license,
    languages,
    distributionPath,
    availability,
    documentation,
    modificationDate,
    releaseDate,
    policyActions,
    spatialRestrictions,
    linkedSchemas,
    byteSize,
    checksum,
    mediaType,
    compressionFormat,
    packagingFormat,
    distributionDCATStatus,
    temporalResolution,
    spatialResolution,
    accessServices,
    ...distributionForm
  } = distributionItem;

  return {
    ...distributionForm,
    languages:
      languages && languages.length > 0
        ? typeof languages === "string"
          ? [languages]
          : languages
        : [],
    file_type: fileFormat ?? null,
    download_urls: downloadURLs ?? [],
    access_urls: Array.isArray(accessURLs) ? accessURLs : !accessURLs ? [] : [accessURLs],
    internal_only:
      typeof internalOnly === "string" ? (internalOnly === "on" ? true : false) : internalOnly,
    is_analytics:
      typeof isAnalytics === "string" ? (isAnalytics === "on" ? true : false) : isAnalytics,
    applicable_legislations:
      applicableLegislations && applicableLegislations.length > 0
        ? typeof applicableLegislations === "string"
          ? [applicableLegislations]
          : applicableLegislations
        : [],
    rights_statement: distributionRightsStatement,
    notes: notes ?? null,
    license: license ?? null,
    distribution_path: distributionPath ?? null,
    availability: availability ?? null,
    documentation: documentation && documentation.length > 0 ? documentation : [],
    policy_actions: (policyActions ?? []).map((a) => ({
      policy_action_type: a.policyActionType,
      policy_constraint_type: a.policyConstraintType ?? null,
      policy_constraint_value: a.policyConstraintValue ?? null,
      temporal_restriction_start: a.temporalRestrictionStart
        ? DateUtils.toYMD(new Date(a.temporalRestrictionStart))
        : null,
      temporal_restriction_end: a.temporalRestrictionEnd
        ? DateUtils.toYMD(new Date(a.temporalRestrictionEnd))
        : null,
      spatial_restrictions:
        a.spatialRestrictions && a.spatialRestrictions.length > 0
          ? Array.isArray(a.spatialRestrictions)
            ? a.spatialRestrictions
            : [a.spatialRestrictions]
          : [],
    })),
    modification_date: modificationDate ? DateUtils.toYMD(new Date(modificationDate)) : null,
    release_date: releaseDate ? DateUtils.toYMD(new Date(releaseDate)) : null,
    linked_schemas: Array.isArray(linkedSchemas)
      ? linkedSchemas
      : !linkedSchemas
        ? []
        : [linkedSchemas],
    byte_size: byteSize
      ? typeof byteSize === "string"
        ? parseInt(byteSize)
        : typeof byteSize === "number"
          ? byteSize
          : null
      : null,
    checksum: checksum ?? null,
    media_type: mediaType ?? null,
    compression_format: compressionFormat ?? null,
    packaging_format: packagingFormat ?? null,
    distribution_dcat_status: distributionDCATStatus ?? null,
    spatial_resolution: spatialResolution
      ? typeof spatialResolution === "string"
        ? parseInt(spatialResolution)
        : typeof spatialResolution === "number"
          ? spatialResolution
          : null
      : null,
    temporal_resolution: temporalResolution ?? null,
    access_service_ids: Array.isArray(accessServices)
      ? accessServices.map(Number)
      : typeof accessServices === "string"
        ? [Number(accessServices)]
        : [],
  };
}
