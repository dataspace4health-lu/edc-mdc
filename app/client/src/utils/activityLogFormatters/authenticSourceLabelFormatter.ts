import { ResourceActivityLog } from "../../types";
import { LogFormatter, LogFormatterContext } from "./types";

interface AuthenticSourceLabelCreateChange {
  field: string;
  change_type: string;
  old_value?: {
    id: number;
    name: string;
    description: string;
  } | null;
  new_value?: {
    id: number;
    name: string;
    description: string;
  } | null;
}

interface AuthenticSourceLabelUpdateChange {
  field: string;
  change_type: string;
  old_value?: {
    id: number;
    name: string;
    entry_id: number | null;
    dataset_id: number | null;
  } | null;
  new_value?: {
    id: number;
    name: string;
    entry_id: number | null;
    dataset_id: number | null;
  } | null;
}

export class AuthenticSourceLabelFormatter implements LogFormatter {
  // @ts-expect-error context' is declared but its value is never read.
  formatMessage(log: ResourceActivityLog, context: LogFormatterContext): string | null {
    try {
      const changesRaw: unknown = JSON.parse(log.changes);
      const changes = changesRaw as
        | AuthenticSourceLabelCreateChange[]
        | AuthenticSourceLabelUpdateChange[];
      const change = changes[0];
      const name = change.new_value?.name || change.old_value?.name;

      if (log.action_type === "update" && change.change_type === "updated") {
        let message = `${log.username} updated`;
        changes.forEach((change) => {
          if (change.field === "name") {
            message += ` name to "${change.new_value}"`;
          } else if (change.field === "description") {
            message += ` description to "${change.new_value}"`;
          }
        });
        return message;
      } else if (log.action_type === "delete") {
        return `${log.username} deleted label ${name}`;
      }

      switch (change.change_type) {
        case "created":
          return `${log.username} added a new authentic source label: ${name}`;
        case "values_changed":
          if (log.action_type === "deprecate") {
            return `${log.username} deprecated authentic source label: ${name}`;
          } else if (log.action_type === "restore") {
            return `${log.username} restored authentic source label: ${name}`;
          }
          return `${log.username} updated authentic source label: ${name}`;
        case "reassigned":
          return `${log.username} reassigned authentic source label ${name} to Dataset ID: ${(change as AuthenticSourceLabelUpdateChange).new_value?.dataset_id}`;
        case "assigned":
          return `${log.username} assigned authentic source label ${name} to Dataset ID: ${(change as AuthenticSourceLabelUpdateChange).new_value?.dataset_id}`;
        case "unassigned":
          return `${log.username} unassigned authentic source label ${name} from Dataset ID: ${(change as AuthenticSourceLabelUpdateChange).old_value?.dataset_id}`;
        default:
          return `${log.username} changed authentic source label for ${name}`;
      }
    } catch (err) {
      return `${log.username} changed a authentic source label , but details could not be read.`;
    }
  }
}
