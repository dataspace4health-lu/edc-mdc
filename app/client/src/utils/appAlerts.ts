import { getDatasetStatusAlertContent } from "./datasetStatusAlertContent";
import type { ReactNode } from "react";

export type AppAlertType = "success" | "error";

export interface AppAlertPayload {
  alertType: AppAlertType;
  message: string;
  title?: string;
  body?: ReactNode;
}

const success = (message: string, body?: ReactNode): AppAlertPayload => ({
  alertType: "success",
  message,
  body,
});
const successWithTitle = (
  title: string,
  body: ReactNode,
  message: string = title,
): AppAlertPayload => ({
  alertType: "success",
  title,
  body,
  message,
});
const error = (message: string): AppAlertPayload => ({ alertType: "error", message });

// Centralized alert catalog. Existing call sites can migrate to these helpers incrementally.
export const appAlerts = {
  successMessage: (message: string) => success(message),
  errorMessage: (message: string) => error(message),

  datasetStatusUpdated: (newStatus: string, previousStatus?: string): AppAlertPayload => {
    const { title, body, message } = getDatasetStatusAlertContent(newStatus, previousStatus);
    return successWithTitle(title, body, message);
  },
  datasetUpdated: () => success("Dataset updated successfully"),
  datasetCloned: () => success("Dataset cloned successfully"),
  datasetVersionCreated: () =>
    successWithTitle(
      "Dataset version created",
      "A new version has been created. Make your changes, save again when done, and submit for review when ready.",
    ),
  datasetDeleted: () => success("Dataset deleted successfully"),
  datasetDeleteFailed: () => error("Failed to delete dataset"),
  datasetDuplicateExists: () =>
    error("A dataset with the same title, description, and publisher already exists."),
  datasetImported: (title: string) => success(`Dataset "${title}" imported successfully.`),
  datasetStatusDeletionBlocked: (status: string) =>
    error(`Comments cannot be deleted while the dataset is in "${status}" status.`),
  groupManagersRequiredBeforeComplete: () =>
    error("Group Managers must be assigned before completing the dataset."),

  relationAdded: () => success("Relation added successfully"),
  relationDeleted: () => success("Relation deleted successfully"),
  relationInvalidData: () => error("Invalid relation data based on the chosen relation kind"),
  linkMustBeValidUrl: () => error("Link must be a valid URL (e.g., https://example.com)"),

  distributionDeleted: () => success("Distribution deleted successfully"),
  distributionDeleteFailed: () => error("Failed to delete distribution."),

  dataServiceCreated: () => success("Data service created successfully"),
  dataServiceUpdated: () => success("Data service updated successfully"),
  dataServiceDeleted: () => success("Data service deleted successfully"),
  dataServiceDeleteBlockedInUse: () => error("The service is in use and cannot be deleted"),
  dataServiceDeleteFailed: () => error("An error occurred while deleting the service"),

  commentDeleted: () => success("Comment deleted successfully"),
  commentDeleteFailed: () => error("Failed to delete comment."),
  commentDeletePermissionDenied: () => error("You do not have permission to delete comments."),

  authenticSourceLabelAdded: () => success("Authentic Source Label added successfully"),
  authenticSourceLabelUpdated: () => success("Authentic Source Label updated successfully"),
  authenticSourceLabelDeleted: () => success("Authentic Source Label deleted successfully"),
  authenticSourceLabelDeleteBlockedInUse: () => error("The label is in use and cannot be deleted"),
  authenticSourceLabeled: () => success("Authentic Source labelled successfully"),
  authenticSourceEntriesSaved: () => success("Authentic Source entries saved successfully"),
  authenticSourceNoEntries: () => success("This dataset can be marked for authentic source."),
  authenticSourcePendingReview: () =>
    success("This dataset contains authentic source entries pending review."),
  authenticSourceMarkedNoSources: () =>
    success("Dataset marked as containing no authentic sources"),
  labelDeprecated: () => success("Label deprecated successfully"),
  labelRestored: () => success("Label restored successfully"),

  organisationCreated: () => success("Organisation created successfully"),
  organisationUpdated: () => success("Organisation updated successfully"),
  organisationRemoved: () => success("Organisation removed successfully"),
  organisationLoadFailed: () => error("Failed to load organisations"),
  organisationDuplicate: () => error("Organisation with this name or email already exists."),

  contactAdded: () => success("Contact added successfully"),
  contactUpdated: () => success("Contact updated successfully"),
  contactDeleted: () => success("Contact deleted successfully"),
  contactDuplicate: () => error("Contact with this name or email already exists."),

  roleAssigned: (): AppAlertPayload => ({
    alertType: "success",
    title: "Role assigned successfully",
    message: "Role assigned successfully",
    body: "The user has been notified by email about the assigned role.",
  }),
  roleRemoved: () => success("Role removed successfully"),

  userDeleted: () => success("User deleted successfully"),
  userDeprecated: () => success("User deprecated successfully."),
  iamRolesRemoved: () => success("IAM roles removed successfully."),
  userDeletePermissionDenied: () => error("You do not have permission to delete users."),
  iamRoleRemovePermissionDenied: () => error("You do not have permission to remove IAM roles."),

  qualifiedAttributionCreated: () => success("Qualified attribution created successfully"),
  qualifiedAttributionUpdated: () => success("Qualified attribution updated successfully"),
  qualifiedAttributionDeleted: () => success("Qualified attribution deleted successfully"),

  formFieldInUse: () => error("The field is in use and cannot be deleted"),
  duplicateAccessUrlsNotAllowed: () => error("Duplicate access URLs are not allowed."),
  duplicateConformsToNotAllowed: () => error("Duplicate conforms to values are not allowed."),
  duplicateDocumentationEntriesNotAllowed: () =>
    error("Duplicate documentation entries are not allowed."),
  duplicateDocumentationValuesNotAllowed: () =>
    error("Duplicate documentation values are not allowed."),
  duplicateDownloadUrlsNotAllowed: () => error("Duplicate download URLs are not allowed."),
  duplicateHealthLegalBasisNotAllowed: () =>
    error("Duplicate health legal basis values are not allowed."),
  duplicateLandingPagesNotAllowed: () => error("Duplicate landing pages are not allowed."),
  duplicateLinkedSchemasNotAllowed: () => error("Duplicate linked schemas are not allowed."),
  duplicateOtherIdentifiersNotAllowed: () => error("Duplicate other identifiers are not allowed."),
  duplicatePersonalDataNotAllowed: () => error("Duplicate personal data values are not allowed."),
  duplicateProvenanceNotAllowed: () => error("Duplicate provenance values are not allowed."),
  duplicatePurposeNotAllowed: () => error("Duplicate purpose values are not allowed."),
  duplicateSpatialResolutionsNotAllowed: () =>
    error("Duplicate spatial resolutions are not allowed."),
  duplicateVersionNotesNotAllowed: () => error("Duplicate version notes are not allowed."),
  duplicateWasGeneratedByNotAllowed: () =>
    error("Duplicate was generated by values are not allowed."),
  endDateBeforeStartDate: () => error("End date cannot be earlier than start date."),
  modifiedDateBeforeStartDate: () => error("Modified date cannot be earlier than start date."),
  modifiedDateAfterEndDate: () => error("Modified date cannot be later than end date."),
  retentionEndDateBeforeStartDate: () =>
    error("Retention period end date cannot be earlier than start date."),
  fileFormatRequiredWhenNonPublic: () =>
    error("File format is required when Rights are non-public."),
  byteSizeRequiredWhenNonPublic: () => error("Byte size is required when Rights are non-public."),
  privacyRiskRequiredForPii: () =>
    error("Privacy risk must be provided if personally identifiable variable is true."),
  healthDatasetsMustIncludeTheme: () => error("Health datasets must include the Health theme."),
  noFileSelected: () => error("No file selected."),
  csvFileRequired: () => error("Please upload a valid CSV file (.csv)."),
  rdfFileRequired: () => error("Please select an RDF file to upload."),
  fileExtensionRequired: () => error("The selected file must have an extension."),
  orderSaved: () => success("Order saved successfully"),
  saveOrderFailed: () => error("Failed to save order"),
  dataDictionaryEntryDeleted: () => success("Data Dictionary Entry deleted successfully"),
  dataDictionaryDeleteFailed: () => error("Failed to delete entry"),
  fieldNameAlreadyInUse: () => error("Field name is already in use"),

  logsCopied: () => success("Logs copied to clipboard"),
  logsCopyFailed: () => error("Failed to copy logs to clipboard"),
  frontOfficeFilesLoaded: (count: number) =>
    success(`Successfully loaded ${count || 0} files from front office server`),

  unknownError: () => error("An unknown error occurred."),
  unexpectedError: () => error("An unexpected error occurred."),
  serverErrorTryLater: () => error("Server error. Please try again later."),
  pleaseFixFormErrors: () => error("Please fix the errors in the form"),
  failedToDeprecateUser: () => error("Failed to deprecate user."),
  failedToDeleteUser: () => error("Failed to delete user."),
  failedToRemoveIamRoles: () => error("Failed to remove IAM roles."),
  failedToPromoteToGlobal: () => error("Failed to promote to global"),
  failedToFetchFrontOfficeFiles: () => error("Failed to fetch files from front office server"),
  organisationDeprecationToggleFailed: () => error("Failed to toggle organisation deprecation."),
  organisationDeprecationToggled: (wasDeprecated: boolean) =>
    success(
      wasDeprecated
        ? "Organisation restored successfully."
        : "Organisation deprecated successfully.",
    ),
  required: () => error("Required"),
  hello: () => success("Hello"),
  bonjour: () => success("Bonjour"),

  // Dynamic or template-based usages found in current codebase
  genericValidationError: (details: string) => error(details),
  alertMessageAsSuccess: (alertMsg: string) => success(alertMsg),
  fallbackErrorMessage: (fallbackMessage: string) => error(fallbackMessage),
  singularCreated: (singular: string) => success(`${singular} created successfully`),
  singularUpdated: (singular: string) => success(`${singular} updated successfully`),
  singularDeleted: (singular: string) => success(`${singular} deleted successfully`),
  singularPromotedToGlobal: (singular: string) =>
    success(`${singular} promoted to global successfully`),
  bulkDatasetsCreated: (successCount: number) =>
    success(`${successCount} dataset${successCount > 1 ? "s" : ""} successfully created!`),
  typeMustBeOneOf: (allowedDataTypes: string[]) =>
    error(`Type must be one of: ${allowedDataTypes.join(", ")}`),
  pleaseFixErrors: (errorsMessage: string): AppAlertPayload =>
    ({
      alertType: "error",
      title: "Please fix the errors",
      body: errorsMessage,
    }) as AppAlertPayload,
} as const;
