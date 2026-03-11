import { DistributionFormType } from "../types";
import { mediaTypes } from "../utils/mediaTypeLabels";
import { rightStatementsOptions } from "../utils/rightStatementsLabels";
import { FormType, ResourceUserType } from "../types";
import { FieldType } from "./field-types";
import { filterFormFieldsByOrganisation } from "../utils/filterFormFieldsByOrganisation";

export const PUBLIC_RIGHTS_STATEMENT =
  "http://publications.europa.eu/resource/authority/access-right/PUBLIC";
export const NON_PUBLIC_RIGHTS_STATEMENT =
  "http://publications.europa.eu/resource/authority/access-right/NON_PUBLIC";

type EnumValue = {
  value: string;
  eng_label: string;
};

interface DistributionSchema {
  name: string;
  apiFieldName: string;
  type: FieldType;
  shortLabel: string;
  longLabel: string;
  required?: boolean;
  recommended?: boolean;
  isMulti?: boolean;
  inputType?: string;
  info?: string;
  explanation?: string;
  placeholder?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  hide?: (user: any) => boolean;
  options?: (
    formLoaderData: FormType,
    user: ResourceUserType | null,
  ) => { label: string; value: string }[];
  minLength?: number;
  maxLength?: number;
  testData?: string | string[] | boolean;
}

export const distributionDCATStatusOptions = [
  { value: "Completed", label: "Completed" },
  { value: "Deprecated", label: "Deprecated" },
  { value: "Under Development", label: "Under Development" },
  { value: "Withdrawn", label: "Withdrawn" },
];

export const actionTypeOptions = [
  { value: "permission", label: "Permission" },
  { value: "prohibition", label: "Prohibition" },
];

export const constraintTypeOptions = [
  { value: "purpose", label: "Purpose Restriction" },
  { value: "temporal", label: "Temporal Restriction" },
  { value: "spatial", label: "Spatial Restriction" },
  { value: "industry", label: "Industry Restriction" },
];

export const purposeOptions = [
  { value: "DUO:0000018", label: "Not for profit, non commercial use only (NPUNCU)" },
  { value: "DUO:0000046", label: "Non-commercial use only (NCU)" },
  { value: "DUO:0000045", label: "Not for profit organisation use only (NPU)" },
  { value: "DUO:0000015", label: "No general methods research (NMDS)" },
  { value: "DUO:0000019", label: "Publication required (PUB)" },
  { value: "DUO:0000024", label: "Publication moratorium (MOR)" },
  { value: "DUO:0000021", label: "Ethics approval required (IRB)" },
  { value: "DUO:0000020", label: "Collaboration required (COL)" },
  { value: "DUO:0000012", label: "Research specific restrictions (RS)" },
  { value: "DUO:0000029", label: "Return to database or resource (RTN)" },
  { value: "DUO:0000042", label: "General research use (GRU)" },
  { value: "DUO:0000043", label: "Clinical care use (CC)" },
  { value: "DUO:0000007", label: "Disease specific research (DS)" },
  { value: "DUO:0000016", label: "Genetic studies only (GSO)" },
  { value: "DUO:0000006", label: "Health or medical or biomedical research (HMB)" },
  { value: "DUO:0000011", label: "Population origins or ancestry research only (POA)" },
  { value: "DUO:0000044", label: "Population origins or ancestry research prohibited (NPOA)" },
];

export const availabilityOptions = [
  {
    value: "http://publications.europa.eu/resource/authority/planned-availability/AVAILABLE", // NOSONAR
    label: "Available",
  },
  {
    value: "http://publications.europa.eu/resource/authority/planned-availability/EXPERIMENTAL", // NOSONAR
    label: "Experimental",
  },
  {
    value: "http://publications.europa.eu/resource/authority/planned-availability/STABLE", // NOSONAR
    label: "Stable",
  },
  {
    value: "http://publications.europa.eu/resource/authority/planned-availability/TEMPORARY", // NOSONAR
    label: "Temporary",
  },
];

