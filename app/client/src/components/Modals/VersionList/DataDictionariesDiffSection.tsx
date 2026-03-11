import { useState } from "react";
import { ChevronDownIcon, ChevronUpIcon } from "@heroicons/react/24/solid";
import { ResourceDataDictionaryEntry } from "../../../types";
import { DataDictionaryFieldLabelMap, IGNORED_FIELDS_DATA_DICTIONARY } from "./Configs";
import { DiffBlock } from "../DiffBlock";
import { Diff } from "./Utils";

export type DataDictionaryDiff = Diff & {
  field: string | null;
};

type Props = {
  fieldName: string;
  diffs: DataDictionaryDiff[];
  currentDataDictionaries: ResourceDataDictionaryEntry[];
  previousDataDictionaries: ResourceDataDictionaryEntry[];
  onToggleExpand?: () => void;
};

export const DataDictionariesDiffSection = ({
  fieldName,
  diffs,
  currentDataDictionaries,
  previousDataDictionaries,
  onToggleExpand,
}: Props) => {
  const [expanded, setExpanded] = useState(false);
  const toggle = () => {
    setExpanded((e) => !e);
    if (onToggleExpand) onToggleExpand();
  };

  const currentEntry = currentDataDictionaries.find((d) => d.field_name === fieldName);
  const previousEntry = previousDataDictionaries.find((d) => d.field_name === fieldName);

  const isUpdated = !!currentEntry && !!previousEntry && diffs.length > 0;

  return (
    <div className='border border-lnds-light-gray dark:border-lnds-gray rounded-lg p-4 bg-white dark:bg-lnds-gray/10'>
      <button
        onClick={toggle}
        className='w-full text-left text-base font-semibold text-lnds-gray dark:text-white flex justify-between items-center hover:text-lnds-dark-blue dark:hover:text-lnds-blue transition-colors'
      >
        <span className='flex items-center gap-2'>
          Data Dictionary: {fieldName}
          {previousEntry && !currentEntry && (
            <span className='bg-lnds-red/20 text-lnds-red px-3 py-1 text-xs rounded-full font-medium border border-lnds-red/20'>
              Deleted
            </span>
          )}
          {currentEntry && !previousEntry && (
            <span className='bg-lnds-green/20 text-lnds-green px-3 py-1 text-xs rounded-full font-medium border border-lnds-green/20'>
              New
            </span>
          )}
          {isUpdated && (
            <span className='bg-lnds-yellow/20 text-lnds-yellow px-3 py-1 text-xs rounded-full font-medium border border-lnds-yellow/20'>
              Updated
            </span>
          )}
        </span>
        {expanded ? (
          <ChevronUpIcon className='w-5 h-5 text-lnds-blue' />
        ) : (
          <ChevronDownIcon className='w-5 h-5 text-lnds-blue' />
        )}
      </button>

      {expanded && (
        <div className='mt-4 space-y-3 text-sm'>
          {diffs.map((diff) => {
            const isWholeObject = !diff.field;

            if (isWholeObject) {
              const entry = diff.newValue || diff.oldValue || {};
              const isAdded = !!diff.newValue && !diff.oldValue;
              return Object.keys(entry)
                .filter(
                  (k) =>
                    !IGNORED_FIELDS_DATA_DICTIONARY.includes(k) &&
                    entry[k] != null &&
                    entry[k] !== "",
                )
                .map((key) => {
                  const label = DataDictionaryFieldLabelMap[key] || key;
                  const value = String(entry[key] ?? "");
                  return (
                    <DiffBlock
                      key={key}
                      label={label}
                      oldValue={!isAdded ? value : undefined}
                      newValue={isAdded ? value : undefined}
                    />
                  );
                });
            }

            const label = DataDictionaryFieldLabelMap[diff.field ?? ""] || diff.field;
            return (
              <DiffBlock
                key={diff.path}
                label={label ?? ""}
                oldValue={diff.oldValue != null ? String(diff.oldValue) : undefined}
                newValue={diff.newValue != null ? String(diff.newValue) : undefined}
              />
            );
          })}
        </div>
      )}
    </div>
  );
};
