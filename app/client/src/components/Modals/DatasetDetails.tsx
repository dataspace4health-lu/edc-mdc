import { useState, useEffect } from "react";
import { ActivityLogList } from "./ActivityLogList";

import { CommentList } from "./CommentList";
import {
  CircleStackIcon,
  UserIcon,
  CalendarIcon,
  ArrowPathIcon,
  KeyIcon,
  FingerPrintIcon,
  BuildingOfficeIcon,
  CalendarDateRangeIcon,
  LinkIcon,
  DocumentIcon,
  UserGroupIcon,
  ArchiveBoxIcon,
  MapPinIcon,
  DocumentTextIcon,
  PencilSquareIcon,
  RectangleGroupIcon,
  TagIcon,
} from "@heroicons/react/24/solid";
import { DateUtils } from "../../utils/dateTimeHelpers";
import { DistributionSection } from "./DistributionSection";
import {
  ResourceDistributionType,
  ResourceDatasetType,
  ResourceDataDictionaryEntry,
  FormType,
  DatasetStatusEnum,
} from "../../types";
import datasetSchema from "../../schemas/datasetSchema";
import { DatasetDetailsTab } from "./DatasetDetailsTab";
import SeriesDatasetsList from "./SeriesDatasetsList";
import RelationLink from "../RelationLink";
import ApplicableLegislationTags from "../ApplicableLegislationTags";
import ConventionTags from "../ConventionTags";
import IncorrectRelationFlashMessage from "../IncorrectRelationFlashMessage";
import DataDictionaryTable from "../../pages/DataDictionary/DataDictionaryTable";
import { fetchDataDictionaries } from "../../pages/DataDictionary/DataDictionaryApi";
import { Tags, Button, Card } from "@lnds-lu/design-system";
import EmptyScreen from "../EmptyScreen";
import { toReadableFormat } from "../../utils/dataProtectionLabels";
import { rightStatementsLabels } from "../../utils/rightStatementsLabels";
import { Link } from "react-router-dom";
import { DatasetVersions } from "./VersionList/DatasetVersions";
import { QualifiedAttributionsTab } from "../QualifiedAttributionsTab";
import IconList from "../IconList";
import FieldInfoHeader from "../FieldInfoHeader";
import HealthDcatDetailsSection from "./HealthDcatDetailsSection";

// eslint-disable-next-line react-refresh/only-export-components
export enum Tabs {
  DATASET = "Dataset",
  SERIES = "Series",
  DISTRIBUTIONS = "Distributions",
  DATA_DICTIONARY = "Data Dictionary",
  RELATIONS = "Relations",
  QUALIFIED_ATTRIBUTIONS = "Qualified Attributions",
  ACTIVITY_LOGS = "Activity Logs",
  COMMENTS = "Comments",
  MEMBER_DATASETS = "Member Datasets",
  VERSIONS = "Versions",
}

interface DatasetDetailsProps {
  dataset: ResourceDatasetType;
  formFields: FormType;
  refreshComments: boolean;
  currentTab: string;
  setCurrentTab: (tab: string) => void;
}

interface DatasetFieldProps {
  fieldName: string;
  label?: string;
  children: React.ReactNode;
}

type DatasetFieldHeaderProps = {
  fieldName: string;
  label?: string;
};

const datasetFieldMetaByApiField = new Map(
  datasetSchema.map((field) => [
    field.apiFieldName,
    { label: field.shortLabel, explanation: field.explanation },
  ]),
);

const DatasetFieldHeader = (props: Readonly<DatasetFieldHeaderProps>) => {
  const { fieldName, label } = props;
  const meta = datasetFieldMetaByApiField.get(fieldName);

  return (
    <FieldInfoHeader
      as='h3'
      label={label ?? meta?.label ?? fieldName}
      popoverInfo={meta?.explanation}
      labelClassName='label-lnds-color leading-6'
    />
  );
};

const DatasetField = (props: Readonly<DatasetFieldProps>) => {
  const { fieldName, label, children } = props;

  return (
    <div>
      <DatasetFieldHeader fieldName={fieldName} label={label} />
      <div className='text-lnds-color flex items-center'>{children}</div>
    </div>
  );
};

