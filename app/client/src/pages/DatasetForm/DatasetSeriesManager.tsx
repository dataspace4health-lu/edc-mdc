import { useState, useEffect } from "react";
import { ResourceDatasetType } from "../../types";
import client from "../../zodiosClient/client";
import DatasetSeriesCard from "./DatasetSeriesCard";
import DatasetSearchSelector from "../../components/DatasetSearchSelector";

interface DatasetSeriesManagerProps {
  selectedDatasets: number[];
  onChange: (datasetIds: number[]) => void;
}

const DatasetSeriesManager: React.FC<DatasetSeriesManagerProps> = ({
  selectedDatasets,
  onChange,
}) => {
  const [selectedDatasetObjects, setSelectedDatasetObjects] = useState<ResourceDatasetType[]>([]);

  const fetchSelectedDatasets = async () => {
    if (selectedDatasets.length === 0) {
      setSelectedDatasetObjects([]);
      return;
    }

    try {
      const datasets = await Promise.all(
        selectedDatasets.map((id) =>
          client.retrieve_dataset_api_v1_datasets__dataset_id__get({
            params: { dataset_id: id },
            withCredentials: true,
          }),
        ),
      );

      setSelectedDatasetObjects(datasets);
    } catch (error) {
      console.error("Error fetching selected datasets:", error);
    }
  };

  useEffect(() => {
    fetchSelectedDatasets();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(selectedDatasets)]);

  const handleAddDataset = (dataset: ResourceDatasetType) => {
    if (!selectedDatasets.includes(dataset.id)) {
      onChange([...selectedDatasets, dataset.id]);
    }
  };

  const handleRemoveDataset = (index: number) => {
    const newSelectedDatasets = [...selectedDatasets];
    newSelectedDatasets.splice(index, 1);
    onChange(newSelectedDatasets);
    setSelectedDatasetObjects((prev) => prev.filter((_, i) => i !== index));
  };

  const handleMoveUp = (index: number) => {
    if (index === 0) return;
    const newSelectedDatasets = [...selectedDatasets];
    const temp = newSelectedDatasets[index];
    newSelectedDatasets[index] = newSelectedDatasets[index - 1];
    newSelectedDatasets[index - 1] = temp;
    onChange(newSelectedDatasets);
  };

  const handleMoveDown = (index: number) => {
    if (index === selectedDatasets.length - 1) return;
    const newSelectedDatasets = [...selectedDatasets];
    const temp = newSelectedDatasets[index];
    newSelectedDatasets[index] = newSelectedDatasets[index + 1];
    newSelectedDatasets[index + 1] = temp;
    onChange(newSelectedDatasets);
  };

  return (
    <div className='border-l-2 border-lnds-blue p-4'>
      <h3 className='text-lg font-medium mb-4 label-lnds-color'>Member Datasets</h3>

      <DatasetSearchSelector
        status='PUBLISHED'
        selectedIds={selectedDatasets}
        onSelect={handleAddDataset}
        pageSize={5}
        alwaysShowSearch={true}
      />

      <div className='mt-6'>
        <h4 className='text-md font-medium mb-2'>Selected Datasets</h4>
        {selectedDatasetObjects.length === 0 ? (
          <div className='text-center py-4 border border-lnds-color rounded text-gray-500'>
            No datasets selected. Search and add datasets to include in this series.
          </div>
        ) : (
          <div className='space-y-2'>
            {selectedDatasetObjects.map((dataset, index) => (
              <DatasetSeriesCard
                key={dataset.id}
                dataset={dataset}
                position={index + 1}
                onRemove={() => handleRemoveDataset(index)}
                onMoveUp={() => handleMoveUp(index)}
                onMoveDown={() => handleMoveDown(index)}
                isFirst={index === 0}
                isLast={index === selectedDatasetObjects.length - 1}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DatasetSeriesManager;
