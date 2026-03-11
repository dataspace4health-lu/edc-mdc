import { ResourceActivityLog } from "../../types";
import { LogFormatter, LogFormatterContext } from "./types";
import { getDatasetFieldShortLabel } from "../../schemas/datasetSchema";
import { getDistributionShortLabel } from "../../schemas/distributionSchema";
import { formatQualifiedAttributionChanges } from "./qualifiedAttributionFormatterHelper";
import { formatDataDictionaryReorder } from "./dataDictionaryFormatter";

interface Change {
  field: string;
  change_type: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  old_value?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  new_value?: any;
  source_instance?: string;
  outcome?: string;
  error_message?: string;
}

interface LabelValue {
  id: number;
  name: string;
  entry_id?: number;
}

export class DatasetFormatter implements LogFormatter {
  // @ts-expect-error context' is declared but its value is never read.
  formatMessage(log: ResourceActivityLog, context: LogFormatterContext): string | null {
    switch (log.action_type.toLowerCase()) {
      case "create":
        return this.formatCreate(log);

      case "update":
        return this.formatUpdate(log);

      case "distribution_policy_update":
        return this.formatPolicyActionUpdates(log);

      case "delete":
        return `${log.username} deleted this ${log.entity_type}.`;

      case "reorder":
        return this.formatReorder(log);

      case "add_comment":
        return this.formatCommentAction(log, "created");
      case "delete_comment":
        return this.formatCommentAction(log, "deleted");

      default:
        return `${log.username} performed an action on this ${log.entity_type}.`;
    }
  }

  private formatCreate(log: ResourceActivityLog): string {
    try {
      const changes: Change[] = JSON.parse(log.changes);

      const harvesterChanges = changes.filter(
        (change: Change) => change.change_type === "external_import",
      );
      if (harvesterChanges.length > 0) {
        return this.formatHarvesterChanges(harvesterChanges[0], log);
      }
    } catch (error) {
      // Ignore parsing errors
    }

    return `${log.username} created this ${log.entity_type}.`;
  }

  private formatPolicyActionUpdates(log: ResourceActivityLog): string {
    try {
      const changes = JSON.parse(log.changes);
      const policyActionChanges = changes.filter(
        (change: Change) => change.field === "policy_action",
      );

      if (policyActionChanges.length > 0) {
        return this.formatPolicyActionChanges(policyActionChanges, log);
      }

      return `${log.username} performed some changes on this ${log.entity_type}.`;
    } catch (error) {
      return `${log.username} performed some changes on this ${log.entity_type}.`;
    }
  }

