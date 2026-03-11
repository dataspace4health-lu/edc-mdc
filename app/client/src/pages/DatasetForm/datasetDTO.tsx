import { z } from "zod";
import { DateUtils } from "../../utils/dateTimeHelpers";
import { seriesMemberShipToDatasetIds } from "../../utils/memberDatasetsutils";
import { ResourceDatasetType, DatasetDtoType } from "../../types";
import { getDuplicateNumberValue, getDuplicateStringValue } from "../../utils/duplicateValidation";

export const getDatasetFormInputsSchema = ({
  enableHealthDcat = false,
}: {
  enableHealthDcat?: boolean;
} = {}) =>
  z
    .object({
      title: z.string().trim().min(1, "Title shouldn't be empty"),
      description: z.string().trim().min(1, "Description shouldn't be empty"),
      contactIds: z.array(z.number().int()).optional(),
      publisherId: z.string().nonempty(),
      keywords: z.array(z.string().nonempty()).optional(),
      themes: z.array(z.string().nonempty()).nonempty(),
      healthCategories: enableHealthDcat
        ? z.array(z.string().nonempty()).nonempty()
        : z.array(z.string().nonempty()).optional(),
      healthThemes: z.array(z.string().nonempty()).optional(),
      maxTypicalAge: z.number().int().positive().optional(),
      minTypicalAge: z.number().int().positive().optional(),
      numberOfRecords: z.number().int().positive().optional(),
      numberOfUniqueIndividuals: z.number().int().positive().optional(),
      spatial_coverages: z.array(z.string().nonempty()).optional(),
      conventions: z.array(z.string().nonempty()).optional(),
      areasOfWork: z.array(z.string().nonempty()).optional(),
      areasOfCompetence: z.array(z.string().nonempty()).optional(),
      applicableLegislations: z.array(z.string().nonempty()).optional(),
      datasetTypes: z.array(z.string().nonempty()).nonempty(),
      rightsStatement: z.string().nonempty(),
      datasetTypeOtherValue: z.string().optional(),
      timePeriodStart: z
        .preprocess((value) => (value === "" ? undefined : value), z.date())
        .optional(),
      timePeriodEnd: z.coerce.date().optional(),
      retentionPeriodStart: z
        .preprocess((value) => (value === "" ? undefined : value), z.date())
        .optional(),
      retentionPeriodEnd: z
        .preprocess((value) => (value === "" ? undefined : value), z.date())
        .optional(),
      periodicity: z.string().optional(),
      notes: z.string().optional(),
      releaseDate: z.preprocess((value) => (value === "" ? undefined : value), z.date().optional()),
      modified_at: z.preprocess(
        (value) => (value === "" || value === null ? undefined : value),
        z.date().optional(),
      ),
      deprecated_at: z.preprocess(
        (value) => (value === "" ? undefined : value),
        z.date().optional(),
      ),
      released_at: z.preprocess((value) => (value === "" ? undefined : value), z.date().optional()),

      version: z.string().optional(),
      duration_of_administrative_utility: z.number().int().min(1).optional(),
      final_disposition: z.string().optional(),
      creatorId: z.array(z.string()).optional(),
      identifier: z.string().optional(),
      groupManagers: z.array(z.number().int()).optional(),
      dataProtectionTypes: z.array(z.string().nonempty()).optional(),
      monitoringLocation: z.string().optional(),
      provenance: z.preprocess((val) => {
        if (!val || !Array.isArray(val)) return [];
        return val.filter(
          (s) =>
            s !== undefined && s !== null && s !== "" && typeof s === "string" && s.trim() !== "",
        );
      }, z.array(z.string()).optional()),
      healthLegalBasis: z.preprocess((val) => {
        if (!val || !Array.isArray(val)) return [];
        return val.filter(
          (s) =>
            s !== undefined && s !== null && s !== "" && typeof s === "string" && s.trim() !== "",
        );
      }, z.array(z.string()).optional()),
      populationCoverage: z.string().optional(),
      codeValues: z.array(z.string()).optional(),
      purpose: z.array(z.string()).optional(),
      codingSystems: z.array(z.string().url()).optional(),
      datasetFormInputsSchema: z.array(z.number()).optional(),
      languages: z.array(z.string().nonempty()).optional(),
      landingPages: z.array(z.string().url()).optional(),
      documentation: z.array(z.string()).optional(),
      conformsTo: z.array(z.string().url()).optional(),
      isDatasetSeries: z.boolean().optional(),
      memberDatasets: z.string().optional(),
      wasGeneratedBy: z.array(z.string()).optional(),
      otherIdentifiers: z.array(z.string()).optional(),
      versionNotes: z.preprocess((val) => {
        if (!val || !Array.isArray(val)) return [];
        return val.filter(
          (s) =>
            s !== undefined && s !== null && s !== "" && typeof s === "string" && s.trim() !== "",
        );
      }, z.array(z.string()).optional()),
      spatialResolutions: z
        .array(z.number().int().min(0, "Spatial resolution must be 0 or greater"))
        .optional(),
      temporalResolution: z.string().optional(),
      personalData: z.array(z.string().nonempty()).optional(),
    })
    .refine(
      (data) =>
        !data.datasetTypes.includes("OTHER") ||
        (data.datasetTypes.includes("OTHER") && !!data.datasetTypeOtherValue),
      {
        message: "Required",
        path: ["datasetTypeOtherValue"],
      },
    )
    .superRefine((data, ctx) => {
      if (enableHealthDcat && !data.themes.some((theme) => theme.endsWith("/HEAL"))) {
        ctx.addIssue({
          path: ["themes"],
          code: z.ZodIssueCode.custom,
          message: "Health datasets must include the Health theme.",
        });
      }

      if (data.timePeriodStart && data.timePeriodEnd && data.timePeriodEnd < data.timePeriodStart) {
        ctx.addIssue({
          path: ["timePeriodEnd"],
          code: z.ZodIssueCode.custom,
          message: "End date cannot be earlier than start date.",
        });
      }

      if (
        data.retentionPeriodEnd &&
        data.retentionPeriodStart &&
        data.retentionPeriodEnd < data.retentionPeriodStart
      ) {
        ctx.addIssue({
          path: ["retentionPeriodEnd"],
          code: z.ZodIssueCode.custom,
          message: "Retention period end date cannot be earlier than start date.",
        });
      }

      if (data.timePeriodStart && data.modified_at && data.modified_at < data.timePeriodStart) {
        ctx.addIssue({
          path: ["modified_at"],
          code: z.ZodIssueCode.custom,
          message: "Modified date cannot be earlier than start date.",
        });
      }

      if (data.timePeriodEnd && data.modified_at && data.modified_at > data.timePeriodEnd) {
        ctx.addIssue({
          path: ["modified_at"],
          code: z.ZodIssueCode.custom,
          message: "Modified date cannot be later than end date.",
        });
      }

      if (getDuplicateStringValue(data.conformsTo)) {
        ctx.addIssue({
          path: ["conformsTo"],
          code: z.ZodIssueCode.custom,
          message: "Duplicate conforms to values are not allowed.",
        });
      }

      if (getDuplicateStringValue(data.landingPages)) {
        ctx.addIssue({
          path: ["landingPages"],
          code: z.ZodIssueCode.custom,
          message: "Duplicate landing pages are not allowed.",
        });
      }

      if (getDuplicateStringValue(data.documentation, (value) => value.trim().toLowerCase())) {
        ctx.addIssue({
          path: ["documentation"],
          code: z.ZodIssueCode.custom,
          message: "Duplicate documentation values are not allowed.",
        });
      }

      if (getDuplicateStringValue(data.purpose, (value) => value.trim().toLowerCase())) {
        ctx.addIssue({
          path: ["purpose"],
          code: z.ZodIssueCode.custom,
          message: "Duplicate purpose values are not allowed.",
        });
      }

      if (getDuplicateStringValue(data.wasGeneratedBy, (value) => value.trim().toLowerCase())) {
        ctx.addIssue({
          path: ["wasGeneratedBy"],
          code: z.ZodIssueCode.custom,
          message: "Duplicate was generated by values are not allowed.",
        });
      }

      if (getDuplicateStringValue(data.otherIdentifiers, (value) => value.trim().toLowerCase())) {
        ctx.addIssue({
          path: ["otherIdentifiers"],
          code: z.ZodIssueCode.custom,
          message: "Duplicate other identifiers are not allowed.",
        });
      }

      if (getDuplicateStringValue(data.provenance, (value) => value.trim().toLowerCase())) {
        ctx.addIssue({
          path: ["provenance"],
          code: z.ZodIssueCode.custom,
          message: "Duplicate provenance values are not allowed.",
        });
      }

      if (getDuplicateStringValue(data.healthLegalBasis, (value) => value.trim().toLowerCase())) {
        ctx.addIssue({
          path: ["healthLegalBasis"],
          code: z.ZodIssueCode.custom,
          message: "Duplicate health legal basis values are not allowed.",
        });
      }

      if (getDuplicateStringValue(data.versionNotes, (value) => value.trim().toLowerCase())) {
        ctx.addIssue({
          path: ["versionNotes"],
          code: z.ZodIssueCode.custom,
          message: "Duplicate version notes are not allowed.",
        });
      }

      if (getDuplicateNumberValue(data.spatialResolutions) !== null) {
        ctx.addIssue({
          path: ["spatialResolutions"],
          code: z.ZodIssueCode.custom,
          message: "Duplicate spatial resolutions are not allowed.",
        });
      }

      if (getDuplicateStringValue(data.personalData, (value) => value.trim().toLowerCase())) {
        ctx.addIssue({
          path: ["personalData"],
          code: z.ZodIssueCode.custom,
          message: "Duplicate personal data values are not allowed.",
        });
      }
    });

