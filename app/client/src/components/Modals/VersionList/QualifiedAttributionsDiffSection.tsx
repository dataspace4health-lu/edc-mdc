import { useState } from "react";
import { ChevronDownIcon, ChevronUpIcon } from "@heroicons/react/24/solid";
import {
  QualifiedAttributionFieldLabelMap,
  IGNORED_FIELDS_QUALIFIED_ATTRIBUTIONS,
} from "./Configs";
import { DiffBlock } from "../DiffBlock";
import { Diff, QualifiedAttribution, getQualifiedAttributionKey } from "./Utils";

export type QualifiedAttributionDiff = Diff & {
  field: string | null;
};

type Props = {
  qaKey: string;
  diffs: QualifiedAttributionDiff[];
  currentQAs: QualifiedAttribution[];
  previousQAs: QualifiedAttribution[];
  onToggleExpand?: () => void;
};

const getQALabel = (qaKey: string, qa?: QualifiedAttribution): string => {
  if (!qa) {
    // Parse the key itself for a label
    const parts = qaKey.split("|");
    return `Organisation ID ${parts[0] ?? "unknown"} - ${parts[1] ?? "unknown"}`;
  }

  const orgName = qa.organisation_name ?? `Organisation ID ${qa.organisation_id ?? "unknown"}`;
  const role = qa.role ?? "unknown";
  return `${orgName} - ${role}`;
};

export const QualifiedAttributionsDiffSection = ({
  qaKey,
  diffs,
  currentQAs,
  previousQAs,
  onToggleExpand,
}: Props) => {
  const [expanded, setExpanded] = useState(false);
  const toggle = () => {
    setExpanded((e) => !e);
    if (onToggleExpand) onToggleExpand();
  };

  const currentEntry = currentQAs.find((qa) => getQualifiedAttributionKey(qa) === qaKey);
  const previousEntry = previousQAs.find((qa) => getQualifiedAttributionKey(qa) === qaKey);

  const isUpdated = !!currentEntry && !!previousEntry && diffs.length > 0;

  const label = getQALabel(qaKey, currentEntry || previousEntry);

  return (
    <div className='border border-lnds-light-gray dark:border-lnds-gray rounded-lg p-4 bg-white dark:bg-lnds-gray/10'>
      <button
        onClick={toggle}
        className='w-full text-left text-base font-semibold text-lnds-gray dark:text-white flex justify-between items-center hover:text-lnds-dark-blue dark:hover:text-lnds-blue transition-colors'
      >
        <span className='flex items-center gap-2'>
          Qualified Attribution: {label}
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
                    !IGNORED_FIELDS_QUALIFIED_ATTRIBUTIONS.includes(k) &&
                    entry[k] != null &&
                    entry[k] !== "",
                )
                .map((key) => {
                  const fieldLabel = QualifiedAttributionFieldLabelMap[key] || key;
                  const value = String(entry[key] ?? "");
                  return (
                    <DiffBlock
                      key={key}
                      label={fieldLabel}
                      oldValue={!isAdded ? value : undefined}
                      newValue={isAdded ? value : undefined}
                    />
                  );
                });
            }

            const fieldLabel = QualifiedAttributionFieldLabelMap[diff.field ?? ""] || diff.field;
            return (
              <DiffBlock
                key={diff.path}
                label={fieldLabel ?? ""}
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