  private formatUpdate(log: ResourceActivityLog): string | null {
    try {
      const changes: Change[] = JSON.parse(log.changes);
      if (changes.length === 0) {
        return null;
      }

      const distributionChanges = changes.filter(
        (change: Change) =>
          change.field === "distribution" &&
          (change.change_type === "created" ||
            change.change_type === "deleted" ||
            change.change_type === "updated"),
      );

      if (distributionChanges.length > 0) {
        return this.formatDistributionChanges(distributionChanges, log);
      }

      const policyActionChanges = changes.filter(
        (change: Change) =>
          change.change_type === "created" ||
          change.change_type === "deleted" ||
          change.change_type === "updated",
      );

      if (policyActionChanges.length > 0) {
        return this.formatPolicyActionChanges(policyActionChanges, log);
      }

      const harvesterChanges = changes.filter(
        (change: Change) =>
          change.change_type === "external_import" || change.change_type === "external_status_sync",
      );
      if (harvesterChanges.length > 0) {
        return this.formatHarvesterChanges(harvesterChanges[0], log);
      }

      const labelChanges = changes.filter(
        (change: Change) =>
          change.change_type === "label_assigned" || change.change_type === "label_unassigned",
      );

      if (labelChanges.length > 0) {
        return this.formatLabelChanges(labelChanges, log);
      }

      const qaChanges = changes.filter(
        (change: Change) => change.field === "qualified_attributions",
      );
      if (qaChanges.length > 0 && changes.length === qaChanges.length) {
        return formatQualifiedAttributionChanges(qaChanges, log);
      }

      const fieldsDescription = changes
        .filter(
          (change: Change) =>
            change.change_type !== "dictionary_item_added" &&
            change.change_type !== "dictionary_item_removed" &&
            change.change_type !== "dictionary_item_updated" &&
            change.change_type !== "created" &&
            change.change_type !== "deleted" &&
            change.field !== "qualified_attributions",
        )
        .map((change: Change) => {
          if (change.field.includes("distributions")) {
            const fieldParts = change.field.split(".");
            const field = fieldParts[2];
            const normalizedField = field.replace(/\[.*\]/g, "");
            const distributionTitle = change.field.split(".")[1];
            let label = getDistributionShortLabel(normalizedField) || field;
            if (normalizedField === "policy_actions") {
              label = "Policy Actions";
            } else {
              const subField = fieldParts.slice(3).join(".");
              if (subField) {
                label = `${label} (${subField})`;
              }
            }
            return `${label} of Distribution with title "${distributionTitle}"`;
          }
          return `${
            getDatasetFieldShortLabel(change.field)
              ? getDatasetFieldShortLabel(change.field)
              : change.field
          }`;
        })
        .join(", ");

      let activityLogMessage = fieldsDescription
        ? `${log.username} updated ${fieldsDescription} in this ${log.entity_type}.`
        : "";

      if (qaChanges.length > 0 && fieldsDescription) {
        const qaMessage = formatQualifiedAttributionChanges(qaChanges, log);
        if (qaMessage) {
          const actionPart = qaMessage
            .replace(`${log.username} `, "")
            .replace(` to this ${log.entity_type}.`, "")
            .replace(` from this ${log.entity_type}.`, "")
            .replace(` in this ${log.entity_type}.`, "");
          activityLogMessage = activityLogMessage.replace(
            ` in this ${log.entity_type}.`,
            ` and ${actionPart} in this ${log.entity_type}.`,
          );
        }
      }

      activityLogMessage = this.processDictionaryChanges(changes, log, activityLogMessage);

      const statusChanges = changes.filter(
        (change: Change) => change.change_type === "status_change",
      );
      if (statusChanges.length > 0) {
        const statusChange = statusChanges[0];
        activityLogMessage = `${log.username} updated the status of this ${log.entity_type} from "${statusChange.old_value}" to "${statusChange.new_value}".`;
      }

      return activityLogMessage;
    } catch (error) {
      return `${log.username} updated this ${log.entity_type} with unrecognized changes.`;
    }
  }

