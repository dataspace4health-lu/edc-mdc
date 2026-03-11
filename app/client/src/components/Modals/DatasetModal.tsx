import { useState, useEffect } from "react";
import { z } from "zod";
import {
  ClockIcon,
  XCircleIcon,
  ExclamationCircleIcon,
  RectangleStackIcon,
} from "@heroicons/react/24/solid";
import { clientWithoutValidation } from "../../zodiosClient/client";
import { schemas } from "../../zodiosClient/openapi.json.client";
import { useSearchParams } from "react-router-dom";
import { useAuthenticSourceLabels } from "../../context/AuthenticSourceLabelsContext";
import { Modal } from "./Modal";
import { LNDSLoader } from "../LNDSLoader";
import { DatasetDetails } from "./DatasetDetails";
import UpdateDatasetStatusButton from "../UpdateDatasetStatusButton";
import DatasetActionsDropdown from "../DatasetActionsDropdown";
import DatasetApprovalWorkflow from "../DatasetApprovalWorkflow";
import { FormType } from "../../types";
import InitialsAvatar from "../InitialsAvatar";
import { Tabs } from "./DatasetDetails";
import DatasetVersionInfo from "../DatasetVersionInfo";
import { FrontOfficeUploadModal } from "./FrontOfficeUploadModal";
import { useFrontOfficeUpload } from "../../hooks/useFrontOfficeUpload";

type Status = "loading" | "not_found" | "server_error" | "found";
type ResourceDatasetType = z.infer<typeof schemas.ResourceDataset>;

interface DatasetModalProps {
  formFields: FormType;
}

