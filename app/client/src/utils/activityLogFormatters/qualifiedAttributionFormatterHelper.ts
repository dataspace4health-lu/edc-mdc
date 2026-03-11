import { ResourceActivityLog } from "../../types";

interface Change {
  field: string;
  change_type: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  old_value?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  new_value?: any;
}

export function formatQualifiedAttributionChanges(
  qaChanges: Change[],
  log: ResourceActivityLog,
): string {
  try {
    const change = qaChanges[0];

    if (change.change_type === "qualified_attribution_added") {
      const orgName = change.new_value?.organisation_name || "Unknown";
      const role = change.new_value?.role || "Unknown";
      return `${log.username} added ${orgName} attribution with role ${role} to this ${log.entity_type}.`;
    }

    if (change.change_type === "qualified_attribution_removed") {
      const orgName = change.old_value?.organisation_name || "Unknown";
      const role = change.old_value?.role || "Unknown";
      return `${log.username} removed ${orgName} attribution with role ${role} from this ${log.entity_type}.`;
    }

    if (change.change_type === "qualified_attribution_updated") {
      const oldOrgName = change.old_value?.organisation_name || "Unknown";
      const oldRole = change.old_value?.role || "Unknown";
      const newOrgName = change.new_value?.organisation_name || "Unknown";
      const newRole = change.new_value?.role || "Unknown";

      if (oldOrgName === newOrgName && oldRole !== newRole) {
        return `${log.username} updated ${oldOrgName} attribution from role ${oldRole} to ${newRole} in this ${log.entity_type}.`;
      }

      if (oldOrgName !== newOrgName && oldRole === newRole) {
        return `${log.username} updated ${oldRole} attribution from ${oldOrgName} to ${newOrgName} in this ${log.entity_type}.`;
      }

      return `${log.username} updated attribution from ${oldOrgName} (${oldRole}) to ${newOrgName} (${newRole}) in this ${log.entity_type}.`;
    }

    const oldValue = change.old_value;
    const newValue = change.new_value;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const parseQAString = (value: any): unknown[] => {
      if (!value) return [];
      if (Array.isArray(value)) return value;

      if (typeof value === "string") {
        if (value === "") return [];
        const matches = value.match(/organisation_id/g);
        return matches ? new Array(matches.length).fill(null) : [];
      }

      if (typeof value === "object") return [value];
      return [];
    };

    const oldArray = parseQAString(oldValue);
    const newArray = parseQAString(newValue);

    if (oldArray.length < newArray.length) {
      const count = newArray.length - oldArray.length;
      return `${log.username} added ${count} qualified attribution${count > 1 ? "s" : ""} to this ${log.entity_type}.`;
    }

    if (oldArray.length > newArray.length) {
      const count = oldArray.length - newArray.length;
      return `${log.username} removed ${count} qualified attribution${count > 1 ? "s" : ""} from this ${log.entity_type}.`;
    }

    if (oldArray.length === newArray.length && oldArray.length > 0) {
      return `${log.username} updated ${oldArray.length} qualified attribution${oldArray.length > 1 ? "s" : ""} in this ${log.entity_type}.`;
    }

    return `${log.username} updated Qualified Attributions in this ${log.entity_type}.`;
  } catch (error) {
    return `${log.username} updated Qualified Attributions in this ${log.entity_type}.`;
  }
}
