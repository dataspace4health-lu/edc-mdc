import { useState, useRef, useEffect } from "react";
import { appAlerts } from "../utils/appAlerts";
import {
  EllipsisVerticalIcon,
  PencilSquareIcon,
  TrashIcon,
  XMarkIcon,
  ArrowDownTrayIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from "@heroicons/react/24/solid";
import { DocumentDuplicateIcon } from "@heroicons/react/24/outline";
import { Link } from "react-router-dom";
import { ResourceDatasetType, DatasetStatusEnum } from "../types";
import { useAuth } from "../context/AuthContext";
import { useDatasets } from "../context/DatasetsContext";
import { useNavigate } from "react-router-dom";
import { useAlert, Button } from "@lnds-lu/design-system";
import client from "../zodiosClient/client";
import { isAxiosError } from "axios";
import Tooltip from "./Tooltip";
import { VersionChangeType, VersionChangeTypeModal } from "./Modals/VersionChangeTypeModal";

interface DatasetActionsDropdownProps {
  dataset: ResourceDatasetType;
}

const DatasetActionsDropdown = (props: Readonly<DatasetActionsDropdownProps>) => {
  const { dataset } = props;
  const { setAlert } = useAlert();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showVersionTypeModal, setShowVersionTypeModal] = useState(false);
  const [showDownloadOptions, setShowDownloadOptions] = useState(false);
  const dropdownRef = useRef(null);
  const { removeDataset } = useDatasets();

  const isImported =
    dataset?.source_dataset_id !== null && dataset?.source_dataset_id !== undefined;

  const canDelete =
    user?.permissions.includes("datasets:delete:draft") ||
    (user?.permissions.includes("datasets:delete:draft:my") && dataset.user_id === user?.id) ||
    (user?.permissions.includes("datasets:delete:draft:organisation") &&
      dataset.publisher_id === user?.current_organisation?.id);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      // @ts-expect-error Property 'contains' does not exist on type 'never'.
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
        setShowDownloadOptions(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleCloneDataset = async () => {
    const clonedDataset = await client.clone_dataset_api_v1_datasets__dataset_id__clone_post(
      undefined,
      {
        params: { dataset_id: dataset.id },
        withCredentials: true,
      },
    );
    setAlert(appAlerts.datasetCloned());
    setTimeout(() => {
      navigate(`/datasets/${clonedDataset.id}/edit`);
    }, 500);
  };

  const handleDatasetVersion = async (versionChangeType: VersionChangeType) => {
    const DatasetNewVersion =
      await client.create_dataset_version_api_v1_datasets__dataset_id__version_post(
        { version_change_type: versionChangeType },
        {
          params: { dataset_id: dataset.id },
          withCredentials: true,
        },
      );
    setAlert(appAlerts.datasetVersionCreated());
    setShowVersionTypeModal(false);
    setTimeout(() => {
      navigate(`/datasets/${DatasetNewVersion.id}/edit`);
    }, 500);
  };

  const handleDeleteDataset = async () => {
    try {
      await client.delete_dataset_api_v1_datasets__dataset_id__delete(undefined, {
        params: { dataset_id: dataset.id },
        withCredentials: true,
      });
      removeDataset(dataset.id);
      setShowDeleteConfirm(false);
      setIsOpen(false);
      setAlert(appAlerts.datasetDeleted());
    } catch (error) {
      if (isAxiosError(error)) {
        // @ts-expect-error error response structure
        setAlert(appAlerts.genericValidationError(error.response.data.detail));
      } else {
        setAlert(appAlerts.datasetDeleteFailed());
      }
    }
  };

  const getDownloadUrl = (format: string) => {
    return `/api/v1/datasets/${dataset.id}/download?format=${format}`;
  };

  return (
    <div className='relative text-base' ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className='p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors'
      >
        <EllipsisVerticalIcon className='h-6 w-6 icon-lnds-color' />
      </button>

      {isOpen && (
        <div className='absolute right-0 mt-2 w-48 z-50 py-2 section-lnds-color border border-lnds-color'>
          {dataset.status === DatasetStatusEnum.DRAFT && (
            <Link
              to={`/datasets/${dataset.id}/edit`}
              className='w-full text-left px-4 py-2 hover:bg-lnds-dark-blue hover:text-white flex items-center'
              onClick={() => setIsOpen(false)}
            >
              <PencilSquareIcon className='h-4 w-4 mr-2' />
              Edit
            </Link>
          )}
          {dataset.status === DatasetStatusEnum.PUBLISHED && (
            <Tooltip
              className='w-full'
              text={
                isImported
                  ? "Imported datasets are read-only"
                  : dataset.has_versions
                    ? "A newer version already exists for this dataset"
                    : ""
              }
            >
              <button
                onClick={() => {
                  if (isImported || dataset.has_versions) return;
                  setShowVersionTypeModal(true);
                  setIsOpen(false);
                }}
                disabled={isImported || dataset.has_versions}
                className={`w-full text-left px-4 py-2 flex items-center ${
                  isImported || dataset.has_versions
                    ? "opacity-50 cursor-not-allowed text-lnds-gray"
                    : "hover:bg-lnds-dark-blue hover:text-white"
                }`}
              >
                <DocumentDuplicateIcon className='h-4 w-4 mr-2' />
                Create a Version
              </button>
            </Tooltip>
          )}
          <Tooltip className='w-full' text={isImported ? "Imported datasets are read-only" : ""}>
            <button
              onClick={() => {
                if (isImported) return;
                handleCloneDataset();
                setIsOpen(false);
              }}
              disabled={isImported}
              className={`w-full text-left px-4 py-2 flex items-center ${
                isImported
                  ? "opacity-50 cursor-not-allowed text-lnds-gray"
                  : "hover:bg-lnds-dark-blue hover:text-white"
              }`}
            >
              <DocumentDuplicateIcon className='h-4 w-4 mr-2' />
              Duplicate
            </button>
          </Tooltip>
          <div className='w-full'>
            <button
              onClick={() => setShowDownloadOptions(!showDownloadOptions)}
              className='w-full text-left px-4 py-2 hover:bg-lnds-dark-blue hover:text-white flex items-center justify-between'
            >
              <div className='flex items-center'>
                <ArrowDownTrayIcon className='h-4 w-4 mr-2' />
                Download RDF
              </div>
              {showDownloadOptions ? (
                <ChevronUpIcon className='h-3 w-3' />
              ) : (
                <ChevronDownIcon className='h-3 w-3' />
              )}
            </button>

            {/* Accordion content */}
            {showDownloadOptions && (
              <div className=''>
                <Link
                  to={getDownloadUrl("rdf")}
                  onClick={() => setIsOpen(false)}
                  className='w-full text-left px-4 py-2 block hover:bg-lnds-dark-blue hover:text-white text-sm'
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  RDF/XML
                </Link>

                <Link
                  to={getDownloadUrl("ttl")}
                  onClick={() => setIsOpen(false)}
                  className='w-full text-left px-4 py-2 block hover:bg-lnds-dark-blue hover:text-white text-sm'
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Turtle (TTL)
                </Link>

                <Link
                  to={getDownloadUrl("jsonld")}
                  onClick={() => setIsOpen(false)}
                  className='w-full text-left px-4 py-2 block hover:bg-lnds-dark-blue hover:text-white text-sm'
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  JSON-LD
                </Link>
              </div>
            )}
          </div>
          {dataset.status === DatasetStatusEnum.DRAFT && canDelete && (
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className='w-full text-left px-4 py-2 hover:bg-lnds-dark-blue hover:text-white flex items-center'
            >
              <TrashIcon className='h-4 w-4 mr-2' />
              Delete
            </button>
          )}
        </div>
      )}
      {isOpen && showDeleteConfirm && (
        <div className='absolute right-0 mt-2 w-64 z-50 py-4 px-4 section-lnds-color border border-lnds-color'>
          <p className='text-sm mb-3'>Are you sure you want to delete this dataset?</p>
          <div className='flex justify-end space-x-2'>
            <Button
              size='small'
              label='Cancel'
              Icon={XMarkIcon}
              btnType='secondary'
              onClick={() => setShowDeleteConfirm(false)}
            />
            <Button
              label='Delete'
              size='small'
              Icon={TrashIcon}
              btnType='danger'
              onClick={handleDeleteDataset}
            />
          </div>
        </div>
      )}
      {showVersionTypeModal && (
        <VersionChangeTypeModal
          isOpen={showVersionTypeModal}
          onClose={() => setShowVersionTypeModal(false)}
          onConfirm={handleDatasetVersion}
        />
      )}
    </div>
  );
};

export default DatasetActionsDropdown;