export const datasetFormInputsSchema = getDatasetFormInputsSchema({ enableHealthDcat: false });

export type DatasetFormInputs = z.infer<ReturnType<typeof getDatasetFormInputsSchema>>;

export function toDatasetDTO(validatedForm: DatasetFormInputs): DatasetDtoType {
  const {
    groupManagers,
    contactIds,
    publisherId,
    timePeriodStart,
    timePeriodEnd,
    retentionPeriodStart,
    retentionPeriodEnd,
    datasetTypes,
    datasetTypeOtherValue,
    rightsStatement,
    notes,
    version,
    duration_of_administrative_utility,
    final_disposition,
    keywords,
    themes,
    healthCategories,
    healthThemes,
    maxTypicalAge,
    minTypicalAge,
    numberOfRecords,
    numberOfUniqueIndividuals,
    spatial_coverages,
    conventions,
    areasOfWork,
    areasOfCompetence,
    applicableLegislations,
    creatorId,
    identifier,
    releaseDate,
    modified_at,
    deprecated_at,
    released_at,
    dataProtectionTypes,
    monitoringLocation,
    isDatasetSeries,
    memberDatasets,
    provenance,
    healthLegalBasis,
    populationCoverage,
    codeValues,
    purpose,
    codingSystems,
    languages,
    landingPages,
    documentation,
    conformsTo,
    wasGeneratedBy,
    otherIdentifiers,
    versionNotes,
    spatialResolutions,
    temporalResolution,
    personalData,
    ...datasetForm
  } = validatedForm;

  return {
    ...datasetForm,
    release_date: releaseDate ? DateUtils.toYMD(new Date(releaseDate)) : null,
    modified_at: modified_at ? DateUtils.toYMD(new Date(modified_at)) : null,
    contact_ids: Array.isArray(contactIds)
      ? contactIds.length > 0
        ? contactIds.map((id) => Number(id))
        : null
      : typeof contactIds === "string" && contactIds
        ? [Number(contactIds)]
        : null,
    publisher_id: parseInt(publisherId as unknown as string),
    submitted_at: DateUtils.nowISO(),
    time_period_end: (timePeriodEnd && DateUtils.toYMD(new Date(timePeriodEnd))) || null,
    time_period_start: timePeriodStart ? DateUtils.toYMD(new Date(timePeriodStart)) : null,
    retention_period_start: retentionPeriodStart
      ? DateUtils.toYMD(new Date(retentionPeriodStart))
      : null,
    retention_period_end: retentionPeriodEnd ? DateUtils.toYMD(new Date(retentionPeriodEnd)) : null,
    dataset_types: typeof datasetTypes === "string" ? [datasetTypes] : datasetTypes,
    rights_statement: rightsStatement,
    notes: notes ?? null,
    version: version ?? null,
    duration_of_administrative_utility: duration_of_administrative_utility
      ? parseInt(duration_of_administrative_utility.toString())
      : null,
    final_disposition: final_disposition ?? null,
    keywords: typeof keywords === "string" ? [keywords] : (keywords ?? []),
    themes: typeof themes === "string" ? [themes] : themes,
    health_categories:
      healthCategories && healthCategories.length > 0
        ? typeof healthCategories === "string"
          ? [healthCategories]
          : healthCategories
        : [],
    health_themes:
      healthThemes && healthThemes.length > 0
        ? typeof healthThemes === "string"
          ? [healthThemes]
          : healthThemes
        : [],
    max_typical_age: maxTypicalAge ? parseInt(maxTypicalAge.toString()) : null,
    min_typical_age: minTypicalAge ? parseInt(minTypicalAge.toString()) : null,
    number_of_records: numberOfRecords ? parseInt(numberOfRecords.toString()) : null,
    number_of_unique_individuals: numberOfUniqueIndividuals
      ? parseInt(numberOfUniqueIndividuals.toString())
      : null,
    applicable_legislations:
      applicableLegislations && applicableLegislations.length > 0
        ? typeof applicableLegislations === "string"
          ? [applicableLegislations]
          : applicableLegislations
        : [],
    spatial_coverages:
      spatial_coverages && spatial_coverages.length > 0
        ? typeof spatial_coverages === "string"
          ? [spatial_coverages]
          : spatial_coverages
        : [],
    conventions:
      conventions && conventions.length > 0
        ? typeof conventions === "string"
          ? [conventions]
          : conventions
        : [],
    areas_of_work:
      areasOfWork && areasOfWork.length > 0
        ? typeof areasOfWork === "string"
          ? [areasOfWork]
          : areasOfWork
        : [],
    areas_of_competence:
      areasOfCompetence && areasOfCompetence.length > 0
        ? typeof areasOfCompetence === "string"
          ? [areasOfCompetence]
          : areasOfCompetence
        : [],
    group_managers: Array.isArray(groupManagers)
      ? groupManagers.map(Number)
      : typeof groupManagers === "string"
        ? [Number(groupManagers)]
        : [],
    creator_ids: Array.isArray(creatorId)
      ? creatorId.map(Number)
      : creatorId
        ? [Number(creatorId)]
        : [],
    identifier,
    data_protection_types:
      dataProtectionTypes && dataProtectionTypes.length > 0
        ? typeof dataProtectionTypes === "string"
          ? [dataProtectionTypes]
          : dataProtectionTypes
        : [],
    monitoring_location: monitoringLocation ?? null,
    provenance: Array.isArray(provenance)
      ? provenance.filter(
          (v) =>
            v !== undefined && v !== null && v !== "" && typeof v === "string" && v.trim() !== "",
        )
      : !provenance
        ? []
        : [provenance],
    health_legal_basis: Array.isArray(healthLegalBasis)
      ? healthLegalBasis.filter(
          (v) =>
            v !== undefined && v !== null && v !== "" && typeof v === "string" && v.trim() !== "",
        )
      : !healthLegalBasis
        ? []
        : [healthLegalBasis],
    population_coverage: populationCoverage ?? null,
    code_values: codeValues ?? [],
    purpose: Array.isArray(purpose) ? purpose : !purpose ? [] : [purpose],
    coding_systems: Array.isArray(codingSystems)
      ? codingSystems
      : !codingSystems
        ? []
        : [codingSystems],
    languages:
      languages && languages.length > 0
        ? typeof languages === "string"
          ? [languages]
          : languages
        : [],
    landing_pages: Array.isArray(landingPages) ? landingPages : !landingPages ? [] : [landingPages],
    documentation: Array.isArray(documentation)
      ? documentation
      : !documentation
        ? []
        : [documentation],
    conforms_to: Array.isArray(conformsTo) ? conformsTo : !conformsTo ? [] : [conformsTo],
    was_generated_by: Array.isArray(wasGeneratedBy)
      ? wasGeneratedBy
      : !wasGeneratedBy
        ? []
        : [wasGeneratedBy],
    is_dataset_series:
      typeof isDatasetSeries === "string"
        ? isDatasetSeries === "on"
          ? true
          : false
        : isDatasetSeries,
    member_datasets: memberDatasets?.split(",").map((id) => Number(id)) ?? undefined,
    other_identifiers: Array.isArray(otherIdentifiers)
      ? otherIdentifiers
      : !otherIdentifiers
        ? []
        : [otherIdentifiers],
    version_notes: Array.isArray(versionNotes)
      ? versionNotes.filter(
          (v) =>
            v !== undefined && v !== null && v !== "" && typeof v === "string" && v.trim() !== "",
        )
      : !versionNotes
        ? []
        : [versionNotes],
    spatial_resolutions: Array.isArray(spatialResolutions)
      ? spatialResolutions.map(Number)
      : spatialResolutions
        ? [Number(spatialResolutions)]
        : [],
    temporal_resolution: !temporalResolution ? null : temporalResolution,
    distributions: [],
    personal_data: Array.isArray(personalData) ? personalData : personalData ? [personalData] : [],
  };
}

