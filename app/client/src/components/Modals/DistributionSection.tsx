import { useState } from "react";
import { FormType, ResourceDistributionType } from "../../types";
import {
  LockClosedIcon,
  KeyIcon,
  DocumentIcon,
  DocumentTextIcon,
  FolderIcon,
  ClockIcon,
  CalendarIcon,
  ShieldCheckIcon,
  ShieldExclamationIcon,
  AdjustmentsHorizontalIcon,
  TagIcon,
  GlobeEuropeAfricaIcon,
  BuildingOfficeIcon,
  TableCellsIcon,
  ServerIcon,
  ChartBarIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  ShareIcon,
  PencilIcon,
  TrashIcon,
  XMarkIcon,
} from "@heroicons/react/24/solid";
import { Tags, Button } from "@lnds-lu/design-system";
import { rightStatementsLabels } from "../../utils/rightStatementsLabels";
import ApplicableLegislationTags from "../ApplicableLegislationTags";
import { DateUtils } from "../../utils/dateTimeHelpers";
import {
  actionTypeOptions,
  constraintTypeOptions,
  purposeOptions,
  availabilityOptions,
} from "../../schemas/distributionSchema";
import distributionSchema from "../../schemas/distributionSchema";
import DataServiceItem from "../../pages/data_services/DataServiceItem";
import IconList from "../IconList";
import FieldInfoHeader from "../FieldInfoHeader";

type DistributionSectionProps = {
  distribution: ResourceDistributionType;
  formFields: FormType;
  isEditable?: boolean;
  onEdit?: () => void;
  onDelete?: () => void;
  confirmingDelete?: boolean;
  onConfirmDelete?: () => void;
  onCancelDelete?: () => void;
};

type DistributionFieldHeaderProps = {
  fieldName: string;
  label?: string;
};

const distributionFieldMetaByApiField = new Map(
  distributionSchema.map((field) => [
    field.apiFieldName,
    { label: field.shortLabel, explanation: field.explanation },
  ]),
);

const DistributionFieldHeader = ({ fieldName, label }: Readonly<DistributionFieldHeaderProps>) => {
  const meta = distributionFieldMetaByApiField.get(fieldName);

  return (
    <FieldInfoHeader
      label={label ?? meta?.label ?? fieldName}
      popoverInfo={meta?.explanation}
      containerClassName='flex items-center gap-1'
    />
  );
};

