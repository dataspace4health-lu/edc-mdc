import { ChatBubbleLeftIcon, ArrowTopRightOnSquareIcon } from "@heroicons/react/24/solid";
import { statusDisplayNames } from "../utils/DatasetFieldDisplayName";
import { ResourceDatasetType } from "../types";
import AuthenticSourceIcon from "./AuthenticSourceIcon";
import { getDatasetStatusColor } from "../utils/DatasetStatusColors";
import Tooltip from "./Tooltip";
import { useUIConfig } from "../context/UIConfigContext";

interface DatasetStatusProps {
  dataset: ResourceDatasetType;
  hideAuthenticSourceIcon?: boolean;
}

export default function DatasetStatus(props: Readonly<DatasetStatusProps>) {
  const { dataset, hideAuthenticSourceIcon } = props;
  const { config } = useUIConfig();
  const color = getDatasetStatusColor(dataset.status);
  const status = dataset.status;
  const commentsCount = dataset.comments_count;
  const isImported = dataset.source_dataset_id !== null && dataset.source_dataset_id !== undefined;

  // Build source URL from config
  const sourceUrl =
    isImported && config?.source_instance_url && config?.source_dataset_url_pattern
      ? `${config.source_instance_url}${config.source_dataset_url_pattern.replace("{id}", dataset.source_dataset_id?.toString() || "")}`
      : null;

  return (
    <div className='flex items-center space-x-1'>
      <div
        className={`h-7 text-black text-center flex items-center justify-center rounded text-xs px-3 py-1 ${color}`}
      >
        {statusDisplayNames[status] || status}
      </div>
      {isImported && sourceUrl && (
        <Tooltip text='View source dataset'>
          <a
            href={sourceUrl}
            target='_blank'
            rel='noopener noreferrer'
            className='h-7 text-white bg-lnds-green hover:bg-lnds-dark-blue text-center flex items-center justify-center rounded text-xs px-3 py-1 transition-colors'
          >
            <ArrowTopRightOnSquareIcon className='h-4 w-4 mr-1' />
            <span className='font-medium'>Source</span>
          </a>
        </Tooltip>
      )}
      {commentsCount > 0 && (
        <div className='relative'>
          <ChatBubbleLeftIcon className='h-6 w-6 text-lnds-gray dark:text-lnds-light-gray' />
          <span className='absolute right-0 top-0 inline-flex -translate-y-1/2 translate-x-1/2 transform items-center justify-center rounded-full bg-lnds-lightest-gray px-2 py-1 text-xs font-bold leading-none text-lnds-gray'>
            {commentsCount || 0}
          </span>
        </div>
      )}
      {!hideAuthenticSourceIcon && <AuthenticSourceIcon dataset={dataset} />}
    </div>
  );
}
