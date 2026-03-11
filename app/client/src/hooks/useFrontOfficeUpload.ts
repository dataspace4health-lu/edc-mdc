import { useState, useCallback } from "react";
import client from "../zodiosClient/client";
import { FrontOfficeUploadStatus, FrontOfficePublishingResult } from "../types";

interface UseFrontOfficeUploadReturn {
  uploadStatus: FrontOfficeUploadStatus;
  uploadResult: FrontOfficePublishingResult | null;
  error: string | null;
  uploadToFrontOffice: (datasetId: number) => Promise<void>;
  resetUpload: () => void;
}

function mergeResults(res1: FrontOfficePublishingResult, res2: FrontOfficePublishingResult) {
  for (const file of res1.files) {
    res2.files.push(file);
  }
  return res2;
}

export function useFrontOfficeUpload(): UseFrontOfficeUploadReturn {
  const [uploadStatus, setUploadStatus] = useState<FrontOfficeUploadStatus>(
    FrontOfficeUploadStatus.IDLE,
  );
  const [uploadResult, setUploadResult] = useState<FrontOfficePublishingResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const uploadToFrontOffice = useCallback(async (datasetId: number) => {
    try {
      setUploadStatus(FrontOfficeUploadStatus.UPLOADING);
      setError(null);
      setUploadResult(null);

      const result =
        await client.publish_dataset_to_front_office_api_v1_datasets__dataset_id__publish_to_front_office_post(
          undefined,
          {
            params: { dataset_id: datasetId },
            withCredentials: true,
          },
        );

      const authSourceResult =
        await client.publish_authentic_source_to_front_office_api_v1_authentic_source_publish_to_front_office_post(
          undefined,
          {
            withCredentials: true,
          },
        );
      mergeResults(authSourceResult, result);
      setUploadResult(result);
      setUploadStatus(FrontOfficeUploadStatus.SUCCESS);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      console.error("FrontOffice upload failed:", err);

      let errorMessage = "Failed to upload to Front Office directory. Please try again.";

      if (err?.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err?.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);
      setUploadStatus(FrontOfficeUploadStatus.ERROR);
    }
  }, []);

  const resetUpload = useCallback(() => {
    setUploadStatus(FrontOfficeUploadStatus.IDLE);
    setUploadResult(null);
    setError(null);
  }, []);

  return {
    uploadStatus,
    uploadResult,
    error,
    uploadToFrontOffice,
    resetUpload,
  };
}
