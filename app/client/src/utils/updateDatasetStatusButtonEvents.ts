import { useCallback } from "react";
import client from "../zodiosClient/client";
import { ResourceDatasetType, ResourceUserType } from "../types";
import { validateDatasetForCompletion } from "../pages/DatasetForm/completionValidation";
import { appAlerts, AppAlertPayload } from "./appAlerts";

interface UseOnTriggerParams {
  user: ResourceUserType | null;
  dataset: ResourceDatasetType;
  comment: string;
  setComment: (value: string) => void;
  updateDatasetLocally: (dataset: ResourceDatasetType) => void;
  updateDatasetStatusOnList: (id: number, status: string) => void;
  onCommentsRefresh: () => void;
  setAlert: (alert: AppAlertPayload) => void;
  updateSelectedTrigger: (trigger: string | null) => void;
  onFrontOfficeUploadStart: () => void;
  openNextSteps: (errors?: string[]) => void;
}

export function useOnTrigger({
  user,
  dataset,
  comment,
  setComment,
  updateDatasetLocally,
  updateDatasetStatusOnList,
  onCommentsRefresh,
  setAlert,
  updateSelectedTrigger,
  onFrontOfficeUploadStart,
  openNextSteps,
}: UseOnTriggerParams) {
  return useCallback(
    async (trigger: string | null) => {
      if (!trigger) return;

      try {
        const needsGroupManagerValidation =
          user?.feature_options.enable_validation_via_group_manager &&
          dataset.group_manager_ids?.length === 0 &&
          trigger === "complete";

        if (
          needsGroupManagerValidation &&
          dataset.group_manager_ids &&
          dataset.group_manager_ids.length === 0
        ) {
          setAlert(appAlerts.groupManagersRequiredBeforeComplete());
          updateSelectedTrigger(null);
          setComment("");
          return;
        }

        if (trigger === "complete") {
          const completionErrors = validateDatasetForCompletion(dataset, {
            enableHealthDcat:
              !!user?.feature_options?.enable_health_dcat &&
              Array.isArray(dataset.health_categories) &&
              dataset.health_categories.length > 0,
          });

          if (completionErrors.length > 0) {
            openNextSteps(completionErrors);
            updateSelectedTrigger(null);
            setComment("");
            return;
          }
        }

        const updatedDataset =
          await client.update_dataset_status_api_v1_datasets__dataset_id__status__status_trigger__post(
            comment ? { comment } : {},
            {
              params: { dataset_id: dataset.id, status_trigger: trigger },
              withCredentials: true,
            },
          );

        updateDatasetLocally(updatedDataset);
        updateDatasetStatusOnList(updatedDataset.id, updatedDataset.status);
        onCommentsRefresh();
        setAlert(appAlerts.datasetStatusUpdated(updatedDataset.status, dataset.status));
        updateSelectedTrigger(null);
        setComment("");

        if (
          (trigger === "publish" || trigger === "unpublish" || trigger === "deprecate") &&
          user?.feature_options.enable_upload_datasets_to_front_office
        ) {
          onFrontOfficeUploadStart();
        }

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } catch (err: any) {
        console.error(err);
        let message =
          err?.response?.data?.detail || err?.message || "Server error. Please try again later.";
        if (typeof message !== "string") {
          message = "Server error. Please try again later.";
        }
        if (err?.response?.status === 403) {
          message = "You do not have permission to perform this action.";
        }
        updateSelectedTrigger(null);
        setComment("");
        openNextSteps([message]);
      }
    },
    [
      user,
      dataset,
      comment,
      setComment,
      updateDatasetLocally,
      updateDatasetStatusOnList,
      onCommentsRefresh,
      setAlert,
      updateSelectedTrigger,
      onFrontOfficeUploadStart,
      openNextSteps,
    ],
  );
}
