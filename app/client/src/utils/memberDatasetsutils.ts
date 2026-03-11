import { SeriesMembershipInfo } from "../types";

export const seriesMemberShipToDatasetIds = (seriesMembershipInfo: SeriesMembershipInfo[]) => {
  const sortedMembershipInfo = [...seriesMembershipInfo];
  sortedMembershipInfo.sort((a, b) => a.position - b.position);
  const datasetIds = sortedMembershipInfo.map((info) => info.dataset_id);
  return datasetIds;
};

export const datasetIdsToSeriesMembership = (datasetIds: string[]) => {
  const seriesMembershipInfo = datasetIds.map((datasetId, index) => ({
    dataset_id: parseInt(datasetId),
    position: index,
    is_first: index === 0,
    is_last: index === datasetIds.length - 1,
  }));
  return seriesMembershipInfo;
};
