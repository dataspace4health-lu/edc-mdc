import { useEffect, useMemo } from "react";
import { CircleStackIcon } from "@heroicons/react/24/solid";
import { useLoaderData } from "react-router";
import { useNavigate } from "react-router-dom";
import { DatasetModal } from "../../components/Modals/DatasetModal";
import EmptyScreen from "../../components/EmptyScreen";
import DismissibleAlert from "../../components/DismissibleAlert";
import SearchPanel from "./SearchPanel";
import { datasetListLoader } from "./loader";
import StatusTabs from "./StatusTabs";
import DatasetCard from "./DatasetCard";
import Pagination from "./Pagination";
import { Spinner } from "../../components/Spinner";
import { useAuth } from "../../context/AuthContext";
import { useDatasets } from "../../context/DatasetsContext";
import FilterList from "../../components/Filters/FilterList";
import { useUrlState } from "../../hooks/useUrlState";
import { FilterTypes, DatasetStatusEnum } from "../../types";
import LinkedNoticeText from "../../components/LinkedNoticeText";
import { usePageTitle } from "../../hooks/usePageTitle";

export default function DatasetList() {
  usePageTitle("Datasets");
  const { user } = useAuth();
  const { getPageParam, getFilter, generateUrl } = useUrlState(user?.permissions || []);
  const { datasets, totalPages, totalDatasets, isLoading, hasError, fetchPaginatedDatasets } =
    useDatasets();
  const { formFields } = useLoaderData() as Awaited<ReturnType<typeof datasetListLoader>>;

  const query = getPageParam("query");
  const statusParam = getPageParam("status");
  const pageParam = getPageParam("page");
  const pageSizeParam = getPageParam("pageSize");

  const allFilters = Object.values(FilterTypes);
  const memoizedFilters = useMemo(() => {
    return new Map<FilterTypes, string[]>(allFilters.map((filter) => [filter, getFilter(filter)]));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [allFilters.map((filter) => getFilter(filter).join(",")).join(",")]);

  const filterState = memoizedFilters;
  const serializedFilterState = JSON.stringify(Array.from(filterState.values()));

  useEffect(() => {
    const fetchParams = {
      status: statusParam,
      page: Number(pageParam),
      pageSize: Number(pageSizeParam),
      query,
      datasetTypes: filterState.get(FilterTypes.DatasetTypes) ?? [],
      rightsStatements: filterState.get(FilterTypes.RightsStatment) ?? [],
      keywords: filterState.get(FilterTypes.Keywords) ?? [],
      themes: filterState.get(FilterTypes.Themes) ?? [],
      applicableLegislations: filterState.get(FilterTypes.ApplicableLegislations) ?? [],
      frequencies: filterState.get(FilterTypes.Frequency) ?? [],
      organisations: filterState.get(FilterTypes.Organisations)?.map(Number) ?? [],
      ...(filterState
        .get(FilterTypes.authenticSource)
        ?.includes("authentic_source_review_pending") &&
        statusParam === DatasetStatusEnum.PUBLISHED && { authenticSourcePending: true }),
      ...(filterState
        .get(FilterTypes.authenticSource)
        ?.includes("has_unlabeled_authentic_source") &&
        statusParam === DatasetStatusEnum.PUBLISHED && { hasUnlabeledAuthenticSource: true }),
    };

    fetchPaginatedDatasets(fetchParams);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusParam, pageParam, pageSizeParam, query, serializedFilterState]);

  const hasFilters =
    query || Object.values(FilterTypes).some((filter) => filterState.get(filter)?.length);

  const navigate = useNavigate();

  let alertMessage;

  if (user?.show_notice_on_homepage) {
    alertMessage = (
      <DismissibleAlert
        message={<LinkedNoticeText message={user.show_notice_on_homepage} />}
        type='warning'
      />
    );
  }

  const openDataset = (datasetId: string) => {
    const url = generateUrl({
      datasetId,
    });
    navigate(url, {
      replace: true,
    });
  };

  if (hasError) {
    return (
      <div className='my-1'>
        <DismissibleAlert
          message='Failed to fetch datasets. Please try again later.'
          type='error'
        />
      </div>
    );
  }

  return (
    <div className='flex flex-col gap-y-6 lg:gap-y-0 lg:flex-row lg:gap-x-4 mx-4 2xl:mx-24 my-4'>
      <div className='w-full lg:w-1/4'>
        <FilterList formFields={formFields} status={statusParam} />
      </div>
      <div className='w-full lg:w-3/4'>
        <SearchPanel query={query} placeholder='Search Dataset' />
        {alertMessage}
        <StatusTabs currentStatus={statusParam} generateUrl={generateUrl} />
        {!isLoading && hasFilters && (
          <div className='mt-3 mb-4 px-4 py-3 section-lnds-color border-l-4 border-lnds-blue rounded-md text-lnds-color text-sm font-medium'>
            <strong className='text-base'>{totalDatasets}</strong>{" "}
            {totalDatasets === 1 ? "result" : "results"} found with filters or query
          </div>
        )}
        <div className='mt-6'>
          {isLoading ? (
            <div className='flex justify-center items-center h-48'>
              <Spinner />
            </div>
          ) : datasets.length === 0 ? (
            <EmptyScreen message='No dataset available' Icon={CircleStackIcon} />
          ) : (
            <div className='flex flex-col gap-y-4'>
              <div className='grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-2 gap-4 mb-6'>
                {datasets.map((dataset) => (
                  <DatasetCard
                    key={dataset.id}
                    dataset={dataset}
                    openDataset={openDataset}
                    formFields={formFields}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
        <Pagination
          currentPage={Number(pageParam)}
          totalPages={totalPages}
          pageSize={Number(pageSizeParam)}
          query={query}
          status={statusParam}
        />
        <DatasetModal formFields={formFields} />
      </div>
    </div>
  );
}