const distributionSchema: DistributionSchema[] = [
  {
    name: "title",
    apiFieldName: "title",
    type: "InputField",
    shortLabel: "Title",
    longLabel: "Title",
    explanation: "A name given to the distribution.",
    required: false,
    info: "This field is optional. If left blank, a title will be generated automatically.",
    maxLength: 120,
    testData: "Sample Distribution Title",
  },
  {
    name: "description",
    apiFieldName: "description",
    type: "TextArea",
    shortLabel: "Description",
    longLabel: "Description",
    explanation: "A free-text account of the distribution.",
    required: false,
    minLength: 3,
    info: "This field is optional.",
    testData: "This is a sample description for the distribution.",
  },
  {
    name: "internalOnly",
    apiFieldName: "internal_only",
    type: "Custom",
    shortLabel: "Internal Only",
    longLabel: "Is this distribution internal only?",
    explanation:
      "If true, this distribution is intended for internal use only and will not be published or made accessible to external users.",
    info: "This field is optional. Mark as internal only if this distribution should not be published.",
    testData: false,
  },
  {
    name: "isAnalytics",
    apiFieldName: "is_analytics",
    type: "Custom",
    shortLabel: "Analytics",
    longLabel: "Does this distribution relate to technical reports or analytics about the dataset?",
    explanation:
      "If true, this distribution is intended to provide technical reports or analytics about the dataset rather than primary data access.",
    testData: false,
  },
  {
    name: "distributionPath",
    apiFieldName: "distribution_path",
    type: "DropdownSelect",
    shortLabel: "Distribution Path",
    longLabel: "Distribution Path",
    explanation: "",
    info: "This field is optional.",
    isMulti: false,
    options: (formLoaderData: FormType) =>
      formLoaderData.distribution.distribution_path.map((enumValue) => ({
        value: enumValue.value as string,
        label: enumValue.eng_label,
      })),
    hide: (user) => !user?.feature_options.enable_distribution_path,
  },
  {
    name: "distributionRightsStatement",
    apiFieldName: "rights_statement",
    type: "RadioButton",
    shortLabel: "Rights",
    longLabel: "Rights",
    explanation:
      "Information indicating whether access to the distribution is public, restricted, or non-public.",
    required: true,
    // @ts-expect-error Not used
    options: (distributionFormData: DistributionFormType) =>
      rightStatementsOptions.map((enumValue: EnumValue) => ({
        value: enumValue.value,
        label: enumValue.eng_label,
      })),
    testData: "http://publications.europa.eu/resource/authority/access-right/PUBLIC",
  },
  {
    name: "fileFormat",
    apiFieldName: "file_type",
    type: "DropdownSelect",
    shortLabel: "Format",
    longLabel: "Format",
    explanation: "The file format of the distribution.",
    isMulti: false,
    recommended: true,
    info: "This field is recommended. Required when Rights are non-public.",
    options: (formLoaderData: FormType) =>
      formLoaderData.distribution.file_types.map((enumValue) => ({
        value: enumValue.value,
        label: enumValue.eng_label,
      })),
  },
  {
    name: "mediaType",
    apiFieldName: "media_type",
    type: "DropdownSelect",
    shortLabel: "Media Type",
    longLabel: "Media Type",
    explanation: "The media type of the distribution as an IANA media type.",
    info: "This field is recommended.",
    recommended: true,
    isMulti: false,
    options: () =>
      mediaTypes.map((media) => ({
        value: media,
        label: media,
      })),
  },
  {
    name: "compressionFormat",
    apiFieldName: "compression_format",
    type: "DropdownSelect",
    shortLabel: "Compression Format",
    longLabel: "Compression Format",
    explanation: "The compression format used for the distribution file.",
    info: "This field is optional.",
    isMulti: false,
    options: () =>
      mediaTypes.map((media) => ({
        value: media,
        label: media,
      })),
  },
  {
    name: "packagingFormat",
    apiFieldName: "packaging_format",
    type: "DropdownSelect",
    shortLabel: "Packaging Format",
    longLabel: "Packaging Format",
    explanation: "The package format used to bundle one or more files in the distribution.",
    info: "This field is optional.",
    isMulti: false,
    options: () =>
      mediaTypes.map((media) => ({
        value: media,
        label: media,
      })),
  },
  {
    name: "byteSize",
    apiFieldName: "byte_size",
    type: "InputField",
    shortLabel: "Byte Size",
    longLabel: "Byte Size",
    explanation: "The size of the distribution in bytes.",
    info: "This field is optional. Required when Rights are non-public.",
    inputType: "number",
  },
  {
    name: "checksum",
    apiFieldName: "checksum",
    type: "InputField",
    shortLabel: "Checksum",
    longLabel: "Checksum",
    explanation: "A checksum value that can be used to verify distribution integrity.",
    info: "This field is optional.",
    inputType: "text",
  },
  {
    name: "accessURLs",
    apiFieldName: "access_urls",
    type: "CreatableSelect",
    shortLabel: "Access URLs",
    longLabel: "Access URLs",
    explanation:
      "A URL providing access to the distribution, such as a landing page, service endpoint, or file location.",
    required: true,
    isMulti: true,
    placeholder: "Add access URL and press enter to add multiple...",
    testData: ["https://example.com/sample-distribution"],
  },
  {
    name: "downloadURLs",
    apiFieldName: "download_urls",
    type: "CreatableSelect",
    shortLabel: "Download URLs",
    longLabel: "Download URLs",
    explanation: "A direct URL where the distribution file can be downloaded.",
    info: "This field is optional.",
    isMulti: true,
    placeholder: "Add download URL and press enter to add multiple...",
    testData: ["https://example.com/sample-distribution"],
  },
  {
    name: "accessServices",
    apiFieldName: "access_service_ids",
    type: "DropdownSelect",
    shortLabel: "Access Services",
    longLabel: "Access Services",
    explanation: "A data service through which the distribution is accessible.",
    isMulti: true,
    info: "This field is optional",
    options: (formLoaderData: FormType) =>
      formLoaderData.data_service.data_services.map((service) => ({
        label: service.eng_label,
        value: service.value,
      })),
  },
  {
    name: "license",
    apiFieldName: "license",
    type: "DropdownSelect",
    shortLabel: "Licence",
    longLabel: "Licence",
    explanation: "A legal document or terms under which the distribution is made available.",
    recommended: true,
    info: "This field is recommended.",
    isMulti: false,
    options: (formLoaderData: FormType) =>
      formLoaderData.distribution.licenses.map((enumValue) => ({
        value: enumValue.value,
        label: enumValue.eng_label,
      })),
    testData: "Apache-2.0",
  },
  {
    name: "hasPolicy",
    apiFieldName: "has_policy",
    shortLabel: "Has Policy",
    longLabel: "Has Policy",
    type: "Custom",
    explanation:
      "The policy expressing the rights associated with the distribution if using the [ODRL] vocabulary.",
    testData: false,
  },
  {
    name: "policyActions",
    apiFieldName: "policy_actions",
    type: "Custom",
    shortLabel: "Policy Actions",
    longLabel: "Data Use Policy Actions",
    explanation: "Restrictions can be expressed as either permissions or prohibitions.",
    info: "Define permissions and prohibitions for this distribution.",
    testData: false,
  },
  {
    name: "applicableLegislations",
    apiFieldName: "applicable_legislations",
    type: "DropdownSelect",
    shortLabel: "Applicable Legislations",
    longLabel: "Applicable Legislations",
    explanation:
      "Legislation that mandates creation, management, access conditions, or reuse conditions of the distribution.",
    info: "This field is optional.",
    isMulti: true,
    required: false,
    options: (formLoaderData: FormType, user: ResourceUserType | null) => {
      const filteredFields = filterFormFieldsByOrganisation(
        formLoaderData.distribution.applicable_legislations,
        { user },
      );

      return filteredFields.map((enumValue: EnumValue) => ({
        label: enumValue.eng_label,
        value: enumValue.value,
      }));
    },
  },
  {
    name: "linkedSchemas",
    apiFieldName: "linked_schemas",
    type: "CreatableSelect",
    shortLabel: "Linked Schemas",
    isMulti: true,
    longLabel: "Linked Schemas",
    explanation: "A schema resource that describes the structure of the distribution data.",
    info: "This field is optional.",
  },
  {
    name: "languages",
    apiFieldName: "languages",
    type: "DropdownSelect",
    shortLabel: "Languages",
    longLabel: "Languages",
    explanation: "A language used in the distribution content.",
    info: "Select all languages that apply. This field is optional.",
    isMulti: true,
    options: (formLoaderData: FormType) =>
      formLoaderData.distribution.languages.map((enumValue) => ({
        label: enumValue.eng_label,
        value: enumValue.value,
      })),
    testData: "http://publications.europa.eu/resource/authority/language/ENG", // NOSONAR
  },
  {
    name: "availability",
    apiFieldName: "availability",
    type: "DropdownSelect",
    shortLabel: "Availability",
    longLabel: "Availability",
    explanation: "The planned availability status of the distribution.",
    info: "This field is recommended.",
    isMulti: false,
    options: () => availabilityOptions,
    recommended: true,
  },
  {
    name: "distributionDCATStatus",
    apiFieldName: "distribution_dcat_status",
    type: "DropdownSelect",
    shortLabel: "Status",
    longLabel: "Status",
    explanation: "The lifecycle status of the distribution resource.",
    required: false,
    isMulti: false,
    options: () => distributionDCATStatusOptions,
  },
  {
    name: "releaseDate",
    apiFieldName: "release_date",
    type: "InputField",
    shortLabel: "Release Date",
    longLabel: "Release Date",
    explanation: "The date of formal issuance (publication) of the distribution.",
    info: "This field is optional.",
    inputType: "date",
    testData: "2023-01-01",
  },
  {
    name: "modificationDate",
    apiFieldName: "modification_date",
    type: "InputField",
    shortLabel: "Modification Date",
    longLabel: "Modification Date",
    explanation: "The most recent date on which the distribution was modified.",
    info: "This field is optional.",
    inputType: "date",
    testData: "2023-01-01",
  },
  {
    name: "documentation",
    apiFieldName: "documentation",
    type: "CreatableSelect",
    shortLabel: "Documentation",
    longLabel: "Documentation",
    explanation: "A page or document that provides additional information about the distribution.",
    isMulti: true,
    info: "This field is optional.",
    placeholder: "Add documentation and press enter to add multiple...",
  },
  {
    name: "notes",
    apiFieldName: "notes",
    type: "TextArea",
    shortLabel: "Notes",
    longLabel: "Additional notes for this distribution",
    explanation:
      "A free-text field for any additional information about the distribution that does not fit into other fields.",
    info: "This field is optional.",
    hide: (user) => !user?.feature_options.enable_distribution_notes,
  },
  {
    name: "spatialResolution",
    apiFieldName: "spatial_resolution",
    type: "InputField",
    inputType: "number",
    shortLabel: "Spatial resolution (in meters)",
    longLabel: "Spatial resolution (in meters)",
    explanation:
      "The minimum spatial separation resolvable in the distribution, measured in meters.",
    info: "This field is optional. Please enter a non-negative number.",
  },
  {
    name: "temporalResolution",
    apiFieldName: "temporal_resolution",
    type: "InputField",
    shortLabel: "Temporal Resolution",
    longLabel: "Temporal Resolution",
    explanation: "The minimum time period resolvable in the distribution.",
    info: "This field is optional. Enter minimum time period between data points using xsd format (e.g., P1D for daily, PT1H for hourly, P1M for monthly).",
  },
];

export default distributionSchema;

export const getDistributionShortLabel = (fieldName: string) => {
  if (fieldName === "policy_type") {
    return "Policy Type";
  } else if (fieldName === "policy_action_type") {
    return "Policy Action Type";
  } else if (fieldName === "policy_constraint_type") {
    return "Policy Constraint Type";
  } else if (fieldName === "policy_constraint_value") {
    return "Policy Constraint Value";
  } else if (fieldName === "policy_actions") {
    return "Policy Actions";
  } else if (fieldName === "access_services") {
    return "Access Services";
  } else if (fieldName === "legal_basis") {
    return "Applicable Legislations";
  }

  const field = distributionSchema.find((field) => field.apiFieldName === fieldName);

  return field ? field.shortLabel : "";
};
