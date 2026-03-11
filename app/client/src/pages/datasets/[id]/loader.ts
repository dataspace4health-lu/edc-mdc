import client from "../../../zodiosClient/client";
import { ResourceDatasetType } from "../../../types";

export const datasetLoader = async (
  datasetId: number,
): Promise<ResourceDatasetType | undefined> => {
  const dataset = await client.retrieve_dataset_api_v1_datasets__dataset_id__get({
    params: { dataset_id: datasetId },
    withCredentials: true,
  });

  return dataset;
};
