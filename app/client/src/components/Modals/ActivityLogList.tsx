import { useMemo, useState, useEffect, useRef } from "react";
import { ResourceActivityLog } from "../../types";
import client from "../../zodiosClient/client";
import {
  PencilSquareIcon,
  XCircleIcon,
  RocketLaunchIcon,
  PlusCircleIcon,
} from "@heroicons/react/24/solid";
import { DateUtils } from "../../utils/dateTimeHelpers";
import { ResourceOrganisation, ResourceRoleType } from "../../types";
import { formatLogMessage } from "../../utils/activityLogFormatters/index";
import { useAuth } from "../../context/AuthContext";

interface ActivityLogListProps {
  entityId: number | null;
  entityType:
    | "dataset"
    | "organisation"
    | "user_assignment"
    | "keyword"
    | "applicable_legislation"
    | "authentic_source_label";
  refreshTrigger?: number;
  organisations?: ResourceOrganisation[];
  roles?: ResourceRoleType[];
}

const PAGE_SIZE = 10;

const activityLogsLoader = async (
  entityId: number | null,
  entityType: ActivityLogListProps["entityType"],
  page: number,
  page_size: number,
  multi_tenant: boolean,
): Promise<ResourceActivityLog[]> => {
  let response;
  if (entityType === "organisation" && entityId === null) {
    response =
      await client.retrieve_all_organisations_activity_logs_api_v1_organisations_activity_logs_get({
        queries: { page, page_size, multi_tenant },
        withCredentials: true,
      });
  } else if (entityType === "organisation") {
    response =
      await client.retrieve_activity_logs_from_organisation_api_v1_organisations__organisation_id__activity_logs_get(
        {
          params: { organisation_id: entityId! },
          queries: { page, page_size },
          withCredentials: true,
        },
      );
  } else if (entityType === "dataset") {
    response =
      await client.retrieve_activity_logs_from_dataset_api_v1_datasets__dataset_id__activity_logs_get(
        {
          params: { dataset_id: entityId! },
          queries: { page, page_size },
          withCredentials: true,
        },
      );
  } else if (entityType === "keyword" || entityType === "applicable_legislation") {
    response =
      await client.retrieve_all_form_fields_activity_logs_api_v1__form_field__activity_logs_get({
        params: { form_field: entityType },
        queries: { page, page_size },
        withCredentials: true,
      });
  } else if (entityType === "authentic_source_label") {
    response =
      await client.retrieve_authentic_source_label_activity_logs_api_v1_activity_logs_authentic_source_labels_get(
        {
          queries: { page, page_size },
          withCredentials: true,
        },
      );
  } else {
    response =
      await client.retrieve_user_assignment_activity_logs_api_v1_activity_logs_assignments_get({
        queries: { page, page_size },
        withCredentials: true,
      });
  }
  return response;
};

const getIcon = (actionType: string) => {
  switch (actionType) {
    case "create":
      return <PlusCircleIcon className='text-lnds-green h-8 w-8' />;
    case "update":
      return <PencilSquareIcon className='text-lnds-purple h-8 w-8' />;
    case "delete":
      return <XCircleIcon className='text-lnds-red h-8 w-8' />;
    default:
      return <RocketLaunchIcon className='text-lnds-purple h-8 w-8' />;
  }
};

const formatDateSection = (dateString: string) => {
  const today = DateUtils.getStartOfToday();
  const logDate = DateUtils.getStartOfDay(dateString);

  if (DateUtils.areDatesEqual(today, logDate)) {
    return "Today";
  } else {
    return DateUtils.formatDate(dateString);
  }
};

