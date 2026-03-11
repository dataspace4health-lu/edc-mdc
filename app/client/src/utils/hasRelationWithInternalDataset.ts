import { ResourceDatasetType } from "../types";

const hasRelationWithInternalDataset = (dataset: ResourceDatasetType) => {
  return dataset.source_relations?.some((r) => r.internal_only);
};

export default hasRelationWithInternalDataset;
