import { useState, useEffect, useRef } from "react";
import { appAlerts } from "../../utils/appAlerts";
import {
  TrashIcon,
  XMarkIcon,
  FunnelIcon,
  TableCellsIcon,
  ArrowDownTrayIcon,
  PencilIcon,
  Bars3Icon,
} from "@heroicons/react/24/solid";
import { Link } from "react-router-dom";
import { Button } from "@lnds-lu/design-system";
import { useAlert } from "@lnds-lu/design-system";
import { deleteDataDictionaryEntryById } from "./DataDictionaryApi";
import { ResourceDataDictionaryEntry, DatasetStatusEnum, ResourceDatasetType } from "../../types";
import EmptyScreen from "../../components/EmptyScreen";
import { useAuth } from "../../context/AuthContext";
import { useAuthenticSourceLabels } from "../../context/AuthenticSourceLabelsContext";
import AuthenticSourceCell from "./AuthenticSourceCell";
import AuthenticSourceStatusMessage from "./AuthenticSourceStatusMessage";
import ReadOnlyAuthenticSourceCell from "./ReadOnlyAuthenticSourceCell";
import Tooltip from "../../components/Tooltip";
import DataDictionaryReorderMode from "./DataDictionaryReorderMode";

type ColumnType = {
  label: string;
  visible: boolean;
};

const initialColumns: ColumnType[] = [
  { label: "Name", visible: true },
  { label: "Type", visible: true },
  { label: "Description", visible: true },
  { label: "Personally Identifiable", visible: false },
  // { label: "Privacy Risk", visible: false },
  { label: "Required", visible: false },
  { label: "Max Value", visible: false },
  { label: "Min Value", visible: false },
  { label: "Unit", visible: false },
  { label: "Allowed Values", visible: false },
  { label: "Allowed Desc", visible: false },
];

