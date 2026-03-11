import { useState } from "react";
import { ArrowUpIcon, ArrowDownIcon, Bars3Icon, XMarkIcon } from "@heroicons/react/24/solid";
import { Button } from "@lnds-lu/design-system";
import { useAlert } from "@lnds-lu/design-system";
import { bulkUpdatePositions } from "./DataDictionaryApi";
import { ResourceDataDictionaryEntry } from "../../types";
import DismissibleAlert from "../../components/DismissibleAlert";
import { appAlerts } from "../../utils/appAlerts";

interface DataDictionaryReorderModeProps {
  datasetId: number;
  data: ResourceDataDictionaryEntry[];
  columns: { label: string; visible: boolean }[];
  renderCellContent: (entry: ResourceDataDictionaryEntry, colLabel: string) => React.ReactNode;
  onComplete: () => void;
  onCancel: () => void;
}

const DataDictionaryReorderMode: React.FC<DataDictionaryReorderModeProps> = ({
  datasetId,
  data,
  columns,
  renderCellContent,
  onComplete,
  onCancel,
}) => {
  const [tempData, setTempData] = useState<ResourceDataDictionaryEntry[]>([...data]);
  const { setAlert } = useAlert();

  const handleMoveUp = (index: number) => {
    if (index === 0) return;
    const newData = [...tempData];
    const temp = newData[index];
    newData[index] = newData[index - 1];
    newData[index - 1] = temp;
    setTempData(newData);
  };

  const handleMoveDown = (index: number) => {
    if (index === tempData.length - 1) return;
    const newData = [...tempData];
    const temp = newData[index];
    newData[index] = newData[index + 1];
    newData[index + 1] = temp;
    setTempData(newData);
  };

  const handleSaveOrder = async () => {
    try {
      const updates = tempData.map((entry, index) => ({
        entry_id: entry.id!,
        position: index,
      }));

      await bulkUpdatePositions(datasetId, updates);
      setAlert(appAlerts.orderSaved());
      onComplete();
    } catch (error) {
      setAlert(appAlerts.saveOrderFailed());
    }
  };

  return (
    <div>
      {/* Toolbar */}
      <div className='flex items-center justify-end mb-4'>
        <div className='flex items-center space-x-2'>
          <Button btnType='primary' label='Save Order' Icon={Bars3Icon} onClick={handleSaveOrder} />
          <Button btnType='secondary' label='Cancel' Icon={XMarkIcon} onClick={onCancel} />
        </div>
      </div>

      {/* Info banner */}
      <DismissibleAlert
        message='Use the arrow buttons to rearrange entries. Click "Save Order" when done or "Cancel" to discard changes.'
        type='info'
        className='mb-4'
      />

      {/* Simple scroll hint */}
      {columns.filter((col) => col.visible).length > 3 && (
        <div className='text-sm text-gray-500 dark:text-gray-400 text-center mb-2'>
          ← → Scroll horizontally to see hidden columns
        </div>
      )}

      {/* Table */}
      <div className='overflow-auto rounded-lg max-h-[70vh]' style={{ minHeight: "400px" }}>
        <table className='min-w-full table-fixed divide-y divide-gray-300 dark:divide-gray-700'>
          <thead className='bg-lnds-purple dark:bg-gray-700 text-white'>
            <tr>
              {columns
                .filter((col) => col.visible)
                .map((col) => (
                  <th key={col.label} className='px-4 py-3 text-left font-semibold text-lg w-[10%]'>
                    {col.label}
                  </th>
                ))}
              <th className='px-4 py-3 text-center font-semibold text-lg w-[10%]'>Reorder</th>
            </tr>
          </thead>
          <tbody className='bg-white dark:bg-gray-800 divide-y divide-gray-300 dark:divide-gray-700'>
            {tempData.map((entry, index) => (
              <tr key={entry.id} className='hover:bg-gray-100 dark:hover:bg-gray-700'>
                {columns
                  .filter((col) => col.visible)
                  .map((col) => (
                    <td
                      key={col.label}
                      className='px-4 py-3 text-gray-800 dark:text-gray-200 w-[10%]'
                    >
                      {renderCellContent(entry, col.label)}
                    </td>
                  ))}
                <td className='px-4 py-3'>
                  <div className='flex justify-center items-center space-x-2'>
                    <button
                      type='button'
                      onClick={() => handleMoveUp(index)}
                      disabled={index === 0}
                      className={`p-1 rounded ${
                        index === 0
                          ? "text-gray-300 dark:text-gray-600 cursor-not-allowed"
                          : "text-gray-500 hover:bg-lnds-dark-blue hover:text-white cursor-pointer"
                      }`}
                      aria-label='Move up'
                    >
                      <ArrowUpIcon className='h-5 w-5' />
                    </button>
                    <button
                      type='button'
                      onClick={() => handleMoveDown(index)}
                      disabled={index === tempData.length - 1}
                      className={`p-1 rounded ${
                        index === tempData.length - 1
                          ? "text-gray-300 dark:text-gray-600 cursor-not-allowed"
                          : "text-gray-500 hover:bg-lnds-dark-blue hover:text-white cursor-pointer"
                      }`}
                      aria-label='Move down'
                    >
                      <ArrowDownIcon className='h-5 w-5' />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className='h-80'></div>
      </div>
    </div>
  );
};

export default DataDictionaryReorderMode;
