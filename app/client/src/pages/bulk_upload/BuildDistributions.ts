import client from "../../zodiosClient/client";
import { DistributionFormInputs, toDistributionDTO } from "../distributions/dto";

export async function submitDistributions(
  datasetId: number,
  distributions: DistributionFormInputs[],
  datasetTitle: string,
  logCallback?: (message: string) => void,
): Promise<string[]> {
  const errors: string[] = [];

  if (!distributions || distributions.length === 0) {
    return errors;
  }

  if (logCallback) {
    logCallback(`    Adding ${distributions.length} distribution(s)`);
  }

  for (const distribution of distributions) {
    try {
      const dto = toDistributionDTO(distribution);
      await client.add_distribution_api_v1_datasets__dataset_id__distributions_post(dto, {
        params: { dataset_id: datasetId },
        withCredentials: true,
      });

      if (logCallback) {
        logCallback(`      ✓ Added distribution: "${distribution.title}"`);
      }
    } catch (err) {
      const backendDetail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "";
      const errorMsg = backendDetail
        ? `Failed to add distribution "${distribution.title}" to dataset "${datasetTitle}": ${backendDetail}`
        : `Failed to add distribution "${distribution.title}" to dataset "${datasetTitle}"`;
      errors.push(errorMsg);
      if (logCallback) {
        logCallback(`      ✗ ${errorMsg}`);
      }
    }
  }

  return errors;
}