  private formatPolicyActionChanges(
    policyActionChanges: Change[],
    log: ResourceActivityLog,
  ): string {
    try {
      const addedActions: { type: string; constraint: string; distribution: string }[] = [];
      const removedActions: { type: string; constraint: string; distribution: string }[] = [];
      const updatedActions: { type: string; constraint: string; distribution: string }[] = [];

      policyActionChanges.forEach((change: Change) => {
        if (
          change.change_type === "created" &&
          change.new_value &&
          change.field === "policy_action"
        ) {
          const { policy_action_type, policy_constraint_type, distribution_title } =
            change.new_value;
          addedActions.push({
            type: policy_action_type,
            constraint: policy_constraint_type,
            distribution: distribution_title || "unknown distribution",
          });
        } else if (
          change.change_type === "deleted" &&
          change.old_value &&
          change.field === "policy_action"
        ) {
          const { policy_action_type, policy_constraint_type, distribution_title } =
            change.old_value;
          removedActions.push({
            type: policy_action_type,
            constraint: policy_constraint_type,
            distribution: distribution_title || "unknown distribution",
          });
        } else if (
          change.change_type === "updated" &&
          change.new_value &&
          change.field === "policy_action"
        ) {
          const { policy_action_type, policy_constraint_type, distribution_title } =
            change.new_value;
          updatedActions.push({
            type: policy_action_type,
            constraint: policy_constraint_type,
            distribution: distribution_title || "unknown distribution",
          });
        }
      });

      const messages: string[] = [];
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const distributionGroups: Map<string, { added: any[]; removed: any[]; updated: any[] }> =
        new Map();

      addedActions.forEach((action) => {
        if (!distributionGroups.has(action.distribution)) {
          distributionGroups.set(action.distribution, { added: [], removed: [], updated: [] });
        }
        distributionGroups.get(action.distribution)!.added.push(action);
      });

      removedActions.forEach((action) => {
        if (!distributionGroups.has(action.distribution)) {
          distributionGroups.set(action.distribution, { added: [], removed: [], updated: [] });
        }
        distributionGroups.get(action.distribution)!.removed.push(action);
      });

      updatedActions.forEach((action) => {
        if (!distributionGroups.has(action.distribution)) {
          distributionGroups.set(action.distribution, { added: [], removed: [], updated: [] });
        }
        distributionGroups.get(action.distribution)!.updated.push(action);
      });

      distributionGroups.forEach((actions, distributionTitle) => {
        const distributionInfo = ` on distribution "${distributionTitle}"`;
        const actionParts: string[] = [];

        if (actions.added.length > 0) {
          const permissionCount = actions.added.filter((a) => a.type === "permission").length;
          const prohibitionCount = actions.added.filter((a) => a.type === "prohibition").length;

          const addedParts: string[] = [];
          if (permissionCount > 0) {
            addedParts.push(`${permissionCount} permission${permissionCount > 1 ? "s" : ""}`);
          }
          if (prohibitionCount > 0) {
            addedParts.push(`${prohibitionCount} prohibition${prohibitionCount > 1 ? "s" : ""}`);
          }

          actionParts.push(`added ${addedParts.join(" and ")}`);
        }

        if (actions.updated.length > 0) {
          const permissionCount = actions.updated.filter((a) => a.type === "permission").length;
          const prohibitionCount = actions.updated.filter((a) => a.type === "prohibition").length;

          const updatedParts: string[] = [];
          if (permissionCount > 0) {
            updatedParts.push(`${permissionCount} permission${permissionCount > 1 ? "s" : ""}`);
          }
          if (prohibitionCount > 0) {
            updatedParts.push(`${prohibitionCount} prohibition${prohibitionCount > 1 ? "s" : ""}`);
          }

          actionParts.push(`updated ${updatedParts.join(" and ")}`);
        }

        if (actions.removed.length > 0) {
          const permissionCount = actions.removed.filter((a) => a.type === "permission").length;
          const prohibitionCount = actions.removed.filter((a) => a.type === "prohibition").length;

          const removedParts: string[] = [];
          if (permissionCount > 0) {
            removedParts.push(`${permissionCount} permission${permissionCount > 1 ? "s" : ""}`);
          }
          if (prohibitionCount > 0) {
            removedParts.push(`${prohibitionCount} prohibition${prohibitionCount > 1 ? "s" : ""}`);
          }

          actionParts.push(`removed ${removedParts.join(" and ")}`);
        }

        if (actionParts.length > 0) {
          messages.push(`${actionParts.join(", ")}${distributionInfo}`);
        }
      });

      if (messages.length === 0) {
        return `${log.username} updated policy actions for this ${log.entity_type}.`;
      }

      const actionsText = messages.join(" and ");
      return `${log.username} ${actionsText}.`;
    } catch (error) {
      return `${log.username} updated policy actions for this ${log.entity_type}, but details were not recognized.`;
    }
  }

  private formatDistributionChanges(
    distributionChanges: Change[],
    log: ResourceActivityLog,
  ): string {
    try {
      const messages: string[] = [];

      distributionChanges.forEach((change: Change) => {
        const getDistributionIdentifier = (data: {
          distribution_title?: string;
          distribution_id?: string | number;
        }): string => {
          if (data?.distribution_title) {
            return `"${data.distribution_title}"`;
          }
          return data?.distribution_id ? `#${data.distribution_id}` : "unknown";
        };

        if (change.change_type === "created" && change.new_value) {
          const identifier = getDistributionIdentifier(change.new_value);
          messages.push(`added distribution ${identifier}`);
        } else if (change.change_type === "updated") {
          const oldIdentifier = change.old_value
            ? getDistributionIdentifier(change.old_value)
            : null;
          const newIdentifier = change.new_value
            ? getDistributionIdentifier(change.new_value)
            : null;

          // Check if it's a title rename
          if (
            oldIdentifier &&
            newIdentifier &&
            oldIdentifier !== newIdentifier &&
            change.old_value?.distribution_title &&
            change.new_value?.distribution_title
          ) {
            messages.push(`renamed distribution from ${oldIdentifier} to ${newIdentifier}`);
          } else if (newIdentifier) {
            messages.push(`updated distribution ${newIdentifier}`);
          } else {
            messages.push(`updated a distribution`);
          }
        } else if (change.change_type === "deleted" && change.old_value) {
          const identifier = getDistributionIdentifier(change.old_value);
          messages.push(`deleted distribution ${identifier}`);
        }
      });

      if (messages.length === 0) {
        return `${log.username} updated distributions for this ${log.entity_type}.`;
      }

      const actionsText = messages.join(" and ");
      return `${log.username} ${actionsText} in this ${log.entity_type}.`;
    } catch (error) {
      return `${log.username} updated distributions for this ${log.entity_type}, but details were not recognized.`;
    }
  }

