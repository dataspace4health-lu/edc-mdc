import { useState, useRef, useEffect } from "react";
import { InformationCircleIcon, XMarkIcon } from "@heroicons/react/24/solid";
import { Link } from "react-router-dom";
import { ResourceDatasetType } from "../types";

interface NextStepsButtonProps {
  dataset: ResourceDatasetType;
  forceOpenSignal?: number;
  forcedErrors?: string[];
}

export default function NextStepsButton({
  dataset,
  forceOpenSignal,
  forcedErrors = [],
}: Readonly<NextStepsButtonProps>) {
  const [isOpen, setIsOpen] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [isErrorMode, setIsErrorMode] = useState(false);
  const dropdownRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  const getNextStepDescription = (trigger: string) => {
    const descriptions: Record<string, string> = {
      complete:
        "Submit your dataset for validation. The users with the permission to validate will be notified to review it.",
      back_to_draft:
        "Revert the dataset back to draft status for further edits. The original submitter will be notified about this change.",
      validate:
        "Validate the dataset's metadata and structure. It will then be ready for approval and the approvers will be notified.",
      approve:
        "Approve the dataset for publication. It will then be ready for publication and the publishers will be notified.",
      mark_internal: "Mark this dataset as internal-only. It will not be available for publishing.",
      restore_approved:
        "Restore the dataset to approved status. It will then be ready for publication and the publishers will be notified.",
      publish:
        "Publish the dataset. The contact points of this dataset along with other relevant users will be notified.",
      unpublish: "Remove the dataset from the publication while keeping it approved.",
      deprecate: "Mark the dataset as deprecated, indicating it's no longer actively maintained.",
    };
    return descriptions[trigger] || "Perform this action on the dataset.";
  };

  const getAwaitingStatusMessage = (status: string) => {
    const messages: Record<string, { title: string; description: string }> = {
      COMPLETED: {
        title: "Awaiting Validation",
        description:
          "This dataset is awaiting validation. Users with permission to validate have been notified.",
      },
      VALIDATED: {
        title: "Awaiting Approval",
        description:
          "This dataset is awaiting approval. Users with permission to approve have been notified.",
      },
      APPROVED: {
        title: "Awaiting Publication",
        description:
          "This dataset is awaiting publication. Users with permission to publish have been notified.",
      },
    };
    return messages[status] || null;
  };

  const showDataDictionaryReminder =
    dataset?.status === "DRAFT" && dataset?.total_dictionaries === 0;

  const showRelationsReminder = dataset?.status === "DRAFT" && dataset?.total_relations === 0;
  const hasNextSteps =
    forcedErrors.length > 0 ||
    (dataset?.status_triggers && dataset.status_triggers.length > 0) ||
    getAwaitingStatusMessage(dataset?.status || "") ||
    showDataDictionaryReminder ||
    showRelationsReminder;

  const handleClose = () => {
    setIsClosing(true);
    setTimeout(() => {
      setIsOpen(false);
      setIsClosing(false);
      setIsAnimating(false);
      setIsErrorMode(false);
    }, 300); // Match animation duration
  };

  useEffect(() => {
    if (isOpen) {
      // Trigger slide-in animation after mount
      requestAnimationFrame(() => {
        setIsAnimating(true);
      });
    }
  }, [isOpen]);

  useEffect(() => {
    if (!forceOpenSignal) {
      return;
    }

    setIsErrorMode(true);
    setIsClosing(false);
    setIsOpen(true);
  }, [forceOpenSignal]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Node;
      const clickedButton = !!dropdownRef.current?.contains(target);
      const clickedPanel = !!panelRef.current?.contains(target);

      if (!clickedButton && !clickedPanel) {
        handleClose();
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  if (!hasNextSteps) {
    return null;
  }

  return (
    <>
      {/* Icon button */}
      <button
        ref={dropdownRef}
        onClick={() => {
          if (isOpen) {
            handleClose();
          } else {
            setIsErrorMode(false);
            setIsOpen(true);
          }
        }}
        className='flex items-center justify-center h-10 w-10 rounded border border-lnds-color text-lnds-color hover:bg-lnds-green/5 transition-all group'
        title='View next steps'
      >
        <InformationCircleIcon className='h-5 w-5 group-hover:scale-110 transition-transform' />
      </button>

      {/* Slide-out panel */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className={`left-[-8px] fixed inset-0 bg-black/20 z-40 transition-opacity duration-300 ${
              isAnimating && !isClosing ? "opacity-100" : "opacity-0"
            }`}
            onClick={handleClose}
          />
          {/* Panel */}
          <div
            ref={panelRef}
            className='fixed top-0 right-0 h-full section-lnds-color shadow-2xl z-50 transition-all duration-300 ease-in-out overflow-hidden'
            style={{
              width: isAnimating && !isClosing ? "24rem" : "0",
            }}
          >
            <div className='w-96 h-full flex flex-col'>
              <div className='p-4 border-b border-lnds-color flex items-center justify-between'>
                <h3 className='text-lg font-semibold text-lnds-color flex items-center space-x-2'>
                  <InformationCircleIcon
                    className={`h-6 w-6 ${isErrorMode ? "text-lnds-red" : "text-lnds-color"}`}
                  />
                  <span className={isErrorMode ? "text-lnds-red" : "text-lnds-color"}>
                    {isErrorMode ? "Action Required" : "Next Steps"}
                  </span>
                </h3>
                <button
                  onClick={handleClose}
                  className='text-gray-400 hover:text-gray-600 transition-colors'
                >
                  <XMarkIcon className='h-6 w-6' />
                </button>
              </div>
              <div className='flex-1 overflow-y-auto p-4 space-y-3'>
                {isErrorMode && forcedErrors.length > 0 && (
                  <div className='rounded-md p-4 border border-lnds-color'>
                    <div className='font-semibold text-base text-lnds-red'>
                      Please fix these before submitting:
                    </div>
                    <ul className='mt-2 list-disc list-inside text-sm text-lnds-color space-y-1'>
                      {forcedErrors.map((error) => (
                        <li key={error}>{error}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {!isErrorMode && showDataDictionaryReminder && (
                  <div className='rounded-md p-4 border border-lnds-color'>
                    <div className='font-semibold text-base text-lnds-color'>
                      Add Data Dictionaries
                    </div>
                    <div className='text-sm text-lnds-color mt-2'>
                      Before submitting your dataset, consider providing data dictionaries if
                      available.{" "}
                      <Link
                        to={`/datasets/${dataset.id}/dictionaries`}
                        className='text-lnds-color underline hover:text-lnds-green font-medium'
                      >
                        Click here to manage dictionaries
                      </Link>
                      .
                    </div>
                  </div>
                )}
                {!isErrorMode && showRelationsReminder && (
                  <div className='rounded-md p-4 border border-lnds-color'>
                    <div className='font-semibold text-base text-lnds-color'>Add Relations</div>
                    <div className='text-sm text-lnds-color mt-2'>
                      Before submitting your dataset, consider adding relations if available.{" "}
                      <Link
                        to={`/datasets/${dataset.id}/relations`}
                        className='text-lnds-color underline hover:text-lnds-green font-medium'
                      >
                        Click here to manage relations
                      </Link>
                      .
                    </div>
                  </div>
                )}
                {!isErrorMode && dataset.status_triggers && dataset.status_triggers.length > 0 ? (
                  dataset.status_triggers.map((trigger) => (
                    <div key={trigger} className='rounded-md p-4 border border-lnds-color'>
                      <div className='font-semibold text-base text-lnds-color capitalize'>
                        {trigger.replace(/_/g, " ")}
                      </div>
                      <div className='text-sm text-lnds-color mt-2'>
                        {getNextStepDescription(trigger)}
                      </div>
                    </div>
                  ))
                ) : (
                  <>
                    {!isErrorMode && getAwaitingStatusMessage(dataset.status) && (
                      <div className='rounded-md p-4 border border-lnds-color'>
                        <div className='font-semibold text-base text-lnds-color'>
                          {getAwaitingStatusMessage(dataset.status)!.title}
                        </div>
                        <div className='text-sm text-lnds-color mt-2'>
                          {getAwaitingStatusMessage(dataset.status)!.description}
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
}
