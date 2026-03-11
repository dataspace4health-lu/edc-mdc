import { ResourceActivityLog } from "../../types";
import { LogFormatter, LogFormatterContext } from "./types";

interface Change {
  field: string;
  change_type: string;
  old_value?: string;
  new_value?: { name: string } | string;
  source_instance?: string;
  label?: string;
}

export class FormFieldFormatter implements LogFormatter {
  // @ts-expect-error context' is declared but its value is never read.
  formatMessage(log: ResourceActivityLog, context: LogFormatterContext): string | null {
    const entityType = log.entity_type;

    if (!["keyword", "applicable_legislation", "legal_basis"].includes(entityType)) {
      return null;
    }

    switch (log.action_type.toLowerCase()) {
      case "create":
        try {
          const changes: Change[] = JSON.parse(log.changes);

          const externalImport = changes.find((change) => change.change_type === "external_import");
          if (externalImport) {
            const sourceInstance = externalImport.source_instance;
            const label = externalImport.label || log.entity_id;
            const entityTypeName =
              entityType === "applicable_legislation" || entityType === "legal_basis"
                ? "Applicable legislation"
                : "Keyword";
            return `${entityTypeName} "${label}" imported from ${sourceInstance}.`;
          }

          const engLabel = changes.find((change) => change.field === "eng_label");
          return `${log.username} created "${engLabel?.new_value}"`;
        } catch (err) {
          return `${log.username} created a ${entityType}, but details were not recognized.`;
        }

      case "update":
        try {
          const changes: Change[] = JSON.parse(log.changes);
          const fieldNames = changes.map((change) => {
            const field = change.field === "eng_label" ? "label" : change.field;
            const raw = change.new_value;
            const val = typeof raw === "object" ? raw.name : raw;
            if (val) {
              return `${field} to "${val}"`;
            }
            return field;
          });
          return `${log.username} updated ${fieldNames.join("; ")}. on field: "${log.entity_id}"`;
        } catch (err) {
          return `${log.username} updated a ${entityType}, but details were not recognized.`;
        }

      case "delete":
        try {
          const changes: Change[] = JSON.parse(log.changes);
          const engLabel = changes.find((change) => change.field === "eng_label");
          const label = engLabel?.old_value ?? `<#${log.entity_id}>`;
          return `${log.username} deleted "${label}"`;
        } catch {
          return `${log.username} deleted ${log.entity_id}.`;
        }

      case "promote_to_global":
        try {
          const changes: Change[] = JSON.parse(log.changes);
          const engLabel = changes.find((change) => change.field === "eng_label");
          const label = engLabel?.new_value || engLabel?.old_value || log.entity_id;
          return `${log.username} promoted "${label}" to global`;
        } catch {
          return `${log.username} promoted this ${entityType} to global`;
        }

      default:
        return `${log.username} performed an action on this ${entityType}.`;
    }
  }
}