  private formatLabelChanges(labelChanges: Change[], log: ResourceActivityLog): string {
    try {
      const assignedChanges = labelChanges.filter(
        (change) => change.change_type === "label_assigned",
      );
      const unassignedChanges = labelChanges.filter(
        (change) => change.change_type === "label_unassigned",
      );

      const messages: string[] = [];

      // Handle assignments
      assignedChanges.forEach((change: Change) => {
        if (change.new_value && change.new_value.name) {
          const labelValue = change.new_value as LabelValue;
          const entryInfo = labelValue.entry_id ? ` to a entry` : "";
          messages.push(`assigned authentic source label "${labelValue.name}"${entryInfo}`);
        }
      });

      // Handle unassignments
      unassignedChanges.forEach((change: Change) => {
        if (change.old_value && change.old_value.name) {
          const labelValue = change.old_value as LabelValue;
          const entryInfo = labelValue.entry_id ? ` from a entry` : "";
          messages.push(`unassigned authentic source label "${labelValue.name}"${entryInfo}`);
        }
      });

      if (messages.length === 0) {
        return `${log.username} updated authentic source labels for this ${log.entity_type}.`;
      }

      const actionsText = messages.join(" and ");
      return `${log.username} ${actionsText} in this ${log.entity_type}.`;
    } catch (error) {
      return `${log.username} updated authentic source labels for this ${log.entity_type}, but details were not recognized.`;
    }
  }

  private processDictionaryChanges(
    changes: Change[],
    log: ResourceActivityLog,
    baseMessage: string,
  ): string {
    let message = baseMessage;
    const fieldsDescription = baseMessage.length > 0;

    changes
      .filter(
        (change: Change) =>
          change.change_type === "dictionary_item_added" ||
          change.change_type === "dictionary_item_removed" ||
          change.change_type === "dictionary_item_updated",
      )
      .forEach((change: Change) => {
        const [prefix, ...rest] = change.field.split(".");
        let entryDescription = rest.join(".");
        let entryType = prefix.substring(0, prefix.length - 1);
        let entryFieldName = "title";

        if (prefix === "relations") {
          const isExternalRelation = rest[0] === "external";

          if (isExternalRelation) {
            entryType = "external relation";
            entryFieldName = "URL";
            entryDescription = rest.slice(1).join(".");
          } else {
            entryType = "dataset relation";
            const relationType = rest[0] || "unknown type";
            const targetDataset = rest[1] || "unknown";

            const relationLabel = relationType.replace("dct:", "");
            entryDescription = `${relationLabel} with dataset ${targetDataset}`;
            entryFieldName = "relationship";
          }
        }
        if (prefix === "data_dictionaries") {
          entryType = "data dictionary entry";
          entryFieldName = "name";
        }
        if (prefix === "distributions") {
          const restJoined = rest.join(".");
          const firstDotIndex = restJoined.indexOf(".");
          if (firstDotIndex !== -1) {
            entryDescription = restJoined.substring(0, firstDotIndex);
          } else {
            entryDescription = restJoined;
          }
        }

        if (change.change_type === "dictionary_item_added") {
          if (fieldsDescription) {
            message = message.concat(
              ` And also added a new ${entryType} with ${entryFieldName} "${entryDescription}" to this ${log.entity_type}.`,
            );
          } else {
            message = `${log.username} added a new ${entryType} with ${entryFieldName} "${entryDescription}" to this ${log.entity_type}.`;
          }
        } else if (change.change_type === "dictionary_item_removed") {
          if (fieldsDescription) {
            message = message.concat(
              ` And also removed a ${entryType} with ${entryFieldName} "${entryDescription}" from this ${log.entity_type}.`,
            );
          } else {
            message = `${log.username} removed a ${entryType} with ${entryFieldName} "${entryDescription}" from this ${log.entity_type}.`;
          }
        } else if (change.change_type === "dictionary_item_updated") {
          if (fieldsDescription) {
            message = message.concat(
              ` And also updated a ${entryType} with ${entryFieldName} "${entryDescription}" in this ${log.entity_type}.`,
            );
          } else {
            message = `${log.username} updated a ${entryType} with ${entryFieldName} "${entryDescription}" in this ${log.entity_type}.`;
          }
        }
      });

    return message;
  }

