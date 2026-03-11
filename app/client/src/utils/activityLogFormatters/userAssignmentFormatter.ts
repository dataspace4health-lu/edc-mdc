import { ResourceActivityLog, ResourceRoleType, ResourceOrganisation } from "../../types";
import { LogFormatter, LogFormatterContext } from "./types";

interface UserAssignmentChange {
  field: string;
  change_type: string;
  old_value?: {
    target_user_id: number;
    target_user_email: string;
    organisation_id: number;
    role_id?: number;
    role_ids?: number[];
  } | null;
  new_value?: {
    target_user_id: number;
    target_user_email: string;
    organisation_id: number;
    role_id?: number;
    role_ids?: number[];
  } | null;
}

function getRoleNameById(roleId: number, allRoles: ResourceRoleType[]): string {
  return allRoles.find((role) => role.id === roleId)?.name || "unknown role";
}

function getOrganisationNameById(orgId: number, organisations: ResourceOrganisation[]): string {
  return organisations.find((org) => org.id === orgId)?.name || "unknown organisation";
}

export class UserAssignmentFormatter implements LogFormatter {
  formatMessage(log: ResourceActivityLog, context: LogFormatterContext): string | null {
    try {
      const changesRaw: unknown = JSON.parse(log.changes);
      const changes = changesRaw as UserAssignmentChange[];
      const change = changes[0];
      const user = change.new_value ?? change.old_value;

      if (!user) return `${log.username} modified a user assignment with no details.`;

      const email = user.target_user_email;
      const roleNames =
        user.role_id !== undefined
          ? getRoleNameById(user.role_id, context.roles)
          : user.role_ids
            ? user.role_ids.map((roleId) => getRoleNameById(roleId, context.roles)).join(", ")
            : "unknown role";

      const orgName = getOrganisationNameById(user.organisation_id, context.organisations);

      switch (change.change_type) {
        case "created":
          return `${log.username} assigned ${email} to ${orgName} with role ${roleNames}`;
        case "deleted":
          return `${log.username} removed user assignment for ${email} in ${orgName}`;
        case "role_added":
          return `${log.username} added the role ${roleNames} for ${email} in ${orgName}`;
        case "role_removed":
          return `${log.username} removed role ${roleNames} from ${email} in ${orgName}`;
        case "deprecated":
          return `${log.username} deprecated user ${email}`;
        case "restored":
          return `${log.username} restored user ${email}`;
        default:
          return `${log.username} updated user assignment for ${email}`;
      }
    } catch (err) {
      return `${log.username} changed a user assignment, but details could not be read.`;
    }
  }
}
