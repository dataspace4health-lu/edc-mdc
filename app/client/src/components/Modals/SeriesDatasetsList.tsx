import { useState, useEffect } from "react";
import { SeriesMembershipInfo, ResourceDatasetType } from "../../types";
import client from "../../zodiosClient/client";
import { LinkIcon } from "@heroicons/react/24/solid";
import EmptyScreen from "../EmptyScreen";
import { Link } from "react-router-dom";

interface SeriesDatasetsListProps {
  memberDatasets: SeriesMembershipInfo[];
}

const SeriesDatasetsList: React.FC<SeriesDatasetsListProps> = ({ memberDatasets }) => {
  const [datasets, setDatasets] = useState<ResourceDatasetType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDatasets = async () => {
    if (memberDatasets.length === 0) {
      setLoading(false);
      setDatasets([]);
      return;
    }

    try {
      setLoading(true);
      const datasets = await Promise.all(
        memberDatasets.map((md) =>
          client.retrieve_dataset_api_v1_datasets__dataset_id__get({
            params: { dataset_id: md.dataset_id },
            withCredentials: true,
          }),
        ),
      );

      setDatasets(datasets);
      setError(null);
    } catch (error) {
      setError("Failed to load datasets");
      console.error("Error fetching selected datasets:", error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchDatasets();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [memberDatasets]);

  if (loading) {
    return <div className='p-4 text-center'>Loading series datasets...</div>;
  }

  if (error) {
    return <div className='p-4 text-center text-red-500'>{error}</div>;
  }

  if (memberDatasets.length === 0) {
    return (
      <EmptyScreen
        message='This dataset is not a series or has no member datasets'
        Icon={LinkIcon}
      />
    );
  }

  const sortedMemberDatasets = memberDatasets.sort((a, b) => {
    return a.position - b.position;
  });

  const getDatasetById = (id: number) => {
    return datasets.find((dataset) => dataset.id === id);
  };

  return (
    <div className='space-y-4'>
      <div className='text-sm text-gray-500 mb-2'>
        This dataset series contains {datasets.length} datasets ordered chronologically.
      </div>

      {sortedMemberDatasets.map((md) => (
        <div className='border border-lnds-color rounded-md p-4 mb-2' key={md.dataset_id}>
          <div className='flex justify-between items-center'>
            <div className='flex items-center'>
              <div className='bg-lnds-dark-blue text-white rounded-full w-6 h-6 flex items-center justify-center mr-2'>
                {md.position + 1}
              </div>
              <h3 className='font-medium'>{getDatasetById(md.dataset_id)!.title}</h3>
            </div>
            <div className='space-x-2 flex'>
              <Link
                to={`/?datasetId=${md.dataset_id}`}
                aria-label='View dataset'
                target='_blank'
                rel='noopener noreferrer'
                className='text-lnds-gray dark:text-gray-400 hover:text-lnds-dark-blue dark:hover:text-white hover:underline'
              >
                View
              </Link>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default SeriesDatasetsList;