  private formatReorder(log: ResourceActivityLog): string {
    return formatDataDictionaryReorder(log);
  }

  private formatCommentAction(log: ResourceActivityLog, actionType: "created" | "deleted"): string {
    const actionVerb = actionType === "created" ? "added" : "deleted";
    const preposition = actionType === "created" ? "to" : "from";

    try {
      const changes: Change[] = JSON.parse(log.changes);
      const commentChange = changes.find(
        (change) => change.field === "comment" && change.change_type === actionType,
      );
      if (commentChange) {
        const value = actionType === "created" ? commentChange.new_value : commentChange.old_value;
        return `${log.username} ${actionVerb} a comment: "${value}" ${preposition} this dataset`;
      }
      return `${log.username} ${actionVerb} a comment ${preposition} this ${log.entity_type}.`;
    } catch (error) {
      return `${log.username} ${actionVerb} a comment ${preposition} this ${log.entity_type}, but details were not recognized.`;
    }
  }

  private formatHarvesterChanges(change: Change, log: ResourceActivityLog): string {
    const { change_type, source_instance, outcome, error_message, new_value } = change;

    if (change_type === "external_import") {
      if (outcome === "success") {
        return `Dataset imported from ${source_instance}.`;
      } else {
        return `Failed to import from ${source_instance}: ${error_message || "Unknown error"}`;
      }
    }

    if (change_type === "external_status_sync") {
      return `Status changed to '${new_value}' (synced from ${source_instance}).`;
    }

    return `External action performed on this ${log.entity_type}.`;
  }
}

export class PolicyActionFormatter implements LogFormatter {
  // @ts-expect-error context' is declared but its value is never read.
  formatMessage(log: ResourceActivityLog, context: LogFormatterContext): string | null {
    switch (log.action_type.toLowerCase()) {
      case "create":
        return this.formatPolicyActionCreated(log);

      case "delete":
        return this.formatPolicyActionDeleted(log);

      case "batch_update":
        return this.formatPolicyActionBatchUpdate(log);

      default:
        return `${log.username} performed an action on policy actions.`;
    }
  }

