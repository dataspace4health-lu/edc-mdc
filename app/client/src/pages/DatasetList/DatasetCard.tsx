import {
  BeakerIcon,
  EyeIcon,
  ExclamationTriangleIcon,
  RectangleStackIcon,
  ShareIcon,
  TableCellsIcon,
} from "@heroicons/react/24/solid";
import DatasetStatus from "../../components/DatasetStatus";
import InitialsAvatar from "../../components/InitialsAvatar";
import DatasetActionsDropdown from "../../components/DatasetActionsDropdown";
import Tooltip from "../../components/Tooltip";
import ApplicableLegislationTags from "../../components/ApplicableLegislationTags";
import hasRelationWithInternalDataset from "../../utils/hasRelationWithInternalDataset";
import AuthenticSourceIcon from "../../components/AuthenticSourceIcon";
import { getDatasetFieldShortLabel } from "../../schemas/datasetSchema";
import { rightStatementsLabels } from "../../utils/rightStatementsLabels";
import { ResourceDatasetType, FormType, DatasetStatusEnum } from "../../types";
import { Button, Card, Tags } from "@lnds-lu/design-system";
import { searchParams } from "../../components/Modals/VersionList/Utils";
import VersionChangeTypeLabel from "../../components/VersionChangeTypeLabel";

const DatasetLabel = ({
  label,
  fieldName,
  className,
}: {
  label?: string;
  fieldName?: string;
  className?: string;
}) => (
  <div className={`text-xs md:text-sm font-semibold label-lnds-color ${className}`}>
    {label || getDatasetFieldShortLabel(fieldName!)}
  </div>
);