export const DatasetDetails = (props: Readonly<DatasetDetailsProps>) => {
  const { dataset, formFields, refreshComments, currentTab, setCurrentTab } = props;
  const [showFullDescription, setShowFullDescription] = useState(false);
  const [showFullProvenance, setShowFullProvenance] = useState(false);
  const [showFullVersionNotes, setShowFullVersionNotes] = useState(false);
  const [dataDictionary, setDataDictionary] = useState<ResourceDataDictionaryEntry[]>([]);

  useEffect(() => {
    if (currentTab === Tabs.DATA_DICTIONARY) {
      const fetchData = async () => {
        try {
          const data = await fetchDataDictionaries(dataset.id);
          setDataDictionary(data);
        } catch (error) {
          console.error("Failed to fetch data dictionary entries:", error);
        }
      };
      fetchData();
    }
  }, [currentTab, dataset.id]);

  const toggleDescription = () => {
    setShowFullDescription((prev) => !prev);
  };

  const toggleProvenance = () => {
    setShowFullProvenance((prev) => !prev);
  };

  const toggleVersionNotes = () => {
    setShowFullVersionNotes((prev) => !prev);
  };

  const descriptionContent =
    showFullDescription || dataset.description.length <= 300
      ? dataset.description
      : dataset.description.slice(0, 300) + "...";

  const provenanceItems = dataset.provenance || [];
  const firstProvenanceItem = provenanceItems[0] || "";
  const truncatedFirstProvenance =
    firstProvenanceItem.length > 200
      ? firstProvenanceItem.slice(0, 200) + "..."
      : firstProvenanceItem;
  const hasMoreProvenance = provenanceItems.length > 1 || firstProvenanceItem.length > 200;

  const versionNotesItems = dataset.version_notes || [];
  const firstVersionNote = versionNotesItems[0] || "";
  const truncatedFirstVersionNote =
    firstVersionNote.length > 200 ? firstVersionNote.slice(0, 200) + "..." : firstVersionNote;
  const hasMoreVersionNotes = versionNotesItems.length > 1 || firstVersionNote.length > 200;

  const applicableLegislations = dataset.applicable_legislations.map((applicableLegislation) => {
    const applicableLegislationField = formFields.dataset.applicable_legislations.find(
      (al) => al.value === applicableLegislation,
    );

    if (applicableLegislationField) {
      return applicableLegislationField;
    } else {
      return {
        value: applicableLegislation,
        eng_label: applicableLegislation,
        description: "",
        link: "",
      };
    }
  });

  const conventions = dataset.conventions.map((convention) => {
    const conventionField = formFields.dataset.conventions.find((c) => c.value === convention);
    if (conventionField) {
      return conventionField.eng_label;
    } else {
      return convention;
    }
  });

  const areas_of_work = dataset.areas_of_work.map((area) => {
    const areaField = formFields.dataset.areas_of_work.find((a) => a.value === area);
    if (areaField) {
      return areaField;
    } else {
      return { value: area, eng_label: area };
    }
  });

  const areas_of_competence = dataset.areas_of_competence.map((area) => {
    const areaField = formFields.dataset.areas_of_competence.find((a) => a.value === area);
    if (areaField) {
      return areaField;
    } else {
      return { value: area, eng_label: area };
    }
  });

  let content = (
    <div className='px-1 sm:px-2'>
      <div>
        <DatasetFieldHeader fieldName='description' />
        <p className='text-lnds-color'>
          {descriptionContent}
          {dataset.description.length > 300 && (
            <button
              onClick={toggleDescription}
              className='ml-1 text-lnds-dark-blue dark:text-gray-400 hover:text-lnds-dark-blue dark:hover:text-white hover:underline focus:outline-none'
            >
              {showFullDescription ? "View less" : "View more"}
            </button>
          )}
        </p>
      </div>
      <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
        {dataset.identifier && (
          <DatasetField fieldName='identifier' label='Identifier'>
            <FingerPrintIcon className='h-5 w-5 label-lnds-color mr-1 flex-shrink-0' />
            <span className='text-wrap break-all line-clamp-2'>{dataset.identifier}</span>
          </DatasetField>
        )}
        {dataset.was_generated_by && dataset.was_generated_by.length > 0 && (
          <DatasetField fieldName='was_generated_by'>
            <Tags
              tags={dataset.was_generated_by.map((type) => ({
                eng_label: type,
              }))}
              className='mt-1'
            />
          </DatasetField>
        )}
        {dataset.other_identifiers && dataset.other_identifiers.length > 0 && (
          <DatasetField fieldName='other_identifiers'>
            <Tags
              tags={dataset.other_identifiers.map((type) => ({
                eng_label: type,
              }))}
              className='mt-1'
            />
          </DatasetField>
        )}
      </div>
      <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
        {dataset.version && dataset.version.length > 0 && (
          <DatasetField fieldName='version'>
            <Tags tags={[{ eng_label: dataset.version }]} className='mt-1' />
          </DatasetField>
        )}
      </div>
      {dataset.version_notes && dataset.version_notes.length > 0 && (
        <div className='mt-4'>
          <DatasetFieldHeader fieldName='version_notes' />
          <ul className='list-disc list-inside text-lnds-color'>
            {showFullVersionNotes ? (
              versionNotesItems.map((note: string, index: number) => <li key={index}>{note}</li>)
            ) : (
              <li>{truncatedFirstVersionNote}</li>
            )}
          </ul>
          {hasMoreVersionNotes && (
            <button
              onClick={toggleVersionNotes}
              className='mt-1 text-lnds-dark-blue dark:text-gray-400 hover:text-lnds-dark-blue dark:hover:text-white hover:underline focus:outline-none'
            >
              {showFullVersionNotes
                ? "View less"
                : versionNotesItems.length > 1
                  ? `View more (${versionNotesItems.length - 1} more)`
                  : "View more"}
            </button>
          )}
        </div>
      )}
      <div className='mt-4 grid grid-cols-1 md:grid-cols-2 gap-4'>
        <DatasetField fieldName='dataset_types'>
          <CircleStackIcon className='h-5 w-5 label-lnds-color mr-1' />
          <Tags tags={dataset.dataset_types} className='mt-1' />
        </DatasetField>
      </div>
      <div className='mt-4 grid grid-cols-1 md:grid-cols-2 gap-4'>
        <DatasetField fieldName='rights_statement'>
          <KeyIcon className='h-5 w-5 label-lnds-color mr-1' />
          {rightStatementsLabels[dataset.rights_statement as keyof typeof rightStatementsLabels]}
        </DatasetField>
        {dataset.data_protection_types && dataset.data_protection_types.length > 0 && (
          <DatasetField fieldName='data_protection_types'>
            <Tags
              tags={dataset.data_protection_types.map((type) => ({
                eng_label: toReadableFormat(type),
              }))}
              className='mt-1'
            />
          </DatasetField>
        )}
      </div>
      <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
        {dataset.creator_names && dataset.creator_names.length > 0 && (
          <DatasetField fieldName='creator_ids' label='Creator Names'>
            <IconList
              items={dataset.creator_names}
              Icon={BuildingOfficeIcon}
              itemClassName='text-wrap break-all'
            />
          </DatasetField>
        )}
        <DatasetField fieldName='publisher_id' label='Publisher Name'>
          <BuildingOfficeIcon className='h-5 w-5 label-lnds-color mr-1 flex-shrink-0' />
          <span className='text-wrap break-all line-clamp-2'>{dataset.publisher_name}</span>
        </DatasetField>
        {dataset.contact_names && dataset.contact_names.length > 0 && (
          <DatasetField fieldName='contact_ids' label='Contacts'>
            <IconList
              items={dataset.contact_names}
              Icon={UserIcon}
              getHref={(_, index) => {
                const email = dataset.contact_emails[index];
                return email ? `mailto:${email}` : undefined;
              }}
              linkClassName='text-lnds-color text-sm truncate underline hover:text-lnds-dark-blue dark:hover:text-white'
            />
          </DatasetField>
        )}
      </div>
      <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
        {(dataset.time_period_start || dataset.time_period_end) && (
          <DatasetField fieldName='time_period_start' label='Time Period'>
            <CalendarIcon className='h-5 w-5 label-lnds-color mr-1' />
            {DateUtils.formatDate(dataset.time_period_start) || "No start date"} -{" "}
            {DateUtils.formatDate(dataset.time_period_end) || "No end date provided"}
          </DatasetField>
        )}
        {dataset.periodicity && (
          <DatasetField fieldName='periodicity'>
            <ArrowPathIcon className='h-5 w-5 label-lnds-color mr-1' />
            {dataset.periodicity.eng_label}
          </DatasetField>
        )}
      </div>
      {dataset.retention_period_start || dataset.retention_period_end ? (
        <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
          <DatasetField fieldName='retention_period_start' label='Retention Period'>
            <CalendarIcon className='h-5 w-5 label-lnds-color mr-1' />
            {dataset.retention_period_start
              ? DateUtils.formatDate(dataset.retention_period_start as string)
              : ""}
            {dataset.retention_period_start && dataset.retention_period_end ? " - " : ""}
            {dataset.retention_period_end
              ? DateUtils.formatDate(dataset.retention_period_end as string)
              : ""}
          </DatasetField>
        </div>
      ) : null}
      <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
        {dataset.release_date && (
          <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
            <DatasetField fieldName='release_date'>
              {DateUtils.formatDate(dataset.release_date)}
            </DatasetField>
          </div>
        )}
        {dataset.modified_at && (
          <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
            <DatasetField fieldName='modified_at'>
              {DateUtils.formatDate(dataset.modified_at)}
            </DatasetField>
          </div>
        )}
      </div>
      <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
        {conventions && conventions.length > 0 && (
          <DatasetField fieldName='conventions'>
            <ConventionTags tags={conventions} />
          </DatasetField>
        )}
      </div>
      <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
        {dataset.keywords && dataset.keywords.length > 0 && (
          <DatasetField fieldName='keywords'>
            <Tags tags={dataset.keywords} className='mt-1' />
          </DatasetField>
        )}
        <DatasetField fieldName='themes'>
          <Tags tags={dataset.themes} className='mt-1' />
        </DatasetField>
      </div>
      <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
        {dataset.spatial_coverages && dataset.spatial_coverages.length > 0 && (
          <DatasetField fieldName='spatial_coverages'>
            <Tags tags={dataset.spatial_coverages} className='mt-1' />
          </DatasetField>
        )}
        {dataset.monitoring_location && (
          <DatasetField fieldName='monitoringlocation' label='Monitoring Location'>
            <div className='flex items-center'>
              <MapPinIcon className='h-5 w-5 label-lnds-color mr-1' />
              {dataset.monitoring_location}
            </div>
          </DatasetField>
        )}
        {dataset.languages && dataset.languages.length > 0 && (
          <DatasetField fieldName='languages'>
            <Tags tags={dataset.languages} className='mt-1' />
          </DatasetField>
        )}
      </div>
      <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
        {applicableLegislations && applicableLegislations.length > 0 && (
          <DatasetField fieldName='applicable_legislations'>
            <ApplicableLegislationTags legislations={applicableLegislations} />
          </DatasetField>
        )}
      </div>
      <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
        {dataset.spatial_resolutions && dataset.spatial_resolutions.length > 0 && (
          <DatasetField fieldName='spatial_resolutions'>
            <Tags
              tags={dataset.spatial_resolutions.map((sr) => ({ eng_label: String(sr) }))}
              className='mt-1'
            />
          </DatasetField>
        )}
        {dataset.temporal_resolution && (
          <DatasetField fieldName='temporal_resolution'>{dataset.temporal_resolution}</DatasetField>
        )}
      </div>
      <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
        {dataset.duration_of_administrative_utility &&
          dataset.duration_of_administrative_utility > 0 && (
            <DatasetField fieldName='duration_of_administrative_utility'>
              <CalendarDateRangeIcon className='h-5 w-5 label-lnds-color mr-1' />
              {dataset.duration_of_administrative_utility}
            </DatasetField>
          )}
        {dataset.final_disposition && (
          <DatasetField fieldName='final_disposition'>
            <ArchiveBoxIcon className='h-5 w-5 label-lnds-color mr-1' />
            {dataset.final_disposition}
          </DatasetField>
        )}
      </div>
      <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
        {areas_of_work && areas_of_work.length > 0 && (
          <DatasetField fieldName='areas_of_work'>
            <Tags tags={areas_of_work} className='mt-1' />
          </DatasetField>
        )}
        {areas_of_competence && areas_of_competence.length > 0 && (
          <DatasetField fieldName='areas_of_competence'>
            <Tags tags={areas_of_competence} className='mt-1' />
          </DatasetField>
        )}
      </div>
      <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
        {dataset.documentation && dataset.documentation.length > 0 && (
          <DatasetField fieldName='documentation'>
            <IconList items={dataset.documentation} Icon={DocumentTextIcon} />
          </DatasetField>
        )}
        {dataset.landing_pages && dataset.landing_pages.length > 0 && (
          <DatasetField fieldName='landing_pages'>
            <IconList
              items={dataset.landing_pages}
              Icon={LinkIcon}
              getHref={(item) => item}
              openInNewTab
            />
          </DatasetField>
        )}
      </div>
      {dataset.provenance && dataset.provenance.length > 0 && (
        <div className='mt-4'>
          <DatasetFieldHeader fieldName='provenance' />
          <ul className='list-disc list-inside text-lnds-color'>
            {showFullProvenance ? (
              provenanceItems.map((entry: string, index: number) => <li key={index}>{entry}</li>)
            ) : (
              <li>{truncatedFirstProvenance}</li>
            )}
          </ul>
          {hasMoreProvenance && (
            <button
              onClick={toggleProvenance}
              className='mt-1 text-lnds-dark-blue dark:text-gray-400 hover:text-lnds-dark-blue dark:hover:text-white hover:underline focus:outline-none'
            >
              {showFullProvenance
                ? "View less"
                : provenanceItems.length > 1
                  ? `View more (${provenanceItems.length - 1} more)`
                  : "View more"}
            </button>
          )}
        </div>
      )}
      <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
        {dataset.conforms_to && dataset.conforms_to.length > 0 && (
          <DatasetField fieldName='conforms_to'>
            <IconList
              items={dataset.conforms_to}
              Icon={DocumentTextIcon}
              getHref={(item) => item}
              openInNewTab
            />
          </DatasetField>
        )}
      </div>
      {dataset.group_manager_names && dataset.group_manager_names.length > 0 && (
        <div className='border-t border-lnds-color mt-4'></div>
      )}
      <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
        {dataset.group_manager_names && dataset.group_manager_names.length > 0 && (
          <DatasetField fieldName='group_managers'>
            <IconList
              items={dataset.group_manager_names}
              Icon={UserGroupIcon}
              itemClassName='text-wrap break-all line-clamp-2'
            />
          </DatasetField>
        )}
      </div>
      <HealthDcatDetailsSection
        dataset={dataset}
        DatasetField={DatasetField}
        DatasetFieldHeader={DatasetFieldHeader}
      />
    </div>
  );

  if (currentTab === Tabs.DISTRIBUTIONS) {
    content = (
      <div className='px-1 sm:px-2'>
        {dataset.status === DatasetStatusEnum.DRAFT && (
          <div className='flex items-center justify-end mb-4'>
            <Button
              btnType='secondary'
              Link={Link}
              to={`/datasets/${dataset.id}/distributions`}
              Icon={PencilSquareIcon}
              label='Manage Distributions'
            />
          </div>
        )}
        {dataset.distributions.length > 0 && (
          <div className='mt-4 space-y-4'>
            {dataset.distributions.map((distribution: ResourceDistributionType) => (
              <DistributionSection
                key={distribution.id}
                distribution={distribution}
                formFields={formFields}
              />
            ))}
          </div>
        )}
        {dataset.distributions.length === 0 && (
          <EmptyScreen message='No distributions available' Icon={DocumentIcon} />
        )}
      </div>
    );
  }

  if (currentTab === Tabs.RELATIONS) {
    const datasetRelations =
      dataset.source_relations?.filter((rel) => rel.relation_kind === "dataset") || [];
    const externalRelations =
      dataset.source_relations?.filter((rel) => rel.relation_kind === "external") || [];

    content = (
      <div className='px-1 sm:px-2'>
        {DatasetStatusEnum.DRAFT === dataset.status && (
          <div className='flex justify-end mb-4'>
            <Button
              btnType='secondary'
              Link={Link}
              to={`/datasets/${dataset.id}/relations`}
              Icon={PencilSquareIcon}
              label='Manage Dataset Relations'
            />
          </div>
        )}
        {!dataset.source_relations || dataset.source_relations.length === 0 ? (
          <EmptyScreen message='No relations available' Icon={LinkIcon} />
        ) : (
          <div className='space-y-8'>
            {datasetRelations.length > 0 && (
              <div className='dark:bg-gray-800 p-4 rounded-lg mb-6'>
                <h3 className='label-lnds-color text-xl font-semibold mb-4 pb-2 border-b-2 border-lnds-color'>
                  Dataset Relations
                </h3>
                <div className='space-y-2'>
                  {datasetRelations.map((relation) => {
                    const newerVersionRelation = dataset.source_relations?.find(
                      (other) =>
                        other.previous_version_dataset_id === relation.dataset_id &&
                        relation.status === DatasetStatusEnum.PUBLISHED,
                    );

                    return (
                      <Card
                        key={`${relation.dataset_id}-${relation.relation_type}`}
                        className='w-full p-4 bg-white dark:bg-gray-800 border-b border-lnds-color'
                      >
                        <RelationLink
                          relationType={relation.relation_type!}
                          datasetTitle={relation.title!}
                          datasetId={relation.dataset_id!}
                          status={relation.status!}
                          hasNewerVersion={!!newerVersionRelation}
                          newerVersionId={newerVersionRelation?.dataset_id ?? undefined}
                        />
                      </Card>
                    );
                  })}
                </div>
              </div>
            )}

            {externalRelations.length > 0 && (
              <div>
                <div className='dark:bg-gray-800 p-4 rounded-lg mb-6'>
                  <h3 className='label-lnds-color text-xl font-semibold mb-4 pb-2 border-b-2 border-lnds-color'>
                    Links to External Resources
                  </h3>
                  <div className='space-y-2'>
                    {externalRelations.map((relation) => (
                      <Card
                        key={relation.id}
                        className='w-full p-4 bg-white dark:bg-gray-800 border-b border-lnds-color'
                      >
                        <div className='flex flex-col break-all'>
                          <a
                            href={relation.external_url!}
                            target='_blank'
                            rel='noopener noreferrer'
                            className='text-lnds-color underline break-all hover:text-lnds-dark-blue dark:hover:text-white flex items-center mb-1'
                          >
                            <RectangleGroupIcon className='h-5 w-5 mr-1' />
                            {relation.external_url}
                          </a>
                          {relation.external_role && (
                            <span className='text-lnds-gray dark:text-gray-400 text-sm flex items-center mb-1'>
                              <TagIcon className='h-4 w-4 mr-1' />
                              {relation.external_role}
                            </span>
                          )}
                          {relation.external_description && (
                            <span className='text-sm text-lnds-gray dark:text-gray-400 break-words'>
                              {relation.external_description}
                            </span>
                          )}
                        </div>
                      </Card>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  if (currentTab === Tabs.QUALIFIED_ATTRIBUTIONS) {
    content = <QualifiedAttributionsTab dataset={dataset} />;
  }

  if (currentTab === Tabs.ACTIVITY_LOGS) {
    content = (
      <div className='px-1 sm:px-2'>
        <ActivityLogList entityId={dataset.id} entityType='dataset' />
      </div>
    );
  }

  if (currentTab === Tabs.DATA_DICTIONARY) {
    content = (
      <div className='px-1 sm:px-2'>
        <DataDictionaryTable dataset={dataset} data={dataDictionary} isEditable={false} />
      </div>
    );
  }

  if (currentTab === Tabs.COMMENTS) {
    content = (
      <div className='px-1 sm:px-2'>
        <CommentList dataset={dataset} refreshComments={refreshComments} />
      </div>
    );
  }

  if (currentTab === Tabs.MEMBER_DATASETS) {
    content = (
      <div className='px-1 sm:px-2'>
        <SeriesDatasetsList memberDatasets={dataset.member_datasets || []} />
      </div>
    );
  }

  if (currentTab === Tabs.VERSIONS) {
    content = (
      <div className='px-1 sm:px-2'>
        <DatasetVersions datasetId={dataset.id} />
      </div>
    );
  }

  let tabList = [
    dataset.is_dataset_series ? Tabs.SERIES : Tabs.DATASET,
    dataset.is_dataset_series ? Tabs.MEMBER_DATASETS : Tabs.DISTRIBUTIONS,
    Tabs.DATA_DICTIONARY,
    Tabs.RELATIONS,
    Tabs.QUALIFIED_ATTRIBUTIONS,
  ];

  tabList = tabList.concat([Tabs.ACTIVITY_LOGS, Tabs.VERSIONS, Tabs.COMMENTS]);

  if (!dataset.previous_version_dataset_id) {
    tabList = tabList.filter((tab) => tab !== Tabs.VERSIONS);
  }

  if (dataset.id === -1) {
    if (dataset.is_dataset_series) {
      tabList = [Tabs.SERIES, Tabs.MEMBER_DATASETS];
    } else {
      tabList = [Tabs.DATASET];
    }
  }

  return (
    <div className='h-full'>
      <IncorrectRelationFlashMessage dataset={dataset} />
      <DatasetDetailsTab currentTab={currentTab} setCurrentTab={setCurrentTab} tabList={tabList} />
      {content}
    </div>
  );
};
