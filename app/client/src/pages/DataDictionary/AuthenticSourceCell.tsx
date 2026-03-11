import { useState } from "react";
import { ChevronDownIcon } from "@heroicons/react/24/solid";
import AuthenticSourceDropdown from "./AuthenticSourceDropdown";
import {
  ResourceDataDictionaryEntry,
  ResourceAuthenticSourceLabel,
  ResourceDatasetType,
} from "../../types";
import { ToggleButton } from "@lnds-lu/design-system";
import { useAuthenticSourceLabels } from "../../context/AuthenticSourceLabelsContext";
import { useAuth } from "../../context/AuthContext";
import StatusBadge from "../../components/StatusBadge";

const AuthenticSourceCell = ({
  labels,
  entry,
  dataset,
  triggerActivityLogRefresh,
}: {
  labels: ResourceAuthenticSourceLabel[];
  entry: ResourceDataDictionaryEntry;
  dataset: ResourceDatasetType;
  triggerActivityLogRefresh?: () => void;
}) => {
  const { user } = useAuth();
  const [isAuthentic, setIsAuthentic] = useState(entry.is_authentic_source || false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const {
    createLabel,
    assignAuthenticSouceLabel,
    toggleAuthenticSourceEntry,
    canAssignLabels,
    activeLabels,
  } = useAuthenticSourceLabels();

  const canAssignLabelsBool = canAssignLabels(dataset.status, user);

  const handleCheckboxChange = () => {
    if (!isAuthentic) {
      setIsDropdownOpen(true);
    }
    setIsAuthentic(!isAuthentic);
    toggleAuthenticSourceEntry(entry.id!, !isAuthentic);
    triggerActivityLogRefresh?.();
  };

  const handleLabelSelect = (labelId: number) => {
    assignAuthenticSouceLabel(entry.id!, labelId, dataset.id);
    setIsDropdownOpen(false);
    triggerActivityLogRefresh?.();
  };

  const handleCreateLabel = (newLabel: ResourceAuthenticSourceLabel) => {
    createLabel(newLabel);
    assignAuthenticSouceLabel(entry.id!, newLabel.id, dataset.id);
    setIsDropdownOpen(false);
    triggerActivityLogRefresh?.();
  };

  const selectedLabel = labels.find((label) => label.data_dictionary_entry_id === entry.id);

  return (
    <div className='flex items-center space-x-2'>
      <ToggleButton
        key={`authentic-source-toggle-${entry.id}`}
        name={`authentic-source-${entry.id}`}
        label=''
        onChange={() => handleCheckboxChange()}
        defaultValue={isAuthentic}
      />

      {canAssignLabelsBool && isAuthentic && (
        <div className='flex-1 min-w-0 relative'>
          <button
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className='flex items-center justify-between w-full px-2 py-1 text-xs bg-gray-50 dark:bg-gray-700 border border-lnds-color rounded focus:outline-none focus:ring-1 focus:ring-lnds-purple'
          >
            <div className='flex items-center gap-2 flex-1 min-w-0'>
              {selectedLabel && selectedLabel.is_deprecated && <StatusBadge isDeprecated={true} />}
              <span className='truncate text-left'>
                {selectedLabel ? selectedLabel.name : "Select Label..."}
              </span>
            </div>
            <ChevronDownIcon className='h-3 w-3 ml-1 flex-shrink-0' />
          </button>

          {isDropdownOpen && (
            <AuthenticSourceDropdown
              isOpen={isDropdownOpen}
              onClose={() => setIsDropdownOpen(false)}
              labels={activeLabels}
              selectedLabelId={selectedLabel ? selectedLabel.id : undefined}
              onLabelSelect={handleLabelSelect}
              onCreateLabel={handleCreateLabel}
              datasetId={dataset.id}
              datasetPreviousVersionId={dataset.previous_version_dataset_id}
            />
          )}
        </div>
      )}

      {!canAssignLabelsBool && isAuthentic && (
        <div className='flex-1 min-w-0'>
          <span className='text-xs text-gray-500 dark:text-gray-400'>
            {selectedLabel ? selectedLabel.name : "No Labels Assigned"}
          </span>
        </div>
      )}
    </div>
  );
};

export default AuthenticSourceCell;
