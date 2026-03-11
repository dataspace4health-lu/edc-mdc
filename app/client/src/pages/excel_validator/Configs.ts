export const requiredSheets = ["DatasetTemplate", "DistributionTemplate", "DataDictionaryTemplate"];

export const requiredHeadersMap: Record<string, { header: string; validationType: string }[]> = {
  DatasetTemplate: [
    { header: "title", validationType: "string" },
    { header: "description", validationType: "string" },
    { header: "publisher", validationType: "string" },
    { header: "contact point name", validationType: "string" },
    { header: "contact point email", validationType: "email" },
    { header: "themes", validationType: "string" },
    { header: "keywords", validationType: "string" },
    { header: "geographical coverage", validationType: "string" },
    { header: "start date", validationType: "date" },
    { header: "end date", validationType: "date" },
    { header: "applicable legislations", validationType: "string" },
    { header: "access rights", validationType: "string" },
    { header: "data protection types", validationType: "string" },
    { header: "dataset types", validationType: "string" },
    { header: "frequency", validationType: "string" },
    { header: "language", validationType: "string" },
    { header: "creator", validationType: "string" },
  ],
  DistributionTemplate: [
    { header: "dataset title", validationType: "string" },
    { header: "distribution title", validationType: "string" },
    { header: "description", validationType: "string" },
    { header: "access url", validationType: "url" },
    { header: "format", validationType: "string" },
    { header: "license", validationType: "string" },
    { header: "rights", validationType: "string" },
    { header: "language", validationType: "string" },
    { header: "media type / compression format / packaging format", validationType: "string" },
    { header: "applicable legislations", validationType: "string" },
    { header: "availability", validationType: "string" },
  ],
  DataDictionaryTemplate: [
    { header: "dataset title", validationType: "string" },
    { header: "field_name", validationType: "string" },
    { header: "description", validationType: "string" },
    { header: "data_type", validationType: "string" },
    { header: "personally_identifiable_variable", validationType: "string" },
    { header: "required", validationType: "string" },
    { header: "max_allowed_value", validationType: "number" },
    { header: "min_allowed_value", validationType: "number" },
    { header: "variable_unit", validationType: "string" },
    { header: "allowed_values", validationType: "string" },
    { header: "allowed_values_description", validationType: "string" },
  ],
};

export const requiredFieldsMap: Record<string, string[]> = {
  DatasetTemplate: [
    "title",
    "description",
    "publisher",
    "contact point name",
    "contact point email",
    "themes",
    "geographical coverage",
    "access rights",
    "dataset types",
  ],
  DistributionTemplate: ["dataset title", "availability"],
  DataDictionaryTemplate: ["dataset title", "field_name", "description", "data_type"],
};

export const dropdownFieldsMap: Record<string, string[]> = {
  DatasetTemplate: [
    "themes",
    // Note: "keywords" are auto-created in processMissingFormFields, so validation would fail
    // Note: "applicable legislations" are auto-created in processMissingFormFields, so validation would fail
    "geographical coverage",
    "language",
    "dataset types",
    "frequency",
    "access rights",
    "data protection types",
  ],
  DistributionTemplate: [
    "format",
    "language",
    "license",
    "availability",
    "rights",
    // Note: "applicable legislations" for distributions are also auto-created
    "media type/compression format/packaging format",
  ],
  DataDictionaryTemplate: ["data_type", "personally_identifiable_variable", "required"],
};

export const multiValueFieldsMap: Record<string, string[]> = {
  DatasetTemplate: [
    "themes",
    // "keywords" removed - auto-created, no need to validate
    "geographical coverage",
    "language",
    "dataset types",
    "data protection types",
  ],
  DataDictionaryTemplate: [],
  DistributionTemplate: ["language"],
};

export const rightStatementsLabelsUpload = {
  "http://publications.europa.eu/resource/authority/access-right/PUBLIC": "public",
  "http://publications.europa.eu/resource/authority/access-right/NON_PUBLIC": "non-public",
};
