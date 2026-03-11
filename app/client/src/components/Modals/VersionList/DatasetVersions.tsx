import { useEffect, useState, useRef, useLayoutEffect } from "react";
import { ResourceDatasetType } from "../../../types";
import {
  deepDiff,
  DatasetVersionsProps,
  fetchDatasetVersions,
  Diff,
  getTimeDiffText,
  formatDataProtectionTypes,
  formatValueWithLabels,
  diffDistributions,
  diffDataDictionaries,
  diffRelations,
  diffQualifiedAttributions,
} from "./Utils";
import { Button } from "@lnds-lu/design-system";
import {
  ChevronDownIcon,
  ChevronUpIcon,
  DocumentMagnifyingGlassIcon,
} from "@heroicons/react/24/solid";
import EmptyScreen from "../../EmptyScreen";
import { fetchFormFields } from "../../../pages/bulk_upload/Loader";
import { rightStatementsLabelsUpload } from "../../../pages/excel_validator/Configs";
import { DistributionDiffSection, DistributionDiff } from "./DistributionDiffSection";
import { notNull } from "../../../pages/bulk_upload/Utils";
import { fetchDataDictionaries } from "../../../pages/DataDictionary/DataDictionaryApi";
import { ResourceDataDictionaryEntry } from "../../../types";
import { DataDictionariesDiffSection, DataDictionaryDiff } from "./DataDictionariesDiffSection";
import { RelationsDiffSection, RelationDiff } from "./RelationsDiffSection";
import {
  QualifiedAttributionsDiffSection,
  QualifiedAttributionDiff,
} from "./QualifiedAttributionsDiffSection";
import {
  IGNORED_FIELDS,
  IGNORED_FIELDS_DISTRIBUTION,
  IGNORED_FIELDS_DATA_DICTIONARY,
  IGNORED_FIELDS_RELATIONS,
  IGNORED_FIELDS_QUALIFIED_ATTRIBUTIONS,
} from "./Configs";
import PreviousVersionsList from "./PreviousVersionsList";
import { DiffBlock } from "../DiffBlock";
import { getDatasetFieldShortLabel } from "../../../schemas/datasetSchema";

interface ChevronToggleIconProps {
  isExpanded: boolean;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [key: string]: any;
}

const ChevronToggleIcon = ({ isExpanded, ...props }: ChevronToggleIconProps) =>
  isExpanded ? (
    <ChevronUpIcon className='w-5 h-5 text-lnds-blue' {...props} />
  ) : (
    <ChevronDownIcon className='w-5 h-5 text-lnds-blue' {...props} />
  );

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const ExpandToggleIcon = (isExpanded: boolean) => (props: any) => (
  <ChevronToggleIcon isExpanded={isExpanded} {...props} />
);