export function toFormInputs(datasetDto: ResourceDatasetType): DatasetFormInputs {
  return {
    title: datasetDto.title,
    description: datasetDto.description,
    periodicity: datasetDto.periodicity?.value ?? "",
    contactIds: datasetDto.contact_ids ?? [],
    publisherId: datasetDto.publisher_id ? datasetDto.publisher_id.toString() : "",
    timePeriodStart: datasetDto.time_period_start
      ? new Date(datasetDto.time_period_start)
      : undefined,
    timePeriodEnd: datasetDto.time_period_end ? new Date(datasetDto.time_period_end) : undefined,
    retentionPeriodStart:
      datasetDto.retention_period_start && typeof datasetDto.retention_period_start === "string"
        ? new Date(datasetDto.retention_period_start)
        : undefined,
    retentionPeriodEnd:
      datasetDto.retention_period_end && typeof datasetDto.retention_period_end === "string"
        ? new Date(datasetDto.retention_period_end)
        : undefined,
    datasetTypes: ["", ...datasetDto.dataset_types.map((it) => it.value)],
    rightsStatement: datasetDto.rights_statement,
    keywords: ["", ...(datasetDto.keywords?.map((it) => it.value) ?? [])],
    themes: ["", ...datasetDto.themes.map((it) => it.value)],
    healthCategories: datasetDto.health_categories?.length
      ? ["", ...datasetDto.health_categories.map((it) => it.value)]
      : [""],
    healthThemes: datasetDto.health_themes?.length
      ? ["", ...datasetDto.health_themes.map((it) => it.value)]
      : [],
    maxTypicalAge: datasetDto.max_typical_age ?? undefined,
    minTypicalAge: datasetDto.min_typical_age ?? undefined,
    numberOfRecords: datasetDto.number_of_records ?? undefined,
    numberOfUniqueIndividuals: datasetDto.number_of_unique_individuals ?? undefined,
    spatial_coverages: datasetDto.spatial_coverages?.length
      ? ["", ...datasetDto.spatial_coverages.map((it) => it.value)]
      : [],
    conventions: datasetDto.conventions,
    areasOfWork: datasetDto.areas_of_work,
    areasOfCompetence: datasetDto.areas_of_competence,
    applicableLegislations: datasetDto.applicable_legislations,
    notes: datasetDto.notes ?? undefined,
    version: datasetDto.version ?? undefined,
    duration_of_administrative_utility: datasetDto.duration_of_administrative_utility ?? undefined,
    final_disposition: datasetDto.final_disposition ?? undefined,
    creatorId: datasetDto.creator_ids?.map((id) => id.toString()) ?? [],
    identifier: datasetDto.identifier ?? null,
    groupManagers: datasetDto.group_manager_ids?.map((id) => Number(id)) ?? [],
    releaseDate: datasetDto.release_date ? new Date(datasetDto.release_date) : undefined,
    modified_at: datasetDto.modified_at ? new Date(datasetDto.modified_at) : undefined,
    dataProtectionTypes: datasetDto.data_protection_types,
    monitoringLocation: datasetDto.monitoring_location ?? undefined,
    isDatasetSeries: datasetDto.is_dataset_series ?? undefined,
    memberDatasets: datasetDto.member_datasets
      ? seriesMemberShipToDatasetIds(datasetDto.member_datasets).join(",")
      : undefined,
    provenance: datasetDto.provenance ?? [],
    healthLegalBasis: datasetDto.health_legal_basis ?? [],
    populationCoverage:
      (datasetDto as { population_coverage?: string }).population_coverage ?? undefined,
    codeValues: datasetDto.code_values ?? [],
    purpose: datasetDto.purpose ?? undefined,
    codingSystems: datasetDto.coding_systems ?? [],
    languages: ["", ...datasetDto.languages.map((it) => it.value)],
    landingPages: datasetDto.landing_pages ?? [],
    documentation: datasetDto.documentation ?? undefined,
    conformsTo: datasetDto.conforms_to ?? [],
    wasGeneratedBy: datasetDto.was_generated_by ?? [],
    otherIdentifiers: datasetDto.other_identifiers ?? [],
    versionNotes: datasetDto.version_notes ?? [],
    spatialResolutions: datasetDto.spatial_resolutions ?? [],
    temporalResolution: datasetDto.temporal_resolution ?? undefined,
    personalData: datasetDto.personal_data ?? [],
  };
}
