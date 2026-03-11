import { ResourceActivityLog, ResourceRoleType, ResourceOrganisation } from "../../types";
import { LogFormatter, LogFormatterContext } from "./types";
import { UserAssignmentFormatter } from "./userAssignmentFormatter";
import { FormFieldFormatter } from "./formFieldFormatter";
import { DatasetFormatter, PolicyActionFormatter } from "./datasetFormatter";
import { OrganizationFormatter } from "./organizationFormatter";
import { AuthenticSourceLabelFormatter } from "./authenticSourceLabelFormatter";
import { AllOrganisationsFormatter } from "./allOrganizationsFormatter";

const formatters: Record<string, LogFormatter> = {
  user_assignment: new UserAssignmentFormatter(),
  keyword: new FormFieldFormatter(),
  applicable_legislation: new FormFieldFormatter(),
  legal_basis: new FormFieldFormatter(),
  policy_action: new PolicyActionFormatter(),
  dataset: new DatasetFormatter(),
  organisation: new OrganizationFormatter(),
  all_organisations: new AllOrganisationsFormatter(),
  authentic_source_label: new AuthenticSourceLabelFormatter(),
};

export const formatLogMessage = (
  log: ResourceActivityLog,
  roles: ResourceRoleType[],
  organisations: ResourceOrganisation[],
  entityType: string,
  entityId: number | null,
): string | null => {
  const context: LogFormatterContext = { roles, organisations };
  const key =
    entityType === "organisation" && entityId === null ? "all_organisations" : log.entity_type;

  const formatter = formatters[key];
  if (formatter) {
    return formatter.formatMessage(log, context);
  }

  return `${log.username} performed an action on this ${log.entity_type}.`;
};