export const DatasetVersions = ({ datasetId }: DatasetVersionsProps) => {
  const [versions, setVersions] = useState<ResourceDatasetType[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false);
  const diffContainerRef = useRef<HTMLDivElement>(null);
  const [height, setHeight] = useState(0);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [formFields, setFormFields] = useState<Record<string, any>>({});
  const [expandedDistributions, setExpandedDistributions] = useState<Record<string, boolean>>({});
  const [expandedDictionaries, setExpandedDictionaries] = useState<Record<string, boolean>>({});
  const [expandedRelations, setExpandedRelations] = useState<Record<string, boolean>>({});
  const [expandedQualifiedAttributions, setExpandedQualifiedAttributions] = useState<
    Record<string, boolean>
  >({});
  const [currentDataDictionaries, setCurrentDataDictionaries] = useState<
    ResourceDataDictionaryEntry[]
  >([]);
  const [previousDataDictionaries, setPreviousDataDictionaries] = useState<
    ResourceDataDictionaryEntry[]
  >([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        setIsLoading(true);
        const versionsData = await fetchDatasetVersions(datasetId);
        setVersions(versionsData);

        const currentVersion = versionsData.find((v) => v.id === datasetId);
        if (!currentVersion) {
          console.warn("Current version not found for datasetId", datasetId);
          setCurrentDataDictionaries([]);
          setPreviousDataDictionaries([]);
          return;
        }

        const dataCurrent = await fetchDataDictionaries(currentVersion.id);
        setCurrentDataDictionaries(dataCurrent);

        if (currentVersion.previous_version_dataset_id) {
          const dataPrevious = await fetchDataDictionaries(
            currentVersion.previous_version_dataset_id,
          );
          setPreviousDataDictionaries(dataPrevious);
        } else {
          setPreviousDataDictionaries([]);
          console.log("No previous version found");
        }
      } catch (error) {
        console.error("Failed to fetch data", error);
        setCurrentDataDictionaries([]);
        setPreviousDataDictionaries([]);
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, [datasetId]);

  useEffect(() => {
    setExpandedDistributions({});
    setExpandedDictionaries({});
    setExpandedRelations({});
    setExpandedQualifiedAttributions({});
    setIsExpanded(false);
  }, [datasetId]);

  useEffect(() => {
    const loadFormFields = async () => {
      try {
        const data = await fetchFormFields();
        setFormFields(data);
      } catch (error) {
        console.error("Failed to fetch form fields", error);
      }
    };
    loadFormFields();
  }, []);

  const hasNoPreviousVersions = versions.length === 1 && versions[0].id === datasetId;

  const toggleDistribution = (distId: string) => {
    setExpandedDistributions((prev) => {
      const newExpanded = { ...prev, [distId]: !prev[distId] };
      return newExpanded;
    });
  };

  const toggleDictionaryExpand = (id: number | string) => {
    const key = id.toString();
    setExpandedDictionaries((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const toggleRelation = (key: string) => {
    setExpandedRelations((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const toggleQualifiedAttribution = (key: string) => {
    setExpandedQualifiedAttributions((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  useLayoutEffect(() => {
    if (isExpanded) {
      if (diffContainerRef.current) {
        setHeight(diffContainerRef.current.scrollHeight);
      }
    } else {
      setHeight(0);
    }
  }, [
    isExpanded,
    versions,
    expandedDistributions,
    expandedDictionaries,
    expandedRelations,
    expandedQualifiedAttributions,
  ]);

  if (isLoading) {
    return <div className='px-1 sm:px-4' />;
  }

  if (hasNoPreviousVersions)
    return <EmptyScreen message='No versions yet' Icon={DocumentMagnifyingGlassIcon} />;

  const currentVersion = versions[versions.length - 1];
  const previousVersion = versions.length > 1 ? versions[versions.length - 2] : null;

  let diffs = previousVersion ? deepDiff(previousVersion, currentVersion) : [];
  const distributionDiffs = diffDistributions(
    previousVersion?.distributions,
    currentVersion.distributions,
  );
  diffs = [...diffs, ...distributionDiffs];
  diffs = diffs.filter((diff) => {
    if (diff.path === "periodicity.value") return false;
    const topLevelField = diff.path.split(".")[0];
    return !IGNORED_FIELDS.includes(topLevelField);
  });

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const formatValue = (path: string, val: any) => {
    if (val === null || val === undefined) return "";
    if (path === "rights_statement") {
      const normalizedMap = Object.fromEntries(
        Object.entries(rightStatementsLabelsUpload).map(([k, v]) => [k.toLowerCase(), v]),
      );
      const normalizedVal = val.toLowerCase();
      return normalizedMap[normalizedVal] || val;
    }
    if (path.includes("data_protection_types")) {
      return formatDataProtectionTypes(val);
    }

    return formatValueWithLabels(val, formFields, path);
  };

  const distributionDiffGroups = diffs
    .filter((diff) => diff.path.startsWith("distributions["))
    .map((diff) => {
      const match = diff.path.match(/^distributions\[(.+?)\](?:\.(.+))?$/);
      if (!match) return null;
      const [, title, subField] = match;

      return {
        id: title,
        diff: {
          ...diff,
          field: subField,
        },
      };
    })
    .filter(notNull)
    .filter(({ diff }) => {
      const field = diff.field;
      return !field || !IGNORED_FIELDS_DISTRIBUTION.includes(field);
    })
    .reduce(
      (acc, { id, diff }) => {
        if (!acc[id]) acc[id] = [];
        acc[id].push(diff);
        return acc;
      },
      {} as Record<string, DistributionDiff[]>,
    );

  const dataDictionaryDiffGroups = diffDataDictionaries(
    previousDataDictionaries,
    currentDataDictionaries,
  )
    .map((diff) => {
      const match = diff.path.match(/^data_dictionaries\[(.+?)\](?:\.(.+))?$/);
      if (!match) return null;
      const [, fieldName, subField] = match;
      return { id: fieldName, diff: { ...diff, field: subField ?? null } };
    })
    .filter(notNull)
    .filter(({ diff }) => !diff.field || !IGNORED_FIELDS_DATA_DICTIONARY.includes(diff.field))
    .reduce(
      (acc, { id, diff }) => {
        if (!acc[id]) acc[id] = [];
        acc[id].push(diff);
        return acc;
      },
      {} as Record<string, DataDictionaryDiff[]>,
    );

  const relationDiffGroups = diffRelations(
    previousVersion?.source_relations ?? [],
    currentVersion.source_relations ?? [],
  )
    .map((diff) => {
      const match = diff.path.match(/^relations\[(.+?)\](?:\.(.+))?$/);
      if (!match) return null;
      const [, key, subField] = match;
      return { id: key, diff: { ...diff, field: subField ?? null } as RelationDiff };
    })
    .filter(notNull)
    .filter(({ diff }) => !diff.field || !IGNORED_FIELDS_RELATIONS.includes(diff.field))
    .reduce(
      (acc, { id, diff }) => {
        if (!acc[id]) acc[id] = [];
        acc[id].push(diff);
        return acc;
      },
      {} as Record<string, RelationDiff[]>,
    );

  const qualifiedAttributionDiffGroups = diffQualifiedAttributions(
    previousVersion?.qualified_attributions ?? [],
    currentVersion.qualified_attributions ?? [],
  )
    .map((diff) => {
      const match = diff.path.match(/^qualified_attributions\[(.+?)\](?:\.(.+))?$/);
      if (!match) return null;
      const [, key, subField] = match;
      return { id: key, diff: { ...diff, field: subField ?? null } as QualifiedAttributionDiff };
    })
    .filter(notNull)
    .filter(
      ({ diff }) => !diff.field || !IGNORED_FIELDS_QUALIFIED_ATTRIBUTIONS.includes(diff.field),
    )
    .reduce(
      (acc, { id, diff }) => {
        if (!acc[id]) acc[id] = [];
        acc[id].push(diff);
        return acc;
      },
      {} as Record<string, QualifiedAttributionDiff[]>,
    );

  const filteredDiffs = diffs.filter((diff) => !diff.path.startsWith("distributions["));
  const hasAnyChanges =
    filteredDiffs.length > 0 ||
    Object.keys(distributionDiffGroups).length > 0 ||
    Object.keys(dataDictionaryDiffGroups).length > 0 ||
    Object.keys(relationDiffGroups).length > 0 ||
    Object.keys(qualifiedAttributionDiffGroups).length > 0;

  const renderDiff = (diff: Diff, index: number) => {
    const { path, oldValue, newValue } = diff;
    const FieldName = path.split(".")[0];

    // Skip contact_emails since will be combined with contact_names
    if (FieldName === "contact_emails") return null;

    const label = getDatasetFieldShortLabel(FieldName);
    if (!label) return null;

    let formattedOld = oldValue == null ? "" : formatValue(path, oldValue);
    let formattedNew = newValue == null ? "" : formatValue(path, newValue);

    if (FieldName === "contact_names") {
      const emailsDiff = filteredDiffs.find((d) => d.path.split(".")[0] === "contact_emails");
      const oldEmails = emailsDiff?.oldValue || [];
      const newEmails = emailsDiff?.newValue || [];

      const combine = (names: string[], emails: string[]) =>
        names.map((name, i) => (emails[i] ? `${name} (${emails[i]})` : name)).join(", ");

      formattedOld = combine(oldValue || [], oldEmails);
      formattedNew = combine(newValue || [], newEmails);
    }

    return <DiffBlock key={index} label={label} oldValue={formattedOld} newValue={formattedNew} />;
  };

  return (
    <div className='px-1 sm:px-4 space-y-8'>
      {previousVersion && (
        <div className='border border-lnds-light-gray dark:border-lnds-gray rounded-lg p-5 space-y-4 bg-white dark:bg-lnds-gray/10'>
          <div className='flex flex-wrap items-center justify-between'>
            <div className='flex flex-wrap items-center'>
              <span className='text-base font-bold text-lnds-gray dark:text-white mr-2'>
                Changes from last version
              </span>
              <span className='bg-lnds-green/20 text-lnds-green px-3 py-1 rounded-full text-xs font-semibold mr-2 border border-lnds-green/20'>
                Current Version
              </span>
              <span className='text-sm text-lnds-gray dark:text-lnds-lightest-gray mr-2'>
                compared to
              </span>
              <span className='bg-lnds-red/20 text-lnds-red px-3 py-1 rounded-full text-xs font-semibold border border-lnds-red/20'>
                Last Version (
                {new Date(previousVersion.submitted_at).toLocaleDateString("en-US", {
                  month: "long",
                  day: "numeric",
                  year: "numeric",
                })}
                )
              </span>
            </div>

            <Button
              onClick={() => setIsExpanded(!isExpanded)}
              label={isExpanded ? "Hide Changes" : "Show Changes"}
              Icon={ExpandToggleIcon(isExpanded)}
              btnType='transparent'
            />
          </div>

          <div className='flex justify-between items-center'>
            <div className='text-sm text-lnds-gray dark:text-lnds-lightest-gray font-medium'>
              {getTimeDiffText(currentVersion.submitted_at, new Date().toISOString())}
            </div>
          </div>

          <div
            style={{
              height: isExpanded ? `${height}px` : "0px",
              overflow: "hidden",
              transition: "height 0.4s ease",
            }}
          >
            <div ref={diffContainerRef}>
              {hasAnyChanges ? (
                <div className='pt-4 space-y-6'>
                  <div className='space-y-2'>
                    {diffs
                      .filter((diff) => !diff.path.startsWith("distributions["))
                      .map(renderDiff)}
                  </div>
                  {Object.keys(distributionDiffGroups).length > 0 && (
                    <div className='space-y-6 pt-4 border-t border-lnds-light-gray dark:border-lnds-gray'>
                      <h3 className='text-lg font-bold text-lnds-gray dark:text-white mb-2'>
                        Distribution Changes
                      </h3>
                      {Object.entries(distributionDiffGroups).map(([distId, diffs], index) => (
                        <DistributionDiffSection
                          key={distId}
                          compositeKey={distId}
                          index={index + 1}
                          diffs={diffs}
                          currentDistributions={currentVersion.distributions}
                          previousDistributions={previousVersion?.distributions || []}
                          formFields={formFields}
                          onToggleExpand={() => toggleDistribution(distId)}
                        />
                      ))}
                    </div>
                  )}
                  {Object.keys(dataDictionaryDiffGroups).length > 0 && (
                    <div className='space-y-6 pt-4 border-t border-lnds-light-gray dark:border-lnds-gray'>
                      <h3 className='text-lg font-bold text-lnds-gray dark:text-white mb-2'>
                        Data Dictionary Changes
                      </h3>
                      {Object.entries(dataDictionaryDiffGroups).map(([fieldName, diffs]) => (
                        <DataDictionariesDiffSection
                          key={fieldName}
                          fieldName={fieldName}
                          diffs={diffs}
                          currentDataDictionaries={currentDataDictionaries}
                          previousDataDictionaries={previousDataDictionaries}
                          onToggleExpand={() => toggleDictionaryExpand(fieldName)}
                        />
                      ))}
                    </div>
                  )}
                  {Object.keys(relationDiffGroups).length > 0 && (
                    <div className='space-y-6 pt-4 border-t border-lnds-light-gray dark:border-lnds-gray'>
                      <h3 className='text-lg font-bold text-lnds-gray dark:text-white mb-2'>
                        Dataset Relation Changes
                      </h3>
                      {Object.entries(relationDiffGroups).map(([key, diffs]) => (
                        <RelationsDiffSection
                          key={key}
                          relationKey={key}
                          diffs={diffs}
                          currentRelations={currentVersion.source_relations ?? []}
                          previousRelations={previousVersion?.source_relations ?? []}
                          onToggleExpand={() => toggleRelation(key)}
                        />
                      ))}
                    </div>
                  )}
                  {Object.keys(qualifiedAttributionDiffGroups).length > 0 && (
                    <div className='space-y-6 pt-4 border-t border-lnds-light-gray dark:border-lnds-gray'>
                      <h3 className='text-lg font-bold text-lnds-gray dark:text-white mb-2'>
                        Qualified Attribution Changes
                      </h3>
                      {Object.entries(qualifiedAttributionDiffGroups).map(([key, diffs]) => (
                        <QualifiedAttributionsDiffSection
                          key={key}
                          qaKey={key}
                          diffs={diffs}
                          currentQAs={currentVersion.qualified_attributions ?? []}
                          previousQAs={previousVersion?.qualified_attributions ?? []}
                          onToggleExpand={() => toggleQualifiedAttribution(key)}
                        />
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className='text-lnds-gray dark:text-lnds-lightest-gray'>
                  No differences were detected between the current and previous version.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      <PreviousVersionsList versions={versions} currentVersion={currentVersion} />
    </div>
  );
};
