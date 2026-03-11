export const DataDictionaryFieldLabelMap: Record<string, string> = {
  field_name: "Field Name",
  data_type: "Data Type",
  description: "Description",
  max_allowed_value: "Max Allowed Value",
  min_allowed_value: "Min Allowed Value",
  variable_unit: "Variable Unit",
  allowed_values: "Allowed Values",
  allowed_values_description: "Allowed Values Description",
  personally_identifiable_variable: "Personally Identifiable Variable",
  required: "Required",
};

export const IGNORED_FIELDS = [
  "id",
  "identifier",
  "previous_version_dataset_id",
  "deprecated_at",
  "submitted_at",
  "status",
  "creator_ids",
  "publisher_id",
  "contact_ids",
  "distributions",
  "source_relations",
  "total_relations",
  "released_at",
  "authentic_source_reviewed_at",
  "is_any_dictionary_authentic_source",
];

export const IGNORED_FIELDS_DISTRIBUTION = ["id", "dataset_id"];

export const IGNORED_FIELDS_RELATIONS = [
  "id",
  "status",
  "internal_only",
  "previous_version_dataset_id",
];

export const RelationFieldLabelMap: Record<string, string> = {
  relation_kind: "Kind",
  title: "Target Dataset",
  dataset_id: "Dataset ID",
  relation_type: "Relation Type",
  external_url: "External URL",
  external_role: "External Role",
  external_description: "External Description",
};

export const IGNORED_FIELDS_DATA_DICTIONARY = [
  "id",
  "dataset_id",
  "is_authentic_source",
  "position",
  "table_name",
  "privacy_risk_type",
];

export const IGNORED_FIELDS_QUALIFIED_ATTRIBUTIONS = ["id", "dataset_id"];

export const QualifiedAttributionFieldLabelMap: Record<string, string> = {
  organisation_name: "Organisation",
  role: "Role",
};