export const ActivityLogList: React.FC<ActivityLogListProps> = ({
  entityId,
  entityType,
  refreshTrigger,
  organisations = [],
  roles = [],
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  const [logs, setLogs] = useState<ResourceActivityLog[]>([]);
  const [page, setPage] = useState<number>(1);
  const [hasMore, setHasMore] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [resetCounter, setResetCounter] = useState<number>(0);

  const { user } = useAuth();
  const multi_tenant = Boolean(user?.feature_options?.enable_multi_tenants ?? true);

  useEffect(() => {
    setLogs([]);
    setPage(1);
    setHasMore(true);
    setResetCounter((c) => c + 1);
  }, [entityId, entityType, refreshTrigger]);

  useEffect(() => {
    if (resetCounter === 0) return;
    if (!entityType || isLoading || !hasMore) return;
    if (
      entityType !== "organisation" &&
      entityType !== "user_assignment" &&
      entityType !== "keyword" &&
      entityType !== "applicable_legislation" &&
      entityType !== "authentic_source_label" &&
      (!entityId || entityId <= 0)
    ) {
      return;
    }

    setIsLoading(true);
    activityLogsLoader(entityId, entityType, page, PAGE_SIZE, multi_tenant)
      .then((newLogs) => {
        if (newLogs.length < PAGE_SIZE) {
          setHasMore(false);
        }
        setLogs((prev) => [...prev, ...newLogs]);
      })
      .catch(console.error)
      .finally(() => {
        setIsLoading(false);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, resetCounter, entityId, entityType]);

  useEffect(() => {
    const rootEl = containerRef.current;
    if (!rootEl) return;

    let node: HTMLElement | null = rootEl.parentElement;
    while (node) {
      const style = getComputedStyle(node);
      const overflowY = style.overflowY;
      if (overflowY === "auto" || overflowY === "scroll") {
        break;
      }
      node = node.parentElement;
    }
    const scrollContainer = node;

    if (!scrollContainer) {
      return;
    }

    const onScroll = () => {
      if (isLoading || !hasMore) return;
      // When we get within 50px of bottom, load next page
      if (
        scrollContainer.scrollHeight - scrollContainer.scrollTop <=
        scrollContainer.clientHeight + 50
      ) {
        setPage((prev) => prev + 1);
      }
    };

    scrollContainer.addEventListener("scroll", onScroll);
    return () => {
      scrollContainer.removeEventListener("scroll", onScroll);
    };
  }, [isLoading, hasMore]);

  const groupLogsByDate = (logs: ResourceActivityLog[]): Record<string, ResourceActivityLog[]> => {
    return logs.reduce((acc: Record<string, ResourceActivityLog[]>, log: ResourceActivityLog) => {
      const date = DateUtils.getStartOfDay(log.timestamp).toISOString();
      acc[date] = acc[date] || [];
      acc[date].push(log);
      return acc;
    }, {});
  };

  const sortedGroupedLogs = useMemo(() => {
    const groupedLogs = groupLogsByDate(logs);
    return Object.entries(groupedLogs).sort(([dateA], [dateB]) => {
      return DateUtils.diff(dateB, dateA);
    });
  }, [logs]);

  return (
    <div ref={containerRef} className='min-h-0 pb-6'>
      {sortedGroupedLogs.map(([date, dateLogs]) => (
        <div key={date} className='mb-6'>
          <h3 className='text-lnds-blue mb-4'>{formatDateSection(date)}</h3>
          <div className='flex flex-col items-center relative'>
            <div
              className='w-1 bg-lnds-blue absolute'
              style={{ left: "24px", top: 0, bottom: 0 }}
            />
            {dateLogs
              .map((log) => ({
                log,
                message: formatLogMessage(log, roles, organisations, entityType, entityId),
              }))
              .filter(({ message }) => !!message)
              .map(({ log, message }) => (
                <div
                  key={`${log.id}-${log.timestamp}`}
                  className='flex items-center pt-4 w-full min-w-0'
                >
                  <div
                    className='z-10 w-6 h-6 rounded-full bg-lnds-dark-blue flex items-center justify-center flex-shrink-0 mb-1'
                    style={{ marginLeft: "14px" }}
                  >
                    <span className='absolute w-3 h-3 rounded-full bg-lnds-blue' />
                  </div>
                  <div className='pl-4 flex flex-col flex-grow min-w-0'>
                    <div className='flex items-center mb-1 min-w-0 w-full'>
                      <div className='flex-shrink-0'>{getIcon(log.action_type)}</div>
                      <div className='flex flex-col items-start ml-2 min-w-0 flex-1'>
                        <p
                          className='text-base text-lnds-color w-full'
                          style={{ overflowWrap: "anywhere" }}
                        >
                          {message}
                        </p>
                        <span className='text-lnds-light-gray text-sm'>
                          {`at ${DateUtils.formatTime(log.timestamp)}`}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      ))}
      {sortedGroupedLogs.length === 0 && (
        <div className='flex items-center justify-center p-4'>
          <p className='text-lnds-light-gray'>No activity logs available.</p>
        </div>
      )}
      {isLoading && (
        <div className='flex justify-center py-4'>
          <p className='text-lnds-color'>Loading more…</p>
        </div>
      )}
      {!hasMore && logs.length > 0 && (
        <div className='flex justify-center py-4'>
          <p className='text-lnds-light-gray'>You’ve reached the end of the logs.</p>
        </div>
      )}
    </div>
  );
};

export default ActivityLogList;
