import { useState } from "react";
import { Diff } from "./Utils";
import { Distribution, getDistributionKey } from "./Utils";
import { ChevronUpIcon, ChevronDownIcon } from "@heroicons/react/24/solid";
import { formatValueWithLabels } from "./Utils";
import { rightStatementsLabelsUpload } from "../../../pages/excel_validator/Configs";
import distributionSchema, { availabilityOptions } from "../../../schemas/distributionSchema";
import { getDistributionShortLabel } from "../../../schemas/distributionSchema";
import { DiffBlock } from "../DiffBlock";

export type DistributionDiff = Diff & {
  field: string | null;
};

export const DistributionDiffSection = ({
  compositeKey,
  index,
  diffs,
  currentDistributions,
  previousDistributions,
  formFields,
  onToggleExpand,
}: {
  compositeKey: string;
  index: number;
  diffs: DistributionDiff[];
  currentDistributions: Distribution[];
  previousDistributions: Distribution[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  formFields: Record<string, any>;
  onToggleExpand?: () => void;
}) => {
  const [expanded, setExpanded] = useState(false);
  const toggle = () => {
    setExpanded((e) => !e);
    if (onToggleExpand) onToggleExpand();
  };

  const findByKey = (dists: Distribution[], key: string) =>
    dists.find((d) => getDistributionKey(d) === key);

  const currentdist = findByKey(currentDistributions, compositeKey);
  const previousdist = findByKey(previousDistributions, compositeKey);

  const isUpdated = !!currentdist && !!previousdist && diffs.length > 0;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const formatValue = (path: string, val: any): string => {
    if (val === null || val === undefined || val === "") return "";
    if (path === "rights_statement") {
      const normalizedMap = Object.fromEntries(
        Object.entries(rightStatementsLabelsUpload).map(([k, v]) => [k.toLowerCase(), v]),
      );
      const normalizedVal = val.toLowerCase();
      return normalizedMap[normalizedVal] || val;
    }

    if (path.includes("availability")) {
      const match = availabilityOptions.find((opt) => opt.value === val);
      return match?.label || val;
    }

    if ((path === "access_services" || path.endsWith(".access_services")) && Array.isArray(val)) {
      return val.map((s) => s.title).join(", ");
    }

    if ((path === "policy_actions" || path.endsWith(".policy_actions")) && Array.isArray(val)) {
      return val
        .map((p) => {
          const type = p.policy_action_type;
          const constraint = p.policy_constraint_type;
          let details = "";

          if (constraint === "spatial" && p.spatial_restrictions?.length) {
            details = `Restriction: ${p.spatial_restrictions.map((r: { eng_label: string }) => r.eng_label).join(", ")}`;
          } else if (constraint === "temporal") {
            const start = p.temporal_restriction_start;
            const end = p.temporal_restriction_end;
            if (start || end) {
              details = `${start || "N/A"} - ${end || "N/A"}`;
            }
          } else if (constraint === "industry" && p.industry_restriction) {
            details = p.industry_restriction;
          } else if (constraint === "purpose" && p.policy_constraint_value) {
            details = `Restriction: ${p.policy_constraint_value}`;
          }

          const policy = details
            ? `Type: ${type}; Constraint: ${constraint}; ${details}`
            : `Type: ${type}; Constraint: ${constraint}`;
          return `"${policy}"`;
        })
        .join(",");
    }

    if (typeof val === "boolean") {
      return val ? "Yes" : "No";
    }

    return formatValueWithLabels(val, formFields, path);
  };

  return (
    <div className='border border-lnds-light-gray dark:border-lnds-gray rounded-lg p-4 bg-white dark:bg-lnds-gray/10'>
      <button
        onClick={toggle}
        className='w-full text-left text-base font-semibold text-lnds-gray dark:text-white flex justify-between items-center hover:text-lnds-dark-blue dark:hover:text-lnds-blue transition-colors'
      >
        <span className='flex items-center gap-2'>
          Distribution #{index}
          {previousdist && !currentdist && (
            <span className='bg-lnds-red/20 text-lnds-red px-3 py-1 text-xs rounded-full font-medium border border-lnds-red/20'>
              Deleted
            </span>
          )}
          {currentdist && !previousdist && (
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
        <div className='mt-4 space-y-3'>
          {diffs.map((diff) => {
            const isWholeObject = !diff.field;

            if (isWholeObject) {
              const dist = diff.newValue || diff.oldValue || {};
              const isAdded = !!diff.newValue && !diff.oldValue;
              const displayKeys = distributionSchema.map((field) => field.apiFieldName);
              return displayKeys.map((key) => {
                const label = getDistributionShortLabel(key);
                const value = dist?.[key];
                if (
                  value === null ||
                  value === undefined ||
                  value === "" ||
                  (Array.isArray(value) && value.length === 0)
                )
                  return null;

                const formattedValue = formatValue(key, value);

                return (
                  <DiffBlock
                    key={key}
                    label={label}
                    oldValue={!isAdded ? formattedValue : undefined}
                    newValue={isAdded ? formattedValue : undefined}
                  />
                );
              });
            }

            const fieldLabel = getDistributionShortLabel(diff.field ?? "");
            const formattedOld = formatValue(diff.path, diff.oldValue);
            const formattedNew = formatValue(diff.path, diff.newValue);
            const isAdded = diff.oldValue === undefined;
            const isRemoved = diff.newValue === undefined;

            return (
              <div key={diff.path} className='text-sm space-y-1'>
                <DiffBlock
                  label={fieldLabel}
                  oldValue={isRemoved ? formattedOld : !isAdded ? formattedOld : undefined}
                  newValue={isAdded ? formattedNew : !isRemoved ? formattedNew : undefined}
                />
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
