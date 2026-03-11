import { Card, Button } from "@lnds-lu/design-system";
import { PencilIcon, GlobeAltIcon } from "@heroicons/react/24/solid";
import { LinkIcon, BuildingOfficeIcon } from "@heroicons/react/24/solid";
import EmptyScreen from "../../components/EmptyScreen";
import InitialsAvatar from "../../components/InitialsAvatar";
import SearchPanel from "../DatasetList/SearchPanel";
import Pagination from "../DatasetList/Pagination";
import PromoteToGlobal from "./PromoteToGlobal";
import { ResourceFormField, ApplicableLegislationFormField } from "../../types";
import { useAuth } from "../../context/AuthContext";

interface FormFieldsListProps {
  fieldType: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  formatting: Record<string, { singular: string; plural: string; Icon: any }>;
  fields: (ResourceFormField | ApplicableLegislationFormField)[];
  current: ResourceFormField | ApplicableLegislationFormField | null;
  canEdit: (field: ResourceFormField | ApplicableLegislationFormField) => boolean;
  onEditField: (field: ResourceFormField | ApplicableLegislationFormField) => void;
  query: string;
  currentPage: number;
  totalPages: number;
  pageSize: number;
  totalCount: number;
  isLoading: boolean;
  filtersApplied: boolean;
  orgOptions: { label: string; value: number }[];
  onFieldUpdated: () => void;
}

const FormFieldsList: React.FC<FormFieldsListProps> = ({
  fieldType,
  formatting,
  fields,
  current,
  canEdit,
  onEditField,
  query,
  currentPage,
  totalPages,
  pageSize,
  totalCount,
  isLoading,
  filtersApplied,
  orgOptions,
  onFieldUpdated,
}) => {
  const { user } = useAuth();
  const Icon = formatting[fieldType].Icon;

  const orgLabelById = new Map(orgOptions.map((o) => [o.value, o.label]));

  const renderOrgList = (ids?: number[]) => {
    if (!Array.isArray(ids) || ids.length === 0) {
      return (
        <span className='text-justify text-sm break-words text-lnds-light-gray'>
          <GlobeAltIcon className='h-4 w-4 inline-block mr-1' />
          Global
        </span>
      );
    }
    const names = ids.map((id) => orgLabelById.get(id) ?? `Org ${id}`);
    return (
      <div className='text-justify text-sm break-words text-lnds-light-gray space-y-1'>
        {names.map((name, index) => (
          <div key={index} className='flex items-center text-xs'>
            <BuildingOfficeIcon className='h-4 w-4 inline-block mr-1' />
            {name}
          </div>
        ))}
      </div>
    );
  };

  const canPromoteToGlobal = (field: ResourceFormField | ApplicableLegislationFormField) => {
    return (
      user?.permissions?.includes("roles:manage") &&
      Array.isArray((field as { organisation_ids?: number[] }).organisation_ids) &&
      (field as { organisation_ids?: number[] }).organisation_ids!.length > 0
    );
  };

  return (
    <>
      <Card className='flex flex-col h-full px-0 pb-0'>
        <div className='px-4 flex justify-between items-center'>
          <div className='flex items-center gap-2'>
            <Icon className='h-5 w-5 heading-lnds-color' />
            <h2 className='text-2xl font-semibold heading-lnds-color'>
              {formatting[fieldType].plural}
              <span className='ml-2 text-sm bg-lnds-purple text-white px-2 py-0.5 rounded-full'>
                {totalCount}
              </span>
            </h2>
          </div>
        </div>
        <SearchPanel
          query={query}
          placeholder={`Search ${formatting[fieldType].plural.toLowerCase()}...`}
          noBorder
        />
      </Card>

      {!isLoading && (filtersApplied || query) && fields.length > 0 && (
        <div className='mt-3 mb-4 px-4 py-3 section-lnds-color border-l-4 border-lnds-blue rounded-md text-lnds-color text-sm font-medium'>
          <strong className='text-base'>{totalCount}</strong>{" "}
          {totalCount === 1 ? "result" : "results"} found with filters or query
        </div>
      )}

      <Card className='mt-4 p-0 flex-grow overflow-y-auto'>
        {fields.length > 0 ? (
          <div>
            {fields.map((field) => (
              <div
                key={field.key}
                className={`border-b border-lnds-color w-full ${
                  current?.key === field.key ? "bg-lnds-purple text-white" : ""
                }`}
              >
                <div className='p-4 flex justify-between items-start w-full'>
                  <InitialsAvatar
                    name={field.created_by_name}
                    showTooltip={true}
                    isSystem={!field.created_by_name}
                  />
                  <div className='flex flex-col w-full flex-1 min-w-0 ml-2 mr-2'>
                    <span
                      className={`font-medium mb-1 ${
                        current?.key === field.key ? "text-white" : "heading-lnds-color"
                      }`}
                    >
                      <Icon className='h-4 w-4 inline-block mr-1' />
                      {field.eng_label}
                    </span>
                    {fieldType === "applicable_legislation" && (
                      <span
                        className={`text-justify text-sm break-words mb-2 ${
                          current?.key === field.key ? "text-white" : "text-lnds-color"
                        }`}
                      >
                        {(field as ApplicableLegislationFormField).description}
                      </span>
                    )}
                    {fieldType === "applicable_legislation" &&
                      !!(field as ApplicableLegislationFormField).link && (
                        <a
                          href={
                            typeof (field as ApplicableLegislationFormField).link === "string"
                              ? (field as ApplicableLegislationFormField).link
                              : ""
                          }
                          target='_blank'
                          rel='noopener noreferrer'
                          className={`text-xs mb-2 hover:underline dark:hover:text-lnds-lightest-gray inline-flex items-center gap-1 hover:text-lnds-dark-blue ${
                            current?.key === field.key
                              ? "text-gray-500 dark:text-lnds-light-gray"
                              : "text-lnds-color"
                          }`}
                        >
                          <LinkIcon className='h-3 w-3 inline-block mr-1' />
                          {typeof (field as ApplicableLegislationFormField).link === "string"
                            ? (field as ApplicableLegislationFormField).link
                            : ""}
                        </a>
                      )}
                    {renderOrgList((field as { organisation_ids?: number[] }).organisation_ids)}
                  </div>
                  {canEdit(field) && (
                    <div className='flex gap-1'>
                      <Button
                        btnType='transparent'
                        Icon={PencilIcon}
                        className={`${current?.key === field.key ? "text-white" : ""}`}
                        onClick={() => onEditField(field)}
                      />
                      {canPromoteToGlobal(field) && (
                        <PromoteToGlobal
                          field={field as ResourceFormField | ApplicableLegislationFormField}
                          fieldType={fieldType}
                          formatting={formatting}
                          onPromoteSuccess={onFieldUpdated}
                          isCurrentField={current?.key === field.key}
                        />
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className='p-4'>
            <EmptyScreen
              message={`No ${formatting[fieldType].plural.toLowerCase()} found`}
              Icon={formatting[fieldType].Icon}
            />
          </div>
        )}
      </Card>

      {totalPages > 1 && (
        <div className='px-4 pb-4'>
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            pageSize={pageSize}
            query={query}
          />
        </div>
      )}
    </>
  );
};

export default FormFieldsList;