export function DatasetModal(props: Readonly<DatasetModalProps>) {
  const { formFields } = props;
  const [params, setParams] = useSearchParams();
  const [dataset, setDataset] = useState<ResourceDatasetType | null>(null);
  const [status, setStatus] = useState<Status>("loading");
  const [refreshComments, setRefreshComments] = useState(false);
  const [showApprovalWorkflow, setShowApprovalWorkflow] = useState(false);
  const [metadataAccuracyReviewed, setMetadataAccuracyReviewed] = useState(false);
  const [publicationDecisionMade, setPublicationDecisionMade] = useState(false);

  const handleResetApprovalWorkflow = () => {
    setMetadataAccuracyReviewed(false);
    setPublicationDecisionMade(false);
    setShowApprovalWorkflow(false);
  };

  const { reset } = useAuthenticSourceLabels();
  const {
    uploadStatus,
    uploadResult,
    error: frontOfficeError,
    uploadToFrontOffice,
    resetUpload,
  } = useFrontOfficeUpload();
  const [showFrontOfficeModal, setShowFrontOfficeModal] = useState(false);

  const fetchDatasetById = async (id: string) => {
    try {
      const dataset =
        await clientWithoutValidation.retrieve_dataset_api_v1_datasets__dataset_id__get({
          params: { dataset_id: parseInt(id) },
          withCredentials: true,
        });

      if (dataset) {
        setDataset(dataset);
      } else {
        setStatus("not_found");
      }
    } catch (error) {
      setStatus("server_error");
      console.error("An error occurred while fetching the dataset:", error);
    }
  };

  const defaultTab = dataset
    ? dataset.is_dataset_series
      ? Tabs.SERIES
      : Tabs.DATASET
    : Tabs.DATASET;
  const [currentTab, setCurrentTab] = useState<string>(defaultTab);

  const onCommentsRefresh = () => {
    setRefreshComments(true);
    setTimeout(() => setRefreshComments(false), 0);
  };

  useEffect(() => {
    const id = params.get("datasetId");
    if (id) {
      reset(); // Reset authentic source labels context
      const startTime = Date.now();
      fetchDatasetById(id).then(() => {
        const endTime = Date.now();
        const elapsedTime = endTime - startTime;
        const minLoadingTime = 500; // Adjust as necessary
        if (elapsedTime < minLoadingTime) {
          setTimeout(() => setStatus("found"), minLoadingTime - elapsedTime);
        } else {
          setStatus("found");
        }
      });
      setShowApprovalWorkflow(false);
      setMetadataAccuracyReviewed(false);
      setPublicationDecisionMade(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params]);

  const onClose = () => {
    params.delete("datasetId");
    setParams(params);
    setDataset(null);
    setStatus("loading");
  };

  const handleFrontOfficeUploadStart = async () => {
    if (!dataset) return;

    setShowFrontOfficeModal(true);
    await uploadToFrontOffice(dataset.id);
  };

  const handleFrontOfficeModalClose = () => {
    setShowFrontOfficeModal(false);
    resetUpload();
  };

  const isImported =
    dataset?.source_dataset_id !== null && dataset?.source_dataset_id !== undefined;

  const renderModalHead = () => {
    switch (status) {
      case "loading":
        return (
          <Modal.Head className='flex items-center text-lnds-color' onClose={onClose}>
            <ClockIcon className='h-5 w-5 md:w-7 md:h-7 mr-2 flex-shrink-0 ml-4' />
            Please Wait
          </Modal.Head>
        );
      case "not_found":
        return (
          <Modal.Head className='flex items-center text-lnds-red' onClose={onClose}>
            <XCircleIcon className='h-5 w-5 md:w-7 md:h-7 mr-2 flex-shrink-0 ml-4' />
            Not Found
          </Modal.Head>
        );
      case "server_error":
        return (
          <Modal.Head className='flex items-center text-lnds-red' onClose={onClose}>
            <ExclamationCircleIcon className='h-5 w-5 md:w-7 md:h-7 mr-2 flex-shrink-0 ml-4' />
            Server Error
          </Modal.Head>
        );
      case "found":
        return (
          <Modal.Head className='flex items-center justify-between' onClose={onClose}>
            <div className='flex items-center max-w-[70%]'>
              {dataset?.author_name && (
                <InitialsAvatar
                  name={dataset?.author_name}
                  showTooltip={true}
                  isImported={isImported}
                />
              )}
              <span className='ml-2 truncate'>{dataset?.title}</span>
            </div>
            <div className='flex items-center space-x-2'>
              {dataset?.is_dataset_series && (
                <div className='flex items-center text-lnds-purple text-sm'>
                  <RectangleStackIcon className='h-4 w-4 mr-1 shrink-0' />
                  <span className='font-medium hidden md:inline'>Series</span>
                </div>
              )}
              <DatasetActionsDropdown dataset={dataset!} />
            </div>
          </Modal.Head>
        );
      default:
        return null;
    }
  };

  const renderBody = () => {
    switch (status) {
      case "loading":
        return (
          <div className='flex items-center justify-center min-h-[500px]'>
            <LNDSLoader />
          </div>
        );
      case "not_found":
        return <p className='text-lnds-red'>Dataset not found.</p>;
      case "server_error":
        return (
          <p className='text-lnds-red'>
            Error occurred while fetching the dataset. Please try again.
          </p>
        );
      case "found":
        if (dataset && showApprovalWorkflow) {
          return (
            <DatasetApprovalWorkflow
              setMetadataAccuracyReviewed={setMetadataAccuracyReviewed}
              setPublicationDecisionMade={setPublicationDecisionMade}
            />
          );
        } else if (dataset) {
          return (
            <DatasetDetails
              dataset={dataset}
              formFields={formFields}
              refreshComments={refreshComments}
              currentTab={currentTab}
              setCurrentTab={setCurrentTab}
            />
          );
        }
        return null;
      default:
        return null;
    }
  };

  return (
    <Modal.Frame
      open={!!params.get("datasetId")}
      onClose={onClose}
      className='relative'
      containerClassName='w-[95vw] max-w-[1200px]'
    >
      {renderModalHead()}
      <Modal.Body>
        <div className='mb-3 -mt-3'>
          {status === "found" &&
            (dataset?.previous_version_dataset_id || dataset?.latest_version_dataset_id) && (
              <DatasetVersionInfo dataset={dataset} setCurrentTab={setCurrentTab} />
            )}
        </div>
        {renderBody()}
        {showFrontOfficeModal && (
          <FrontOfficeUploadModal
            isOpen={showFrontOfficeModal}
            onClose={handleFrontOfficeModalClose}
            datasetTitle={dataset?.title || ""}
            uploadStatus={uploadStatus}
            uploadResult={uploadResult}
            error={frontOfficeError}
          />
        )}
      </Modal.Body>
      {dataset && (
        <UpdateDatasetStatusButton
          dataset={dataset}
          updateDatasetLocally={setDataset}
          onCommentsRefresh={onCommentsRefresh}
          onFrontOfficeUploadStart={handleFrontOfficeUploadStart}
          setShowApprovalWorkflow={setShowApprovalWorkflow}
          metadataAccuracyReviewed={metadataAccuracyReviewed}
          publicationDecisionMade={publicationDecisionMade}
          onResetApprovalWorkflow={handleResetApprovalWorkflow}
        />
      )}
    </Modal.Frame>
  );
}
