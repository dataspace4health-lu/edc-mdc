import { makeApi, Zodios, type ZodiosOptions } from "@zodios/core";
import { z } from "zod";

const FeatureOptions = z
  .object({
    enable_duration_of_data: z.boolean(),
    enable_conventions: z.boolean(),
    enable_area_of_work_and_competence: z.boolean(),
    enable_distribution_path: z.boolean(),
    enable_notes: z.boolean(),
    enable_distribution_notes: z.boolean(),
    enable_validation_via_group_manager: z.boolean(),
    enable_monitoring_location: z.boolean(),
    enable_authentic_source: z.boolean(),
    enable_multi_tenants: z.boolean(),
    enable_upload_datasets_to_front_office: z.boolean(),
    enable_dual_instance: z.boolean(),
  })
  .passthrough();
const ResourceRole = z.object({ id: z.number().int(), name: z.string() }).passthrough();
const ResourceOrganisationAssignment = z
  .object({
    organisation_id: z.number().int(),
    organisation_name: z.string(),
    roles: z.array(ResourceRole),
    is_deprecated: z.boolean().optional().default(false),
  })
  .passthrough();
const ResourceUserOrganisation = z
  .object({
    id: z.number().int(),
    name: z.string(),
    type: z.union([z.string(), z.null()]),
    email: z.union([z.string(), z.null()]),
  })
  .passthrough();
const ResourceUser = z
  .object({
    id: z.number().int(),
    name: z.string(),
    email: z.string(),
    feature_options: FeatureOptions,
    iam_roles: z.array(z.string()),
    permissions: z.array(z.string()),
    assignments: z.array(ResourceOrganisationAssignment),
    current_organisation: z.union([ResourceUserOrganisation, z.null()]),
    show_notice_on_homepage: z.union([z.string(), z.null()]),
    can_edit_form_fields: z.boolean().optional().default(false),
    default_themes: z.array(z.string()).optional(),
    is_deprecated: z.boolean().optional().default(false),
    last_login_at: z.union([z.string(), z.null()]).optional(),
    has_ctie_only_access: z.boolean().optional().default(false),
  })
  .passthrough();
const ValidationError = z
  .object({ loc: z.array(z.union([z.string(), z.number()])), msg: z.string(), type: z.string() })
  .passthrough();
const HTTPValidationError = z
  .object({ detail: z.array(ValidationError) })
  .partial()
  .passthrough();
const ResourceDataDictionaryEntry = z
  .object({
    id: z.union([z.number(), z.null()]).optional(),
    field_name: z.string(),
    description: z.string(),
    data_type: z.string(),
    personally_identifiable_variable: z.union([z.boolean(), z.null()]).optional(),
    required: z.union([z.boolean(), z.null()]).optional(),
    max_allowed_value: z.union([z.number(), z.null()]).optional(),
    min_allowed_value: z.union([z.number(), z.null()]).optional(),
    variable_unit: z.union([z.string(), z.null()]).optional(),
    allowed_values: z.union([z.string(), z.null()]).optional(),
    allowed_values_description: z.union([z.string(), z.null()]).optional(),
    table_name: z.union([z.string(), z.null()]).optional(),
    dataset_id: z.union([z.number(), z.null()]).optional(),
    is_authentic_source: z.union([z.boolean(), z.null()]).optional(),
    privacy_risk_type: z.union([z.string(), z.null()]).optional(),
    position: z.union([z.number(), z.null()]).optional(),
  })
  .passthrough();
const Body_bulk_upload_data_dictionaries_api_v1_datasets__dataset_id__data_dictionaries_bulk_upload_post =
  z.object({ file: z.instanceof(File) }).passthrough();
