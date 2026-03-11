import React from "react";
import { Button } from "@lnds-lu/design-system";
import { ArrowUturnLeftIcon } from "@heroicons/react/24/solid";
import { Link } from "react-router-dom";
import { ResourceDatasetType, DatasetStatusEnum } from "../types";
import VersionChangeTypeLabel from "./VersionChangeTypeLabel";

interface DatasetVersionInfoProps {
  dataset?: ResourceDatasetType;
  setCurrentTab: (tab: string) => void;
}

const DatasetVersionInfo: React.FC<DatasetVersionInfoProps> = ({ dataset, setCurrentTab }) => {
  if (!dataset) return null;

  const previousVersionDatasetId = dataset.previous_version_dataset_id;
  const latestVersionDatasetId = dataset.latest_version_dataset_id;

  if (latestVersionDatasetId && dataset.status === DatasetStatusEnum.DEPRECATED) {
    return (
      <div className='px-6 py-4 font-semibold bg-orange-50 dark:bg-orange-900/20 dark:border-orange-800 dark:text-white border border-orange-200 rounded-md'>
        <p>
          This dataset is deprecated. A{" "}
          <Link
            to={`/?datasetId=${latestVersionDatasetId}`}
            className='underline hover:text-lnds-dark-blue hover:dark:text-lnds-dark-blue'
            target='_blank'
          >
            newer version
          </Link>{" "}
          is available.
        </p>
      </div>
    );
  }

  if (previousVersionDatasetId) {
    return (
      <div className='px-6 py-4 font-semibold bg-blue-50 dark:bg-blue-900/20 dark:border-blue-800 dark:text-white border border-blue-200 rounded-md'>
        <div className='flex items-center justify-between gap-2'>
          <p>
            This dataset is a version of a{" "}
            <Link
              to={`/?datasetId=${previousVersionDatasetId}`}
              className='underline hover:text-lnds-dark-blue hover:dark:text-lnds-dark-blue'
              target='_blank'
            >
              previous dataset
            </Link>
          </p>
          <Button
            label='View Changes'
            Icon={ArrowUturnLeftIcon}
            btnType='transparent'
            className='hover:bg-lnds-dark-blue'
            onClick={() => setCurrentTab("Versions")}
          />
        </div>
        <p className='mt-1'>
          <VersionChangeTypeLabel versionChangeType={dataset.version_change_type} />
        </p>
      </div>
    );
  }

  return null;
};

export default DatasetVersionInfo;
