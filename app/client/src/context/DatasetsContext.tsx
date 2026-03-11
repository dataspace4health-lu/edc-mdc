import { createContext, useContext, useState, ReactNode, useRef } from "react";
import { ResourceDatasetType } from "../types";
import { clientWithoutValidation } from "../zodiosClient/client";

interface DatasetsContextType {
  datasets: ResourceDatasetType[];
  totalPages: number;
  totalDatasets: number;
  isLoading: boolean;
  hasError: boolean;
  updateDatasetStatus: (datasetId: number, status: string) => void;
  removeDataset: (datasetId: number) => void;
  fetchPaginatedDatasets: (params?: {
    status: string;
    page: number;
    pageSize: number;
    query: string;
    datasetTypes: string[];
    rightsStatements: string[];
    keywords: string[];
    themes: string[];
    applicableLegislations: string[];
    frequencies: string[];
    organisations: number[];
    authenticSourcePending?: boolean;
    hasUnlabeledAuthenticSource?: boolean;
  }) => Promise<void>;
}

const DatasetsContext = createContext<DatasetsContextType | null>(null);

interface DatasetsProviderProps {
  children: ReactNode;
}

export const DatasetsProvider = ({ children }: DatasetsProviderProps) => {
  const [datasets, setDatasets] = useState<ResourceDatasetType[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [totalPages, setTotalPages] = useState(0);
  const [totalDatasets, setTotalDatasets] = useState(0);

  const currentRequestAbortController = useRef<AbortController | null>(null);
  const isInitialMount = useRef(true);

  const fetchPaginatedDatasets = async (
    params = {
      status: "PUBLISHED",
      page: 1,
      pageSize: 10,
      query: "",
      datasetTypes: [] as string[],
      rightsStatements: [] as string[],
      keywords: [] as string[],
      themes: [] as string[],
      applicableLegislations: [] as string[],
      frequencies: [] as string[],
      organisations: [] as number[],
      authenticSourcePending: undefined,
      hasUnlabeledAuthenticSource: undefined,
    },
  ) => {
    // Don't cancel the request on initial page load
    const shouldCancelPrevious = !isInitialMount.current;
    try {
      // If there's an ongoing request, cancel it (but not on initial load)
      if (shouldCancelPrevious && currentRequestAbortController.current) {
        currentRequestAbortController.current.abort();
      }

      // After initial mount, always cancel previous requests
      if (isInitialMount.current) {
        isInitialMount.current = false;
      }

      // Create a new AbortController for this request
      const abortController = new AbortController();
      currentRequestAbortController.current = abortController;

      setHasError(false);
      setIsLoading(true);

      const response =
        await clientWithoutValidation.paginated_datasets_api_v1_paginated_datasets_post(
          {
            status: params.status,
            page: params.page,
            page_size: params.pageSize,
            query: params.query,
            dataset_types: params.datasetTypes,
            rights_statements: params.rightsStatements,
            keywords: params.keywords,
            themes: params.themes,
            applicable_legislations: params.applicableLegislations,
            periodicities: params.frequencies,
            organisations: params.organisations,
            authentic_source_pending: params.authenticSourcePending,
            has_unlabeled_authentic_source: params.hasUnlabeledAuthenticSource,
          },
          {
            withCredentials: true,
            signal: abortController.signal, // Pass the abort signal to the API call
          },
        );

      // Only update state if this request wasn't aborted
      if (!abortController.signal.aborted) {
        setDatasets(response.items);
        setTotalPages(response.meta.total_pages);
        setTotalDatasets(response.meta.total_items);
        setHasError(false);
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
      // Check if the error is due to an aborted/canceled request
      // Handle both standard AbortError and Axios CanceledError
      if (
        (error instanceof DOMException && error.name === "AbortError") ||
        error.name === "CanceledError" ||
        error.code === "ERR_CANCELED"
      ) {
        // Request was aborted/canceled, don't update error state
        console.log("Request was cancelled");
        return;
      }

      setHasError(true);
      console.error(error);
      setDatasets([]);
    } finally {
      // Only update loading state if this request wasn't aborted
      if (currentRequestAbortController.current?.signal.aborted === false) {
        setIsLoading(false);
      }
    }
  };

  const updateDatasetStatus = async (datasetId: number, status: string) => {
    setDatasets((prevDatasets) => {
      return prevDatasets.map((dataset) => {
        if (dataset.id === datasetId) {
          return { ...dataset, status };
        }
        return dataset;
      });
    });
  };

  const removeDataset = async (datasetId: number) => {
    setDatasets((prevDatasets) => {
      return prevDatasets.filter((dataset) => dataset.id !== datasetId);
    });
    setTotalDatasets((prevTotal) => prevTotal - 1);
    setTotalPages((prevTotal) => {
      const newTotal = prevTotal - 1;
      return newTotal < 1 ? 1 : newTotal;
    });
  };

  return (
    <DatasetsContext.Provider
      value={{
        datasets,
        totalPages,
        totalDatasets,
        isLoading,
        updateDatasetStatus,
        hasError,
        // @ts-expect-error authenticSourcePending: Type 'false' is not assignable to type 'undefined'
        fetchPaginatedDatasets,
        removeDataset,
      }}
    >
      {children}
    </DatasetsContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useDatasets = () => {
  const context = useContext(DatasetsContext);
  if (!context) {
    throw new Error("useDatasets must be used within an DatasetsProvider");
  }
  return context;
};
