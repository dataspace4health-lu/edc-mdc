import { XMarkIcon, ArrowUpIcon, ArrowDownIcon } from "@heroicons/react/24/solid";
import { ResourceDatasetType } from "../../types";

interface DatasetSeriesCardProps {
  dataset: ResourceDatasetType;
  position: number;
  onRemove: () => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
  isFirst: boolean;
  isLast: boolean;
}

const DatasetSeriesCard: React.FC<DatasetSeriesCardProps> = ({
  dataset,
  position,
  onRemove,
  onMoveUp,
  onMoveDown,
  isFirst,
  isLast,
}) => {
  return (
    <div className='border border-lnds-color rounded-md p-4 mb-2'>
      <div className='flex justify-between items-center'>
        <div className='flex items-center'>
          <div className='bg-lnds-dark-blue text-white rounded-full w-6 h-6 flex items-center justify-center mr-2'>
            {position}
          </div>
          <h3 className='font-medium'>{dataset.title}</h3>
        </div>
        <div className='space-x-2 flex'>
          <button
            type='button'
            onClick={onMoveUp}
            disabled={isFirst}
            className={`p-1 rounded ${
              isFirst
                ? "text-gray-300 dark:text-gray-600"
                : "text-gray-500 hover:bg-lnds-dark-blue hover:text-white"
            }`}
            aria-label='Move up'
          >
            <ArrowUpIcon className='h-4 w-4' />
          </button>
          <button
            type='button'
            onClick={onMoveDown}
            disabled={isLast}
            className={`p-1 rounded ${
              isLast
                ? "text-gray-300 dark:text-gray-600"
                : "text-gray-500 hover:bg-lnds-dark-blue hover:text-white"
            }`}
            aria-label='Move down'
          >
            <ArrowDownIcon className='h-4 w-4' />
          </button>
          <button
            type='button'
            onClick={onRemove}
            className='text-gray-400 hover:text-red-500'
            aria-label='Remove dataset'
          >
            <XMarkIcon className='h-5 w-5' />
          </button>
        </div>
      </div>
    </div>
  );
};

export default DatasetSeriesCard;
