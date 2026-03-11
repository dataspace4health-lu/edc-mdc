import { useState, useRef, useEffect } from "react";
import { PlusIcon, CheckIcon } from "@heroicons/react/24/solid";
import AuthenticSourceLabelForm from "../authentic_sources/AuthenticSourceLabelForm";
import { ResourceAuthenticSourceLabel } from "../../types";

const AuthenticSourceDropdown = ({
  isOpen,
  onClose,
  labels,
  selectedLabelId,
  onLabelSelect,
  onCreateLabel,
  datasetId,
  datasetPreviousVersionId,
}: {
  isOpen: boolean;
  onClose: () => void;
  labels: ResourceAuthenticSourceLabel[];
  selectedLabelId?: number;
  onLabelSelect: (labelId: number) => void;
  onCreateLabel: (label: ResourceAuthenticSourceLabel) => void;
  datasetId: number;
  datasetPreviousVersionId: number | null | undefined;
}) => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        onClose();
        setShowCreateForm(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [isOpen, onClose]);

  const handleCreateLabel = (label: ResourceAuthenticSourceLabel) => {
    onCreateLabel(label);
    setShowCreateForm(false);
  };

  if (!isOpen) return null;

  return (
    <div
      ref={dropdownRef}
      className='absolute top-full left-0 right-0 z-50 mt-1 bg-white dark:bg-gray-800 border border-lnds-color rounded-lg shadow-lg max-h-72 overflow-y-auto min-w-80'
    >
      {!showCreateForm ? (
        <>
          <div className='p-2 space-y-1'>
            {labels.map((label: ResourceAuthenticSourceLabel) => (
              <button
                key={label.id}
                onClick={() => onLabelSelect(label.id)}
                className='w-full text-left px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md group'
              >
                <div className='flex items-center justify-between'>
                  <div className='flex-1 min-w-0'>
                    <div className='font-medium text-lnds-gray dark:text-lnds-lightest-gray truncate'>
                      {label.name}
                    </div>
                    <div className='text-xs text-gray-500 dark:text-gray-400 truncate'>
                      {label.description}
                    </div>
                    {label.dataset_id === datasetId && (
                      <div className='text-xs mt-1 text-lnds-green'>Current Dataset</div>
                    )}
                    {label.dataset_id && label.dataset_id === datasetPreviousVersionId && (
                      <a
                        href={`/?datasetId=${label.dataset_id}`}
                        target='_blank'
                        className='text-lnds-red hover:underline'
                        onClick={(e) => e.stopPropagation()}
                      >
                        Assigned to previous version
                      </a>
                    )}
                    {label.dataset_id !== datasetId &&
                      label.dataset_id !== datasetPreviousVersionId &&
                      label.dataset_title && (
                        <div className='text-xs mt-1'>
                          <div
                            className='flex items-center gap-1'
                            title={
                              label.dataset_is_deprecated ? "This dataset is deprecated" : undefined
                            }
                          >
                            <a
                              href={`/?datasetId=${label.dataset_id}`}
                              target='_blank'
                              className={`hover:underline ${
                                label.dataset_is_deprecated ? "text-gray-500" : "text-lnds-purple"
                              }`}
                              onClick={(e) => e.stopPropagation()}
                            >
                              Used in: {label.dataset_is_deprecated && "(deprecated) "}
                              {label.dataset_title}
                            </a>
                          </div>
                        </div>
                      )}
                    {!label.dataset_title && label.dataset_id !== datasetId && (
                      <div className='text-xs mt-1 text-lnds-blue'>Unassigned</div>
                    )}
                  </div>
                  {selectedLabelId === label.id && (
                    <CheckIcon className='h-4 w-4 text-lnds-blue flex-shrink-0 ml-2' />
                  )}
                </div>
              </button>
            ))}
          </div>

          <div className='border-t border-lnds-color p-2'>
            <button
              onClick={() => setShowCreateForm(true)}
              className='w-full flex items-center px-3 py-2 text-sm text-lnds-color hover:bg-lnds-dark-blue hover:text-white rounded-md'
            >
              <PlusIcon className='h-4 w-4 mr-2' />
              Create new label
            </button>
          </div>
        </>
      ) : (
        <AuthenticSourceLabelForm
          onCreate={handleCreateLabel}
          onCancel={() => setShowCreateForm(false)}
          isCondensed={true}
        />
      )}
    </div>
  );
};

export default AuthenticSourceDropdown;
