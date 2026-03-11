import { z } from "zod";
import { schemas } from "./zodiosClient/openapi.json.client";

export type ResourceDistributionType = z.infer<typeof schemas.ResourceDistribution>;
export type ResourceDatasetType = z.infer<typeof schemas.ResourceDataset>;
export type FormType = z.infer<typeof schemas.Form>;

export type DatasetDtoType = z.input<typeof schemas.DatasetDto>;
export type DistributionDtoType = z.input<typeof schemas.DistributionDto>;

export type DistributionFormType = z.infer<typeof schemas.DistributionForm>;
export type EnumValueType = z.infer<typeof schemas.EnumValue>;
export type ApplicableLegislationEnumValueType = z.infer<
  typeof schemas.ApplicableLegislationEnumValue
>;

export type ResourceUserType = z.infer<typeof schemas.ResourceUser>;
export type ResourceRoleType = z.infer<typeof schemas.ResourceRole>;

export type ResourceActivityLog = z.infer<typeof schemas.ResourceActivityLog>;

export type ResourceDatasetComment = z.infer<typeof schemas.ResourceDatasetComment>;

export type ResourceDataDictionaryEntry = z.infer<typeof schemas.ResourceDataDictionaryEntry>;

export type ResourceOrganisation = z.infer<typeof schemas.ResourceOrganisation>;

export type ResourceDataService = z.infer<typeof schemas.ResourceDataService>;
export type ResourceDataServiceEndpoint = z.infer<typeof schemas.DataServiceEndpointDto>;

export type ResourceFormField = z.infer<typeof schemas.ResourceFormField>;
export type ResourceLabelAssignmentHistory = z.infer<typeof schemas.LabelAssignmentHistory>;
export type ResourceAuthenticSourceLabel = z.infer<typeof schemas.ResourceAuthenticSourceLabel>;
export type ApplicableLegislationFormField = z.infer<typeof schemas.ApplicableLegislationFormField>;

export type ResourceContact = z.infer<typeof schemas.ResourceContact>;

export type SeriesMembershipInfo = z.infer<typeof schemas.SeriesMembershipInfo>;

export type DatasetCountsResponse = z.infer<typeof schemas.DatasetCountsResponse>;

export type FrontOfficePublishingResult = z.infer<typeof schemas.FrontOfficePublishingResult>;

export type FrontOfficeFileInfo = z.infer<typeof schemas.FrontOfficeFileInfo>;

export type ResourceQualifiedAttribution = z.infer<typeof schemas.ResourceQualifiedAttribution>;

export type DatasetRelation = {
  id: number;
  relationKind: "dataset" | "external";

  datasetId?: number | null;
  title?: string | null;
  status?: string | null;
  relationType?: string | null;

  externalUrl?: string | null;
  externalRole?: string | null;
  externalDescription?: string | null;
};

export enum DatasetStatusEnum {
  DRAFT = "DRAFT",
  COMPLETED = "COMPLETED",
  VALIDATED = "VALIDATED",
  APPROVED = "APPROVED",
  INTERNAL_ONLY = "INTERNAL_ONLY",
  PUBLISHED = "PUBLISHED",
  DEPRECATED = "DEPRECATED",
}

export enum FilterTypes {
  DatasetTypes = "datasetTypes",
  RightsStatment = "rightsStatement",
  Keywords = "keywords",
  Themes = "themes",
  Organisations = "organisations",
  FormFieldOrganisations = "organisation_filters",
  ApplicableLegislations = "applicableLegislations",
  Frequency = "frequency",
  UserOrganisations = "organisation_ids",
  UserRoles = "role_ids",
  OnlyUnassigned = "only_unassigned",
  authenticSource = "authentic_source",
  deprecatedUsers = "deprecated",
}

export enum FrontOfficeUploadStatus {
  IDLE = "IDLE",
  UPLOADING = "UPLOADING",
  SUCCESS = "SUCCESS",
  ERROR = "ERROR",
}
