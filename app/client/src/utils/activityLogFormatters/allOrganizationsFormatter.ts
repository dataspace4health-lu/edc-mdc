import { ResourceActivityLog } from "../../types";
import { LogFormatter, LogFormatterContext } from "./types";

interface Change {
  field: string;
  change_type: string;
  old_value?: string;
  new_value?: { name: string } | string;
}

export class AllOrganisationsFormatter implements LogFormatter {
  formatMessage(log: ResourceActivityLog, context: LogFormatterContext): string | null {
    if (log.entity_type !== "organisation") {
      return null;
    }

    const name =
      context.organisations.find((o) => o.id === Number(log.entity_id))?.name ||
      "unknown organisation";

    let changes: Change[];
    try {
      changes = JSON.parse(log.changes) as Change[];
    } catch {
      return `${log.username} performed an action on ${name}, but details weren’t recognized.`;
    }

    switch (log.action_type.toLowerCase()) {
      case "restore":
        return `${log.username} restored ${name}.`;
      case "create":
        return `${log.username} created ${name}.`;

      case "deprecate":
        return `${log.username} deprecated ${name}.`;

      case "add_contact": {
        const c = changes.find((c) => c.field === "contact" && c.change_type === "values_changed");
        const contactName =
          typeof c?.new_value === "object" && c.new_value !== null ? c.new_value.name : "unknown";
        return `${log.username} added contact "${contactName}" to ${name}.`;
      }

      case "update_contact": {
        const fields = changes.map((c) => c.field).join(", ");
        const vals = changes
          .map((c) => {
            if (c.new_value === null || c.new_value === "") return "(cleared)";
            if (typeof c.new_value === "object" && c.new_value !== null) return c.new_value.name;
            return c.new_value;
          })
          .join(", ");
        return `${log.username} updated contact ${fields} to ${vals} in ${name}.`;
      }

      case "deprecate_contact": {
        const vals = changes
          .map((c) => {
            if (c.new_value === null || c.new_value === "") return "(cleared)";
            if (typeof c.new_value === "object" && c.new_value !== null) return c.new_value.name;
            return c.new_value;
          })
          .join(", ");
        return `${log.username} deprecated contact ${vals} in ${name}.`;
      }

      case "update": {
        const parts = changes.map((c) => {
          const raw = c.new_value;
          const val =
            typeof raw === "object" && raw !== null && "name" in raw
              ? (raw as { name: string }).name
              : raw;
          return `${c.field} to "${val}"`;
        });
        return `${log.username} updated ${parts.join(", ")} of ${name}.`;
      }

      default:
        return `${log.username} performed an action on ${name}, but details weren’t recognized.`;
    }
  }
}
