import { useState, useEffect, useRef } from "react";
import { appAlerts } from "../../utils/appAlerts";
import { Button, Card } from "@lnds-lu/design-system";
import {
  PencilIcon,
  CircleStackIcon,
  ShieldCheckIcon,
  ClockIcon,
  CalendarDaysIcon,
  ServerIcon,
  ArrowDownTrayIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from "@heroicons/react/24/solid";
import EmptyScreen from "../../components/EmptyScreen";
import InitialsAvatar from "../../components/InitialsAvatar";
import SearchBar from "../../components/SearchBar";
import { RightSidebar } from "../../components/RightSidebar";
import { useAuthenticSourceLabels } from "../../context/AuthenticSourceLabelsContext";
import { ResourceAuthenticSourceLabel, ResourceLabelAssignmentHistory } from "../../types";
import { DateUtils } from "../../utils/dateTimeHelpers";
import LabelFormContainer from "./LabelFormContainer";
import { useAuth } from "../../context/AuthContext";
import client from "../../zodiosClient/client";
import ConfirmableActionButton from "../../components/ConfirmableActionButton";
import { useAlert } from "@lnds-lu/design-system";
import { isAxiosError } from "axios";
import StatusBadge from "../../components/StatusBadge";
import Tooltip from "../../components/Tooltip";
import { deprecatedBgClasses } from "../../components/DeprecatedTag";
import { usePageTitle } from "../../hooks/usePageTitle";

const AuthenticSourceManagement: React.FC = () => {
  usePageTitle("Authentic Sources");
  const { user } = useAuth();
  const { labels, fetchLabels, createLabel, removeLabel, updateLabel } = useAuthenticSourceLabels();
  const [showDownloadOptions, setShowDownloadOptions] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    fetchLabels();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      // @ts-expect-error Property 'contains' does not exist on type 'never'.
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDownloadOptions(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const [expandedItems, setExpandedItems] = useState<Set<number>>(new Set());
  const [sidebarKey, setSidebarKey] = useState(0);
  const [editingLabel, setEditingLabel] = useState<ResourceAuthenticSourceLabel | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [historyLoading, setHistoryLoading] = useState(false);
  const [history, setHistory] = useState<ResourceLabelAssignmentHistory[]>([]);
  const { setAlert } = useAlert();

  const canEditLabels = user?.permissions?.includes("authentic-source:assign");

  const toggleExpanded = (sourceId: number) => {
    setExpandedItems((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(sourceId)) {
        newSet.delete(sourceId);
      } else {
        newSet.add(sourceId);
      }
      return newSet;
    });
  };

  const fetchHistory = async (labelId: number) => {
    if (expandedItems.has(labelId)) {
      toggleExpanded(labelId);
      return;
    }

    setHistoryLoading(true);

    const response =
      await client.get_authentic_source_label_history_api_v1_authentic_source_labels__label_id__history_get(
        {
          params: { label_id: labelId },
          withCredentials: true,
        },
      );
    setHistory(response as ResourceLabelAssignmentHistory[]);
    toggleExpanded(labelId);
    setHistoryLoading(false);
  };

  const handleLabelCreate = (newLabel: ResourceAuthenticSourceLabel) => {
    createLabel(newLabel);
    setSidebarKey((prev) => prev + 1);
  };

  const handleLabelUpdate = (updatedLabel: ResourceAuthenticSourceLabel) => {
    updateLabel(updatedLabel);
    setSidebarKey((prev) => prev + 1);
  };

  const handleLabelDelete = async (labelId: number) => {
    try {
      await client.delete_authentic_source_label_api_v1_authentic_source_labels__label_id__delete(
        undefined,
        {
          params: { label_id: labelId },
          withCredentials: true,
        },
      );
      setAlert(appAlerts.authenticSourceLabelDeleted());
      removeLabel(labelId);
      setSidebarKey((prev) => prev + 1);
    } catch (error: unknown) {
      if (isAxiosError(error)) {
        if (error.response?.status === 400) {
          setAlert(appAlerts.authenticSourceLabelDeleteBlockedInUse());
        } else {
          setAlert(
            appAlerts.genericValidationError(
              error.response?.data?.detail || appAlerts.serverErrorTryLater().message,
            ),
          );
        }
      } else {
        setAlert(appAlerts.unknownError());
      }
    }
  };

  const handleLabelDeprecate = async (labelId: number) => {
    await client.change_deprecation_status_api_v1_authentic_source_labels__label_id__toggle_deprecation_patch(
      undefined,
      {
        params: { label_id: labelId },
        withCredentials: true,
      },
    );
    await fetchLabels();
    setSidebarKey((prev) => prev + 1);
    const label = labels.find((l) => l.id === labelId);
    if (label?.is_deprecated) {
      setAlert(appAlerts.labelRestored());
    } else {
      setAlert(appAlerts.labelDeprecated());
    }
  };

  const getDownloadUrl = (format: string) => {
    return `/api/v1/authentic-source-labels/catalogue.${format}`;
  };

  const filteredLabels = labels.filter(
    (label) =>
      label.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      label.description?.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <div className='relative flex justify-center transition-all duration-300'>
      <div className='w-full max-w-6xl transition-all duration-300'>
        <div className='my-6 mx-6 max-w-6xl md:mx-auto'>
          {canEditLabels && (
            <LabelFormContainer
              onLabelCreate={handleLabelCreate}
              onLabelUpdate={handleLabelUpdate}
              editingLabel={editingLabel}
              onEditingChange={setEditingLabel}
            />
          )}
          <Card className='flex flex-col h-full px-0 py-0'>
            <div className='px-6 py-4 border-b border-lnds-color'>
              <div className='flex items-center justify-between'>
                <div className='flex items-center gap-2'>
                  <ShieldCheckIcon className='h-5 w-5 heading-lnds-color' />
                  <h2 className='text-xl font-semibold heading-lnds-color'>
                    Authentic Sources{" "}
                    <span className='text-sm bg-lnds-purple text-white px-2 py-0.5 rounded-full ml-2'>
                      {labels.length}
                    </span>
                  </h2>
                </div>
                <div className='relative' ref={dropdownRef}>
                  <Button
                    btnType='secondary'
                    label='Download RDF'
                    Icon={ArrowDownTrayIcon}
                    onClick={() => setShowDownloadOptions(!showDownloadOptions)}
                    className='pr-7'
                  />
                  <div className='pointer-events-none absolute right-2 inset-y-0 flex items-center'>
                    {showDownloadOptions ? (
                      <ChevronUpIcon className='h-4 w-4 ml-2 text-white' />
                    ) : (
                      <ChevronDownIcon className='h-4 w-4 ml-2 text-white' />
                    )}
                  </div>
                  {showDownloadOptions && (
                    <div className='absolute left-0 top-full mt-1 w-full z-50 py-2 section-lnds-color border border-lnds-color shadow-lg rounded'>
                      <a
                        href={getDownloadUrl("rdf")}
                        target='_blank'
                        rel='noopener noreferrer'
                        className='w-full text-left px-4 py-2 block hover:bg-lnds-dark-blue hover:text-white text-sm'
                        onClick={() => setShowDownloadOptions(false)}
                      >
                        RDF/XML
                      </a>
                      <a
                        href={getDownloadUrl("ttl")}
                        target='_blank'
                        rel='noopener noreferrer'
                        download
                        onClick={() => setShowDownloadOptions(false)}
                        className='w-full text-left px-4 py-2 block hover:bg-lnds-dark-blue hover:text-white text-sm'
                      >
                        Turtle (TTL)
                      </a>
                      <a
                        href={getDownloadUrl("jsonld")}
                        target='_blank'
                        rel='noopener noreferrer'
                        download
                        onClick={() => setShowDownloadOptions(false)}
                        className='w-full text-left px-4 py-2 block hover:bg-lnds-dark-blue hover:text-white text-sm'
                      >
                        JSON-LD
                      </a>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <SearchBar
              searchTerm={searchTerm}
              onSearch={setSearchTerm}
              placeholder='Search authentic sources...'
            />
            <div className='flex-grow overflow-y-auto' style={{ height: "calc(60vh)" }}>
              {filteredLabels.length > 0 ? (
                <div>
                  {filteredLabels.map((label) => {
                    const isExpanded = expandedItems.has(label.id);

                    return (
                      <div
                        key={label.id}
                        className={`section-lnds-color border-b border-lnds-color ${
                          label.is_deprecated ? deprecatedBgClasses : "text-lnds-color"
                        }`}
                      >
                        <div className='p-4'>
                          <div className='flex items-start justify-between'>
                            <div className='flex items-start space-x-4 flex-1'>
                              <InitialsAvatar
                                name={label.created_by_name}
                                showTooltip={true}
                                isSystem={!label.created_by_name}
                              />

                              <div className='flex-1 min-w-0'>
                                <div className='flex items-center gap-3 mb-2'>
                                  <h3 className='text-lg font-medium text-lnds-color'>
                                    <ShieldCheckIcon className='h-4 w-4 inline-block mr-1 text-lnds-purple' />
                                    {label.name}
                                  </h3>
                                  <StatusBadge
                                    isDeprecated={!!label.is_deprecated}
                                    isActive={!!label.dataset_id}
                                  />
                                </div>

                                <p className='text-lnds-color mb-3 leading-relaxed'>
                                  {label.description}
                                </p>

                                {label.dataset_id && (
                                  <div className='border border-lnds-color p-3 rounded-lg mb-3'>
                                    <div className='flex items-center gap-2 mb-2'>
                                      <span className='text-sm font-medium text-lnds-color'>
                                        Currently assigned to:
                                      </span>
                                    </div>

                                    <div
                                      className='flex items-center gap-1 text-base section-lnds-color'
                                      title={
                                        label.dataset_is_deprecated
                                          ? "This dataset is deprecated"
                                          : undefined
                                      }
                                    >
                                      <CircleStackIcon className='h-4 w-4 inline-block text-lnds-color' />
                                      <a
                                        href={`/?datasetId=${label.dataset_id}`}
                                        target='_blank'
                                        className='hover:underline dark:hover:text-lnds-lightest-gray hover:text-lnds-dark-blue text-lnds-color'
                                        onClick={(e) => e.stopPropagation()}
                                      >
                                        {label.dataset_is_deprecated ? " (deprecated) " : ""}
                                        {label.dataset_title}
                                      </a>
                                    </div>
                                  </div>
                                )}

                                {/* Metadata */}
                                <div className='flex flex-wrap items-center gap-4 text-sm text-gray-500 dark:text-gray-400'>
                                  <div className='flex items-center gap-1'>
                                    <CalendarDaysIcon className='h-4 w-4' />
                                    Created {DateUtils.formatRelativeTime(label.created_at)}
                                  </div>
                                </div>
                              </div>
                            </div>

                            {/* Actions */}
                            <div className='flex items-center gap-2 ml-4'>
                              {canEditLabels && (
                                <>
                                  {!label.is_deprecated && (
                                    <>
                                      <Tooltip text='Edit Label'>
                                        <Button
                                          btnType='transparent'
                                          Icon={PencilIcon}
                                          onClick={() => {
                                            setEditingLabel(label);
                                          }}
                                          className='p-2 w-10 h-10 rounded-md flex items-center justify-center text-lnds-color'
                                        />
                                      </Tooltip>
                                      <ConfirmableActionButton
                                        action='delete'
                                        onConfirm={() => handleLabelDelete(label.id)}
                                      />
                                    </>
                                  )}
                                  <ConfirmableActionButton
                                    action={label.is_deprecated ? "restore" : "deprecate"}
                                    onConfirm={() => handleLabelDeprecate(label.id)}
                                  />
                                </>
                              )}
                              <Tooltip text='View History'>
                                <Button
                                  btnType='transparent'
                                  Icon={ClockIcon}
                                  onClick={() => fetchHistory(label.id)}
                                  className='p-2 w-10 h-10 rounded-md flex items-center justify-center text-lnds-color'
                                />
                              </Tooltip>
                            </div>
                          </div>
                        </div>

                        {/* History Section */}
                        {isExpanded && history.length > 0 ? (
                          <div className='border-t border-lnds-color bg-gray-50 dark:bg-gray-900'>
                            <div className='p-6'>
                              <h4 className='text-md font-medium text-gray-900 dark:text-white mb-4 flex items-center gap-2'>
                                <ClockIcon className='h-4 w-4' />
                                Assignment History ({history.length})
                              </h4>

                              <div className='space-y-2'>
                                {history.map((assignment) => (
                                  <div key={assignment.dataset_id} className={`relative pl-8 pb-2`}>
                                    <div className='bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-lnds-color'>
                                      <div className='flex items-start justify-between mb-2'>
                                        <a
                                          href={`/?datasetId=${assignment.dataset_id}`}
                                          target='_blank'
                                          className='hover:underline dark:hover:text-lnds-lightest-gray hover:text-lnds-dark-blue text-lnds-color'
                                          onClick={(e) => e.stopPropagation()}
                                        >
                                          {assignment.dataset_is_deprecated && "(deprecated) "}
                                          {assignment.dataset_title}
                                        </a>
                                      </div>

                                      <div className='space-y-2 text-sm'>
                                        <div className='flex items-center gap-2 text-gray-600 dark:text-gray-400'>
                                          <CalendarDaysIcon className='h-3 w-3' />
                                          <span>
                                            Assigned on{" "}
                                            {DateUtils.formatRelativeTime(
                                              assignment.asignment_datetime
                                                ? assignment.asignment_datetime
                                                : "",
                                            )}
                                          </span>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        ) : isExpanded && history.length === 0 && historyLoading ? (
                          <div className='text-lnds-color p-4'>
                            {" "}
                            Fetching history. Please wait...{" "}
                          </div>
                        ) : isExpanded && history.length === 0 ? (
                          <div className='p-4'>
                            <EmptyScreen message='No history found.' Icon={ServerIcon} />
                          </div>
                        ) : (
                          <div />
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className='p-8'>
                  <EmptyScreen message='No authentic source labels found.' Icon={ShieldCheckIcon} />
                </div>
              )}
            </div>
          </Card>
        </div>

        <RightSidebar
          refreshTrigger={sidebarKey}
          entityType='authentic_source_label'
          className='border-l border-lnds-color'
          defaultIsOpen={false}
        />
      </div>
    </div>
  );
};

export default AuthenticSourceManagement;
