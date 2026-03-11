import { ResourceActivityLog } from "../../types";
import { LogFormatter, LogFormatterContext } from "./types";

interface Change {
  field: string;
  change_type: string;
  old_value?: string;
  new_value?: { name: string } | string;
}

export class OrganizationFormatter implements LogFormatter {
  // @ts-expect-error context' is declared but its value is never read.
  formatMessage(log: ResourceActivityLog, context: LogFormatterContext): string | null {
    switch (log.action_type.toLowerCase()) {
      case "create":
        return `${log.username} created this ${log.entity_type}.`;

      case "add_contact":
        return this.formatAddContact(log);

      case "update_contact":
        return this.formatUpdateContact(log);

      case "deprecate":
        return this.formatDeprecateContact(log);

      case "restore":
        return this.formatRestoreContact(log);

      case "delete_contact":
        return this.formatDeleteContact(log);

      case "update":
        return `${log.username} updated this ${log.entity_type}.`;

      case "delete":
        return `${log.username} deleted this ${log.entity_type}.`;

      default:
        return `${log.username} performed an action on this ${log.entity_type}.`;
    }
  }

  private formatAddContact(log: ResourceActivityLog): string {
    try {
      const changes: Change[] = JSON.parse(log.changes);
      const contactChange = changes.find(
        (change) => change.field === "contact" && change.change_type === "values_changed",
      );
      if (
        contactChange &&
        contactChange.new_value !== undefined &&
        typeof contactChange.new_value !== "string"
      ) {
        const contactName = contactChange.new_value.name;
        return `${log.username} added contact "${contactName}" to this ${log.entity_type}.`;
      }
      return `${log.username} added a contact to this ${log.entity_type}.`;
    } catch (error) {
      return `${log.username} added a contact to this ${log.entity_type}, but details were not recognized.`;
    }
  }

  private formatUpdateContact(log: ResourceActivityLog): string {
    try {
      const changes: Change[] = JSON.parse(log.changes);
      const changedFieldNames = changes.map((change) => change.field).join(", ");
      const changedFieldValues = changes.map((change) => change.new_value).join(", ");
      return `${log.username} updated a contact with fields: ${changedFieldNames} to values: ${changedFieldValues} in this ${log.entity_type}.`;
    } catch (error) {
      return `${log.username} updated a contact to this ${log.entity_type}, but details were not recognized.`;
    }
  }

  private formatDeprecateContact(log: ResourceActivityLog): string {
    try {
      const changes: Change[] = JSON.parse(log.changes);
      const firstChange = changes[0];
      const contactName =
        typeof firstChange?.new_value === "object" && firstChange?.new_value !== null
          ? firstChange.new_value.name
          : "unknown";
      return `${log.username} deprecated contact "${contactName}" in this ${log.entity_type}.`;
    } catch (error) {
      return `${log.username} deprecated a contact in this ${log.entity_type}, but details were not recognized.`;
    }
  }

  private formatRestoreContact(log: ResourceActivityLog): string {
    try {
      const changes: Change[] = JSON.parse(log.changes);
      const firstChange = changes[0];
      const contactName =
        typeof firstChange?.new_value === "object" && firstChange?.new_value !== null
          ? firstChange.new_value.name
          : "unknown";
      return `${log.username} restored contact "${contactName}" in this ${log.entity_type}.`;
    } catch (error) {
      return `${log.username} restored a contact in this ${log.entity_type}, but details were not recognized.`;
    }
  }

  private formatDeleteContact(log: ResourceActivityLog): string {
    try {
      const changes: Change[] = JSON.parse(log.changes);
      const change = changes[0];
      if (change && change.old_value) {
        // @ts-expect-error 'change.old_value.name' is possibly not existing
        return `${log.username} deleted contact "${change.old_value.name}" from this ${log.entity_type}.`;
      }
      return `${log.username} deleted a contact from this ${log.entity_type}.`;
    } catch (error) {
      return `${log.username} deleted a contact from this ${log.entity_type}, but details were not recognized.`;
    }
  }
}
