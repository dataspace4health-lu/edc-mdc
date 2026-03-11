import { CircleStackIcon, LinkIcon } from "@heroicons/react/24/solid";
import { RelationsTypesOptions } from "../pages/Relations/dto";
import { twMerge } from "tailwind-merge";
import { getDatasetStatusColor } from "../utils/DatasetStatusColors";

interface RelationLinkProps {
  relationType: string;
  datasetTitle: string;
  status: string;
  datasetId: number;
  hasNewerVersion?: boolean;
  newerVersionId?: number;
  className?: string;
}
export default function RelationLink({
  relationType,
  datasetTitle,
  status,
  datasetId,
  hasNewerVersion,
  newerVersionId,
  className,
}: Readonly<RelationLinkProps>) {
  const formattedType = RelationsTypesOptions.find((op) => op.value === relationType)!.label;

  return (
    <span className={twMerge("flex flex-col", className)}>
      <span className='label-lnds-color text-lg flex items-center mb-2'>
        <LinkIcon className='h-5 w-5 mr-1' />
        <span>{formattedType}</span>
      </span>

      <div className='flex items-center justify-between w-full'>
        <div className='flex items-center space-x-3'>
          <a
            href={`/?datasetId=${datasetId}`}
            target='_blank'
            rel='noopener noreferrer'
            className='text-sm text-lnds-color underline break-all hover:text-lnds-dark-blue dark:hover:text-white flex items-center'
          >
            <CircleStackIcon className='h-4 w-4 mr-1' />
            {datasetTitle}
          </a>

          {hasNewerVersion && newerVersionId && (
            <a
              href={`/?datasetId=${newerVersionId}`}
              target='_blank'
              rel='noopener noreferrer'
              className='text-sm underline text-lnds-blue hover:text-lnds-dark-blue'
            >
              View Newer Version
            </a>
          )}
        </div>

        <div className='flex items-center justify-center w-40'>
          {status && (
            <div
              className={`h-7 text-black text-center flex items-center justify-center rounded text-xs px-3 py-1 ${getDatasetStatusColor(
                status,
              )}`}
            >
              {status}
            </div>
          )}
        </div>
      </div>
    </span>
  );
}
