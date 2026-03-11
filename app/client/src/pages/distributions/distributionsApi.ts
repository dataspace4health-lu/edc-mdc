import client from "../../zodiosClient/client";
import { ResourceDistributionType, ResourceDatasetType } from "../../types";

export const fetchDistributions = async (
  datasetId: number,
): Promise<ResourceDistributionType[]> => {
  const response =
    await client.get_distributions_by_dataset_id_api_v1_datasets__dataset_id__distributions_get({
      params: { dataset_id: datasetId },
      withCredentials: true,
    });
  return response;
};

export const deleteDistributionById = async (datasetId: number, distributionId: number) => {
  await client.delete_distribution_api_v1_datasets__dataset_id__distributions__distribution_id__delete(
    undefined,
    {
      params: { dataset_id: datasetId, distribution_id: distributionId },
      withCredentials: true,
    },
  );
};

export const getDataset = async (datasetId: number): Promise<ResourceDatasetType | undefined> => {
  const dataset = await client.retrieve_dataset_api_v1_datasets__dataset_id__get({
    params: { dataset_id: datasetId },
    withCredentials: true,
  });

  return dataset;
};