export default function DatasetCard({
  dataset,
  openDataset,
  formFields,
}: Readonly<{
  dataset: ResourceDatasetType;
  openDataset: (datasetId: string) => void;
  formFields: FormType;
}>) {
  const hasIncorrectRelation = hasRelationWithInternalDataset(dataset);
  const isImported = dataset.source_dataset_id !== null && dataset.source_dataset_id !== undefined;
  const hasHealthMetadata =
    (dataset.health_categories && dataset.health_categories.length > 0) ||
    (dataset.health_themes && dataset.health_themes.length > 0);
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

  return (
    <Card
      className={`relative p-4 transition-transform transform hover:-translate-y-1 flex flex-col min-h-[350px] dataset-card-${dataset.id}`}
    >
      <div className='flex flex-row justify-between items-center heading-lnds-color pb-2 mb-4 border-b border-lnds-color'>
        <div className='flex items-center font-bold text-base md:text-lg flex-1 min-w-0'>
          {hasIncorrectRelation && (
            <Tooltip text='This dataset has a relation with an Internal dataset'>
              <ExclamationTriangleIcon className='h-5 w-5 mr-2 text-lnds-red' />
            </Tooltip>
          )}
          <InitialsAvatar name={dataset.author_name} showTooltip={true} isImported={isImported} />
          <span
            className='ml-3 md:ml-4 overflow-hidden text-ellipsis whitespace-nowrap text-xl font-semibold'
            style={{ maxWidth: "calc(100% - 1.5rem)" }}
            title={dataset.title}
          >
            {dataset.title}
          </span>
        </div>
        {dataset.is_dataset_series && (
          <div className='flex items-center text-lnds-purple text-sm mr-2'>
            <RectangleStackIcon className='h-4 w-4 mr-1' />
            <span className='font-medium'>Series</span>
          </div>
        )}
        <div className='flex items-center space-x-2'>
          {hasHealthMetadata && (
            <Tooltip text='Health-related dataset'>
              <span className='inline-flex items-center justify-center w-7 h-7 rounded-full bg-blue-50 dark:bg-blue-900/20'>
                <BeakerIcon className='h-4 w-4 text-lnds-green' />
              </span>
            </Tooltip>
          )}
          <DatasetActionsDropdown dataset={dataset} />
        </div>
      </div>
      {dataset.previous_version_dataset_id && !dataset.latest_version_dataset_id && (
        <div className='mb-4 px-4 py-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md dark:text-white'>
          <p className='text-sm font-semibold'>
            This dataset is a version of a{" "}
            <a
              href={`/?${searchParams({
                ...dataset,
                id: dataset.previous_version_dataset_id,
              })}`}
              target='_blank'
              rel='noopener noreferrer'
              className='underline hover:text-lnds-dark-blue dark:hover:text-lnds-dark-blue'
            >
              previous dataset
            </a>
          </p>
          <p className='mt-1 text-sm font-semibold'>
            <VersionChangeTypeLabel versionChangeType={dataset.version_change_type} />
          </p>
        </div>
      )}
      {dataset.latest_version_dataset_id && dataset.status === DatasetStatusEnum.DEPRECATED && (
        <div className='mb-4 px-4 py-3 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-md dark:text-white'>
          <p className='text-sm font-semibold'>
            Deprecated. A newer{" "}
            <a
              href={`/?${searchParams({
                ...dataset,
                id: dataset.latest_version_dataset_id,
              })}`}
              target='_blank'
              rel='noopener noreferrer'
              className='underline hover:text-lnds-dark-blue dark:hover:text-lnds-dark-blue'
            >
              version
            </a>{" "}
            is available.
          </p>
        </div>
      )}
      <div className='flex flex-col flex-grow'>
        <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mb-4'>
          <div>
            <DatasetLabel fieldName='dataset_types' />
            <Tags tags={dataset.dataset_types} />
          </div>
          <div>
            <DatasetLabel fieldName='rights_statement' />
            <p className='text-lnds-color text-sm'>
              {
                rightStatementsLabels[
                  dataset.rights_statement as keyof typeof rightStatementsLabels
                ]
              }
            </p>
          </div>
        </div>
        <p className='text-sm line-clamp-3 text-lnds-color flex-grow'>{dataset.description}</p>
        <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mb-4'>
          {dataset.keywords && dataset.keywords.length > 0 && (
            <div>
              <DatasetLabel fieldName='keywords' className='mt-4 mb-1' />
              <Tags tags={dataset.keywords} />
            </div>
          )}
          <div>
            <DatasetLabel fieldName='themes' className='mt-4 mb-1' />
            <Tags tags={dataset.themes} />
          </div>
          {dataset.health_categories && dataset.health_categories.length > 0 && (
            <div>
              <DatasetLabel fieldName='health_categories' className='mt-4 mb-1' />
              <Tags tags={dataset.health_categories} />
            </div>
          )}
          {dataset.health_themes && dataset.health_themes.length > 0 && (
            <div>
              <DatasetLabel fieldName='health_themes' className='mt-4 mb-1' />
              <Tags tags={dataset.health_themes} />
            </div>
          )}
          {dataset.applicable_legislations && dataset.applicable_legislations.length > 0 && (
            <div>
              <DatasetLabel fieldName='applicable_legislations' className='mt-4 mb-1' />
              <ApplicableLegislationTags legislations={applicableLegislations} />
            </div>
          )}
        </div>
        <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mb-4'>
          {dataset.contact_names && dataset.contact_names.length > 0 && (
            <div>
              <DatasetLabel label='Contacts' />
              <div className='flex flex-col gap-1'>
                {dataset.contact_names.map((name, index) => (
                  <a
                    key={index}
                    href={`mailto:${dataset.contact_emails[index]}`}
                    className='text-lnds-color text-sm truncate underline hover:text-lnds-dark-blue dark:hover:text-white'
                  >
                    {name}
                  </a>
                ))}
              </div>
            </div>
          )}
          {(!dataset.contact_names || dataset.contact_names.length === 0) && (
            <div>
              <DatasetLabel label='Publisher' />
              <p>
                <p className='text-sm text-lnds-color'>{dataset.publisher_name}</p>
              </p>
            </div>
          )}
        </div>
        {dataset.monitoring_location && (
          <div className='mb-2'>
            <DatasetLabel fieldName='monitoring_location' />
            <p className='text-sm text-lnds-color'>{dataset.monitoring_location}</p>
          </div>
        )}
        <div className='flex gap-4 mb-4 py-4 border-t border-b border-lnds-color'>
          <div className='flex-1 flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg'>
            <div className='w-10 h-10 rounded-lg bg-lnds-lightest-gray flex items-center justify-center'>
              <ShareIcon className='h-5 w-5 text-lnds-gray' />
            </div>
            <div>
              <div className='text-2xl font-bold text-lnds-color'>
                {dataset.distributions.length}
              </div>
              <div className='text-xs text-gray-500 font-medium'>Distributions</div>
            </div>
          </div>
          <div className='flex-1 flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg'>
            <div className='w-10 h-10 rounded-lg bg-lnds-lightest-gray flex items-center justify-center'>
              <TableCellsIcon className='h-5 w-5 text-lnds-gray' />
            </div>
            <div className='flex-1'>
              <div className='flex items-center gap-2'>
                <div className='text-2xl font-bold text-lnds-color'>
                  {dataset.total_dictionaries || 0}
                </div>
                <AuthenticSourceIcon dataset={dataset} />
              </div>
              <div className='text-xs text-gray-500 font-medium'>Dictionary Entries</div>
            </div>
          </div>
        </div>

        <div className='border-t border-lnds-color pt-4 flex items-center justify-between'>
          <DatasetStatus dataset={dataset} hideAuthenticSourceIcon={true} />
          <Button
            className='h-10'
            label='View'
            Icon={EyeIcon}
            onClick={() => openDataset(dataset.id.toString())}
          />
        </div>
      </div>
    </Card>
  );
}
