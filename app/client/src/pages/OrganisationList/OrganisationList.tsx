import { useState, useEffect, useRef } from "react";
import { appAlerts } from "../../utils/appAlerts";
import { Button, Card, CardHeading, InputField, DropdownSelect } from "@lnds-lu/design-system";
import {
  PlusCircleIcon,
  BuildingOfficeIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  XMarkIcon,
} from "@heroicons/react/24/solid";
import { useLoaderData } from "react-router";
import EmptyScreen from "../../components/EmptyScreen";
import SearchBar from "../../components/SearchBar";
import OrganisationItem from "./OrganisationItem";
import { ResourceOrganisation } from "../../types";
import { Form } from "react-router-dom";
import { useForm, getFormProps } from "@conform-to/react";
import { parseWithZod } from "@conform-to/zod/v4";
import { useAlert } from "@lnds-lu/design-system";
import { OrganisationFormInputsSchema } from "./dto";
import client from "../../zodiosClient/client";
import { organisationListLoader } from "./loader";
import { isAxiosError } from "axios";
import { useAuth } from "../../context/AuthContext";
import { RightSidebar } from "../../components/RightSidebar";
import { usePageTitle } from "../../hooks/usePageTitle";

const OrganisationList: React.FC = () => {
  usePageTitle("Organisations");
  const [organisations, setOrganisations] = useState<ResourceOrganisation[]>([]);
  const [selectedOrganisation, setSelectedOrganisation] = useState<ResourceOrganisation | null>(
    null,
  );
  const [isFormExpanded, setIsFormExpanded] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const fetchedOrganisations =
    (useLoaderData() as Awaited<ReturnType<typeof organisationListLoader>>) || [];
  const { user } = useAuth();
  const canAddOrganisation = user?.permissions.includes("organisations:edit");
  const canEditOrganisations =
    user?.permissions.includes("organisations:edit") ||
    user?.permissions.includes("organisations:edit:organisation");

  useEffect(() => {
    if (fetchedOrganisations) {
      setOrganisations(fetchedOrganisations);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const scopedOrganisations = organisations.filter((org) => {
    if (user?.permissions?.includes("organisations:edit")) {
      return true;
    }
    return user?.current_organisation?.id === org.id;
  });

  const filteredOrganisations = scopedOrganisations.filter(
    (org) =>
      org.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (org.email || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
      (org.type || "").toLowerCase().includes(searchTerm.toLowerCase()),
  );

  const onEdit = (organisation: ResourceOrganisation) => {
    setFormKey((prev) => prev + 1);
    setSelectedOrganisation(organisation);
    setIsFormExpanded(true);
  };

  const handleCancel = () => {
    setSelectedOrganisation(null);
    setFormErrors({});
    setFormKey((prev) => prev + 1);
    setIsFormExpanded(false);
  };

  const { setAlert, clearAlert } = useAlert();
  const formRef = useRef(null);

  const [formKey, setFormKey] = useState(0);
  const [formErrors, setFormErrors] = useState<Record<string, string[] | null>>({});

  const errorsInDebugMode =
    import.meta.env.DEV && formErrors && Object.keys(formErrors).length !== 0
      ? JSON.stringify(formErrors, null, 2)
      : null;
  const validationErrors =
    formErrors && Object.keys(formErrors).length !== 0 ? "Please fix the errors in the form" : null;

  const [form] = useForm({
    shouldValidate: "onSubmit",
    defaultValue: {},
    async onSubmit(event, { formData }) {
      event.preventDefault();
      const submission = parseWithZod(formData, { schema: OrganisationFormInputsSchema });

      const reply = await submission.reply();

      if (reply.status === "error" && reply.error) {
        setFormErrors(reply.error);

        return;
      }

      try {
        const accessibleWithinCtieValue =
          submission.payload.accessible_within_ctie === "yes"
            ? true
            : submission.payload.accessible_within_ctie === "no"
              ? false
              : undefined;

        const basePayload = {
          name: submission.payload.name as string,
          type: submission.payload.type as string,
          email: submission.payload.email as string,
        };

        const fullPayload = user?.feature_options?.enable_multi_tenants
          ? {
              ...basePayload,
              category: submission.payload.category as string | undefined,
              accessible_within_ctie: accessibleWithinCtieValue,
            }
          : basePayload;

        if (selectedOrganisation) {
          const updatedOrg =
            await client.update_organisation_api_v1_organisations__organisation_id__put(
              fullPayload,
              {
                params: {
                  organisation_id: selectedOrganisation.id,
                },
                withCredentials: true,
              },
            );

          setOrganisations((prev) =>
            prev.map((org) => (org.id === selectedOrganisation.id ? updatedOrg : org)),
          );
          setAlert(appAlerts.organisationUpdated());
          handleCancel();
        } else {
          const createdOrg = await client.create_organisation_api_v1_organisations_post(
            fullPayload,
            {
              withCredentials: true,
            },
          );

          setOrganisations((prev) => [createdOrg, ...prev]);
          setAlert(appAlerts.organisationCreated());
        }
        setFormKey((prev) => prev + 1);
        setFormErrors({});
      } catch (error: unknown) {
        if (isAxiosError(error)) {
          if (error.response?.status === 400) {
            setAlert(appAlerts.organisationDuplicate());
          } else {
            // @ts-expect-error error response structure
            setAlert(appAlerts.genericValidationError(error.response.data.detail));
          }
        } else {
          setAlert(appAlerts.unknownError());
        }
      }
    },
  });

  const handleDeprecate = async (organisation: ResourceOrganisation, isDeprecated: boolean) => {
    setOrganisations((prev) =>
      prev.map((org) =>
        org.id === organisation.id ? { ...org, is_deprecated: isDeprecated } : org,
      ),
    );
  };

  useEffect(() => {
    if (errorsInDebugMode || validationErrors) {
      setAlert(appAlerts.genericValidationError(errorsInDebugMode || validationErrors!));
    } else {
      clearAlert();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [errorsInDebugMode, validationErrors]);

  return (
    <div className='my-6 mx-6 max-w-2xl lg:max-w-4xl md:mx-auto'>
      {(selectedOrganisation && canEditOrganisations) || canAddOrganisation ? (
        <Card className='p-4 md:p-8' key={formKey}>
          <div
            className={`rounded-t flex flex-row justify-between items-center section-lnds-color ${isFormExpanded ? "mb-4" : ""}`}
          >
            <CardHeading
              label={selectedOrganisation ? "Edit Organisation" : "Add Organisation"}
              Icon={PlusCircleIcon}
              className='flex'
            />
            <Button
              label={isFormExpanded ? "Collapse Form" : "Expand Form"}
              onClick={() => setIsFormExpanded(!isFormExpanded)}
              Icon={isFormExpanded ? ChevronUpIcon : ChevronDownIcon}
            />
          </div>

          <div
            className={`transition-all duration-300 ${
              isFormExpanded ? "max-h-[1000px] opacity-100" : "max-h-0 opacity-0 overflow-hidden"
            }`}
          >
            <div className='flex flex-col gap-6'>
              <Form
                method='post'
                className='flex flex-col gap-6'
                {...getFormProps(form)}
                ref={formRef}
              >
                <InputField
                  name='name'
                  label='Organisation Name'
                  info='Enter the name of the organisation'
                  errors={formErrors?.name || []}
                  defaultValue={selectedOrganisation?.name}
                  type='text'
                />
                <DropdownSelect
                  isMulti={false}
                  name='type'
                  label='Organisation Type'
                  info='Select the type of the organisation'
                  errors={formErrors?.type || []}
                  defaultValue={selectedOrganisation?.type || ""}
                  options={[
                    {
                      value: "academic_scientific_organisation",
                      label: "Academic - Scientific Organisation",
                    },
                    { value: "company", label: "Company" },
                    { value: "industry_consortium", label: "Industry Consortium" },
                    { value: "local_authority", label: "Local Authority" },
                    { value: "national_authority", label: "National Authority" },
                    {
                      value: "non_governmental_organisation",
                      label: "Non Governmental Organisation",
                    },
                    { value: "non_profit_organisation", label: "Non Profit Organisation" },
                    { value: "private_individuals", label: "Private Individual(s)" },
                    { value: "regional_authority", label: "Regional Authority" },
                    { value: "standardisation_body", label: "Standardisation Body" },
                    { value: "supra_national_authority", label: "Supra National Authority" },
                  ]}
                />
                <InputField
                  name='email'
                  label='Organisation Email'
                  info='Enter the email of the organisation'
                  errors={formErrors?.email || []}
                  defaultValue={selectedOrganisation?.email || ""}
                  type='email'
                />
                {user?.feature_options?.enable_multi_tenants && (
                  <>
                    <DropdownSelect
                      isMulti={false}
                      name='category'
                      label='Organisation Category'
                      info='Select EP (Entité publique) or OSP (Organisme du secteur public)'
                      errors={formErrors?.category || []}
                      defaultValue={selectedOrganisation?.category || ""}
                      options={[
                        { value: "EP", label: "EP (Entité publique / Public entity)" },
                        {
                          value: "OSP",
                          label: "OSP (Organisme du secteur public / Public sector body)",
                        },
                      ]}
                    />
                    <DropdownSelect
                      isMulti={false}
                      name='accessible_within_ctie'
                      label='Accessible within CTIE'
                      info='Indicate if this organisation is accessible within the CTIE infrastructure'
                      errors={formErrors?.accessible_within_ctie || []}
                      defaultValue={
                        selectedOrganisation?.accessible_within_ctie === true
                          ? "yes"
                          : selectedOrganisation?.accessible_within_ctie === false
                            ? "no"
                            : ""
                      }
                      options={[
                        { value: "", label: "Not known" },
                        { value: "yes", label: "Yes" },
                        { value: "no", label: "No" },
                      ]}
                    />
                  </>
                )}

                <div className='flex flex-row gap-3 justify-end'>
                  {selectedOrganisation && (
                    <Button
                      btnType='secondary'
                      Icon={XMarkIcon}
                      label='Cancel'
                      onClick={handleCancel}
                    />
                  )}
                  <Button
                    isFormSubmit={true}
                    Icon={BuildingOfficeIcon}
                    label={selectedOrganisation ? "Update Organisation" : "Create Organisation"}
                  />
                </div>
              </Form>
            </div>
          </div>
        </Card>
      ) : (
        <Card className='p-4 md:p-8'>
          <CardHeading label='Organisations' Icon={BuildingOfficeIcon} className='flex' />
        </Card>
      )}
      <div className='mt-6'>
        <Card className='p-0 overflow-hidden'>
          <SearchBar
            searchTerm={searchTerm}
            onSearch={setSearchTerm}
            placeholder='Search Organisations...'
          />

          <div
            className='overflow-y-auto border-t border-lnds-color relative'
            style={{
              height: "calc(50vh)",
              scrollbarWidth: "thin",
              scrollbarColor: "#cbd5e0 #f7fafc",
            }}
          >
            <div className='sticky top-0 h-3  z-10 pointer-events-none'></div>

            {filteredOrganisations.length > 0 ? (
              <div className='pb-4'>
                {filteredOrganisations.map((organisation) => (
                  <OrganisationItem
                    organisation={organisation}
                    onEdit={onEdit}
                    onDeprecate={handleDeprecate}
                    key={organisation.id}
                  />
                ))}
              </div>
            ) : (
              <div className='p-8'>
                <EmptyScreen message='No organisations available' Icon={BuildingOfficeIcon} />
              </div>
            )}

            {filteredOrganisations.length > 3 && (
              <div className='sticky bottom-0 h-3 z-10 pointer-events-none'></div>
            )}
          </div>

          <div className='p-3 bg-gray-50 dark:bg-gray-700 border-t border-lnds-color text-xs text-gray-500 dark:text-gray-400'>
            Showing {filteredOrganisations.length} of {scopedOrganisations.length} organisations
          </div>
        </Card>
      </div>
      <RightSidebar
        entityId={null}
        entityType='organisation'
        organisations={organisations}
        className='border-l border-lnds-color'
        defaultIsOpen={false}
        refreshTrigger={organisations.length}
        onSidebarToggle={() => {}}
      />
    </div>
  );
};

export default OrganisationList;