const UpdateAuthenticSourceDto = z.object({
  entry_id: z.number().int().gt(0),
  is_authentic_source: z.boolean(),
});
const BulkUpdateAuthenticSourceDto = z.object({
  entries: z.array(UpdateAuthenticSourceDto).min(1).max(100),
});
const UpdatePositionDto = z.object({
  entry_id: z.number().int().gt(0),
  position: z.number().int().gte(0),
});
const BulkUpdatePositionDto = z.object({ updates: z.array(UpdatePositionDto).min(1).max(1000) });
const ResourceRelation = z
  .object({
    id: z.union([z.number(), z.null()]).optional(),
    source_dataset: z.number().int(),
    relation_kind: z.enum(["dataset", "external"]),
    target_dataset: z.union([z.number(), z.null()]).optional(),
    relation_type: z.union([z.string(), z.null()]).optional(),
    external_url: z.union([z.string(), z.null()]).optional(),
    external_role: z.union([z.string(), z.null()]).optional(),
    external_description: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const AddRelation = z
  .object({
    relation_kind: z.enum(["dataset", "external"]),
    target_dataset: z.union([z.number(), z.null()]).optional(),
    relation_type: z.union([z.string(), z.null()]).optional(),
    external_url: z.union([z.string(), z.null()]).optional(),
    external_role: z.union([z.string(), z.null()]).optional(),
    external_description: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const EnumValue = z.object({ value: z.string(), eng_label: z.string() }).passthrough();
const DataServiceEndpointDto = z.object({
  endpoint_url: z.string().min(1).max(500),
  endpoint_description: z.union([z.string(), z.null()]).optional(),
});
const ResourceDataService = z
  .object({ id: z.number().int(), title: z.string(), endpoints: z.array(DataServiceEndpointDto) })
  .passthrough();
const ResourcePolicyAction = z
  .object({
    policy_action_type: z.string(),
    policy_constraint_type: z.union([z.string(), z.null()]),
    policy_constraint_value: z.union([z.string(), z.null()]),
    temporal_restriction_start: z.union([z.string(), z.null()]).optional(),
    temporal_restriction_end: z.union([z.string(), z.null()]).optional(),
    spatial_restrictions: z.array(EnumValue).optional(),
  })
  .passthrough();
const ResourceDistribution = z
  .object({
    id: z.number().int(),
    title: z.string(),
    description: z.union([z.string(), z.null()]),
    dataset_id: z.number().int(),
    distribution_dcat_status: z.union([z.string(), z.null()]),
    download_urls: z.array(z.string()),
    access_urls: z.array(z.string()),
    file_type: z.union([EnumValue, z.null()]),
    rights_statement: z.string(),
    languages: z.array(EnumValue),
    internal_only: z.union([z.boolean(), z.null()]),
    is_analytics: z.union([z.boolean(), z.null()]),
    applicable_legislations: z.array(z.string()),
    notes: z.union([z.string(), z.null()]),
    license: z.union([EnumValue, z.null()]),
    distribution_path: z.union([z.string(), z.null()]),
    availability: z.union([z.string(), z.null()]),
    linked_schemas: z.array(z.string()),
    access_services: z.array(ResourceDataService),
    modification_date: z.union([z.string(), z.null()]).optional(),
    release_date: z.union([z.string(), z.null()]).optional(),
    documentation: z.array(z.string()).optional(),
    byte_size: z.union([z.number(), z.null()]).optional(),
    checksum: z.union([z.string(), z.null()]).optional(),
    policy_actions: z.array(ResourcePolicyAction).optional(),
    media_type: z.union([z.string(), z.null()]).optional(),
    compression_format: z.union([z.string(), z.null()]).optional(),
    packaging_format: z.union([z.string(), z.null()]).optional(),
    spatial_resolution: z.union([z.number(), z.null()]).optional(),
    temporal_resolution: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const PolicyActionDto = z
  .object({
    policy_action_type: z.string().max(100),
    policy_constraint_type: z.union([z.string(), z.null()]).optional(),
    policy_constraint_value: z.union([z.string(), z.null()]).optional(),
    temporal_restriction_start: z.union([z.string(), z.null()]).optional(),
    temporal_restriction_end: z.union([z.string(), z.null()]).optional(),
    spatial_restrictions: z.array(z.string()).optional(),
  })
  .passthrough();
const DistributionDto = z
  .object({
    title: z.union([z.string(), z.null()]).optional(),
    description: z.union([z.string(), z.null()]).optional(),
    download_urls: z.array(z.string().min(1).url()).optional(),
    access_urls: z.array(z.string().min(1).url()).min(1),
    file_type: z.union([z.string(), z.null()]).optional(),
    rights_statement: z.string().min(1).max(500),
    internal_only: z.boolean().optional().default(false),
    is_analytics: z.boolean().optional().default(false),
    applicable_legislations: z.array(z.string()).optional(),
    languages: z.array(z.string()),
    notes: z.union([z.string(), z.null()]).optional(),
    license: z.union([z.string(), z.null()]).optional(),
    distribution_path: z.union([z.string(), z.null()]).optional(),
    policy_actions: z.array(PolicyActionDto).optional(),
    availability: z.union([z.string(), z.null()]).optional(),
    documentation: z.array(z.string().max(2000)).optional(),
    modification_date: z.union([z.string(), z.null()]).optional(),
    release_date: z.union([z.string(), z.null()]).optional(),
    linked_schemas: z.array(z.string()).optional(),
    byte_size: z.union([z.number(), z.null()]).optional(),
    checksum: z.union([z.string(), z.null()]).optional(),
    media_type: z.union([z.string(), z.null()]).optional(),
    compression_format: z.union([z.string(), z.null()]).optional(),
    packaging_format: z.union([z.string(), z.null()]).optional(),
    distribution_dcat_status: z.union([z.string(), z.null()]).optional(),
    spatial_resolution: z.union([z.number(), z.null()]).optional(),
    temporal_resolution: z.union([z.string(), z.null()]).optional(),
    access_service_ids: z.array(z.number().int()).optional(),
  })
  .passthrough();
const DatasetListRequest = z
  .object({
    status: z.string(),
    page: z.number().int().optional().default(1),
    page_size: z.number().int().optional().default(10),
    query: z.union([z.string(), z.null()]).optional(),
    dataset_types: z.array(z.string()).optional().default([]),
    rights_statements: z.array(z.string()).optional().default([]),
    keywords: z.array(z.string()).optional().default([]),
    themes: z.array(z.string()).optional().default([]),
    applicable_legislations: z.array(z.string()).optional().default([]),
    periodicities: z.array(z.string()).optional().default([]),
    organisations: z.array(z.number().int()).optional().default([]),
    authentic_source_pending: z.union([z.boolean(), z.null()]).optional(),
    has_unlabeled_authentic_source: z.union([z.boolean(), z.null()]).optional(),
  })
  .passthrough();
const HierarchicalEnumValue = z
  .object({
    value: z.string(),
    eng_label: z.string(),
    parent_value: z.union([z.string(), z.null()]),
  })
  .passthrough();
const ResourceQualifiedAttribution = z
  .object({
    id: z.number().int(),
    dataset_id: z.number().int(),
    organisation_id: z.number().int(),
    role: z.string(),
    organisation_name: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const ResourceSourceRelation = z
  .object({
    id: z.number().int(),
    relation_kind: z.string(),
    title: z.union([z.string(), z.null()]).optional(),
    status: z.union([z.string(), z.null()]).optional(),
    internal_only: z.union([z.boolean(), z.null()]).optional(),
    dataset_id: z.union([z.number(), z.null()]).optional(),
    relation_type: z.union([z.string(), z.null()]).optional(),
    previous_version_dataset_id: z.union([z.number(), z.null()]).optional(),
    external_url: z.union([z.string(), z.null()]).optional(),
    external_role: z.union([z.string(), z.null()]).optional(),
    external_description: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const SeriesMembershipInfo = z
  .object({
    dataset_id: z.number().int(),
    position: z.number().int(),
    is_first: z.boolean(),
    is_last: z.boolean(),
  })
  .passthrough();
const ResourceDataset = z
  .object({
    id: z.number().int(),
    status: z.string(),
    status_triggers: z.array(z.string()),
    title: z.string(),
    description: z.string(),
    contact_ids: z.array(z.number().int()),
    contact_names: z.array(z.string()),
    contact_emails: z.array(z.string()),
    user_id: z.number().int(),
    publisher_name: z.string(),
    publisher_id: z.number().int(),
    identifier: z.string(),
    submitted_at: z.string(),
    time_period_start: z.union([z.string(), z.null()]),
    dataset_types: z.array(EnumValue),
    themes: z.array(EnumValue),
    keywords: z.array(HierarchicalEnumValue),
    health_categories: z.array(EnumValue),
    health_themes: z.array(EnumValue),
    spatial_coverages: z.array(EnumValue),
    conventions: z.array(z.string()),
    areas_of_work: z.array(z.string()),
    areas_of_competence: z.array(z.string()),
    applicable_legislations: z.array(z.string()),
    languages: z.array(EnumValue),
    distributions: z.array(ResourceDistribution),
    group_manager_ids: z.array(z.number().int()),
    group_manager_names: z.array(z.string()),
    data_protection_types: z.array(z.string()),
    creator_names: z.array(z.string()),
    creator_ids: z.array(z.number().int()),
    release_date: z.union([z.string(), z.null()]),
    released_at: z.union([z.string(), z.null()]),
    modified_at: z.union([z.string(), z.null()]),
    deprecated_at: z.union([z.string(), z.null()]),
    time_period_end: z.union([z.string(), z.null()]),
    retention_period_start: z.union([z.string(), z.null()]),
    retention_period_end: z.union([z.string(), z.null()]),
    rights_statement: z.string(),
    periodicity: z.union([EnumValue, z.null()]),
    version: z.union([z.string(), z.null()]),
    version_change_type: z.union([z.string(), z.null()]),
    notes: z.union([z.string(), z.null()]),
    conforms_to: z.union([z.array(z.string()), z.null()]),
    duration_of_administrative_utility: z.union([z.number(), z.null()]),
    max_typical_age: z.union([z.number(), z.null()]),
    min_typical_age: z.union([z.number(), z.null()]),
    number_of_records: z.union([z.number(), z.null()]),
    number_of_unique_individuals: z.union([z.number(), z.null()]),
    is_any_dictionary_authentic_source: z.union([z.boolean(), z.null()]),
    final_disposition: z.union([z.string(), z.null()]),
    author_name: z.string().optional().default(""),
    qualified_attributions: z.union([z.array(ResourceQualifiedAttribution), z.null()]).optional(),
    source_relations: z.union([z.array(ResourceSourceRelation), z.null()]).optional(),
    total_dictionaries: z.number().int().optional().default(0),
    total_relations: z.number().int().optional().default(0),
    comments_count: z.number().int().optional().default(0),
    monitoring_location: z.union([z.string(), z.null()]).optional(),
    source: z.union([z.string(), z.null()]).optional(),
    source_dataset_id: z.union([z.number(), z.null()]).optional(),
    provenance: z.array(z.string()).optional(),
    health_legal_basis: z.array(z.string()).optional(),
    landing_pages: z.array(z.string()).optional(),
    documentation: z.array(z.string()).optional(),
    purpose: z.array(z.string()).optional(),
    is_dataset_series: z.boolean().optional().default(false),
    member_datasets: z.union([z.array(SeriesMembershipInfo), z.null()]).optional(),
    series_memberships: z.union([z.array(SeriesMembershipInfo), z.null()]).optional(),
    first_dataset_id: z.union([z.number(), z.null()]).optional(),
    last_dataset_id: z.union([z.number(), z.null()]).optional(),
    spatial_resolutions: z.array(z.number().int()).optional(),
    temporal_resolution: z.union([z.string(), z.null()]).optional(),
    authentic_source_reviewed_at: z.union([z.string(), z.null()]).optional(),
    previous_version_dataset_id: z.union([z.number(), z.null()]).optional(),
    latest_version_dataset_id: z.union([z.number(), z.null()]).optional(),
    has_versions: z.boolean().optional().default(false),
    was_generated_by: z.union([z.array(z.string()), z.null()]).optional(),
    other_identifiers: z.union([z.array(z.string()), z.null()]).optional(),
    version_notes: z.array(z.string()).optional(),
    population_coverage: z.union([z.string(), z.null()]).optional(),
    code_values: z.array(z.string()).optional(),
    coding_systems: z.array(z.string()).optional(),
    personal_data: z.array(z.string()).optional(),
  })
  .passthrough();
const schemas__dataset__PaginationMeta = z
  .object({
    total_items: z.number().int(),
    page: z.number().int(),
    page_size: z.number().int(),
    total_pages: z.number().int(),
  })
  .passthrough();
const PaginatedDatasetResponse = z
  .object({ items: z.array(ResourceDataset), meta: schemas__dataset__PaginationMeta })
  .passthrough();
const DatasetCountsResponse = z
  .object({
    draft: z.number().int(),
    published: z.number().int(),
    completed: z.number().int(),
    validated: z.number().int(),
    approved: z.number().int(),
    internal_only: z.number().int(),
    deprecated: z.number().int(),
    total: z.number().int(),
  })
  .passthrough();
const DatasetDto = z
  .object({
    status: z.string().optional().default("DRAFT"),
    title: z.string().min(1).max(500),
    description: z.string().min(1).max(5000),
    contact_ids: z.union([z.array(z.number().int()), z.null()]).optional(),
    publisher_id: z.number().int(),
    time_period_start: z.union([z.string(), z.null()]).optional(),
    time_period_end: z.union([z.string(), z.null()]).optional(),
    retention_period_start: z.union([z.string(), z.null()]).optional(),
    retention_period_end: z.union([z.string(), z.null()]).optional(),
    release_date: z.union([z.string(), z.null()]).optional(),
    modified_at: z.union([z.string(), z.null()]).optional(),
    deprecated_at: z.union([z.string(), z.null()]).optional(),
    released_at: z.union([z.string(), z.null()]).optional(),
    rights_statement: z.string().min(1).max(500),
    periodicity: z.union([z.string(), z.null()]).optional(),
    version: z.union([z.string(), z.null()]).optional(),
    version_change_type: z.union([z.string(), z.null()]).optional(),
    duration_of_administrative_utility: z.union([z.number(), z.null()]).optional(),
    max_typical_age: z.union([z.number(), z.null()]).optional(),
    min_typical_age: z.union([z.number(), z.null()]).optional(),
    number_of_records: z.union([z.number(), z.null()]).optional(),
    number_of_unique_individuals: z.union([z.number(), z.null()]).optional(),
    final_disposition: z.union([z.string(), z.null()]).optional(),
    notes: z.union([z.string(), z.null()]).optional(),
    themes: z.array(z.string()).min(1),
    keywords: z.array(z.string()),
    health_categories: z.array(z.string()),
    health_themes: z.array(z.string()),
    applicable_legislations: z.array(z.string()),
    spatial_coverages: z.array(z.string()),
    conventions: z.array(z.string()),
    areas_of_work: z.array(z.string()),
    areas_of_competence: z.array(z.string()),
    dataset_types: z.array(z.string()).min(1),
    distributions: z.union([z.array(DistributionDto), z.null()]).optional(),
    creator_ids: z.array(z.number().int()),
    group_managers: z.union([z.array(z.number().int()), z.null()]).optional(),
    data_protection_types: z.array(z.string()),
    monitoring_location: z.union([z.string(), z.null()]).optional(),
    provenance: z.array(z.string().max(1000)).optional(),
    health_legal_basis: z
      .union([z.array(z.string().max(1000)), z.null()])
      .optional()
      .default([]),
    languages: z.array(z.string()),
    landing_pages: z.array(z.string().min(1).url()).optional(),
    documentation: z.array(z.string()).optional(),
    purpose: z.array(z.string()).optional().default([]),
    conforms_to: z.array(z.string().min(1).url()).optional(),
    is_dataset_series: z.boolean().optional().default(false),
    member_datasets: z.union([z.array(z.number().int()), z.null()]).optional(),
    was_generated_by: z.union([z.array(z.string()), z.null()]),
    other_identifiers: z.union([z.array(z.string()), z.null()]),
    version_notes: z.array(z.string().max(1000)).optional(),
    spatial_resolutions: z.array(z.number().int()).optional(),
    temporal_resolution: z.union([z.string(), z.null()]).optional(),
    population_coverage: z.union([z.string(), z.null()]).optional(),
    source: z.union([z.string(), z.null()]).optional(),
    source_dataset_id: z.union([z.number(), z.null()]).optional(),
    coding_systems: z.array(z.string()).optional(),
    code_values: z.array(z.string()).optional(),
    personal_data: z.array(z.string()).optional(),
  })
  .passthrough();
const Body_import_dataset_from_rdf_api_v1_datasets_import_rdf_post = z
  .object({ rdf_file: z.instanceof(File), rdf_format: z.string().optional().default("turtle") })
  .passthrough();
const DatasetStatusUpdateDto = z
  .object({ comment: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const DatasetVersionCreateDto = z
  .object({ version_change_type: z.string().default("METADATA_ONLY") })
  .partial()
  .passthrough();
const create_dataset_version_api_v1_datasets__dataset_id__version_post_Body = z.union([
  DatasetVersionCreateDto,
  z.null(),
]);
const KeywordEnumValue = z
  .object({
    value: z.string(),
    eng_label: z.string(),
    parent_value: z.union([z.string(), z.null()]),
    organisation_ids: z.array(z.number().int()).optional(),
  })
  .passthrough();
const ApplicableLegislationEnumValue = z
  .object({
    value: z.string(),
    eng_label: z.string(),
    organisation_ids: z.array(z.number().int()).optional(),
    description: z.union([z.string(), z.null()]).optional(),
    link: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const DatasetForm = z
  .object({
    dataset_types: z.array(EnumValue),
    periodicities: z.array(EnumValue),
    themes: z.array(EnumValue),
    keywords: z.array(KeywordEnumValue),
    health_categories: z.array(EnumValue),
    health_themes: z.array(EnumValue),
    spatial_coverages: z.array(EnumValue),
    applicable_legislations: z.array(ApplicableLegislationEnumValue),
    conventions: z.array(EnumValue),
    areas_of_work: z.array(EnumValue),
    areas_of_competence: z.array(EnumValue),
    group_managers: z.array(EnumValue),
    languages: z.array(EnumValue),
  })
  .passthrough();
const DistributionForm = z
  .object({
    file_types: z.array(EnumValue),
    languages: z.array(EnumValue),
    licenses: z.array(EnumValue),
    distribution_path: z.array(EnumValue),
    applicable_legislations: z.array(ApplicableLegislationEnumValue),
    spatial_restrictions: z.array(EnumValue),
  })
  .passthrough();
const OrganisationEnumValue = z
  .object({
    value: z.string(),
    eng_label: z.string(),
    is_deprecated: z.union([z.boolean(), z.null()]).optional(),
    accessible_within_ctie: z.union([z.boolean(), z.null()]).optional(),
  })
  .passthrough();
const OrganisationForm = z.object({ organisations: z.array(OrganisationEnumValue) }).passthrough();
const DataServiceEnumValue = z
  .object({ value: z.string(), eng_label: z.string(), endpoints: z.array(DataServiceEndpointDto) })
  .passthrough();
const DataServiceForm = z.object({ data_services: z.array(DataServiceEnumValue) }).passthrough();
const ContactEnumValue = z
  .object({
    value: z.string(),
    eng_label: z.string(),
    parent_value: z.union([z.string(), z.null()]),
    is_deprecated: z.union([z.boolean(), z.null()]).optional(),
  })
  .passthrough();
const ContactForm = z.object({ contacts: z.array(ContactEnumValue) }).passthrough();
const Form = z
  .object({
    dataset: DatasetForm,
    distribution: DistributionForm,
    organisation: OrganisationForm,
    data_service: DataServiceForm,
    contact: ContactForm,
  })
  .passthrough();
const ResourceActivityLog = z
  .object({
    id: z.number().int(),
    username: z.string(),
    action_type: z.string(),
    entity_type: z.string(),
    entity_id: z.string(),
    changes: z.string(),
    timestamp: z.string(),
  })
  .passthrough();
const ResourceContact = z
  .object({
    id: z.number().int(),
    name: z.string(),
    email: z.string(),
    role: z.union([z.string(), z.null()]).optional(),
    is_deprecated: z.boolean().optional().default(false),
  })
  .passthrough();
const ResourceOrganisation = z
  .object({
    id: z.number().int(),
    name: z.string(),
    type: z.union([z.string(), z.null()]),
    email: z.union([z.string(), z.null()]),
    is_deprecated: z.boolean().optional().default(false),
    category: z.union([z.string(), z.null()]),
    accessible_within_ctie: z.union([z.boolean(), z.null()]),
    contacts: z.array(ResourceContact),
  })
  .passthrough();
const ContactDto = z.object({
  name: z.string().min(1).max(255),
  email: z.string().email(),
  role: z.union([z.string(), z.null()]).optional(),
});
const OrganisationDto = z
  .object({
    name: z.string().min(1),
    type: z.union([z.string(), z.null()]).optional(),
    email: z.union([z.string(), z.null()]).optional(),
    category: z.union([z.string(), z.null()]).optional(),
    accessible_within_ctie: z.union([z.boolean(), z.null()]).optional(),
    contacts: z.array(ContactDto).optional(),
  })
  .passthrough();
const FormFieldListRequest = z
  .object({
    page: z.number().int().default(1),
    page_size: z.number().int().default(10),
    query: z.union([z.string(), z.null()]),
    organisation_filters: z.union([z.array(z.string()), z.null()]),
  })
  .partial()
  .passthrough();
const ResourceFormField = z
  .object({
    key: z.string(),
    eng_label: z.string(),
    organisation_ids: z.union([z.array(z.number().int()), z.null()]).optional(),
    created_by_id: z.union([z.number(), z.null()]).optional(),
    created_by_name: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const ApplicableLegislationFormField = z
  .object({
    key: z.string(),
    eng_label: z.string(),
    organisation_ids: z.union([z.array(z.number().int()), z.null()]).optional(),
    created_by_id: z.union([z.number(), z.null()]).optional(),
    created_by_name: z.union([z.string(), z.null()]).optional(),
    description: z.string(),
    link: z.string(),
  })
  .passthrough();
const PaginatedFormFieldResponse = z
  .object({
    items: z.union([z.array(ResourceFormField), z.array(ApplicableLegislationFormField)]),
    meta: schemas__dataset__PaginationMeta,
  })
  .passthrough();
const ApplicableLegislationFormFieldDto = z
  .object({
    key: z.string().min(1).max(100),
    eng_label: z.string().min(1).max(500),
    organisation_ids: z.union([z.array(z.number().int()), z.null()]).optional(),
    description: z.string().max(1000),
    link: z.string().max(500),
  })
  .passthrough();
const CreateApplicableLegislationFormFieldDto = z
  .object({
    eng_label: z.string().min(1).max(500),
    organisation_ids: z.union([z.array(z.number().int()), z.null()]).optional(),
    description: z.string().max(1000),
    link: z.string().max(500),
  })
  .passthrough();
const CreateFormFieldDto = z
  .object({
    eng_label: z.string().min(1).max(500),
    organisation_ids: z.union([z.array(z.number().int()), z.null()]).optional(),
  })
  .passthrough();
const FormFieldDto = z
  .object({
    key: z.string().min(1).max(100),
    eng_label: z.string().min(1).max(500),
    organisation_ids: z.union([z.array(z.number().int()), z.null()]).optional(),
  })
  .passthrough();
const ResourceDatasetComment = z
  .object({
    id: z.number().int(),
    content: z.string(),
    author: z.string(),
    dataset_id: z.number().int(),
    timestamp: z.string(),
  })
  .passthrough();
const DataServiceDto = z.object({
  title: z.string().min(1).max(200),
  endpoints: z.array(DataServiceEndpointDto).max(50).optional(),
});
const UserListRequest = z
  .object({
    page: z.number().int().default(1),
    page_size: z.number().int().default(10),
    query: z.union([z.string(), z.null()]),
    organisation_ids: z.union([z.array(z.number().int()), z.null()]),
    role_ids: z.union([z.array(z.number().int()), z.null()]),
    only_unassigned: z.union([z.boolean(), z.null()]).default(false),
    is_deprecated: z.union([z.boolean(), z.null()]).default(false),
  })
  .partial()
  .passthrough();
const PaginatedUserResponse = z
  .object({ items: z.array(ResourceUser), meta: schemas__dataset__PaginationMeta })
  .passthrough();
const UserAssignmentDto = z.object({ email: z.string(), role_id: z.number().int() }).passthrough();
const AuthenticSourceLabelDto = z.object({
  name: z.string().min(1).max(200),
  description: z.union([z.string(), z.null()]).optional(),
  is_deprecated: z.boolean().optional().default(false),
});
const ResourceAuthenticSourceLabel = z
  .object({
    id: z.number().int(),
    name: z.string(),
    description: z.union([z.string(), z.null()]).optional(),
    created_at: z.string(),
    created_by: z.union([z.number(), z.null()]).optional(),
    created_by_name: z.union([z.string(), z.null()]).optional(),
    data_dictionary_entry_id: z.union([z.number(), z.null()]).optional(),
    dataset_id: z.union([z.number(), z.null()]).optional(),
    dataset_title: z.union([z.string(), z.null()]).optional(),
    dataset_is_deprecated: z.union([z.boolean(), z.null()]).optional(),
    is_deprecated: z.union([z.boolean(), z.null()]).optional().default(false),
  })
  .passthrough();
const LabelAssignmentHistory = z
  .object({
    dataset_id: z.union([z.number(), z.null()]),
    dataset_title: z.union([z.string(), z.null()]),
    dataset_description: z.union([z.string(), z.null()]),
    asignment_datetime: z.union([z.string(), z.null()]),
    is_deprecated: z.boolean().default(false),
    dataset_is_deprecated: z.union([z.boolean(), z.null()]),
  })
  .partial()
  .passthrough();
const LabelAssignmentDto = z.object({
  label_id: z.number().int().gt(0),
  assigned_entry_id: z.union([z.number(), z.null()]).optional(),
});
const BulkLabelAssignmentDto = z.object({
  label_assignments: z.array(LabelAssignmentDto).min(1).max(100),
});
const PublishingStatus = z.enum(["success", "failed"]);
const FilePublishingResult = z
  .object({
    filename: z.union([z.string(), z.null()]).optional(),
    remote_path: z.union([z.string(), z.null()]).optional(),
    publishing_status: PublishingStatus,
    error: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const FrontOfficePublishingResult = z
  .object({ timestamp: z.string(), files: z.array(FilePublishingResult) })
  .passthrough();
const FrontOfficeFileInfo = z
  .object({
    filename: z.string(),
    remote_path: z.string(),
    size_bytes: z.union([z.number(), z.null()]).optional(),
    modified_time: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const QualifiedAttributionDto = z
  .object({ organisation_id: z.number().int().gt(0), role: z.string().min(1).max(255) })
  .passthrough();
const LegiluxLegislation = z
  .object({ id: z.string(), label: z.string(), description: z.string(), link: z.string() })
  .passthrough();
const EurlexLegislation = z
  .object({ id: z.string(), label: z.string(), description: z.string(), link: z.string() })
  .passthrough();
const Body_scan_file_api_v1_antivirus_scan_post = z
  .object({ file: z.instanceof(File) })
  .passthrough();
const ReleasedDatasetItem = z
  .object({
    id: z.number().int(),
    identifier: z.string(),
    status: z.string(),
    released_at: z.union([z.string(), z.null()]).optional(),
    previous_version_dataset_id: z.union([z.number(), z.null()]).optional(),
    version_change_type: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const PaginatedReleasedDatasetsResponse = z
  .object({ items: z.array(ReleasedDatasetItem), meta: schemas__dataset__PaginationMeta })
  .passthrough();

export const schemas = {
  FeatureOptions,
  ResourceRole,
  ResourceOrganisationAssignment,
  ResourceUserOrganisation,
  ResourceUser,
  ValidationError,
  HTTPValidationError,
  ResourceDataDictionaryEntry,
  Body_bulk_upload_data_dictionaries_api_v1_datasets__dataset_id__data_dictionaries_bulk_upload_post,
  UpdateAuthenticSourceDto,
  BulkUpdateAuthenticSourceDto,
  UpdatePositionDto,
  BulkUpdatePositionDto,
  ResourceRelation,
  AddRelation,
  EnumValue,
  DataServiceEndpointDto,
  ResourceDataService,
  ResourcePolicyAction,
  ResourceDistribution,
  PolicyActionDto,
  DistributionDto,
  DatasetListRequest,
  HierarchicalEnumValue,
  ResourceQualifiedAttribution,
  ResourceSourceRelation,
  SeriesMembershipInfo,
  ResourceDataset,
  schemas__dataset__PaginationMeta,
  PaginatedDatasetResponse,
  DatasetCountsResponse,
  DatasetDto,
  Body_import_dataset_from_rdf_api_v1_datasets_import_rdf_post,
  DatasetStatusUpdateDto,
  DatasetVersionCreateDto,
  create_dataset_version_api_v1_datasets__dataset_id__version_post_Body,
  KeywordEnumValue,
  ApplicableLegislationEnumValue,
  DatasetForm,
  DistributionForm,
  OrganisationEnumValue,
  OrganisationForm,
  DataServiceEnumValue,
  DataServiceForm,
  ContactEnumValue,
  ContactForm,
  Form,
  ResourceActivityLog,
  ResourceContact,
  ResourceOrganisation,
  ContactDto,
  OrganisationDto,
  FormFieldListRequest,
  ResourceFormField,
  ApplicableLegislationFormField,
  PaginatedFormFieldResponse,
  ApplicableLegislationFormFieldDto,
  CreateApplicableLegislationFormFieldDto,
  CreateFormFieldDto,
  FormFieldDto,
  ResourceDatasetComment,
  DataServiceDto,
  UserListRequest,
  PaginatedUserResponse,
  UserAssignmentDto,
  AuthenticSourceLabelDto,
  ResourceAuthenticSourceLabel,
  LabelAssignmentHistory,
  LabelAssignmentDto,
  BulkLabelAssignmentDto,
  PublishingStatus,
  FilePublishingResult,
  FrontOfficePublishingResult,
  FrontOfficeFileInfo,
  QualifiedAttributionDto,
  LegiluxLegislation,
  EurlexLegislation,
  Body_scan_file_api_v1_antivirus_scan_post,
  ReleasedDatasetItem,
  PaginatedReleasedDatasetsResponse,
};

const endpoints = makeApi([
  {
    method: "get",
    path: "/:full_path",
    alias: "not_found__full_path__get",
    requestFormat: "json",
    parameters: [
      {
        name: "full_path",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.void(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/docs/config",
    alias: "docs_config_api_docs_config_get",
    description: `Serve configuration for documentation feature flags`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/health",
    alias: "health_check_api_health_get",
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/v1/:form_field/activity-logs",
    alias: "retrieve_all_form_fields_activity_logs_api_v1__form_field__activity_logs_get",
    requestFormat: "json",
    parameters: [
      {
        name: "form_field",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "page",
        type: "Query",
        schema: z.number().int().optional().default(1),
      },
      {
        name: "page_size",
        type: "Query",
        schema: z.number().int().optional().default(10),
      },
    ],
    response: z.array(ResourceActivityLog),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/activity-logs/assignments",
    alias: "retrieve_user_assignment_activity_logs_api_v1_activity_logs_assignments_get",
    requestFormat: "json",
    parameters: [
      {
        name: "page",
        type: "Query",
        schema: z.number().int().optional().default(1),
      },
      {
        name: "page_size",
        type: "Query",
        schema: z.number().int().optional().default(10),
      },
    ],
    response: z.array(ResourceActivityLog),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/activity-logs/authentic_source_labels",
    alias:
      "retrieve_authentic_source_label_activity_logs_api_v1_activity_logs_authentic_source_labels_get",
    requestFormat: "json",
    parameters: [
      {
        name: "page",
        type: "Query",
        schema: z.number().int().optional().default(1),
      },
      {
        name: "page_size",
        type: "Query",
        schema: z.number().int().optional().default(10),
      },
    ],
    response: z.array(ResourceActivityLog),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/antivirus/scan",
    alias: "scan_file_api_v1_antivirus_scan_post",
    requestFormat: "form-data",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ file: z.instanceof(File) }).passthrough(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/authentic-source-assignments",
    alias: "assign_authentic_source_label_api_v1_authentic_source_assignments_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: BulkLabelAssignmentDto,
      },
    ],
    response: z.array(ResourceAuthenticSourceLabel),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/authentic-source-labels",
    alias: "create_authentic_source_label_api_v1_authentic_source_labels_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: AuthenticSourceLabelDto,
      },
    ],
    response: ResourceAuthenticSourceLabel,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/authentic-source-labels",
    alias: "get_authentic_source_labels_api_v1_authentic_source_labels_get",
    requestFormat: "json",
    parameters: [
      {
        name: "include_deprecated",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
    ],
    response: z.array(ResourceAuthenticSourceLabel),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "put",
    path: "/api/v1/authentic-source-labels/:label_id",
    alias: "update_authentic_source_label_api_v1_authentic_source_labels__label_id__put",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: AuthenticSourceLabelDto,
      },
      {
        name: "label_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceAuthenticSourceLabel,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/v1/authentic-source-labels/:label_id",
    alias: "delete_authentic_source_label_api_v1_authentic_source_labels__label_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "label_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.void(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/authentic-source-labels/:label_id/history",
    alias:
      "get_authentic_source_label_history_api_v1_authentic_source_labels__label_id__history_get",
    requestFormat: "json",
    parameters: [
      {
        name: "label_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.array(LabelAssignmentHistory),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/v1/authentic-source-labels/:label_id/toggle-deprecation",
    alias:
      "change_deprecation_status_api_v1_authentic_source_labels__label_id__toggle_deprecation_patch",
    requestFormat: "json",
    parameters: [
      {
        name: "label_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceAuthenticSourceLabel,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/authentic-source-labels/catalogue.:format",
    alias:
      "retrieve_authentic_source_labels_catalogue_api_v1_authentic_source_labels_catalogue__format__get",
    requestFormat: "json",
    parameters: [
      {
        name: "format",
        type: "Path",
        schema: z.enum(["ttl", "rdf", "jsonld"]),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/authentic-source/publish-to-front-office",
    alias:
      "publish_authentic_source_to_front_office_api_v1_authentic_source_publish_to_front_office_post",
    requestFormat: "json",
    response: FrontOfficePublishingResult,
  },
  {
    method: "get",
    path: "/api/v1/catalogue.:format",
    alias: "retrieve_catalogue_api_v1_catalogue__format__get",
    requestFormat: "json",
    parameters: [
      {
        name: "format",
        type: "Path",
        schema: z.enum(["ttl", "rdf", "jsonld"]),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/catalogue/:format/upload",
    alias: "retrieve_catalogue_and_upload_s3_api_v1_catalogue__format__upload_get",
    requestFormat: "json",
    parameters: [
      {
        name: "format",
        type: "Path",
        schema: z.enum(["ttl", "rdf", "jsonld"]),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/config/roles",
    alias: "get_config_roles_api_v1_config_roles_get",
    requestFormat: "json",
    response: z.array(z.object({}).partial().passthrough()),
  },
  {
    method: "get",
    path: "/api/v1/data_services",
    alias: "get_data_services_api_v1_data_services_get",
    requestFormat: "json",
    response: z.array(ResourceDataService),
  },
  {
    method: "post",
    path: "/api/v1/data_services",
    alias: "create_data_service_api_v1_data_services_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DataServiceDto,
      },
    ],
    response: ResourceDataService,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/data_services/:data_service_id",
    alias: "get_data_service_by_id_api_v1_data_services__data_service_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "data_service_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceDataService,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "put",
    path: "/api/v1/data_services/:data_service_id",
    alias: "update_data_service_api_v1_data_services__data_service_id__put",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DataServiceDto,
      },
      {
        name: "data_service_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceDataService,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/v1/dataset-comments/:comment_id",
    alias: "delete_comment_api_v1_dataset_comments__comment_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "comment_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.void(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/datasets",
    alias: "create_dataset_api_v1_datasets_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DatasetDto,
      },
    ],
    response: ResourceDataset,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/datasets/:dataset_id",
    alias: "retrieve_dataset_api_v1_datasets__dataset_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceDataset,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "put",
    path: "/api/v1/datasets/:dataset_id",
    alias: "edit_dataset_api_v1_datasets__dataset_id__put",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DatasetDto,
      },
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceDataset,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/v1/datasets/:dataset_id",
    alias: "delete_dataset_api_v1_datasets__dataset_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.void(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/datasets/:dataset_id/activity-logs",
    alias: "retrieve_activity_logs_from_dataset_api_v1_datasets__dataset_id__activity_logs_get",
    requestFormat: "json",
    parameters: [
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
      {
        name: "page",
        type: "Query",
        schema: z.number().int().optional().default(1),
      },
      {
        name: "page_size",
        type: "Query",
        schema: z.number().int().optional().default(10),
      },
    ],
    response: z.array(ResourceActivityLog),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/datasets/:dataset_id/authentic-source/complete-review",
    alias:
      "complete_authentic_source_review_api_v1_datasets__dataset_id__authentic_source_complete_review_post",
    requestFormat: "json",
    parameters: [
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.void(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/datasets/:dataset_id/clone",
    alias: "clone_dataset_api_v1_datasets__dataset_id__clone_post",
    requestFormat: "json",
    parameters: [
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceDataset,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/datasets/:dataset_id/comments",
    alias: "get_dataset_comments_api_v1_datasets__dataset_id__comments_get",
    requestFormat: "json",
    parameters: [
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.array(ResourceDatasetComment),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/datasets/:dataset_id/data-dictionaries",
    alias: "get_data_dictionaries_by_dataset_id_api_v1_datasets__dataset_id__data_dictionaries_get",
    requestFormat: "json",
    parameters: [
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.array(ResourceDataDictionaryEntry),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/datasets/:dataset_id/data-dictionaries",
    alias: "add_data_dictionary_api_v1_datasets__dataset_id__data_dictionaries_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ResourceDataDictionaryEntry,
      },
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceDataDictionaryEntry,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "put",
    path: "/api/v1/datasets/:dataset_id/data-dictionaries/:entry_id",
    alias: "update_data_dictionary_api_v1_datasets__dataset_id__data_dictionaries__entry_id__put",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ResourceDataDictionaryEntry,
      },
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
      {
        name: "entry_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceDataDictionaryEntry,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/v1/datasets/:dataset_id/data-dictionaries/:entry_id",
    alias:
      "delete_data_dictionary_entry_api_v1_datasets__dataset_id__data_dictionaries__entry_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
      {
        name: "entry_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.void(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/datasets/:dataset_id/data-dictionaries/bulk-update-authentic-source",
    alias:
      "bulk_update_authentic_source_api_v1_datasets__dataset_id__data_dictionaries_bulk_update_authentic_source_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: BulkUpdateAuthenticSourceDto,
      },
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.array(ResourceDataDictionaryEntry),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/datasets/:dataset_id/data-dictionaries/bulk-update-positions",
    alias:
      "bulk_update_positions_api_v1_datasets__dataset_id__data_dictionaries_bulk_update_positions_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: BulkUpdatePositionDto,
      },
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.array(ResourceDataDictionaryEntry),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/datasets/:dataset_id/data-dictionaries/bulk-upload",
    alias:
      "bulk_upload_data_dictionaries_api_v1_datasets__dataset_id__data_dictionaries_bulk_upload_post",
    requestFormat: "form-data",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ file: z.instanceof(File) }).passthrough(),
      },
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/datasets/:dataset_id/data-dictionaries/download",
    alias:
      "download_data_dictionary_csv_api_v1_datasets__dataset_id__data_dictionaries_download_get",
    requestFormat: "json",
    parameters: [
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.void(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/datasets/:dataset_id/distributions",
    alias: "get_distributions_by_dataset_id_api_v1_datasets__dataset_id__distributions_get",
    requestFormat: "json",
    parameters: [
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.array(ResourceDistribution),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/datasets/:dataset_id/distributions",
    alias: "add_distribution_api_v1_datasets__dataset_id__distributions_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DistributionDto,
      },
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceDistribution,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "put",
    path: "/api/v1/datasets/:dataset_id/distributions/:distribution_id",
    alias: "update_distribution_api_v1_datasets__dataset_id__distributions__distribution_id__put",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DistributionDto,
      },
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
      {
        name: "distribution_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceDistribution,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/v1/datasets/:dataset_id/distributions/:distribution_id",
    alias:
      "delete_distribution_api_v1_datasets__dataset_id__distributions__distribution_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
      {
        name: "distribution_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.void(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/datasets/:dataset_id/download",
    alias: "retrieve_individual_dataset_catalogue_api_v1_datasets__dataset_id__download_get",
    requestFormat: "json",
    parameters: [
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
      {
        name: "format",
        type: "Query",
        schema: z.enum(["ttl", "rdf", "jsonld"]),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/datasets/:dataset_id/publish-to-front-office",
    alias:
      "publish_dataset_to_front_office_api_v1_datasets__dataset_id__publish_to_front_office_post",
    requestFormat: "json",
    parameters: [
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: FrontOfficePublishingResult,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/datasets/:dataset_id/qualified-attributions",
    alias:
      "get_qualified_attributions_by_dataset_id_api_v1_datasets__dataset_id__qualified_attributions_get",
    requestFormat: "json",
    parameters: [
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.array(ResourceQualifiedAttribution),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/datasets/:dataset_id/qualified-attributions",
    alias: "add_qualified_attribution_api_v1_datasets__dataset_id__qualified_attributions_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: QualifiedAttributionDto,
      },
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceQualifiedAttribution,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "put",
    path: "/api/v1/datasets/:dataset_id/qualified-attributions/:attribution_id",
    alias:
      "update_qualified_attribution_api_v1_datasets__dataset_id__qualified_attributions__attribution_id__put",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: QualifiedAttributionDto,
      },
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
      {
        name: "attribution_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceQualifiedAttribution,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/v1/datasets/:dataset_id/qualified-attributions/:attribution_id",
    alias:
      "delete_qualified_attribution_api_v1_datasets__dataset_id__qualified_attributions__attribution_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
      {
        name: "attribution_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.void(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/datasets/:dataset_id/relations",
    alias: "get_relations_by_dataset_id_api_v1_datasets__dataset_id__relations_get",
    requestFormat: "json",
    parameters: [
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.array(ResourceRelation),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/datasets/:dataset_id/relations",
    alias: "add_relation_api_v1_datasets__dataset_id__relations_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: AddRelation,
      },
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceRelation,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/v1/datasets/:dataset_id/relations/:relation_id",
    alias: "delete_relation_api_v1_datasets__dataset_id__relations__relation_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
      {
        name: "relation_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.void(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/datasets/:dataset_id/status/:status_trigger",
    alias: "update_dataset_status_api_v1_datasets__dataset_id__status__status_trigger__post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DatasetStatusUpdateDto,
      },
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
      {
        name: "status_trigger",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: ResourceDataset,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/datasets/:dataset_id/version",
    alias: "create_dataset_version_api_v1_datasets__dataset_id__version_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: create_dataset_version_api_v1_datasets__dataset_id__version_post_Body,
      },
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceDataset,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/datasets/:dataset_id/versions-chain",
    alias: "get_dataset_versions_chain_api_v1_datasets__dataset_id__versions_chain_get",
    requestFormat: "json",
    parameters: [
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.array(ResourceDataset),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/datasets/counts",
    alias: "get_dataset_counts_api_v1_datasets_counts_get",
    requestFormat: "json",
    response: DatasetCountsResponse,
  },
  {
    method: "post",
    path: "/api/v1/datasets/import/rdf",
    alias: "import_dataset_from_rdf_api_v1_datasets_import_rdf_post",
    requestFormat: "form-data",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: Body_import_dataset_from_rdf_api_v1_datasets_import_rdf_post,
      },
    ],
    response: ResourceDataset,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/eurlex/legislation/search",
    alias: "search_legislation_api_v1_eurlex_legislation_search_get",
    requestFormat: "json",
    parameters: [
      {
        name: "query",
        type: "Query",
        schema: z.string().optional().default(""),
      },
    ],
    response: z.array(EurlexLegislation),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/form-fields",
    alias: "retrieve_form_fields_api_v1_form_fields_get",
    requestFormat: "json",
    response: Form,
  },
  {
    method: "post",
    path: "/api/v1/form-fields/:field_type",
    alias: "create_form_field_api_v1_form_fields__field_type__post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CreateFormFieldDto,
      },
      {
        name: "field_type",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: ResourceFormField,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "put",
    path: "/api/v1/form-fields/:field_type",
    alias: "update_form_field_api_v1_form_fields__field_type__put",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: FormFieldDto,
      },
      {
        name: "field_type",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: ResourceFormField,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "put",
    path: "/api/v1/form-fields/:field_type/:key/promote-global",
    alias: "promote_form_field_to_global_api_v1_form_fields__field_type___key__promote_global_put",
    requestFormat: "json",
    parameters: [
      {
        name: "field_type",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "key",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([ResourceFormField, ApplicableLegislationFormField]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/form-fields/:field_type/all",
    alias: "get_all_form_fields_api_v1_form_fields__field_type__all_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: FormFieldListRequest,
      },
      {
        name: "field_type",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: PaginatedFormFieldResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "put",
    path: "/api/v1/form-fields/:field_type/delete",
    alias: "delete_form_field_api_v1_form_fields__field_type__delete_put",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: FormFieldDto,
      },
      {
        name: "field_type",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "put",
    path: "/api/v1/form-fields/applicable_legislation",
    alias: "update_applicable_legislation_form_field_api_v1_form_fields_applicable_legislation_put",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ApplicableLegislationFormFieldDto,
      },
    ],
    response: ApplicableLegislationFormField,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/form-fields/applicable_legislation",
    alias:
      "create_applicable_legislation_form_field_api_v1_form_fields_applicable_legislation_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CreateApplicableLegislationFormFieldDto,
      },
    ],
    response: ApplicableLegislationFormField,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/front-office-files",
    alias: "list_front_office_files_api_v1_front_office_files_get",
    requestFormat: "json",
    response: z.array(FrontOfficeFileInfo),
  },
  {
    method: "get",
    path: "/api/v1/legilux/legislation/search",
    alias: "search_legislation_api_v1_legilux_legislation_search_get",
    description: `Search for legislation in LegiLux.

Args:
    query: Search term to filter legislation by title, description, or URI

Returns:
    List of matching legislation with id, label, description, and link (limited to 10 results)`,
    requestFormat: "json",
    parameters: [
      {
        name: "query",
        type: "Query",
        schema: z.string().optional().default(""),
      },
    ],
    response: z.array(LegiluxLegislation),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/organisations",
    alias: "get_organisations_api_v1_organisations_get",
    requestFormat: "json",
    response: z.array(ResourceOrganisation),
  },
  {
    method: "post",
    path: "/api/v1/organisations",
    alias: "create_organisation_api_v1_organisations_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: OrganisationDto,
      },
    ],
    response: ResourceOrganisation,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/organisations/:organisation_id",
    alias: "get_organisation_by_id_api_v1_organisations__organisation_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "organisation_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceOrganisation,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "put",
    path: "/api/v1/organisations/:organisation_id",
    alias: "update_organisation_api_v1_organisations__organisation_id__put",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: OrganisationDto,
      },
      {
        name: "organisation_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceOrganisation,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/organisations/:organisation_id/activity-logs",
    alias:
      "retrieve_activity_logs_from_organisation_api_v1_organisations__organisation_id__activity_logs_get",
    requestFormat: "json",
    parameters: [
      {
        name: "organisation_id",
        type: "Path",
        schema: z.number().int(),
      },
      {
        name: "page",
        type: "Query",
        schema: z.number().int().optional().default(1),
      },
      {
        name: "page_size",
        type: "Query",
        schema: z.number().int().optional().default(10),
      },
    ],
    response: z.array(ResourceActivityLog),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/organisations/:organisation_id/assignments",
    alias: "create_organisation_assignment_api_v1_organisations__organisation_id__assignments_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: UserAssignmentDto,
      },
      {
        name: "organisation_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/v1/organisations/:organisation_id/assignments/:user_id",
    alias:
      "delete_organisation_assignment_api_v1_organisations__organisation_id__assignments__user_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "organisation_id",
        type: "Path",
        schema: z.number().int(),
      },
      {
        name: "user_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.void(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/v1/organisations/:organisation_id/assignments/:user_id/roles/:role_id",
    alias:
      "delete_user_role_assignment_api_v1_organisations__organisation_id__assignments__user_id__roles__role_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "organisation_id",
        type: "Path",
        schema: z.number().int(),
      },
      {
        name: "user_id",
        type: "Path",
        schema: z.number().int(),
      },
      {
        name: "role_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.void(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/organisations/:organisation_id/contacts",
    alias: "add_contact_api_v1_organisations__organisation_id__contacts_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ContactDto,
      },
      {
        name: "organisation_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceContact,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "put",
    path: "/api/v1/organisations/:organisation_id/contacts/:contact_id",
    alias: "update_contact_api_v1_organisations__organisation_id__contacts__contact_id__put",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ContactDto,
      },
      {
        name: "organisation_id",
        type: "Path",
        schema: z.number().int(),
      },
      {
        name: "contact_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceContact,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/v1/organisations/:organisation_id/contacts/:contact_id",
    alias: "delete_contact_api_v1_organisations__organisation_id__contacts__contact_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "organisation_id",
        type: "Path",
        schema: z.number().int(),
      },
      {
        name: "contact_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.void(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/v1/organisations/:organisation_id/contacts/:contact_id/toggle-deprecation",
    alias:
      "change_deprecation_status_api_v1_organisations__organisation_id__contacts__contact_id__toggle_deprecation_patch",
    requestFormat: "json",
    parameters: [
      {
        name: "organisation_id",
        type: "Path",
        schema: z.number().int(),
      },
      {
        name: "contact_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceContact,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/v1/organisations/:organisation_id/toggle-deprecation",
    alias:
      "toggle_organisation_deprecation_api_v1_organisations__organisation_id__toggle_deprecation_patch",
    requestFormat: "json",
    parameters: [
      {
        name: "organisation_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: ResourceOrganisation,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/organisations/activity-logs",
    alias: "retrieve_all_organisations_activity_logs_api_v1_organisations_activity_logs_get",
    requestFormat: "json",
    parameters: [
      {
        name: "multi_tenant",
        type: "Query",
        schema: z.boolean().optional().default(true),
      },
      {
        name: "page",
        type: "Query",
        schema: z.number().int().optional().default(1),
      },
      {
        name: "page_size",
        type: "Query",
        schema: z.number().int().optional().default(10),
      },
    ],
    response: z.array(ResourceActivityLog),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/paginated_datasets",
    alias: "paginated_datasets_api_v1_paginated_datasets_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DatasetListRequest,
      },
    ],
    response: PaginatedDatasetResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/released-datasets",
    alias: "get_released_datasets_api_v1_released_datasets_get",
    requestFormat: "json",
    parameters: [
      {
        name: "page",
        type: "Query",
        schema: z.number().int().gte(1).optional().default(1),
      },
      {
        name: "page_size",
        type: "Query",
        schema: z.number().int().gte(1).lte(500).optional().default(50),
      },
    ],
    response: PaginatedReleasedDatasetsResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/released-datasets/:dataset_id/download",
    alias: "download_released_dataset_rdf_api_v1_released_datasets__dataset_id__download_get",
    requestFormat: "json",
    parameters: [
      {
        name: "dataset_id",
        type: "Path",
        schema: z.number().int(),
      },
      {
        name: "format",
        type: "Query",
        schema: z.enum(["ttl", "rdf", "jsonld"]).optional(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/roles",
    alias: "get_roles_api_v1_roles_post",
    requestFormat: "json",
    response: z.array(ResourceRole),
  },
  {
    method: "post",
    path: "/api/v1/switch-organisation/:org_id",
    alias: "switch_organisation_api_v1_switch_organisation__org_id__post",
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/ui_config",
    alias: "get_ui_config_api_v1_ui_config_get",
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/v1/user",
    alias: "get_user_api_v1_user_get",
    requestFormat: "json",
    response: ResourceUser,
  },
  {
    method: "post",
    path: "/api/v1/users",
    alias: "users_api_v1_users_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: UserListRequest,
      },
    ],
    response: PaginatedUserResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/v1/users/:user_id",
    alias: "delete_unassigned_user_api_v1_users__user_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "user_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.void(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/v1/users/:user_id/iam-roles",
    alias: "remove_user_iam_roles_api_v1_users__user_id__iam_roles_delete",
    requestFormat: "json",
    parameters: [
      {
        name: "user_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.void(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/v1/users/:user_id/toggle-deprecation",
    alias: "change_deprecation_status_api_v1_users__user_id__toggle_deprecation_patch",
    requestFormat: "json",
    parameters: [
      {
        name: "user_id",
        type: "Path",
        schema: z.number().int(),
      },
    ],
    response: z.void(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/auth",
    alias: "auth_auth_get",
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/data-dictionary-template.csv",
    alias: "public_csv_files_data_dictionary_template_csv_get",
    requestFormat: "json",
    response: z.void(),
  },
  {
    method: "get",
    path: "/favicon.svg",
    alias: "public_svg_files_favicon_svg_get",
    requestFormat: "json",
    response: z.void(),
  },
  {
    method: "get",
    path: "/fonts/:font_name",
    alias: "public_fonts_fonts__font_name__get",
    requestFormat: "json",
    parameters: [
      {
        name: "font_name",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/login",
    alias: "login_login_get",
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/logout",
    alias: "logout_logout_get",
    requestFormat: "json",
    response: z.unknown(),
  },
]);

export const api = new Zodios(endpoints);

export function createApiClient(baseUrl: string, options?: ZodiosOptions) {
  return new Zodios(baseUrl, endpoints, options);
}
