import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../../zodiosClient/client";
import { DatasetCountsResponse } from "../../types";
import { useAuth } from "../../context/AuthContext";
import { DRAFT_EDIT_PERMISSIONS } from "../../utils/permissions";

interface StatusTabsProps {
  currentStatus: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  generateUrl: (params: Record<string, any>) => string;
}

const GENERAL_READ_PERMISSIONS = [
  "datasets:read:all-after-draft",
  "datasets:read:all-after-draft:organisation",
  "datasets:read:all-after-complete",
];

const STATUSES = [
  {
    id: "DRAFT",
    label: "Draft",
    countKey: "draft",
    permissions: [
      ...DRAFT_EDIT_PERMISSIONS,
      "datasets:status-change:draft",
      "datasets:status-change:draft:group",
    ],
  },
  {
    id: "COMPLETED",
    label: "Completed",
    countKey: "completed",
    permissions: [
      ...GENERAL_READ_PERMISSIONS,
      "datasets:read:completed",
      "datasets:status-change:complete",
      "datasets:status-change:complete:my",
      "datasets:status-change:complete:group",
      "datasets:status-change:complete:organisation",
      "datasets:status-change:validate",
      "datasets:status-change:validate:group",
    ],
  },
  {
    id: "VALIDATED",
    label: "Validated",
    countKey: "validated",
    permissions: [
      ...GENERAL_READ_PERMISSIONS,
      "datasets:read:validated",
      "datasets:status-change:validate",
      "datasets:status-change:validate:group",
      "datasets:status-change:approve",
    ],
  },
  {
    id: "APPROVED",
    label: "Approved",
    countKey: "approved",
    permissions: [
      ...GENERAL_READ_PERMISSIONS,
      "datasets:read:approved",
      "datasets:status-change:approve",
      "datasets:status-change:publish",
    ],
  },
  {
    id: "PUBLISHED",
    label: "Published",
    countKey: "published",
    permissions: [
      ...GENERAL_READ_PERMISSIONS,
      "datasets:read:published",
      "datasets:status-change:publish",
      "datasets:status-change:deprecate",
      "datasets:status-change:internal-only",
    ],
  },
  {
    id: "INTERNAL_ONLY",
    label: "Internal Only",
    countKey: "internal_only",
    permissions: [...GENERAL_READ_PERMISSIONS, "datasets:status-change:internal-only"],
  },
  {
    id: "DEPRECATED",
    label: "Deprecated",
    countKey: "deprecated",
    permissions: [...GENERAL_READ_PERMISSIONS, "datasets:status-change:deprecate"],
  },
];

export default function StatusTabs(props: Readonly<StatusTabsProps>) {
  const { currentStatus, generateUrl } = props;
  const { user } = useAuth();
  const [counts, setCounts] = useState<DatasetCountsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const userPermissions = user?.permissions || [];

  const filteredStatuses = STATUSES.filter((status) =>
    status.permissions.some((p) => userPermissions.includes(p)),
  );

  useEffect(() => {
    const fetchCounts = async () => {
      try {
        setIsLoading(true);

        const response = await client.get_dataset_counts_api_v1_datasets_counts_get({
          withCredentials: true,
        });

        setCounts(response);
      } catch (err) {
        console.error("Failed to fetch dataset counts:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCounts();
  }, []);

  const getCountForStatus = (statusId: string): number | null => {
    if (!counts) return null;

    // Find the appropriate count key for this status
    const status = STATUSES.find((status) => status.id === statusId);
    if (!status) return null;

    const countKey = status.countKey as keyof DatasetCountsResponse;
    return counts[countKey] as number | null;
  };

  return (
    <div className='flex flex-wrap border-b border-lnds-color mt-6 overflow-x-auto'>
      {filteredStatuses.map((status) => {
        const count = getCountForStatus(status.id);

        return (
          <Link
            key={status.id}
            to={generateUrl({ status: status.id, page: 1 })}
            className={`py-2 px-4 relative ${
              currentStatus === status.id
                ? "text-lnds-blue border-b-2 border-lnds-blue font-medium"
                : "text-lnds-gray dark:text-white hover:text-lnds-dark-blue dark:hover:text-lnds-dark-blue"
            }`}
          >
            {status.label}
            {isLoading ? (
              <span className='ml-2 inline-block w-4 h-4'>
                <svg
                  className='animate-spin h-4 w-4 text-gray-400'
                  xmlns='http://www.w3.org/2000/svg'
                  fill='none'
                  viewBox='0 0 24 24'
                >
                  <circle
                    className='opacity-25'
                    cx='12'
                    cy='12'
                    r='10'
                    stroke='currentColor'
                    strokeWidth='4'
                  ></circle>
                  <path
                    className='opacity-75'
                    fill='currentColor'
                    d='M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z'
                  ></path>
                </svg>
              </span>
            ) : (
              count !== null && (
                <span
                  className={`ml-2 text-xs font-medium px-2 py-0.5 rounded-full ${
                    currentStatus === status.id
                      ? "bg-lnds-blue text-white"
                      : "bg-lnds-gray text-white"
                  }`}
                >
                  {count}
                </span>
              )
            )}
          </Link>
        );
      })}
    </div>
  );
}
