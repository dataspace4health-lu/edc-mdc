import { useEffect, useRef, useState } from "react";
import { appAlerts } from "../../utils/appAlerts";
import { useAuth } from "../../context/AuthContext";
import { loginUrl } from "../../utils/authUrls";
import { useUIConfig } from "../../context/UIConfigContext";
import { useLoaderData } from "react-router";
import { Form, useActionData, useNavigate, useOutletContext } from "react-router-dom";
import client from "../../zodiosClient/client";
import { toDatasetDTO, toFormInputs, DatasetFormInputs } from "./datasetDTO";
import { defaultDatasetFormInputs } from "./test-data";
import { useForm, getFormProps } from "@conform-to/react";
import { useAutoSave } from "../../hooks/useAutoSave";
import DatasetFormCacheManager from "../../utils/DatasetFormCacheManager";
import { XMarkIcon, EyeIcon } from "@heroicons/react/24/solid";
import { datasetFormLoader } from "./loader";
import Header from "./Header";
import PreviewDataset from "./PreviewDataset";
import DatasetSeriesManager from "./DatasetSeriesManager";
import type { SubmissionResult } from "@conform-to/react";
import {
  InputField,
  DropdownSelect,
  TextArea,
  MultiTextArea,
  Button,
  RadioButton,
  ToggleButton,
  useAlert,
  Card,
} from "@lnds-lu/design-system";
import { ResourceDatasetType, DatasetStatusEnum } from "../../types";
import datasetSchema from "../../schemas/datasetSchema";
import CreatableDropdownSelect from "../../components/CreatableDropdown";
import { useUnsaved } from "../../context/UnSavedChangesContext";
import { filterOrganisationsByAccess } from "../../utils/organisations";
import HealthDatasetSelector from "../../components/HealthDatasetSelector";
import { useHealthDataset } from "../../hooks/useHealthDataset";
import { parseBackendErrors } from "../../utils/backendErrorParser";
import DismissibleAlert from "../../components/DismissibleAlert";
import type { MultiValue, SingleValue } from "react-select";
import { getFieldErrors } from "../../utils/formFieldErrors";
import { usePageTitle } from "../../hooks/usePageTitle";

