import { ResourceActivityLog } from "../../types";

interface Change {
  field: string;
  change_type: string;
  old_value?: unknown;
  new_value?: unknown;
}

export const formatDataDictionaryReorder = (log: ResourceActivityLog): string => {
  try {
    const changes: Change[] = JSON.parse(log.changes);
    const orderChange = changes.find((change) => change.change_type === "order_changed");

    if (orderChange?.field === "data_dictionaries.position") {
      return `${log.username} reordered the data dictionary entries in this dataset.`;
    }

    return `${log.username} reordered items in this ${log.entity_type}.`;
  } catch (error) {
    return `${log.username} reordered items in this ${log.entity_type}.`;
  }
};
