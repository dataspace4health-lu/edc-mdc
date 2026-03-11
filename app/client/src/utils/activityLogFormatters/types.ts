import { ResourceActivityLog, ResourceOrganisation, ResourceRoleType } from "../../types";

export interface LogFormatterContext {
  roles: ResourceRoleType[];
  organisations: ResourceOrganisation[];
}

export interface LogFormatter {
  formatMessage(log: ResourceActivityLog, context: LogFormatterContext): string | null;
}
