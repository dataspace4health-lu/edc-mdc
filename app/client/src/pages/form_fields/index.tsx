import { useState, useEffect, useMemo } from "react";
import { TagIcon, ScaleIcon } from "@heroicons/react/24/solid";
import { useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { RightSidebar } from "../../components/RightSidebar";
import { ResourceFormField, ApplicableLegislationFormField, FilterTypes } from "../../types";
import { useUrlState } from "../../hooks/useUrlState";
import client from "../../zodiosClient/client";
import FormFieldsForm from "./FormFieldsForm";
import FormFieldsList from "./FormFieldsList";
import FormFieldFilterList from "../../components/Filters/FormFieldFilterList";
import { Spinner } from "../../components/Spinner";
import { usePageTitle } from "../../hooks/usePageTitle";

const FormFields: React.FC = () => {
  const [fieldType, setFieldType] = useState("keyword");
  const [sidebarKey, setSidebarKey] = useState(0);
  const [current, setCurrent] = useState<ResourceFormField | ApplicableLegislationFormField | null>(
    null,
  );
  const [fieldValues, setFieldValues] = useState<
    ResourceFormField[] | ApplicableLegislationFormField[]
  >([]);
  const [isLoading, setIsLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(0);
  const [error, setError] = useState<Error | null>(null);
  const [filtersApplied, setFiltersApplied] = useState(false);

  const path = useLocation().pathname;
  const { user } = useAuth();
  const { getPageParam, getFilter } = useUrlState(user?.permissions || []);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [orgOptions, setOrgOptions] = useState<{ label: string; value: number }[]>([]);

  const pageTitle = path.includes("applicable_legislation")
    ? "Applicable Legislations"
    : "Keywords";
  usePageTitle(pageTitle);

  const query = getPageParam("query");
  const page = getPageParam("page");
  const pageSize = getPageParam("pageSize");

  const allFilters = [FilterTypes.FormFieldOrganisations];
  const filterMap = useMemo(() => {
    return new Map<FilterTypes, string[]>(allFilters.map((filter) => [filter, getFilter(filter)]));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [allFilters.map((f) => getFilter(f).join(",")).join(",")]);

  const serializedFilterMap = JSON.stringify(Array.from(filterMap.values()));

  useEffect(() => {
    (async () => {
      const orgs = await client.get_organisations_api_v1_organisations_get({
        withCredentials: true,
      });

      const filteredOrgs = (orgs || []).filter((o) => !o.is_deprecated);

      setOrgOptions(
        filteredOrgs.map((o) => ({
          label: o.name,
          value: o.id,
        })),
      );
    })();
  }, []);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const formatting: Record<string, { singular: string; plural: string; Icon: any }> = {
    keyword: { singular: "Keyword", plural: "Keywords", Icon: TagIcon },
    applicable_legislation: {
      singular: "Applicable Legislation",
      plural: "Applicable Legislations",
      Icon: ScaleIcon,
    },
  };

  const fetchFormFields = async (fType: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const organisationFilters = filterMap.get(FilterTypes.FormFieldOrganisations) ?? [];

      const response = await client.get_all_form_fields_api_v1_form_fields__field_type__all_post(
        {
          page: Number(page),
          page_size: Number(pageSize),
          query: query || undefined,
          organisation_filters: organisationFilters.length ? organisationFilters : undefined,
        },
        {
          params: {
            field_type: fType,
          },
          withCredentials: true,
        },
      );

      setFieldValues(response.items || []);
      setTotalCount(response.meta?.total_items || 0);
    } catch (error) {
      console.error("Failed to fetch form fields:", error);
      setError(error as Error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    let fieldType = "keyword";
    if (path.includes("keywords")) {
      fieldType = "keyword";
    } else if (path.includes("applicable_legislation")) {
      fieldType = "applicable_legislation";
    }
    setFieldType(fieldType);
    setCurrent(null);
    const organisationFilters = filterMap.get(FilterTypes.FormFieldOrganisations) ?? [];

    const isAnyFilterApplied = (query && query.length > 0) || organisationFilters.length > 0;

    setFiltersApplied(isAnyFilterApplied);
    fetchFormFields(fieldType);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [path, query, serializedFilterMap, page, pageSize]);

  if (error) {
    throw error;
  }

  const canEdit = (field: ResourceFormField | ApplicableLegislationFormField) => {
    if (user?.permissions.includes("form-fields:edit")) return true;

    if (user?.permissions.includes("form-fields:edit:my")) {
      return field.created_by_id === user?.id;
    }
    if (user?.permissions.includes("form-fields:edit:organisation")) {
      const orgField = field as { organisation_ids?: number[] };
      const ids = orgField.organisation_ids;

      return Array.isArray(ids)
        ? user?.assignments.map((a) => a.organisation_id).some((orgId) => ids.includes(orgId))
        : false;
    }
    return false;
  };

  const filteredOrgOptions = orgOptions.filter((og) => {
    if (user?.permissions?.includes("form-fields:edit")) {
      return true;
    }
    return user?.current_organisation?.id === og.value;
  });

  const showOrgDropdown =
    user?.permissions?.includes("roles:manage") || (user?.assignments?.length ?? 0) > 0;

  const handleEditField = (field: ResourceFormField | ApplicableLegislationFormField) => {
    const base = {
      key: field.key,
      eng_label: field.eng_label,
      description: (field as ApplicableLegislationFormField).description || "",
      link: (field as ApplicableLegislationFormField).link || "",
      created_by_id: field.created_by_id,
      created_by_name: field.created_by_name,
    };

    const withOrgIds = {
      ...base,
      organisation_ids: Array.isArray((field as { organisation_ids?: number[] }).organisation_ids)
        ? (field as { organisation_ids?: number[] }).organisation_ids
        : [],
    };

    setCurrent(withOrgIds);
  };

  const handleFieldUpdated = () => {
    fetchFormFields(fieldType);
    setSidebarKey((prev) => prev + 1);
  };

  return (
    <div className='flex flex-col gap-y-6 lg:gap-y-0 lg:flex-row lg:gap-x-4 mx-4 2xl:mx-24 my-4'>
      <div className='w-full lg:w-1/4 mt-6'>
        <FormFieldFilterList
          organisations={filteredOrgOptions}
          fieldTypeName={formatting[fieldType].plural}
        />
      </div>

      <div className='w-full lg:w-3/4'>
        <div className='my-6'>
          <FormFieldsForm
            fieldType={fieldType}
            current={current}
            setCurrent={setCurrent}
            formatting={formatting}
            filteredOrgOptions={filteredOrgOptions}
            showOrgDropdown={showOrgDropdown}
            onFieldUpdated={handleFieldUpdated}
            setSidebarKey={setSidebarKey}
          />

          <div className='mt-6'>
            {isLoading ? (
              <div className='flex justify-center items-center h-48'>
                <Spinner />
              </div>
            ) : (
              <FormFieldsList
                fieldType={fieldType}
                formatting={formatting}
                fields={fieldValues}
                current={current}
                canEdit={canEdit}
                onEditField={handleEditField}
                query={query}
                currentPage={Number(page)}
                totalPages={Math.ceil(totalCount / Number(pageSize))}
                pageSize={Number(pageSize)}
                totalCount={totalCount}
                isLoading={isLoading}
                filtersApplied={filtersApplied}
                orgOptions={orgOptions}
                onFieldUpdated={handleFieldUpdated}
              />
            )}
          </div>
        </div>
      </div>

      <div
        className={`transition-all duration-300 ease-in-out ${
          isSidebarOpen ? "w-[28rem]" : "w-0"
        } overflow-hidden`}
      >
        <RightSidebar
          refreshTrigger={sidebarKey}
          /* @ts-expect-error  entityType: "dataset" | "organisation" do not exist in the type */
          entityType={fieldType}
          className='border-l border-lnds-color'
          defaultIsOpen={false}
          onSidebarToggle={(isOpen: boolean) => setIsSidebarOpen(isOpen)}
          isOpen={isSidebarOpen}
        />
      </div>
    </div>
  );
};

export default FormFields;
