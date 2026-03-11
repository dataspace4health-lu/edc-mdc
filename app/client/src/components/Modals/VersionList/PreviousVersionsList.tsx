import { ResourceDatasetType } from "../../../types";
import { formatDateTime, searchParams } from "./Utils";
import DatasetStatus from "../../DatasetStatus";

type PreviousVersionsListProps = {
  versions: ResourceDatasetType[];
  currentVersion: ResourceDatasetType;
};

const PreviousVersionsList = ({ versions, currentVersion }: PreviousVersionsListProps) => {
  const previousVersions = versions.slice(0, versions.length - 1).reverse();

  return (
    <div>
      <h2 className='text-lnds-gray dark:text-white font-extrabold text-lg mb-4'>
        Previous Versions
      </h2>

      <div className='border-2 border-lnds-purple p-5 rounded-lg bg-white dark:bg-lnds-gray/10 flex justify-between items-center mb-6'>
        <div className='text-sm font-semibold text-lnds-gray dark:text-lnds-lightest-gray flex items-center flex-wrap gap-x-2'>
          <span>
            Created:{" "}
            <span className='font-normal'>{formatDateTime(currentVersion.submitted_at)}</span>
          </span>
          {currentVersion.released_at && (
            <>
              <span>|</span>
              <span>
                Published:{" "}
                <span className='font-normal'>{formatDateTime(currentVersion.released_at)}</span>
              </span>
            </>
          )}
          <span className='ml-4'>
            <DatasetStatus dataset={currentVersion} />
          </span>
        </div>
        <div>
          <span className='bg-lnds-green/20 text-lnds-green px-3 py-1 rounded-full font-semibold text-sm select-none border border-lnds-green/20'>
            Current Version
          </span>
        </div>
      </div>

      <div className='space-y-4'>
        {previousVersions.map((version) => {
          const params = searchParams(version);
          return (
            <div
              key={version.id}
              className='border border-lnds-light-gray dark:border-lnds-gray rounded-lg bg-white dark:bg-lnds-gray/10 flex justify-between items-center p-4'
            >
              <div className='text-sm font-semibold text-lnds-gray dark:text-lnds-lightest-gray flex items-center flex-wrap gap-x-2'>
                <span>
                  Created:{" "}
                  <span className='font-normal'>{formatDateTime(version.submitted_at)}</span>
                </span>
                {version.released_at && (
                  <>
                    <span>|</span>
                    <span>
                      Published:{" "}
                      <span className='font-normal'>{formatDateTime(version.released_at)}</span>
                    </span>
                  </>
                )}
                <span className='ml-4'>
                  <DatasetStatus dataset={version} />
                </span>
              </div>
              <a
                href={`/?${params}`}
                target='_blank'
                rel='noopener noreferrer'
                className='text-lnds-gray dark:text-lnds-lightest-gray hover:text-lnds-dark-blue dark:hover:text-white hover:underline text-sm font-medium transition-colors'
              >
                View Version
              </a>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default PreviousVersionsList;
