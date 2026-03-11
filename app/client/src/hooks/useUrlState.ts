import { useSearchParams } from "react-router-dom";
import { FilterTypes } from "../types";
import { DRAFT_EDIT_PERMISSIONS } from "../utils/permissions";

export const VALUE_SEPARATOR = ",";

type PageParam = {
  page?: number;
  pageSize?: number;
  status?: string;
  query?: string;
  datasetId?: string;
};

export function useUrlState(userPermissions: string[] = []) {
  const [searchParams, setSearchParams] = useSearchParams();

  const getDefaultStatus = () => {
    const hasDraftAccess = DRAFT_EDIT_PERMISSIONS.some((p) => userPermissions.includes(p));

    if (!hasDraftAccess) return "COMPLETED";
    if (userPermissions.includes("datasets:status-change:validate:group")) return "COMPLETED";
    return "DRAFT";
  };

  const DEFAULTS = {
    page: "1",
    pageSize: "10",
    status: getDefaultStatus(),
    query: "",
  };

  const getPageParam = (key: keyof typeof DEFAULTS | string): string => {
    if (key in DEFAULTS) {
      return searchParams.get(key) || DEFAULTS[key as keyof typeof DEFAULTS];
    }
    return searchParams.get(key) || "";
  };

  const generateUrl = (
    params: PageParam,
    options?: {
      removeAllFilters?: boolean;
    },
  ): string => {
    const newParams = new URLSearchParams();
    const allFilterTypes: string[] = Object.values(FilterTypes);

    searchParams.forEach((value, key) => {
      const isPageParam = Object.keys(params).includes(key);

      const isFilterParam = allFilterTypes.includes(key);
      const shouldSkipFilter = options?.removeAllFilters && isFilterParam;

      if (!isPageParam && !shouldSkipFilter) {
        newParams.set(key, value);
      }
    });

    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        newParams.set(key, value.toString());
      }
    });

    return `?${newParams.toString()}`;
  };

  const getFilter = (filterType: FilterTypes): string[] => {
    const value = searchParams.get(filterType);
    return value ? value.split(VALUE_SEPARATOR) : [];
  };

  const updateFilter = (filterType: FilterTypes, values: string[]): void => {
    const newSearchParams = new URLSearchParams(searchParams);

    if (values.length > 0) {
      newSearchParams.set(filterType, values.join(VALUE_SEPARATOR));
    } else {
      newSearchParams.delete(filterType);
    }

    setSearchParams(newSearchParams, { replace: true });
  };

  const clearFilter = (filterType: FilterTypes): void => {
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.delete(filterType);
    setSearchParams(newSearchParams, { replace: true });
  };

  return {
    getPageParam,
    generateUrl,
    getFilter,
    updateFilter,
    clearFilter,
  };
}
