import { useState } from "react";
import { Button, Card, CardHeading, useAlert } from "@lnds-lu/design-system";
import { CloudIcon, DocumentIcon, ArrowPathIcon, ClockIcon } from "@heroicons/react/24/solid";
import client from "../../zodiosClient/client";
import { FrontOfficeFileInfo } from "../../types";
import { DateUtils } from "../../utils/dateTimeHelpers";
import { appAlerts } from "../../utils/appAlerts";
import { usePageTitle } from "../../hooks/usePageTitle";

export default function FrontOfficeDirectory() {
  usePageTitle("Front Office Directory");
  const [files, setFiles] = useState<FrontOfficeFileInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);
  const { setAlert } = useAlert();

  const fetchFiles = async () => {
    setIsLoading(true);
    try {
      const files = await client.list_front_office_files_api_v1_front_office_files_get({
        withCredentials: true,
      });
      setFiles(files || []);
      setHasLoaded(true);
      setAlert(appAlerts.frontOfficeFilesLoaded(files.length || 0));
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
      console.error("Failed to fetch front office files:", error);
      setAlert(
        appAlerts.genericValidationError(
          error.response?.data?.detail || appAlerts.failedToFetchFrontOfficeFiles().message,
        ),
      );
    } finally {
      setIsLoading(false);
    }
  };

  const formatFileSize = (bytes: number | null) => {
    if (!bytes) return "Unknown";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <Card className='my-6 p-8 mx-6  max-w-2xl lg:max-w-4xl md:mx-auto'>
      <CardHeading label='Front Office Directory' Icon={CloudIcon} className='mb-4' />

      <div className='flex justify-between items-center mb-4'>
        <div className='text-sm text-lnds-color'>
          {hasLoaded && (
            <span>
              {files.length} {files.length === 1 ? "file" : "files"} found on server
            </span>
          )}
        </div>
        <Button
          label={hasLoaded ? "Refresh Files" : "Fetch Files"}
          Icon={hasLoaded ? ArrowPathIcon : CloudIcon}
          onClick={fetchFiles}
          className='flex items-center space-x-2'
          isLoading={isLoading}
        />
      </div>

      {isLoading && (
        <div className='flex justify-center items-center h-48'>
          <div className='text-center'>
            <p className='mt-2 text-lnds-color'>Connecting to front office server...</p>
          </div>
        </div>
      )}

      {!isLoading && hasLoaded && files.length === 0 && (
        <div className='text-center py-12'>
          <CloudIcon className='w-16 h-16 mx-auto text-gray-400 mb-4' />
          <h3 className='text-lg font-medium text-lnds-color mb-2'>No Files Found</h3>
          <p className='text-lnds-color'>The front office server directory appears to be empty.</p>
        </div>
      )}

      {!isLoading && hasLoaded && files.length > 0 && (
        <div className='space-y-3'>
          {files.map((file, index) => (
            <div key={index} className='border rounded-lg p-4 transition-colors border-lnds-color'>
              <div className='flex items-start justify-between'>
                <div className='flex items-start space-x-3 flex-1'>
                  <DocumentIcon className='w-6 h-6 text-lnds-color flex-shrink-0 mt-1' />
                  <div className='flex-1 min-w-0'>
                    <div className='flex items-center space-x-2 mb-1'>
                      <h4 className='text-sm font-medium text-lnds-color truncate'>
                        {file.filename}
                      </h4>
                    </div>

                    <p className='text-xs text-lnds-color mb-2 truncate'>{file.remote_path}</p>

                    <div className='flex items-center space-x-4 text-xs text-lnds-color'>
                      {file.size_bytes && (
                        <div className='flex items-center space-x-1'>
                          <DocumentIcon className='w-3 h-3' />
                          <span>{formatFileSize(file.size_bytes)}</span>
                        </div>
                      )}
                      {file.modified_time && (
                        <div className='flex items-center space-x-1'>
                          <ClockIcon className='w-3 h-3' />
                          <span>{DateUtils.formatDateTime(file.modified_time)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {!hasLoaded && !isLoading && (
        <div className='text-center py-12'>
          <CloudIcon className='w-16 h-16 mx-auto text-lnds-color mb-4' />
          <h3 className='text-lg font-medium text-lnds-color mb-2'>Front Office File Explorer</h3>
          <p className='text-lnds-color mb-4'>
            Click "Fetch Files" to view all files currently stored on the front office server.
          </p>
        </div>
      )}
    </Card>
  );
}
