import { rightStatementsOptions } from "../utils/rightStatementsLabels";
import { dataProtectionTypeOptions } from "../utils/dataProtectionLabels";
import sortPeriodicities from "../utils/sortPeriodicities";
import { FormType, ResourceUserType } from "../types";
import { FieldType } from "./field-types";
import {
  filterFormFieldsByOrganisation,
  sortFormFieldsByLabel,
} from "../utils/filterFormFieldsByOrganisation";
import { personalDataOptions } from "../utils/personalDataLabels";

type EnumValue = {
  value: string;
  eng_label: string;
};

interface DatasetSchema {
  name: string;
  apiFieldName: string;
  type: FieldType;
  shortLabel: string;
  longLabel: string;
  required?: boolean;
  recommended?: boolean;
  isMulti?: boolean;
  isClearable?: boolean;
  inputType?: string;
  info?: string;
  explanation?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  hide?: (user: any) => boolean;
  options?: (
    formLoaderData: FormType,
    user: ResourceUserType | null,
    selectedPublisherId?: string | null,
  ) => { label: string; value: string }[];
  minLength?: number;
  maxLength?: number;
  testData?: string | string[];
  placeholder?: string;
}

const datasetSchema: DatasetSchema[] = [
  {
    name: "title",
    apiFieldName: "title",
    type: "InputField",
    inputType: "text",
    shortLabel: "Title",
    longLabel: "Title",
    explanation: "A name given to the dataset metadata record.",
    required: true,
    maxLength: 120,
    testData: `Dataset Title ${Math.random().toString(36).substring(2, 15)}`, // NOSONAR: Math.random() is safe here - used only for test data generation, not for security purposes
  },
  {
    name: "description",
    apiFieldName: "description",
    type: "TextArea",
    shortLabel: "Description",
    longLabel: "Description",
    explanation: "A free-text account in the metadata record describing the underlying data.",
    required: true,
    minLength: 3,
    testData: "This is a sample description for the dataset.",
  },
  {
    name: "isDatasetSeries",
    apiFieldName: "is_dataset_series",
    type: "Custom",
    shortLabel: "Dataset Series",
    longLabel: "Is this a dataset series?",
    explanation:
      "A dataset series is a collection of datasets published separately but sharing common characteristics.",
  },
  {
    name: "version",
    apiFieldName: "version",
    type: "InputField",
    shortLabel: "Version",
    longLabel: "Version",
    explanation: "The version indicator (name or identifier) of a resource.",
    info: "This field is optional.",
    inputType: "text",
    testData: "0.0.1",
  },
  {
    name: "versionNotes",
    apiFieldName: "version_notes",
    type: "MultiTextArea",
    shortLabel: "Version Notes",
    longLabel: "Version Notes",
    explanation:
      "A description of differences between this metadata record version and a previous version.",
    info: "This field is optional.",
    placeholder: "Add description between versions",
  },
  {
    name: "publisherId",
    apiFieldName: "publisher_id",
    type: "Custom",
    shortLabel: "Publisher",
    longLabel: "Publisher",
    explanation:
      "An entity (organisation) responsible for making the dataset metadata record available.",
    required: true,
    isMulti: false,
    options: (formLoaderData: FormType, user: ResourceUserType | null) => {
      const filteredOrgs = formLoaderData.organisation.organisations.filter((org) => {
        if (
          user?.permissions?.includes("roles:manage") ||
          !user?.feature_options.enable_multi_tenants
        ) {
          return true;
        }

        return user?.current_organisation?.id.toString() === org.value.toString();
      });

      return filteredOrgs.map((org) => ({
        label: org.eng_label,
        value: org.value,
      }));
    },
    testData: "1",
  },
  {
    name: "creatorId",
    apiFieldName: "creator_ids",
    type: "DropdownSelect",
    shortLabel: "Creators",
    longLabel: "Creators",
    explanation: "An entity responsible for producing the underlying data.",
    info: "This field is optional.",
    isMulti: true,
    options: (formLoaderData: FormType) =>
      formLoaderData.organisation.organisations
        .filter((org) => !org.is_deprecated)
        .map((org) => ({
          label: org.eng_label,
          value: org.value,
        })),
    testData: ["1"],
  },
  {
    name: "contactIds",
    apiFieldName: "contact_ids",
    type: "DropdownSelect",
    shortLabel: "Contact Points",
    longLabel: "Contact Points",
    explanation:
      "Contact information for sending comments about the underlying data or its metadata record.",
    info: "This field is recommended.",
    recommended: true,
    required: false,
    isMulti: true,
    testData: "1",
  },
  {
    name: "groupManagers",
    apiFieldName: "group_managers",
    type: "DropdownSelect",
    shortLabel: "Group Managers",
    longLabel: "Group Managers",
    explanation: "Group manager(s) responsible for validating the dataset metadata record.",
    info: "Choose the group manager(s) who will be informed about this dataset. This field is optional.",
    isMulti: true,
    hide: (user) => !user?.feature_options.enable_validation_via_group_manager,
    options: (formLoaderData: FormType) =>
      formLoaderData.dataset.group_managers.map((enumValue: EnumValue) => ({
        label: enumValue.eng_label,
        value: enumValue.value.toString(),
      })),
    testData: "1",
  },
  {
    name: "keywords",
    apiFieldName: "keywords",
    type: "DropdownSelect",
    shortLabel: "Keywords",
    longLabel: "Keywords",
    explanation:
      "A keyword or tag describing the underlying data represented by this metadata record.",
    recommended: true,
    info: "This field is recommended.",
    isMulti: true,
    options: (
      formLoaderData: FormType,
      user: ResourceUserType | null,
      selectedPublisherId?: string | null,
    ) => {
      const filteredFields = filterFormFieldsByOrganisation(formLoaderData.dataset.keywords, {
        user,
        selectedPublisherId,
      });

      return filteredFields.map((enumValue: EnumValue) => ({
        label: enumValue.eng_label,
        value: enumValue.value,
      }));
    },
    testData: "employment",
  },
  {
    name: "themes",
    apiFieldName: "themes",
    type: "DropdownSelect",
    shortLabel: "Themes",
    longLabel: "Themes",
    explanation:
      "A category assigned in the metadata record for the underlying data. Multiple themes are possible.",
    required: true,
    isMulti: true,
    options: (formLoaderData: FormType) =>
      formLoaderData.dataset.themes.map((enumValue: EnumValue) => ({
        label: enumValue.eng_label,
        value: enumValue.value,
      })),
    testData: "http://publications.europa.eu/resource/authority/data-theme/ENVI",
  },
  {
    name: "healthCategories",
    apiFieldName: "health_categories",
    type: "DropdownSelect",
    shortLabel: "Health Category",
    longLabel: "Health Category",
    explanation:
      "The health category assigned to the underlying data, using the mandatory controlled vocabulary.",
    isMulti: true,
    // Visibility now controlled by HealthDatasetSelector state, not feature flag
    options: (formLoaderData: FormType) =>
      formLoaderData.dataset.health_categories.map((enumValue: EnumValue) => ({
        label: enumValue.eng_label,
        value: enumValue.value,
      })),
    testData: "EHRS",
    required: true,
  },
  {
    name: "healthThemes",
    apiFieldName: "health_themes",
    type: "DropdownSelect",
    shortLabel: "Health Theme",
    longLabel: "Health Theme",
    explanation:
      "Health-specific thematic category assigned in the metadata record for the underlying data.",
    isMulti: true,
    // Visibility now controlled by HealthDatasetSelector state, not feature flag
    options: (formLoaderData: FormType) =>
      formLoaderData.dataset.health_themes.map((enumValue: EnumValue) => ({
        label: enumValue.eng_label,
        value: enumValue.value,
      })),
    testData: ["ENVIRONMENTAL_HEALTH"],
  },
  {
    name: "healthLegalBasis",
    apiFieldName: "health_legal_basis",
    type: "MultiTextArea",
    shortLabel: "Health Legal Basis",
    longLabel: "Health Legal Basis",
    explanation: "Legal basis linked to access, use, or management of the underlying health data.",
    info: "This field is recommended.",
    placeholder: "Enter health legal basis information",
    testData: ["Health regulation reference"],
    recommended: true,
  },
  {
    name: "maxTypicalAge",
    apiFieldName: "max_typical_age",
    type: "InputField",
    inputType: "number",
    shortLabel: "Maximum Typical Age",
    longLabel: "Maximum Typical Age",
    explanation:
      "The maximum typical age of individuals represented in the underlying health data.",
    info: "This field is recommended.",
    recommended: true,
  },
  {
    name: "minTypicalAge",
    apiFieldName: "min_typical_age",
    type: "InputField",
    inputType: "number",
    shortLabel: "Minimum Typical Age",
    longLabel: "Minimum Typical Age",
    explanation:
      "The minimum typical age of individuals represented in the underlying health data.",
    info: "This field is recommended.",
    recommended: true,
  },
  {
    name: "numberOfRecords",
    apiFieldName: "number_of_records",
    type: "InputField",
    inputType: "number",
    shortLabel: "Number of Records",
    longLabel: "Number of Records",
    explanation: "The number of records in the underlying data.",
    info: "This field is recommended.",
    recommended: true,
  },
  {
    name: "numberOfUniqueIndividuals",
    apiFieldName: "number_of_unique_individuals",
    type: "InputField",
    inputType: "number",
    shortLabel: "Number of Unique Individuals",
    longLabel: "Number of Unique Individuals",
    explanation: "The number of unique individuals represented in the underlying health data.",
    info: "This field is recommended.",
    recommended: true,
  },
  {
    name: "populationCoverage",
    apiFieldName: "population_coverage",
    type: "TextArea",
    shortLabel: "Population Coverage",
    longLabel: "Population Coverage",
    explanation: "The population or demographic groups covered by the underlying health data.",
    info: "This field is recommended.",
    recommended: true,
    minLength: 3,
  },
  {
    name: "codeValues",
    apiFieldName: "code_values",
    type: "CreatableSelect",
    shortLabel: "Code Values",
    longLabel: "Code Values",
    explanation:
      "Code values used in the underlying data, including coding systems and value sets.",
    info: "This field is recommended.",
    recommended: true,
    isMulti: true,
    placeholder: "Add code value and press enter to add multiple...",
  },
  {
    name: "purpose",
    apiFieldName: "purpose",
    type: "CreatableSelect",
    shortLabel: "Purpose",
    longLabel: "Purpose",
    explanation:
      "Purpose(s) linked to collection, processing, or use of the underlying health data.",
    info: "This field is recommended.",
    recommended: true,
    isMulti: true,
    placeholder: "Add purpose and press enter to add multiple...",
  },
  {
    name: "codingSystems",
    apiFieldName: "coding_systems",
    type: "CreatableSelect",
    shortLabel: "Coding System",
    longLabel: "Coding System",
    explanation: "Coding systems used in the underlying health data.",
    isMulti: true,
    info: "This field is recommended.",
    recommended: true,
    placeholder: "Add coding system URL and press enter to add multiple...",
  },
  {
    name: "personalData",
    apiFieldName: "personal_data",
    type: "DropdownSelect",
    shortLabel: "Personal Data",
    longLabel: "Personal Data",
    explanation: "Personal-data categories associated with the underlying data.",
    info: "This field is recommended.",
    recommended: true,
    isMulti: true,
    options: () =>
      personalDataOptions.map((option: { value: string; label: string }) => ({
        value: option.value,
        label: option.label,
      })),
  },
  {
    name: "datasetTypes",
    apiFieldName: "dataset_types",
    type: "DropdownSelect",
    shortLabel: "Dataset Types",
    longLabel: "Dataset Types",
    explanation: "A type assigned in the metadata record that characterizes the underlying data.",
    required: true,
    isMulti: true,
    options: (formLoaderData: FormType) =>
      formLoaderData.dataset.dataset_types.map((enumValue: EnumValue) => ({
        label: enumValue.eng_label,
        value: enumValue.value,
      })),
    testData: "http://publications.europa.eu/resource/authority/dataset-type/TEST_DATA",
  },
  {
    name: "timePeriodStart",
    apiFieldName: "time_period_start",
    type: "InputField",
    shortLabel: "Start of Temporal Coverage",
    longLabel: "Start of Temporal Coverage",
    explanation: "Start of the temporal period covered by the underlying data.",
    info: "This field is optional.",
    inputType: "date",
    required: false,
    testData: "2022-01-01",
  },
  {
    name: "timePeriodEnd",
    apiFieldName: "time_period_end",
    type: "InputField",
    shortLabel: "End of Temporal Coverage",
    longLabel: "End of Temporal Coverage",
    explanation: "End of the temporal period covered by the underlying data.",
    info: "This field is optional. If you only know the end month, select the last day of the month. If you only know the end year, select 31 December of that year.",
    inputType: "date",
    testData: "2023-01-01",
  },
  {
    name: "retentionPeriodStart",
    apiFieldName: "retention_period_start",
    type: "InputField",
    shortLabel: "Start of Retention Period",
    longLabel: "Start of Retention Period",
    explanation: "Start of the period for which health data is retained.",
    info: "This field is recommended.",
    inputType: "date",
    recommended: true,
    required: false,
    testData: "2023-01-01",
  },
  {
    name: "retentionPeriodEnd",
    apiFieldName: "retention_period_end",
    type: "InputField",
    shortLabel: "End of Retention Period",
    longLabel: "End of Retention Period",
    explanation: "End of the period for which health data is retained.",
    info: "This field is recommended.",
    inputType: "date",
    recommended: true,
    required: false,
    testData: "2025-01-01",
  },
  {
    name: "periodicity",
    apiFieldName: "periodicity",
    type: "DropdownSelect",
    shortLabel: "Frequency",
    longLabel: "Frequency",
    explanation: "The frequency at which the underlying data is updated.",
    recommended: true,
    info: "This field is recommended.",
    isMulti: false,
    isClearable: true,
    options: (formLoaderData: FormType) =>
      sortPeriodicities(formLoaderData.dataset.periodicities).map((enumValue: EnumValue) => ({
        label: enumValue.eng_label,
        value: enumValue.value,
      })),
    testData: "http://publications.europa.eu/resource/authority/frequency/ANNUAL",
  },
  {
    name: "releaseDate",
    apiFieldName: "release_date",
    type: "InputField",
    shortLabel: "Release Date",
    longLabel: "Release Date",
    explanation:
      "The date of formal issuance (for example publication) of the dataset metadata record.",
    info: "This field is optional.",
    inputType: "date",
    testData: "2022-01-01",
  },
  {
    name: "modified_at",
    apiFieldName: "modified_at",
    type: "InputField",
    shortLabel: "Modification Date",
    longLabel: "Modification Date",
    explanation: "The most recent date on which the dataset metadata record was changed.",
    info: "This field is optional.",
    inputType: "date",
    testData: "2022-01-01",
  },
  {
    name: "rightsStatement",
    apiFieldName: "rights_statement",
    type: "Custom",
    shortLabel: "Access Rights",
    longLabel: "Access Rights",
    explanation:
      "Information indicating whether access to the underlying data is public, restricted, or non-public.",
    required: true,
    // @ts-expect-error Not used
    options: (formLoaderData: FormType) =>
      rightStatementsOptions.map((enumValue: EnumValue) => ({
        value: enumValue.value,
        label: enumValue.eng_label,
      })),
    testData: "http://publications.europa.eu/resource/authority/access-right/PUBLIC",
  },
  {
    name: "dataProtectionTypes",
    apiFieldName: "data_protection_types",
    type: "DropdownSelect",
    shortLabel: "Data Protection Types",
    longLabel: "Data Protection Types",
    explanation: "Data-protection categories that apply to the underlying data.",
    info: "This field is recommended.",
    recommended: true,
    isMulti: true,
    // @ts-expect-error Not used
    options: (formLoaderData: FormType) => dataProtectionTypeOptions,
    testData: "commercial_confidentiality",
  },
  {
    name: "applicableLegislations",
    apiFieldName: "applicable_legislations",
    type: "DropdownSelect",
    shortLabel: "Applicable Legislations",
    longLabel: "Applicable Legislations",
    explanation:
      "Legislation that mandates creation or management of the underlying data or its metadata record.",
    info: "This field is optional.",
    isMulti: true,
    options: (
      formLoaderData: FormType,
      user: ResourceUserType | null,
      selectedPublisherId?: string | null,
    ) => {
      const filteredFields = filterFormFieldsByOrganisation(
        formLoaderData.dataset.applicable_legislations,
        {
          user,
          selectedPublisherId,
        },
      );

      const mappedFields = filteredFields.map((enumValue: EnumValue) => ({
        label: enumValue.eng_label,
        value: enumValue.value,
      }));

      return sortFormFieldsByLabel(mappedFields);
    },
    testData: "health",
  },
  {
    name: "conformsTo",
    apiFieldName: "conforms_to",
    type: "CreatableSelect",
    shortLabel: "Conforms to",
    isMulti: true,
    longLabel: "An implementing rule or other specification.",
    explanation: "An implementing rule or other specification referenced by the metadata record.",
  },
  {
    name: "languages",
    apiFieldName: "languages",
    type: "DropdownSelect",
    shortLabel: "Languages",
    longLabel: "Languages",
    explanation:
      "A language used in the underlying data. This can be repeated when multiple languages are present.",
    info: "This field is optional.",
    isMulti: true,
    options: (formLoaderData: FormType) =>
      formLoaderData.dataset.languages.map((enumValue: EnumValue) => ({
        label: enumValue.eng_label,
        value: enumValue.value,
      })),
    testData: "http://publications.europa.eu/resource/authority/language/ENG",
  },
  {
    name: "spatial_coverages",
    apiFieldName: "spatial_coverages",
    type: "DropdownSelect",
    shortLabel: "Geographical Coverage",
    longLabel: "Geographical Coverage",
    explanation: "A geographic region covered by the underlying data.",
    info: "This field is recommended.",
    recommended: true,
    isMulti: true,
    options: (formLoaderData: FormType) =>
      formLoaderData.dataset.spatial_coverages.map((enumValue: EnumValue) => ({
        label: enumValue.eng_label,
        value: enumValue.value,
      })),
    testData: "http://publications.europa.eu/resource/authority/country/LUX",
  },
  {
    name: "monitoringLocation",
    apiFieldName: "monitoringlocation",
    type: "InputField",
    shortLabel: "Monitoring Location",
    longLabel: "Monitoring Location",
    explanation: "",
    info: "This field is optional.",
    inputType: "text",
    hide: (user) => !user?.feature_options.enable_monitoring_location,
    testData: "Luxembourg",
  },
  {
    name: "landingPages",
    apiFieldName: "landing_pages",
    type: "CreatableSelect",
    shortLabel: "Landing Pages",
    longLabel: "Landing Pages",
    explanation:
      "A web page providing access to the metadata record, distributions, and/or additional information.",
    isMulti: true,
    info: "This field is optional.",
    placeholder: "Add landing page URL and press enter to add multiple...",
  },
  {
    name: "documentation",
    apiFieldName: "documentation",
    type: "CreatableSelect",
    shortLabel: "Documentation",
    longLabel: "Documentation",
    explanation: "A page or document about the metadata record or the underlying data.",
    isMulti: true,
    info: "This field is optional.",
    placeholder: "Add documentation and press enter to add multiple...",
  },
  {
    name: "provenance",
    apiFieldName: "provenance",
    type: "MultiTextArea",
    shortLabel: "Provenance",
    longLabel: "Provenance",
    explanation: "A statement about the lineage of the underlying data.",
    info: "This field is optional.",
    placeholder: "Enter provenance information",
    testData: ["Official records"],
  },
  {
    name: "conventions",
    apiFieldName: "conventions",
    type: "DropdownSelect",
    shortLabel: "Conventions",
    longLabel: "Conventions",
    explanation: "",
    info: "This field is optional.",
    isMulti: true,
    options: (formLoaderData: FormType) =>
      formLoaderData.dataset.conventions.map((enumValue: EnumValue) => ({
        label: enumValue.eng_label,
        value: enumValue.value,
      })),
    hide: (user) => !user?.feature_options.enable_conventions,
    testData: "CONVENTION",
  },
  {
    name: "areasOfWork",
    apiFieldName: "areas_of_work",
    type: "DropdownSelect",
    shortLabel: "Areas of Work",
    longLabel: "Areas of Work",
    explanation: "",
    info: "This field is optional.",
    isMulti: true,
    options: (formLoaderData: FormType) =>
      formLoaderData.dataset.areas_of_work.map((enumValue: EnumValue) => ({
        label: enumValue.eng_label,
        value: enumValue.value,
      })),
    hide: (user) => !user?.feature_options.enable_area_of_work_and_competence,
    testData: "autorisations_certificats_subventions",
  },
  {
    name: "areasOfCompetence",
    apiFieldName: "areas_of_competence",
    type: "DropdownSelect",
    shortLabel: "Areas of Competence",
    longLabel: "Areas of Competence",
    explanation: "",
    info: "This field is optional.",
    isMulti: true,
    options: (formLoaderData: FormType) =>
      formLoaderData.dataset.areas_of_competence.map((enumValue: EnumValue) => ({
        label: enumValue.eng_label,
        value: enumValue.value,
      })),
    hide: (user) => !user?.feature_options.enable_area_of_work_and_competence,
    testData: "autorisations_certificats_subventions",
  },
  {
    name: "duration_of_administrative_utility",
    apiFieldName: "duration_of_administrative_utility",
    type: "InputField",
    shortLabel: "Duration of administrative utility (in years)",
    longLabel: "Duration of administrative utility (in years)",
    explanation: "",
    info: "This field is optional.",
    inputType: "number",
    hide: (user) => !user?.feature_options.enable_duration_of_data,
    testData: "3",
  },
  {
    name: "final_disposition",
    apiFieldName: "final_disposition",
    type: "DropdownSelect",
    shortLabel: "Final Disposition",
    longLabel: "Final Disposition",
    explanation: "",
    info: "This field is optional.",
    isMulti: false,
    // @ts-expect-error Not used
    options: (formLoaderData: FormType) => [
      { value: "archive", label: "Archive" },
      { value: "destroy", label: "Destroy" },
      { value: "unknown", label: "Unknown" },
    ],
    hide: (user) => !user?.feature_options.enable_duration_of_data,
    testData: "archive",
  },
  {
    name: "notes",
    apiFieldName: "notes",
    type: "TextArea",
    shortLabel: "Additional notes",
    longLabel: "Additional notes",
    explanation:
      "A free-text field for any additional information about the dataset metadata record or the underlying data that is not captured in other fields.",
    info: "This field is optional.",
    hide: (user) => !user?.feature_options.enable_notes,
  },
  {
    name: "spatialResolutions",
    apiFieldName: "spatial_resolutions",
    type: "CreatableSelect",
    shortLabel: "Spatial Resolution (in meters)",
    longLabel: "Spatial Resolution (in meters)",
    explanation:
      "The minimum spatial separation resolvable in the underlying data, measured in meters.",
    isMulti: true,
    info: "This field is optional. Enter positive numbers for spatial resolution in meters.",
    placeholder: "Add spatial resolution and press enter to add multiple...",
  },
  {
    name: "temporalResolution",
    apiFieldName: "temporal_resolution",
    type: "InputField",
    shortLabel: "Temporal Resolution",
    longLabel: "Temporal Resolution",
    explanation: "The minimum time period resolvable in the underlying data.",
    info: "This field is optional. Enter minimum time period between data points using xsd format (e.g., P1D for daily, PT1H for hourly, P1M for monthly).",
  },
  {
    name: "wasGeneratedBy",
    apiFieldName: "was_generated_by",
    type: "CreatableSelect",
    shortLabel: "Was Generated By",
    longLabel: "Was Generated By",
    explanation:
      "An activity that generated, or provides business context for, creation of the underlying data.",
    isMulti: true,
    info: "This field is optional.",
    placeholder: "Add was generated by and press enter to add multiple...",
  },
  {
    name: "otherIdentifiers",
    apiFieldName: "other_identifiers",
    type: "CreatableSelect",
    shortLabel: "Other Identifiers",
    longLabel: "Other Identifiers",
    explanation: "A secondary identifier associated with the metadata record or underlying data.",
    isMulti: true,
    info: "This field is optional.",
    placeholder: "Add secondary identifier and press enter to add multiple...",
  },
];

export default datasetSchema;

export const getDatasetFieldShortLabel = (fieldName: string) => {
  if (fieldName === "identifier") {
    return "Identifier";
  } else if (fieldName === "monitoring_location") {
    return "Monitoring Location";
  } else if (fieldName === "creator_name") {
    return "Creator Names";
  } else if (fieldName === "creator_names") {
    return "Creator Names";
  } else if (fieldName === "publisher_name") {
    return "Publisher Name";
  } else if (fieldName === "created") {
    return "Created at";
  } else if (fieldName === "period") {
    return "Time Period";
  } else if (fieldName === "retention_period") {
    return "Retention Period";
  } else if (fieldName === "contact") {
    return "Contacts";
  } else if (fieldName === "member_datasets") {
    return "Member Datasets";
  } else if (fieldName === "contact_names" || fieldName === "contact_emails") {
    return "Contact Points";
  } else if (fieldName === "legal_basis") {
    return "Applicable Legislations";
  }

  const field = datasetSchema.find((field) => field.apiFieldName === fieldName);

  return field ? field.shortLabel : "";
};
