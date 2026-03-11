import client from "../../zodiosClient/client";
import { ResourceDataDictionaryEntry, ResourceDatasetType } from "../../types";

export const fetchDataDictionaries = async (
  datasetId: number,
): Promise<ResourceDataDictionaryEntry[]> => {
  const response =
    await client.get_data_dictionaries_by_dataset_id_api_v1_datasets__dataset_id__data_dictionaries_get(
      {
        params: { dataset_id: datasetId },
        withCredentials: true,
      },
    );
  return response;
};

export const deleteDataDictionaryEntryById = async (datasetId: number, entryId: number) => {
  await client.delete_data_dictionary_entry_api_v1_datasets__dataset_id__data_dictionaries__entry_id__delete(
    undefined,
    {
      params: { dataset_id: datasetId, entry_id: entryId },
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

export const bulkUpdatePositions = async (
  datasetId: number,
  updates: { entry_id: number; position: number }[],
): Promise<ResourceDataDictionaryEntry[]> => {
  const response =
    await client.bulk_update_positions_api_v1_datasets__dataset_id__data_dictionaries_bulk_update_positions_post(
      { updates },
      {
        params: { dataset_id: datasetId },
        withCredentials: true,
      },
    );
  return response;
};
