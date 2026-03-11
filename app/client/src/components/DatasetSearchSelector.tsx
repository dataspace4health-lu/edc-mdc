import { useEffect, useState } from "react";
import { InputField, Button } from "@lnds-lu/design-system";
import client from "../zodiosClient/client";
import { ResourceDatasetType } from "../types";
import {
  ArrowLeftIcon,
  ArrowRightIcon,
  MagnifyingGlassIcon,
  PlusCircleIcon,
} from "@heroicons/react/24/solid";

interface DatasetSearchSelectorProps {
  status: string;
  selectedIds?: number[];
  onSelect: (dataset: ResourceDatasetType) => void;
  pageSize?: number;
  addButtonLabel?: string;
  alwaysShowSearch?: boolean;
}

export default function DatasetSearchSelector({
  status,
  selectedIds = [],
  onSelect,
  pageSize = 5,
  addButtonLabel = "Add",
  alwaysShowSearch = false,
}: Readonly<DatasetSearchSelectorProps>) {
  const [searchTerm, setSearchTerm] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [datasets, setDatasets] = useState<ResourceDatasetType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDataset, setSelectedDataset] = useState<ResourceDatasetType | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  const shouldShowSearchBar = alwaysShowSearch || !selectedDataset || isEditing;

  useEffect(() => {
    if (shouldShowSearchBar) {
      fetchDatasets();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchTerm, page, status]);

  const fetchDatasets = async () => {
    setIsLoading(true);
    try {
      const response = await client.paginated_datasets_api_v1_paginated_datasets_post(
        {
          status,
          query: searchTerm || null,
          page,
          page_size: pageSize,
        },
        { withCredentials: true },
      );

      const term = searchTerm.trim().toLowerCase();
      const filtered = response.items
        .filter((d) => !selectedIds.includes(d.id) && d.title.toLowerCase().includes(term))
        .sort((a, b) => {
          const aTitle = a.title.toLowerCase();
          const bTitle = b.title.toLowerCase();
          if (aTitle === term) return -1;
          if (bTitle === term) return 1;
          if (aTitle.startsWith(term) && !bTitle.startsWith(term)) return -1;
          if (!aTitle.startsWith(term) && bTitle.startsWith(term)) return 1;
          return aTitle.localeCompare(bTitle);
        });

      setDatasets(filtered);
      setTotalPages(response.meta.total_pages);
    } catch (err) {
      console.error("Failed to fetch datasets", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelect = (ds: ResourceDatasetType) => {
    setSelectedDataset(ds);
    setSearchTerm(ds.title);
    setDatasets([]);
    setIsEditing(false);
    onSelect(ds);
  };

  return (
    <div className='flex flex-col gap-4'>
      <div className='flex items-center gap-2'>
        {shouldShowSearchBar ? (
          <>
            <InputField
              type='text'
              name='datasetSearch'
              placeholder='Search for datasets to add...'
              defaultValue={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className='flex-1'
            />
            <Button Icon={MagnifyingGlassIcon} onClick={fetchDatasets} />
          </>
        ) : (
          <button
            type='button'
            className='border border-gray-300 rounded px-3 py-2 text-sm text-gray-700 w-full cursor-pointer dark:bg-gray-700 dark:text-gray-200 dark:border-gray-700'
            onClick={() => {
              setIsEditing(true);
              setSearchTerm("");
              setDatasets([]);
            }}
          >
            {selectedDataset?.title}
          </button>
        )}
      </div>

      {shouldShowSearchBar && searchTerm && (
        <div className='mb-6'>
          <h4 className='text-md font-medium mb-2'>Search Results</h4>
          {isLoading ? (
            <div className='text-center py-4'>Loading...</div>
          ) : datasets.length === 0 ? (
            <div className='text-center py-4 text-gray-500'>No datasets found</div>
          ) : (
            <div className='max-h-60 overflow-y-auto border border-lnds-color rounded dark:bg-gray-800'>
              {datasets.map((ds) => (
                <div
                  key={ds.id}
                  className='p-3 border-b border-lnds-color last:border-b-0 hover:bg-lnds-purple hover:text-white flex justify-between items-center'
                >
                  <div className='font-medium'>{ds.title}</div>
                  <Button
                    Icon={PlusCircleIcon}
                    label={addButtonLabel}
                    btnType='primary'
                    size='small'
                    onClick={() => handleSelect(ds)}
                  />
                </div>
              ))}
            </div>
          )}
          {totalPages > 1 && (
            <div className='flex justify-between items-center mt-2'>
              <Button
                label='Previous'
                btnType='secondary'
                size='small'
                onClick={() => setPage(Math.max(1, page - 1))}
                Icon={ArrowLeftIcon}
              />
              <span className='text-sm'>
                Page {page} of {totalPages}
              </span>
              <Button
                label='Next'
                btnType='secondary'
                size='small'
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                Icon={ArrowRightIcon}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