export function DistributionSection({
  distribution,
  formFields,
  isEditable = false,
  onEdit,
  onDelete,
  confirmingDelete = false,
  onConfirmDelete,
  onCancelDelete,
}: Readonly<DistributionSectionProps>) {
  const [isExpanded, setIsExpanded] = useState(false);

  const applicableLegislations = distribution.applicable_legislations.map(
    (applicableLegislation) => {
      const applicableLegislationField = formFields.distribution.applicable_legislations.find(
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
    },
  );

  const getConstraintIcon = (type: string) => {
    switch (type) {
      case "purpose":
        return <TagIcon className='h-5 w-5 label-lnds-color mr-1' />;
      case "temporal":
        return <ClockIcon className='h-5 w-5 label-lnds-color mr-1' />;
      case "spatial":
        return <GlobeEuropeAfricaIcon className='h-5 w-5 label-lnds-color mr-1' />;
      case "industry":
        return <BuildingOfficeIcon className='h-5 w-5 label-lnds-color mr-1' />;
      default:
        return <AdjustmentsHorizontalIcon className='h-5 w-5 label-lnds-color mr-1' />;
    }
  };

  const getConstraintValue = (type: string, value: string) => {
    if (type === "purpose") {
      return purposeOptions.find((option) => option.value === value)?.label || value;
    } else if (type === "temporal") {
      return DateUtils.formatDate(value);
    } else {
      return value;
    }
  };

  return (
    <section className='border border-gray-200 dark:border-gray-700 rounded-md section-lnds-color'>
      <div className='flex items-center justify-between p-4'>
        <div
          className='flex items-center gap-4 flex-1 min-h-0 cursor-pointer'
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <ShareIcon className='h-5 w-5 text-lnds-color cursor-pointer hover:text-lnds-dark-blue dark:hover:text-white' />
          <h4 className='text-lg md:text-xl text-lnds-color break-all leading-tight'>
            {distribution.title}
          </h4>
          <div className='flex items-center gap-4'>
            {distribution.is_analytics && (
              <div className='flex items-center text-sm text-lnds-color'>
                <ChartBarIcon className='h-4 w-4 label-lnds-color mr-1' />
                <span>Analytics</span>
              </div>
            )}
            {distribution.internal_only && (
              <div className='flex items-center text-sm text-lnds-color'>
                <LockClosedIcon className='h-4 w-4 label-lnds-color mr-1' />
                <span>Internal Only</span>
              </div>
            )}
          </div>
        </div>
        <button
          className='ml-4 p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full flex-shrink-0'
          aria-label={isExpanded ? "Collapse" : "Expand"}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? (
            <ChevronUpIcon className='h-6 w-6 text-lnds-color' />
          ) : (
            <ChevronDownIcon className='h-6 w-6 text-lnds-color' />
          )}
        </button>
      </div>

      {isExpanded && (
        <div className='px-4 pb-4'>
          {isEditable && (
            <div className='flex justify-end gap-2 mb-4 pt-2'>
              <Button
                label='Edit'
                Icon={PencilIcon}
                btnType='secondary'
                size='small'
                onClick={onEdit}
              />
              {confirmingDelete ? (
                <>
                  <Button
                    label='Confirm'
                    Icon={TrashIcon}
                    btnType='danger'
                    size='small'
                    onClick={onDelete}
                  />
                  <Button
                    label='Cancel'
                    Icon={XMarkIcon}
                    btnType='secondary'
                    size='small'
                    onClick={onCancelDelete}
                  />
                </>
              ) : (
                <Button
                  label='Delete'
                  Icon={TrashIcon}
                  btnType='danger'
                  size='small'
                  onClick={onConfirmDelete}
                />
              )}
            </div>
          )}
          <div className='grid grid-cols-1 mt-4'>
            <div>
              <DistributionFieldHeader fieldName='description' />
              <p className='text-lnds-color'>{distribution.description || "N/A"}</p>
            </div>
          </div>
          {!!distribution.distribution_path && (
            <div className='grid grid-cols-1 mt-4'>
              <DistributionFieldHeader fieldName='distribution_path' />
              <div className='text-lnds-color flex items-center'>
                <FolderIcon className='h-5 w-5 label-lnds-color mr-1' />
                <p className='text-lnds-color'>{distribution.distribution_path}</p>
              </div>
            </div>
          )}
          {!!distribution.download_urls?.length && (
            <div className='grid grid-cols-1 mt-4'>
              <div>
                <DistributionFieldHeader fieldName='download_urls' />
                <IconList
                  items={distribution.download_urls}
                  Icon={ShareIcon}
                  getHref={(item) => item}
                  openInNewTab
                  linkClassName='text-lnds-color underline break-all hover:text-lnds-dark-blue dark:hover:text-white'
                />
              </div>
            </div>
          )}
          {!!distribution.access_urls?.length && (
            <div className='grid grid-cols-1 mt-4'>
              <div>
                <DistributionFieldHeader fieldName='access_urls' />
                <IconList
                  items={distribution.access_urls}
                  Icon={ShareIcon}
                  getHref={(item) => item}
                  openInNewTab
                  linkClassName='text-lnds-color underline break-all hover:text-lnds-dark-blue dark:hover:text-white'
                />
              </div>
            </div>
          )}
          <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
            {!!distribution.rights_statement && (
              <div>
                <DistributionFieldHeader fieldName='rights_statement' label='Rights Statement' />
                <div className='text-lnds-color flex items-center'>
                  <KeyIcon className='h-5 w-5 label-lnds-color mr-1' />
                  {
                    rightStatementsLabels[
                      distribution.rights_statement as keyof typeof rightStatementsLabels
                    ]
                  }
                </div>
              </div>
            )}
            {!!distribution.license && (
              <div>
                <DistributionFieldHeader fieldName='license' label='License' />
                <div className='text-lnds-color flex items-center'>
                  <DocumentTextIcon className='h-5 w-5 label-lnds-color mr-1' />
                  <p className='text-lnds-color'>{distribution.license.eng_label}</p>
                </div>
              </div>
            )}
          </div>
          {distribution.policy_actions && distribution.policy_actions.length > 0 && (
            <div className='mt-6 mb-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md'>
              <div className='flex items-center pb-2 mb-3 border-b border-blue-200 dark:border-blue-800'>
                <DocumentTextIcon className='h-5 w-5 label-lnds-color mr-2 text-blue-700 dark:text-blue-400' />
                <div className='text-blue-800 dark:text-blue-300'>
                  <DistributionFieldHeader label='Data Use Policy' fieldName='policy_actions' />
                </div>
              </div>

              <div className='space-y-4'>
                {distribution.policy_actions.map((action, index) => (
                  <div
                    key={index}
                    className='p-4 bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-md'
                  >
                    <div className='flex items-center pb-2 mb-3 border-b-2 border-gray-300 dark:border-gray-600'>
                      <DocumentTextIcon className='h-5 w-5 mr-2 text-gray-600 dark:text-gray-300' />
                      <h6 className='font-medium text-gray-900 dark:text-gray-100'>
                        Policy Action {index + 1}
                      </h6>
                    </div>

                    <div className='grid grid-cols-1 md:grid-cols-2 gap-3'>
                      <div>
                        <label className='label-lnds-color text-sm'>Action Type</label>
                        <div className='text-lnds-color flex items-center'>
                          {action.policy_action_type === "permission" ? (
                            <ShieldCheckIcon className='h-5 w-5 text-green-600 dark:text-green-400 mr-1' />
                          ) : (
                            <ShieldExclamationIcon className='h-5 w-5 text-red-600 dark:text-red-400 mr-1' />
                          )}
                          <p
                            className={`${
                              action.policy_action_type === "permission"
                                ? "text-green-700 dark:text-green-400"
                                : "text-red-700 dark:text-red-400"
                            }`}
                          >
                            {
                              actionTypeOptions.find(
                                (option) => option.value === action.policy_action_type,
                              )?.label
                            }
                          </p>
                        </div>
                      </div>

                      {action.policy_constraint_type && (
                        <div>
                          <label className='label-lnds-color text-sm'>Constraint Type</label>
                          <div className='text-lnds-color flex items-center'>
                            <AdjustmentsHorizontalIcon className='h-5 w-5 label-lnds-color mr-1' />
                            <p className='text-lnds-color'>
                              {
                                constraintTypeOptions.find(
                                  (option) => option.value === action.policy_constraint_type,
                                )?.label
                              }
                            </p>
                          </div>
                        </div>
                      )}
                      {action.policy_constraint_type === "temporal" &&
                        (action.temporal_restriction_start || action.temporal_restriction_end) && (
                          <div className='md:col-span-2'>
                            <label className='label-lnds-color text-sm'>Temporal Restriction</label>
                            <div className='text-lnds-color flex items-center'>
                              <ClockIcon className='h-5 w-5 label-lnds-color mr-1' />
                              <p className='text-sm'>
                                {action.temporal_restriction_start
                                  ? `From ${DateUtils.formatDate(action.temporal_restriction_start)}`
                                  : ""}
                                {action.temporal_restriction_start &&
                                action.temporal_restriction_end
                                  ? " - "
                                  : ""}
                                {action.temporal_restriction_end
                                  ? `Until ${DateUtils.formatDate(action.temporal_restriction_end)}`
                                  : ""}
                              </p>
                            </div>
                          </div>
                        )}

                      {action.policy_constraint_type === "spatial" &&
                        action.spatial_restrictions &&
                        action.spatial_restrictions.length > 0 && (
                          <div className='md:col-span-2'>
                            <label className='label-lnds-color text-sm'>Spatial Restrictions</label>
                            <div className='text-lnds-color flex items-center'>
                              <GlobeEuropeAfricaIcon className='h-5 w-5 label-lnds-color mr-1' />
                              <p className='text-lnds-color'>
                                {action.spatial_restrictions.map((opt) => opt.eng_label).join(", ")}
                              </p>
                            </div>
                          </div>
                        )}

                      {(action.policy_constraint_type === "purpose" ||
                        action.policy_constraint_type === "industry") &&
                        action.policy_constraint_value && (
                          <div className='md:col-span-2'>
                            <label className='label-lnds-color text-sm'>
                              {action.policy_constraint_type === "purpose" ? "Purpose" : "Industry"}{" "}
                              Restriction
                            </label>
                            <div className='text-lnds-color flex items-center'>
                              {getConstraintIcon(action.policy_constraint_type)}
                              <p className='text-lnds-color'>
                                {getConstraintValue(
                                  action.policy_constraint_type,
                                  action.policy_constraint_value,
                                )}
                              </p>
                            </div>
                          </div>
                        )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
            {!!distribution.languages && distribution.languages.length > 0 && (
              <div>
                <DistributionFieldHeader fieldName='languages' />
                <Tags tags={distribution.languages} />
              </div>
            )}
            {!!distribution.applicable_legislations &&
              distribution.applicable_legislations.length > 0 && (
                <div className='grid grid-cols-1'>
                  <DistributionFieldHeader fieldName='applicable_legislations' />
                  <ApplicableLegislationTags legislations={applicableLegislations} />
                </div>
              )}
            {!!distribution.file_type && (
              <div>
                <DistributionFieldHeader fieldName='file_type' label='File Type' />
                <div className='text-lnds-color flex items-center'>
                  <DocumentIcon className='h-5 w-5 label-lnds-color mr-1' />
                  <p className='text-lnds-color'>{distribution.file_type.eng_label}</p>
                </div>
              </div>
            )}
            {!!distribution.media_type && (
              <div>
                <DistributionFieldHeader fieldName='media_type' />
                <div className='text-lnds-color flex items-center'>
                  <TableCellsIcon className='h-5 w-5 label-lnds-color mr-1' />
                  {distribution.media_type}
                </div>
              </div>
            )}
            {!!distribution.compression_format && (
              <div>
                <DistributionFieldHeader fieldName='compression_format' />
                <div className='text-lnds-color flex items-center'>
                  <TableCellsIcon className='h-5 w-5 label-lnds-color mr-1' />
                  {distribution.compression_format}
                </div>
              </div>
            )}
            {!!distribution.packaging_format && (
              <div>
                <DistributionFieldHeader fieldName='packaging_format' />
                <div className='text-lnds-color flex items-center'>
                  <TableCellsIcon className='h-5 w-5 label-lnds-color mr-1' />
                  {distribution.packaging_format}
                </div>
              </div>
            )}
            {distribution.byte_size && (
              <div>
                <DistributionFieldHeader fieldName='byte_size' label='Size in bytes' />
                <div className='text-lnds-color flex items-center'>
                  <p className='text-lnds-color'>
                    {distribution.byte_size.toLocaleString(undefined, { minimumFractionDigits: 0 })}
                  </p>
                </div>
              </div>
            )}
            {distribution.checksum && (
              <div>
                <DistributionFieldHeader fieldName='checksum' />
                <div className='text-lnds-color flex items-center'>
                  <p className='text-lnds-color'>{distribution.checksum}</p>
                </div>
              </div>
            )}
            {!!distribution.availability && (
              <div>
                <DistributionFieldHeader fieldName='availability' />
                <div className='text-lnds-color flex items-center'>
                  <ClockIcon className='h-5 w-5 label-lnds-color mr-1' />
                  <p className='text-lnds-color'>
                    {
                      availabilityOptions.find(
                        (option) => option.value === distribution.availability,
                      )?.label
                    }
                  </p>
                </div>
              </div>
            )}
            {!!distribution.release_date && (
              <div>
                <DistributionFieldHeader fieldName='release_date' />
                <div className='flex items-center text-lnds-color'>
                  <CalendarIcon className='h-5 w-5 mr-1' />
                  <p className='text-lnds-color'>
                    {DateUtils.formatDate(distribution.release_date)}
                  </p>
                </div>
              </div>
            )}
            {!!distribution.modification_date && (
              <div>
                <DistributionFieldHeader fieldName='modification_date' />
                <div className='flex items-center text-lnds-color'>
                  <CalendarIcon className='h-5 w-5 mr-1' />
                  <p className='text-lnds-color'>
                    {DateUtils.formatDate(distribution.modification_date)}
                  </p>
                </div>
              </div>
            )}
            {distribution.documentation && distribution.documentation.length > 0 && (
              <div>
                <DistributionFieldHeader fieldName='documentation' />
                <IconList items={distribution.documentation} Icon={DocumentTextIcon} />
              </div>
            )}
            {distribution.linked_schemas && distribution.linked_schemas.length > 0 && (
              <div>
                <DistributionFieldHeader fieldName='linked_schemas' />
                <IconList items={distribution.linked_schemas} Icon={TableCellsIcon} />
              </div>
            )}
            {distribution.distribution_dcat_status && (
              <div>
                <DistributionFieldHeader fieldName='distribution_dcat_status' />
                <div className='text-lnds-color flex items-center'>
                  <TagIcon className='h-5 w-5 label-lnds-color mr-1' />
                  <p className='text-lnds-color'>{distribution.distribution_dcat_status}</p>
                </div>
              </div>
            )}
            {distribution.spatial_resolution && (
              <div>
                <DistributionFieldHeader fieldName='spatial_resolution' />
                <div className='text-lnds-color flex items-center'>
                  <p className='text-lnds-color'>{distribution.spatial_resolution}</p>
                </div>
              </div>
            )}
            {distribution.temporal_resolution && (
              <div>
                <DistributionFieldHeader fieldName='temporal_resolution' />
                <div className='text-lnds-color flex items-center'>
                  <p className='text-lnds-color'>{distribution.temporal_resolution}</p>
                </div>
              </div>
            )}
          </div>
          {!!distribution.access_services && distribution.access_services.length > 0 && (
            <div className='mt-6 mb-4 p-4 border border-blue-200 dark:border-blue-800 rounded-md'>
              <div className='flex items-center pb-2 mb-3 border-b border-blue-200 dark:border-blue-800'>
                <ServerIcon className='h-5 w-5 label-lnds-color mr-2 text-blue-700 dark:text-blue-400' />
                <div className='text-blue-800 dark:text-blue-300'>
                  <DistributionFieldHeader fieldName='access_service_ids' />
                </div>
              </div>
              <div>
                {distribution.access_services.map((service) => (
                  <DataServiceItem
                    isSelected={false}
                    onClick={() => {}}
                    service={service}
                    clickable={false}
                    key={service.id}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
