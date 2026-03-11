import { useEffect, useState } from "react";
import { CloudArrowUpIcon, CheckCircleIcon, XCircleIcon } from "@heroicons/react/24/solid";
import { Modal } from "./Modal";
import { FrontOfficeUploadStatus, FrontOfficePublishingResult } from "../../types";

interface FrontOfficeUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  datasetTitle: string;
  uploadStatus: FrontOfficeUploadStatus;
  uploadResult?: FrontOfficePublishingResult | null;
  error?: string | null;
}

export function FrontOfficeUploadModal({
  isOpen,
  onClose,
  datasetTitle,
  uploadStatus,
  uploadResult,
  error,
}: FrontOfficeUploadModalProps) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (uploadStatus === FrontOfficeUploadStatus.UPLOADING) {
      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) return prev;
          return prev + Math.random() * 15; // NOSONAR: Math.random() is safe here - used only for UI progress bar animation, not for security purposes
        });
      }, 500);

      return () => clearInterval(interval);
    } else if (uploadStatus === FrontOfficeUploadStatus.SUCCESS) {
      setProgress(100);
    }
  }, [uploadStatus]);

  const renderContent = () => {
    switch (uploadStatus) {
      case FrontOfficeUploadStatus.UPLOADING:
        return (
          <div className='text-center py-8'>
            <CloudArrowUpIcon className='h-16 w-16 text-lnds-blue mx-auto mb-4' />
            <h3 className='text-lg font-medium text-lnds-color mb-2'>Publishing to Front Office</h3>
            <p className='text-sm mb-6'>Uploading "{datasetTitle}" to Front Office directory...</p>

            <div className='w-full bg-gray-200 rounded-full h-2 mb-4'>
              <div
                className='bg-lnds-blue h-2 rounded-full transition-all duration-300'
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        );

      case FrontOfficeUploadStatus.SUCCESS:
        return (
          <div className='text-center py-8'>
            <CheckCircleIcon className='w-20 h-20 text-lnds-green animate-bounce mx-auto mb-4' />
            <h3 className='text-lg font-medium text-lnds-color mb-2'>Successfully Uploaded!</h3>
            {uploadResult && (
              <div className='bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-4'>
                <div className='text-xs text-blue-700 dark:text-blue-400 space-y-1'>
                  <p>
                    <strong>Files Generated:</strong>
                  </p>
                  <ul className='list-disc list-inside ml-4 space-y-1'>
                    {uploadResult.files.map((file, index) => (
                      <li
                        key={index}
                        className={`flex items-center text-xs ${
                          file.publishing_status === "success" ? "text-lnds-green" : "text-lnds-red"
                        }`}
                      >
                        {file.publishing_status === "success" ? (
                          <CheckCircleIcon className='h-3 w-3 mr-1' />
                        ) : (
                          <XCircleIcon className='h-3 w-3 mr-1' />
                        )}
                        {file.filename || "Unknown file"}
                        {file.error && <span className='ml-2 text-red-500'>({file.error})</span>}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        );

      case FrontOfficeUploadStatus.ERROR:
        return (
          <div className='text-center py-8'>
            <XCircleIcon className='h-20 w-20 text-lnds-red mx-auto mb-4' />
            <h3 className='text-lg font-medium text-lnds-color mb-2'>Upload Failed</h3>
            <p className='text-sm mb-4'>
              Failed to upload "{datasetTitle}" to the Front Office Directory.
            </p>

            {error && (
              <div className='border border-lnds-red rounded-lg p-3 mb-4'>
                <p className='text-sm text-lnds-red'>{error}</p>
              </div>
            )}

            <p className='text-xs text-lnds-color'>
              Please try again or contact support if the problem persists.
            </p>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <Modal.Frame
      open={isOpen}
      onClose={uploadStatus !== FrontOfficeUploadStatus.UPLOADING ? onClose : () => {}}
    >
      <Modal.Head
        className='flex items-center'
        onClose={uploadStatus !== FrontOfficeUploadStatus.UPLOADING ? onClose : undefined}
      >
        <CloudArrowUpIcon className='h-6 w-6 mr-2 icon-lnds-color' />
        Front Office Upload
      </Modal.Head>
      <Modal.Body>{renderContent()}</Modal.Body>
    </Modal.Frame>
  );
}
