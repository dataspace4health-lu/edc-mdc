import {
  ResourceDataDictionaryEntry,
  ResourceAuthenticSourceLabel,
  ResourceDatasetType,
  DatasetStatusEnum,
} from "../../types";
import StatusBadge from "../../components/StatusBadge";

const ReadOnlyAuthenticSourceCell = ({
  labels,
  entry,
  dataset,
}: {
  labels: ResourceAuthenticSourceLabel[];
  entry: ResourceDataDictionaryEntry;
  dataset: ResourceDatasetType;
}) => {
  if (
    dataset.status !== DatasetStatusEnum.PUBLISHED &&
    dataset.status !== DatasetStatusEnum.DEPRECATED
  ) {
    return "Pending after publication";
  }

  if (!entry.is_authentic_source) {
    return "No";
  }

  const label = labels.find((label) => label.data_dictionary_entry_id === entry.id);

  if (!label) {
    return "Awaiting label";
  }

  return (
    <div className='flex items-center space-x-2'>
      <div className='flex-1 min-w-0'>
        <div className='flex items-center gap-2 mb-1'>
          {label.is_deprecated && <StatusBadge isDeprecated={true} />}
          <div className='font-medium text-lnds-gray dark:text-white truncate'>{label.name}</div>
        </div>
        <div className='text-xs text-gray-500 dark:text-gray-400 truncate'>{label.description}</div>
      </div>
    </div>
  );
};

export default ReadOnlyAuthenticSourceCell;
