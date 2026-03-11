import { useState } from "react";
import { BeakerIcon, DocumentTextIcon, LinkIcon } from "@heroicons/react/24/solid";
import { Tags } from "@lnds-lu/design-system";
import IconList from "../IconList";
import FieldInfoHeader from "../FieldInfoHeader";
import { ResourceDatasetType } from "../../types";
import { HEALTH_RELATED_DATA_EXPLANATION } from "../../constants/health";

type DatasetFieldProps = {
  fieldName: string;
  label?: string;
  children: React.ReactNode;
};

type DatasetFieldHeaderProps = {
  fieldName: string;
  label?: string;
};

type HealthDcatDetailsSectionProps = {
  dataset: ResourceDatasetType;
  DatasetField: React.ComponentType<DatasetFieldProps>;
  DatasetFieldHeader: React.ComponentType<DatasetFieldHeaderProps>;
};

const hasHealthRelatedData = (dataset: ResourceDatasetType): boolean => {
  return Boolean(
    (dataset.health_categories && dataset.health_categories.length > 0) ||
    (dataset.health_themes && dataset.health_themes.length > 0) ||
    (dataset.personal_data && dataset.personal_data.length > 0) ||
    (dataset.health_legal_basis && dataset.health_legal_basis.length > 0) ||
    (dataset.max_typical_age && dataset.max_typical_age > 0) ||
    (dataset.min_typical_age && dataset.min_typical_age > 0) ||
    (dataset.number_of_records && dataset.number_of_records > 0) ||
    (dataset.number_of_unique_individuals && dataset.number_of_unique_individuals > 0) ||
    dataset.population_coverage ||
    (dataset.code_values && dataset.code_values.length > 0) ||
    (dataset.purpose && dataset.purpose.length > 0) ||
    (dataset.coding_systems && dataset.coding_systems.length > 0),
  );
};

export default function HealthDcatDetailsSection({
  dataset,
  DatasetField,
  DatasetFieldHeader,
}: Readonly<HealthDcatDetailsSectionProps>) {
  const [showFullHealthLegalBasis, setShowFullHealthLegalBasis] = useState(false);

  if (!hasHealthRelatedData(dataset)) {
    return null;
  }

  const healthLegalBasisItems = dataset.health_legal_basis || [];
  const firstHealthLegalBasisItem = healthLegalBasisItems[0] || "";
  const truncatedFirstHealthLegalBasis =
    firstHealthLegalBasisItem.length > 200
      ? firstHealthLegalBasisItem.slice(0, 200) + "..."
      : firstHealthLegalBasisItem;
  const hasMoreHealthLegalBasis =
    healthLegalBasisItems.length > 1 || firstHealthLegalBasisItem.length > 200;

  return (
    <section className='mt-6 mb-4 p-4 border border-lnds-color rounded-md'>
      <div className='flex items-center pb-2 mb-3 border-b border-lnds-color'>
        <BeakerIcon className='h-5 w-5 label-lnds-color mr-2 text-lnds-green' />
        <div>
          <FieldInfoHeader
            as='h3'
            label='Health-related details'
            labelClassName='font-semibold text-lg'
            containerClassName='flex items-center gap-1'
            popoverInfo={HEALTH_RELATED_DATA_EXPLANATION}
          />
        </div>
      </div>

      <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
        {dataset.health_categories && dataset.health_categories.length > 0 && (
          <DatasetField fieldName='health_categories'>
            <Tags tags={dataset.health_categories} className='mt-1' />
          </DatasetField>
        )}
        {dataset.health_themes && dataset.health_themes.length > 0 && (
          <DatasetField fieldName='health_themes'>
            <Tags tags={dataset.health_themes} className='mt-1' />
          </DatasetField>
        )}
        {dataset.personal_data && dataset.personal_data.length > 0 && (
          <DatasetField fieldName='personal_data'>
            <Tags
              tags={dataset.personal_data.map((item) => ({ eng_label: item }))}
              className='mt-1'
            />
          </DatasetField>
        )}
      </div>

      {dataset.health_legal_basis && dataset.health_legal_basis.length > 0 && (
        <div className='mt-4'>
          <DatasetFieldHeader fieldName='health_legal_basis' />
          <ul className='list-disc list-inside text-lnds-color'>
            {showFullHealthLegalBasis ? (
              healthLegalBasisItems.map((entry: string, index: number) => (
                <li key={index}>{entry}</li>
              ))
            ) : (
              <li>{truncatedFirstHealthLegalBasis}</li>
            )}
          </ul>
          {hasMoreHealthLegalBasis && (
            <button
              onClick={() => setShowFullHealthLegalBasis((prev) => !prev)}
              className='mt-1 text-lnds-dark-blue dark:text-gray-400 hover:text-lnds-dark-blue dark:hover:text-white hover:underline focus:outline-none'
            >
              {showFullHealthLegalBasis
                ? "View less"
                : healthLegalBasisItems.length > 1
                  ? `View more (${healthLegalBasisItems.length - 1} more)`
                  : "View more"}
            </button>
          )}
        </div>
      )}

      <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
        {dataset.max_typical_age && dataset.max_typical_age > 0 && (
          <DatasetField fieldName='max_typical_age'>{dataset.max_typical_age}</DatasetField>
        )}
        {dataset.min_typical_age && dataset.min_typical_age > 0 && (
          <DatasetField fieldName='min_typical_age'>{dataset.min_typical_age}</DatasetField>
        )}
      </div>

      <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
        {dataset.number_of_records && dataset.number_of_records > 0 && (
          <DatasetField fieldName='number_of_records'>{dataset.number_of_records}</DatasetField>
        )}
        {dataset.number_of_unique_individuals && dataset.number_of_unique_individuals > 0 && (
          <DatasetField fieldName='number_of_unique_individuals'>
            {dataset.number_of_unique_individuals}
          </DatasetField>
        )}
        {dataset.population_coverage && (
          <DatasetField fieldName='population_coverage'>
            <DocumentTextIcon className='h-5 w-5 label-lnds-color mr-1' />
            {dataset.population_coverage}
          </DatasetField>
        )}
        {dataset.code_values && dataset.code_values.length > 0 && (
          <DatasetField fieldName='code_values'>
            <Tags
              tags={dataset.code_values.map((codeValue) => ({
                eng_label: codeValue,
              }))}
              className='mt-1'
            />
          </DatasetField>
        )}
        {dataset.purpose && dataset.purpose.length > 0 && (
          <DatasetField fieldName='purpose'>
            <Tags
              tags={dataset.purpose.map((purpose) => ({
                eng_label: purpose,
              }))}
              className='mt-1'
            />
          </DatasetField>
        )}
        {dataset.coding_systems && dataset.coding_systems.length > 0 && (
          <DatasetField fieldName='coding_systems'>
            <IconList
              items={dataset.coding_systems}
              Icon={LinkIcon}
              getHref={(item) => item}
              openInNewTab
            />
          </DatasetField>
        )}
      </div>
    </section>
  );
}