  private formatPolicyActionBatchUpdate(log: ResourceActivityLog): string {
    try {
      const changes: Change[] = JSON.parse(log.changes);
      const addedActions: { type: string; constraint: string; distribution: string }[] = [];
      const removedActions: { type: string; constraint: string; distribution: string }[] = [];
      const updatedActions: { type: string; constraint: string; distribution: string }[] = [];

      changes.forEach((change: Change) => {
        if (
          change.change_type === "created" &&
          change.new_value &&
          change.field === "policy_action"
        ) {
          const { policy_action_type, policy_constraint_type, distribution_title } =
            change.new_value;
          addedActions.push({
            type: policy_action_type,
            constraint: policy_constraint_type,
            distribution: distribution_title || "unknown distribution",
          });
        } else if (
          change.change_type === "deleted" &&
          change.old_value &&
          change.field === "policy_action"
        ) {
          const { policy_action_type, policy_constraint_type, distribution_title } =
            change.old_value;
          removedActions.push({
            type: policy_action_type,
            constraint: policy_constraint_type,
            distribution: distribution_title || "unknown distribution",
          });
        } else if (
          change.change_type === "updated" &&
          change.new_value &&
          change.field === "policy_action"
        ) {
          const { policy_action_type, policy_constraint_type, distribution_title } =
            change.new_value;
          updatedActions.push({
            type: policy_action_type,
            constraint: policy_constraint_type,
            distribution: distribution_title || "unknown distribution",
          });
        }
      });
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const distributionGroups: Map<string, { added: any[]; removed: any[]; updated: any[] }> =
        new Map();

      addedActions.forEach((action) => {
        if (!distributionGroups.has(action.distribution)) {
          distributionGroups.set(action.distribution, { added: [], removed: [], updated: [] });
        }
        distributionGroups.get(action.distribution)!.added.push(action);
      });

      removedActions.forEach((action) => {
        if (!distributionGroups.has(action.distribution)) {
          distributionGroups.set(action.distribution, { added: [], removed: [], updated: [] });
        }
        distributionGroups.get(action.distribution)!.removed.push(action);
      });

      updatedActions.forEach((action) => {
        if (!distributionGroups.has(action.distribution)) {
          distributionGroups.set(action.distribution, { added: [], removed: [], updated: [] });
        }
        distributionGroups.get(action.distribution)!.updated.push(action);
      });

      const messages: string[] = [];
      distributionGroups.forEach((actions, distributionTitle) => {
        const distributionInfo = ` on distribution "${distributionTitle}"`;
        const actionParts: string[] = [];

        if (actions.added.length > 0) {
          const permissionCount = actions.added.filter((a) => a.type === "permission").length;
          const prohibitionCount = actions.added.filter((a) => a.type === "prohibition").length;

          const addedParts: string[] = [];
          if (permissionCount > 0) {
            addedParts.push(`${permissionCount} permission${permissionCount > 1 ? "s" : ""}`);
          }
          if (prohibitionCount > 0) {
            addedParts.push(`${prohibitionCount} prohibition${prohibitionCount > 1 ? "s" : ""}`);
          }

          actionParts.push(`added ${addedParts.join(" and ")}`);
        }

        if (actions.updated.length > 0) {
          const permissionCount = actions.updated.filter((a) => a.type === "permission").length;
          const prohibitionCount = actions.updated.filter((a) => a.type === "prohibition").length;

          const updatedParts: string[] = [];
          if (permissionCount > 0) {
            updatedParts.push(`${permissionCount} permission${permissionCount > 1 ? "s" : ""}`);
          }
          if (prohibitionCount > 0) {
            updatedParts.push(`${prohibitionCount} prohibition${prohibitionCount > 1 ? "s" : ""}`);
          }

          actionParts.push(`updated ${updatedParts.join(" and ")}`);
        }

        if (actions.removed.length > 0) {
          const permissionCount = actions.removed.filter((a) => a.type === "permission").length;
          const prohibitionCount = actions.removed.filter((a) => a.type === "prohibition").length;

          const removedParts: string[] = [];
          if (permissionCount > 0) {
            removedParts.push(`${permissionCount} permission${permissionCount > 1 ? "s" : ""}`);
          }
          if (prohibitionCount > 0) {
            removedParts.push(`${prohibitionCount} prohibition${prohibitionCount > 1 ? "s" : ""}`);
          }
          actionParts.push(`removed ${removedParts.join(" and ")}`);
        }

        if (actionParts.length > 0) {
          messages.push(`${actionParts.join(", ")}${distributionInfo}`);
        }
      });

      if (messages.length === 0) {
        return `${log.username} updated policy actions.`;
      }

      const actionsText = messages.join(" and ");
      return `${log.username} ${actionsText}.`;
    } catch (error) {
      return `${log.username} updated policy actions, but details were not recognized.`;
    }
  }

  private formatPolicyActionCreated(log: ResourceActivityLog): string {
    try {
      const changes: Change[] = JSON.parse(log.changes);
      const change = changes.find((c) => c.change_type === "created");

      if (change?.new_value) {
        const { policy_action_type, policy_constraint_type, distribution_title } = change.new_value;
        const actionType = this.getActionTypeLabel(policy_action_type);
        const distributionInfo = distribution_title
          ? ` to distribution "${distribution_title}"`
          : "";

        return `${log.username} added ${actionType} "${policy_constraint_type}"${distributionInfo}.`;
      }

      return `${log.username} added a new policy action.`;
    } catch (error) {
      return `${log.username} added a new policy action, but details were not recognized.`;
    }
  }

  private formatPolicyActionDeleted(log: ResourceActivityLog): string {
    try {
      const changes: Change[] = JSON.parse(log.changes);
      const change = changes.find((c) => c.change_type === "deleted");

      if (change?.old_value) {
        const { policy_action_type, policy_constraint_type, distribution_title } = change.old_value;
        const actionType = this.getActionTypeLabel(policy_action_type);
        const distributionInfo = distribution_title
          ? ` from distribution "${distribution_title}"`
          : "";

        return `${log.username} removed ${actionType} "${policy_constraint_type}"${distributionInfo}.`;
      }

      return `${log.username} removed a policy action.`;
    } catch (error) {
      return `${log.username} removed a policy action, but details were not recognized.`;
    }
  }

  private getActionTypeLabel(policyActionType: string): string {
    return `policy action "${policyActionType}"`;
  }
}