export default function DatasetForm() {
  const { isLoading, user } = useAuth();
  const { config: uiConfig } = useUIConfig();
  const { setAlert, clearAlert } = useAlert();
  const [formSubmitClicked, setFormSubmitClicked] = useState(false);
  const [selectedPublisherId, setSelectedPublisherId] = useState<string | null>(null);
  const [selectedContactIds, setSelectedContactIds] = useState<number[]>([]);
  const [datasetCreated, setDatasetCreated] = useState(false);
  const [currentTab, setCurrentTab] = useState<string>("");
  const { isUnSaved, setIsUnSaved } = useUnsaved();
  const [showResetMessage, setShowResetMessage] = useState(false);

  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (!isUnSaved) return;
      e.preventDefault();
      e.returnValue = "";
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [isUnSaved, setIsUnSaved]);

  if (!isLoading && !user) {
    window.location.href = loginUrl();
  }

  const navigate = useNavigate();
  const outletContext = useOutletContext() as
    | { dataset: ResourceDatasetType; triggerActivityLogRefresh: () => void }
    | null
    | undefined;

  const datasetLoaderData = outletContext?.dataset;
  const triggerActivityLogRefresh = outletContext?.triggerActivityLogRefresh;
  const formLoaderData = (useLoaderData() as Awaited<ReturnType<typeof datasetFormLoader>>) || [
    null,
    null,
  ];

  usePageTitle(datasetLoaderData ? datasetLoaderData.title : "Add Dataset");

  // Use health dataset hook
  const {
    isHealthDataset,
    healthDataAccessLevel,
    setIsHealthDataset,
    setHealthDataAccessLevel,
    handleAccessLevelChange,
    shouldShowHealthFields,
  } = useHealthDataset(datasetLoaderData);

  const onSaveDraft = async (dataset: DatasetFormInputs) => {
    try {
      if (datasetLoaderData) {
        await client.edit_dataset_api_v1_datasets__dataset_id__put(toDatasetDTO(dataset), {
          params: { dataset_id: datasetLoaderData.id },
          withCredentials: true,
        });
        setAlert(appAlerts.datasetUpdated());
        setIsUnSaved(false);
        triggerActivityLogRefresh?.();
        return navigate(`/datasets/${datasetLoaderData.id}/edit`);
      } else {
        const response = await client.create_dataset_api_v1_datasets_post(toDatasetDTO(dataset), {
          withCredentials: true,
        });
        DatasetFormCacheManager.clear();
        setDatasetCreated(true);
        setTimeout(() => {
          navigate(`/datasets/${response.id}/edit`);
        }, 3000);
        setIsUnSaved(false);
        return;
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      console.log(err);
      if (err?.response?.status === 422) {
        // Parse backend validation errors
        const parsedErrors = parseBackendErrors(err.response);
        // Show alert with field-specific error if available
        const errorEntries = Object.entries(parsedErrors);
        const errorMessages = errorEntries.map(([field, messages]) => {
          const fieldName = field.split(".").pop() || field; // Get last part of nested field
          return `${fieldName}: ${messages[0]}`;
        });

        setAlert(
          appAlerts.genericValidationError(
            errorMessages.join("; ") || appAlerts.pleaseFixFormErrors().message,
          ),
        );
      } else if (err?.response?.status === 409) {
        setAlert(appAlerts.datasetDuplicateExists());
      } else {
        setAlert(
          appAlerts.genericValidationError(err?.message || appAlerts.serverErrorTryLater().message),
        );
      }
    }
  };

  const actionData = useActionData() as SubmissionResult<string[]>;
  const formErrors = actionData?.status === "error" ? actionData?.error : null;

  const errorsInDebugMode =
    import.meta.env.DEV && formErrors && Object.keys(formErrors).length !== 0
      ? JSON.stringify(formErrors, null, 2)
      : null;

  const validationErrors =
    formErrors && Object.keys(formErrors).length !== 0 ? "Please fix the errors in the form" : null;
  const hadValidationAlertRef = useRef(false);

  let savedFormData = DatasetFormCacheManager.getFormData();
  if (datasetLoaderData) {
    savedFormData = toFormInputs(datasetLoaderData);

    if (datasetLoaderData.status !== DatasetStatusEnum.DRAFT) {
      const customError = new Error("Dataset is not in DRAFT status");
      // @ts-expect-error custom error handling
      customError.response = { status: 409 };
      throw customError;
    }
  }

  const luxembourgSpatialCoverage = formLoaderData.dataset.spatial_coverages.find(
    (c) => c.value === "http://publications.europa.eu/resource/authority/country/LUX",
  );

  const formDefaultValues =
    formLoaderData.organisation.organisations.length === 1
      ? {
          spatial_coverages: luxembourgSpatialCoverage
            ? [luxembourgSpatialCoverage.value]
            : undefined,
          themes: user?.default_themes ?? [],
          publisherId: formLoaderData.organisation.organisations[0].value,
          creatorId: [formLoaderData.organisation.organisations[0].value],
          contactIds:
            formLoaderData.contact.contacts.length === 1
              ? [formLoaderData.contact.contacts[0].value]
              : [],
        }
      : {
          themes: user?.default_themes ?? [],
          spatial_coverages: luxembourgSpatialCoverage
            ? [luxembourgSpatialCoverage.value]
            : undefined,
        };

  const [form, fields] = useForm({
    lastResult: actionData || undefined,
    shouldValidate: "onSubmit",
    defaultValue:
      savedFormData || (import.meta.env.DEV ? defaultDatasetFormInputs : formDefaultValues),
  });

  useEffect(() => {
    if (!selectedPublisherId && fields.publisherId.value) {
      setSelectedPublisherId(fields.publisherId.value);
    }
  }, [fields.publisherId.value, selectedPublisherId]);

  const [isDatasetSeries, setIsDatasetSeries] = useState(
    fields.isDatasetSeries.value === undefined
      ? !!datasetLoaderData?.is_dataset_series
      : fields.isDatasetSeries.value,
  );

  const [memberDatasets, setMemberDatasets] = useState<string>(fields.memberDatasets.value || "");

  useEffect(() => {
    if (errorsInDebugMode || validationErrors) {
      window.scrollTo({ top: 0, behavior: "instant" });
      setAlert(appAlerts.genericValidationError(errorsInDebugMode ?? validationErrors!));
      hadValidationAlertRef.current = true;
    } else {
      // Do not clear alerts on initial mount; only clear validation alerts we previously set here.
      if (hadValidationAlertRef.current) {
        clearAlert();
        hadValidationAlertRef.current = false;
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [errorsInDebugMode, validationErrors]);

  const formRef = useRef(null);

  if (!datasetLoaderData) {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    useAutoSave({ formRef }); // NOSONAR
  }

  const contactOptions = formLoaderData.contact.contacts
    .filter((contact) => {
      if (contact.is_deprecated) return false;
      if (selectedPublisherId) {
        return contact.parent_value === selectedPublisherId.toString();
      }

      if (fields.publisherId.value) {
        return contact.parent_value === fields.publisherId.value.toString();
      }

      // If no publisher is selected yet, filter by user's organization for multi-tenant users
      if (
        user?.feature_options.enable_multi_tenants &&
        !user?.permissions?.includes("roles:manage")
      ) {
        // Show only contacts from user's current organization
        return contact.parent_value === user?.current_organisation?.id.toString();
      }

      // For admin users or single-tenant setups, show all contacts
      return true;
    })
    .map((contact) => ({
      label: contact.eng_label,
      value: contact.value,
    }));

  const getCreatedOptions = (values: (string | undefined)[] | string) => {
    if (!Array.isArray(values)) {
      return [];
    }

    return values.map((v) => ({ value: v!, label: v! }));
  };

  const rawKeywords = form.value?.keywords;
  const keywords = Array.isArray(rawKeywords)
    ? (rawKeywords.filter((k): k is string => typeof k === "string") as string[])
    : typeof rawKeywords === "string"
      ? [rawKeywords]
      : undefined;

  const rawApplicableLegislations = form.value?.applicableLegislations;
  const applicableLegislations = Array.isArray(rawApplicableLegislations)
    ? (rawApplicableLegislations.filter((l): l is string => typeof l === "string") as string[])
    : typeof rawApplicableLegislations === "string"
      ? [rawApplicableLegislations]
      : undefined;

  const handlePublisherChange = ({
    contactIds,
    keywords,
    applicableLegislations,
  }: {
    contactIds: number[] | undefined;
    keywords: string[] | undefined;
    applicableLegislations: string[] | undefined;
  }) => {
    const isEmpty =
      contactIds === undefined || contactIds.length === 0
        ? (keywords === undefined || keywords.length === 0) &&
          (applicableLegislations === undefined || applicableLegislations.length === 0)
        : false;

    if (!isEmpty) {
      setShowResetMessage(true);
    }
  };

  return (
    <>
      <Card
        className={`my-6 p-8 ${
          datasetLoaderData
            ? "max-w-3xl flex flex-col justify-self-center"
            : "mx-6  max-w-2xl lg:max-w-4xl md:mx-auto"
        }`}
      >
        <Header isEditForm={!!datasetLoaderData} />
        <div>
          <div className='flex flex-col gap-6'>
            {datasetLoaderData?.version_change_type === "UNDERLYING_DATA" && (
              <DismissibleAlert
                type='info'
                message='Data and metadata changed. Please review Version, Version Notes, and Modification Date fields before submitting.'
              />
            )}
            <Form
              method='post'
              {...getFormProps(form)}
              className='flex flex-col gap-6'
              ref={formRef}
              onChange={() => setIsUnSaved(true)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && e.target instanceof HTMLInputElement) {
                  e.preventDefault();
                }
              }}
            >
              <HealthDatasetSelector
                isHealthDataset={isHealthDataset}
                healthDataAccessLevel={healthDataAccessLevel}
                onHealthDatasetChange={(isHealth) => {
                  setIsHealthDataset(isHealth);
                  if (!isHealth) {
                    setHealthDataAccessLevel(null);
                  }
                  setIsUnSaved(true);
                }}
                onAccessLevelChange={(level) => {
                  handleAccessLevelChange(level);
                  setIsUnSaved(true);
                }}
              />
              <input
                type='hidden'
                name='_enableHealthDcat'
                value={isHealthDataset ? "true" : "false"}
              />

              {datasetSchema.map((field) => {
                // Hide health-specific fields based on state
                if (!shouldShowHealthFields(field.name)) {
                  return null;
                }

                if (field.hide && field.hide(user)) {
                  return null;
                }

                if (field.name === "publisherId") {
                  const activeOrganisations = filterOrganisationsByAccess(
                    formLoaderData.organisation.organisations,
                    uiConfig?.is_ctie_instance,
                    user?.feature_options?.enable_multi_tenants,
                    user?.feature_options?.enable_dual_instance,
                  );

                  const filteredFormLoaderData = {
                    ...formLoaderData,
                    organisation: {
                      ...formLoaderData.organisation,
                      organisations: activeOrganisations,
                    },
                  };
                  return (
                    <div key={field.name} className='relative'>
                      <DropdownSelect
                        key={field.name}
                        name={field.name}
                        label={field.longLabel}
                        popoverInfo={field.explanation}
                        options={field.options!(filteredFormLoaderData, user)}
                        isMulti={field.isMulti!}
                        required={field.required}
                        errors={formErrors?.[field.name]}
                        defaultValue={fields[field.name].value}
                        // eslint-disable-next-line @typescript-eslint/no-explicit-any
                        onChange={(option: any) => {
                          handlePublisherChange({
                            contactIds: selectedContactIds,
                            keywords,
                            applicableLegislations,
                          });
                          setSelectedPublisherId(option!.value);
                          setIsUnSaved(true);
                        }}
                      />
                      {showResetMessage && user?.feature_options.enable_multi_tenants && (
                        <span className='mt-1 text-sm text-lnds-red'>
                          You have changed the selected <strong> Publisher</strong>. Please verify
                          the <strong>Contact Point</strong>,<strong> Keywords</strong>, and
                          <strong> Applicable Legislation</strong> fields as they may have been
                          updated or reset.
                        </span>
                      )}
                    </div>
                  );
                } else if (field.name === "contactIds") {
                  return (
                    <DropdownSelect
                      key={field.name + "-" + selectedPublisherId}
                      name={field.name}
                      label={field.longLabel}
                      popoverInfo={field.explanation}
                      options={contactOptions}
                      defaultValue={fields[field.name].value}
                      errors={formErrors?.[field.name]}
                      isMulti={field.isMulti!}
                      required={field.required}
                      recommended={field.recommended}
                      info={field.info}
                      // eslint-disable-next-line @typescript-eslint/no-explicit-any
                      onChange={(option: any) => {
                        const selections = Array.isArray(option) ? option : option ? [option] : [];
                        // eslint-disable-next-line @typescript-eslint/no-explicit-any
                        setSelectedContactIds(selections.map((o: any) => Number(o.value)));
                        setIsUnSaved(true);
                      }}
                    />
                  );
                } else if (field.name === "rightsStatement") {
                  return (
                    <RadioButton
                      key={field.name}
                      name={field.name}
                      label={field.longLabel}
                      popoverInfo={field.explanation}
                      defaultValue={fields[field.name].value}
                      options={field.options!(formLoaderData, user)}
                      errors={formErrors?.[field.name]}
                      onClick={() => {
                        setIsUnSaved(true);
                      }}
                      required={field.required}
                    />
                  );
                } else if (field.name === "isDatasetSeries" && !datasetLoaderData) {
                  return (
                    <>
                      <ToggleButton
                        yesLabel='Yes'
                        noLabel='No'
                        key={fields[field.name as keyof typeof fields].name}
                        name='isDatasetSeries'
                        popoverInfo={field.explanation}
                        onChange={(ev) => {
                          setIsDatasetSeries(ev.target.checked);
                          setIsUnSaved(true);
                        }}
                        defaultValue={!!isDatasetSeries}
                        label={field.longLabel}
                      />
                      {isDatasetSeries && (
                        <>
                          <DatasetSeriesManager
                            selectedDatasets={
                              memberDatasets
                                ? memberDatasets.split(",").map((id) => parseInt(id))
                                : []
                            }
                            onChange={(datasetIds) => {
                              setMemberDatasets(datasetIds.join(","));
                              setIsUnSaved(true);
                            }}
                          />
                          <input
                            type='hidden'
                            name={fields.memberDatasets.name}
                            value={memberDatasets}
                          />
                        </>
                      )}
                    </>
                  );
                } else if (field.type === "InputField") {
                  return (
                    <InputField
                      key={field.name}
                      name={field.name}
                      label={field.longLabel}
                      popoverInfo={field.explanation}
                      type={field.inputType!}
                      defaultValue={fields[field.name as keyof typeof fields].value as string}
                      errors={fields[field.name as keyof typeof fields].errors}
                      required={field.required}
                      recommended={field.recommended}
                      maxLength={field.maxLength}
                      info={field.info}
                    />
                  );
                } else if (field.type === "TextArea") {
                  return (
                    <TextArea
                      key={field.name}
                      name={field.name}
                      label={field.longLabel}
                      popoverInfo={field.explanation}
                      defaultValue={fields[field.name as keyof typeof fields].value as string}
                      errors={fields[field.name as keyof typeof fields].errors}
                      required={field.required}
                      recommended={field.recommended}
                      minLength={field.minLength}
                      info={field.info}
                    />
                  );
                } else if (field.type === "MultiTextArea") {
                  const fieldValue = fields[field.name as keyof typeof fields].value;
                  const defaultValues = Array.isArray(fieldValue)
                    ? (fieldValue.filter((v): v is string => typeof v === "string") as string[])
                    : fieldValue
                      ? [fieldValue as string]
                      : [];
                  return (
                    <MultiTextArea
                      key={field.name}
                      name={field.name}
                      label={field.longLabel}
                      popoverInfo={field.explanation}
                      defaultValues={defaultValues}
                      errors={fields[field.name as keyof typeof fields].errors}
                      required={field.required}
                      recommended={field.recommended}
                      minLength={field.minLength}
                      info={field.info}
                      placeholder={field.placeholder}
                      onChange={(values) => {
                        form.update({ name: field.name, value: values });
                        setIsUnSaved(true);
                      }}
                    />
                  );
                } else if (field.type === "DropdownSelect") {
                  const isResettable = ["keywords", "applicableLegislations"].includes(field.name);
                  const isHealthField =
                    field.name === "healthCategories" || field.name === "healthThemes";
                  // Use key to force remount health fields when toggling, resettable fields on publisher change
                  const key = isHealthField
                    ? `${field.name}-${isHealthDataset}`
                    : isResettable
                      ? `${field.name}-${selectedPublisherId}`
                      : field.name;

                  const options = field.options!(formLoaderData, user, selectedPublisherId);

                  return (
                    <DropdownSelect
                      key={key}
                      name={field.name}
                      label={field.longLabel}
                      popoverInfo={field.explanation}
                      options={options}
                      defaultValue={fields[field.name as keyof typeof fields].value}
                      errors={formErrors?.[field.name]}
                      isMulti={field.isMulti!}
                      isClearable={field.isClearable}
                      info={field.info}
                      required={field.required}
                      recommended={field.recommended}
                      onChange={(newValue) => {
                        const values = Array.isArray(newValue) ? newValue.map((v) => v.value) : [];
                        form.update({ name: field.name, value: values });
                        setIsUnSaved(true);
                      }}
                    />
                  );
                } else if (field.type === "CreatableSelect") {
                  return (
                    <CreatableDropdownSelect
                      key={fields[field.name as keyof typeof fields].name}
                      name={fields[field.name as keyof typeof fields].name}
                      label={field.shortLabel}
                      explanation={field.explanation}
                      popoverInfo={field.explanation}
                      options={getCreatedOptions(
                        (fields[field.name as keyof typeof fields].value as
                          | string
                          | (string | undefined)[]) || [],
                      )}
                      isMulti={field.isMulti!}
                      required={field.required}
                      errors={getFieldErrors(formErrors, field.name)}
                      info={field.info}
                      defaultValue={fields[field.name as keyof typeof fields].value}
                      recommended={field.recommended}
                      placeholder={field.placeholder}
                      onChange={(newValue) => {
                        const singleValue = newValue as SingleValue<{
                          label: string;
                          value: string;
                        }>;
                        const values = Array.isArray(newValue)
                          ? (newValue as MultiValue<{ label: string; value: string }>).map(
                              (item) => item.value,
                            )
                          : singleValue?.value
                            ? [singleValue.value]
                            : [];

                        form.update({ name: field.name, value: values });
                        setIsUnSaved(true);
                      }}
                    />
                  );
                }
              })}
              <div className='flex flex-row gap-3 justify-end'>
                <Button
                  btnType='danger'
                  Icon={XMarkIcon}
                  label='Cancel'
                  onClick={(e) => {
                    e.preventDefault();
                    setIsUnSaved(false);
                    navigate("/");
                  }}
                />
                <Button
                  isFormSubmit={true}
                  Icon={EyeIcon}
                  label='Preview & Save'
                  onClick={() => setFormSubmitClicked(true)}
                />
              </div>
            </Form>
          </div>
        </div>
      </Card>
      <PreviewDataset
        onSubmission={onSaveDraft}
        datasetFormValues={
          actionData?.status === "success"
            ? (form.value as unknown as DatasetFormInputs)
            : undefined
        }
        isSubmitting={actionData?.status === "success" && formSubmitClicked}
        formLoaderData={formLoaderData}
        onModalOpen={() => setFormSubmitClicked(false)}
        datasetCreated={datasetCreated}
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
      />
    </>
  );
}