const DataDictionaryTable = ({
  dataset,
  data,
  isEditable,
  onDelete,
  onEdit,
  triggerActivityLogRefresh,
  onReorderComplete,
}: {
  dataset: ResourceDatasetType;
  data: ResourceDataDictionaryEntry[];
  isEditable: boolean;
  onDelete?: (entryId: number) => void;
  onEdit?: (entry: ResourceDataDictionaryEntry) => void;
  triggerActivityLogRefresh?: () => void;
  onReorderComplete?: () => void;
}) => {
  const datasetId = dataset.id;
  const isDatasetInDraft = dataset.status === DatasetStatusEnum.DRAFT;
  const { user } = useAuth();
  const { labels, fetchLabels, canAssignLabels, canMarkAsAuthenticSource } =
    useAuthenticSourceLabels();

  const canAssignLabelsBool = canAssignLabels(dataset.status, user);

  const canMarkAsAuthenticSourceBool = canMarkAsAuthenticSource(dataset, user);

  const [isReorderMode, setIsReorderMode] = useState(false);

  useEffect(() => {
    fetchLabels();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (user?.feature_options.enable_authentic_source) {
    if (!initialColumns.some((col) => col.label === "Authentic Source")) {
      if (canAssignLabelsBool || canMarkAsAuthenticSourceBool) {
        initialColumns.splice(2, 0, { label: "Authentic Source", visible: true });
      } else {
        initialColumns.push({ label: "Authentic Source", visible: false });
      }
    }
  }

  const [columns, setColumns] = useState(initialColumns);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement | null>(null);
  const { setAlert } = useAlert();

  useEffect(() => {
    setColumns(initialColumns);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialColumns]);

  const toggleColumnVisibility = (label: string) => {
    setColumns((prevColumns) =>
      prevColumns.map((col) => (col.label === label ? { ...col, visible: !col.visible } : col)),
    );
  };

  const clearSelection = () => {
    setColumns((prevColumns) => prevColumns.map((col) => ({ ...col, visible: false })));
  };

  const renderCellContent = (entry: ResourceDataDictionaryEntry, colLabel: string) => {
    switch (colLabel) {
      case "Name":
        return entry.field_name;
      case "Type":
        return entry.data_type;
      case "Description":
        return entry.description;
      case "Personally Identifiable":
        return entry.personally_identifiable_variable === null
          ? ""
          : entry.personally_identifiable_variable
            ? "Yes"
            : "No";
      case "Required":
        return entry.required === null ? "" : entry.required ? "Yes" : "No";
      case "Max Value":
        return entry.max_allowed_value;
      case "Min Value":
        return entry.min_allowed_value;
      case "Unit":
        return entry.variable_unit;
      case "Allowed Values":
        return entry.allowed_values;
      case "Allowed Desc":
        return entry.allowed_values_description;
      case "Authentic Source":
        return canAssignLabelsBool || canMarkAsAuthenticSourceBool ? (
          <AuthenticSourceCell
            entry={entry}
            labels={labels}
            dataset={dataset}
            triggerActivityLogRefresh={triggerActivityLogRefresh}
          />
        ) : (
          <ReadOnlyAuthenticSourceCell entry={entry} labels={labels} dataset={dataset} />
        );
      default:
        return "";
    }
  };

  const renderTableHeader = () => (
    <thead className='bg-lnds-purple dark:bg-gray-700 text-white sticky top-0 z-10'>
      <tr>
        {columns
          .filter((col) => col.visible)
          .map((col) => (
            <th key={col.label} className='px-4 py-3 text-left font-semibold text-lg w-[10%]'>
              {col.label}
            </th>
          ))}
        {isEditable && (
          <th className='px-4 py-3 text-center font-semibold text-lg w-[10%]'>Actions</th>
        )}
      </tr>
    </thead>
  );

  const renderTableBody = () => (
    <tbody className='bg-white dark:bg-gray-800 divide-y divide-gray-300 dark:divide-gray-700'>
      {data.map((entry) => (
        <tr key={entry.id} className='hover:bg-gray-100 dark:hover:bg-gray-700'>
          {columns
            .filter((col) => col.visible)
            .map((col) => (
              <td key={col.label} className='px-4 py-3 text-gray-800 dark:text-gray-200 w-[10%]'>
                {renderCellContent(entry, col.label)}
              </td>
            ))}
          {isEditable && (
            <td className='px-4 py-3'>
              <div className='flex justify-center items-center gap-2'>
                <Tooltip text='Edit Entry'>
                  <PencilIcon
                    className='h-6 w-6 icon-lnds-color cursor-pointer'
                    onClick={() => onEdit && onEdit(entry)}
                  />
                </Tooltip>
                <Tooltip text='Delete Entry'>
                  <TrashIcon
                    className='h-6 w-6 icon-lnds-color cursor-pointer'
                    onClick={() => handleDeleteClick(entry.id!)}
                  />
                </Tooltip>
              </div>
            </td>
          )}
        </tr>
      ))}
    </tbody>
  );

  const handleDeleteClick = async (entryId: number) => {
    try {
      await deleteDataDictionaryEntryById(datasetId, entryId);
      onDelete && onDelete(entryId);
      triggerActivityLogRefresh?.();
      setAlert(appAlerts.dataDictionaryEntryDeleted());
    } catch (error) {
      setAlert(appAlerts.dataDictionaryDeleteFailed());
    }
  };

  const handleStartReorder = () => {
    setIsReorderMode(true);
  };

  const handleReorderComplete = () => {
    setIsReorderMode(false);
    onReorderComplete?.();
  };

  const handleReorderCancel = () => {
    setIsReorderMode(false);
  };

  return (
    <div className='relative pb-64'>
      {data.length === 0 ? (
        <>
          <div className='flex items-center justify-end mb-4'>
            {!isEditable && isDatasetInDraft && (
              <Button
                btnType='secondary'
                Link={Link}
                to={`/datasets/${datasetId}/dictionaries`}
                Icon={PencilIcon}
                label='Manage Dictionaries'
              />
            )}
          </div>
          <EmptyScreen message='No entries available' Icon={TableCellsIcon} />
        </>
      ) : (
        <>
          {isReorderMode ? (
            <DataDictionaryReorderMode
              datasetId={datasetId}
              data={data}
              columns={columns}
              renderCellContent={renderCellContent}
              onComplete={handleReorderComplete}
              onCancel={handleReorderCancel}
            />
          ) : (
            <>
              <div className='flex items-center justify-end mb-4'>
                <div className='relative'>
                  <div className='flex items-center space-x-2'>
                    {!isEditable && isDatasetInDraft && (
                      <Button
                        btnType='secondary'
                        Link={Link}
                        to={`/datasets/${datasetId}/dictionaries`}
                        Icon={PencilIcon}
                        label='Manage Dictionaries'
                      />
                    )}
                    {isEditable && data.length > 1 && (
                      <Button
                        btnType='secondary'
                        label='Reorder'
                        Icon={Bars3Icon}
                        onClick={handleStartReorder}
                      />
                    )}
                    <Link to={`/api/v1/datasets/${datasetId}/data-dictionaries/download`} target="_blank" rel="noopener noreferrer">
                      <Button
                        btnType='secondary'
                        label='Download as CSV'
                        Icon={ArrowDownTrayIcon}
                        onClick={() => {}}
                      />
                    </Link>
                    <Button
                      label='Filter Columns'
                      Icon={FunnelIcon}
                      onClick={() => setDropdownOpen(!dropdownOpen)}
                    />
                  </div>
                  {dropdownOpen && (
                    <div
                      ref={dropdownRef}
                      className='absolute z-20 right-0 mt-2 bg-white dark:bg-gray-800 rounded-lg w-64 border border-lnds-color'
                    >
                      <div className='py-3 px-4'>
                        <div className='flex justify-between items-center'>
                          <XMarkIcon
                            className='h-5 w-5 ml-auto text-gray-500 dark:text-gray-200 cursor-pointer'
                            onClick={() => setDropdownOpen(false)}
                          />
                        </div>
                        <div className='space-y-2 mt-2'>
                          {columns.map((col) => (
                            <div key={col.label} className='flex items-center'>
                              <input
                                type='checkbox'
                                id={col.label}
                                checked={col.visible}
                                onChange={() => toggleColumnVisibility(col.label)}
                                className='form-checkbox h-4 w-4 text-lnds-blue border-gray-300 rounded focus:ring-2 focus:ring-lnds-blue'
                              />
                              <label
                                htmlFor={col.label}
                                className='ml-2 text-gray-700 dark:text-gray-200'
                              >
                                {col.label}
                              </label>
                            </div>
                          ))}
                        </div>
                        <button className='text-lnds-blue underline mt-2' onClick={clearSelection}>
                          Clear Selection
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
              <div className='flex-1 overflow-hidden'>
                <AuthenticSourceStatusMessage dataset={dataset} entries={data} />

                {/* Simple scroll hint when multiple columns are visible */}
                {columns.filter((col) => col.visible).length > 3 && (
                  <div className='text-sm text-gray-500 dark:text-gray-400 text-center mb-2'>
                    ← → Scroll horizontally to see hidden columns
                  </div>
                )}

                <div
                  className='overflow-auto rounded-lg max-h-[70vh]'
                  style={{ minHeight: "400px" }}
                >
                  <table className='min-w-full table-fixed divide-y divide-gray-300 dark:divide-gray-700'>
                    {renderTableHeader()}
                    {renderTableBody()}
                  </table>
                  {/* Add padding at the bottom to ensure dropdown has space */}
                  <div className='h-80'></div>
                </div>
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
};

export default DataDictionaryTable;
