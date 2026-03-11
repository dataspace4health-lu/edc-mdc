import { useState, useRef, useEffect } from "react";
import { appAlerts } from "../../utils/appAlerts";
import {
  Button,
  Card,
  CardHeading,
  DropdownSelect,
  InputField,
  TextArea,
} from "@lnds-lu/design-system";
import {
  PlusCircleIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  XMarkIcon,
  TrashIcon,
} from "@heroicons/react/24/solid";
import { Form } from "react-router-dom";
import { useForm, getFormProps } from "@conform-to/react";
import { parseWithZod } from "@conform-to/zod/v4";
import { useAlert } from "@lnds-lu/design-system";
import { FormInputsSchema, toFormInputs } from "./dto";
import client from "../../zodiosClient/client";
import { ResourceFormField, ApplicableLegislationFormField } from "../../types";
import LegislationSearch, { LegislationResult } from "./LegislationSearch";

interface FormFieldsFormProps {
  fieldType: string;
  current: ResourceFormField | ApplicableLegislationFormField | null;
  setCurrent: (field: ResourceFormField | ApplicableLegislationFormField | null) => void;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  formatting: Record<string, { singular: string; plural: string; Icon: any }>;
  filteredOrgOptions: { label: string; value: number }[];
  showOrgDropdown: boolean;
  onFieldUpdated: () => void;
  setSidebarKey: (fn: (prev: number) => number) => void;
}

const FormFieldsForm: React.FC<FormFieldsFormProps> = ({
  fieldType,
  current,
  setCurrent,
  formatting,
  filteredOrgOptions,
  showOrgDropdown,
  onFieldUpdated,
  setSidebarKey,
}) => {
  const [isFormExpanded, setIsFormExpanded] = useState(false);
  const [formKey, setFormKey] = useState(0);
  const [formErrors, setFormErrors] = useState<Record<string, string[] | null>>({});
  const { setAlert, clearAlert } = useAlert();
  const formRef = useRef(null);
  const [legislationData, setLegislationData] = useState<LegislationResult | null>(null);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const getErrorMessage = (err: any): string => {
    if (err?.cause?.issues) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return err.cause.issues.map((issue: any) => issue.message).join(", ");
    }
    if (err?.response?.data?.detail) {
      return err.response.data.detail;
    }
    return "Server error. Please try again later.";
  };

  const errorsInDebugMode =
    import.meta.env.DEV && formErrors && Object.keys(formErrors).length !== 0
      ? JSON.stringify(formErrors, null, 2)
      : null;
  const validationErrors =
    formErrors && Object.keys(formErrors).length !== 0 ? "Please fix the errors in the form" : null;

  useEffect(() => {
    if (current) {
      setIsFormExpanded(true);
      setFormErrors({});
      setFormKey((prev) => prev + 1);
      setLegislationData(null);
    }
  }, [current]);

  useEffect(() => {
    if (errorsInDebugMode || validationErrors) {
      setAlert(appAlerts.genericValidationError(errorsInDebugMode || validationErrors!));
    } else {
      clearAlert();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [errorsInDebugMode, validationErrors]);

  const handleDelete = async () => {
    if (current) {
      try {
        await client.delete_form_field_api_v1_form_fields__field_type__delete_put(
          {
            key: current.key,
            eng_label: current.eng_label,
          },
          {
            params: {
              field_type: fieldType,
            },
            withCredentials: true,
          },
        );

        setAlert(appAlerts.singularDeleted(formatting[fieldType].singular));
        setCurrent(null);
        setFormErrors({});
        setIsFormExpanded(false);
        setSidebarKey((prev) => prev + 1);
        onFieldUpdated();
      } catch (error) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        if ((error as any).status === 400) {
          setAlert(appAlerts.formFieldInUse());
        } else {
          setAlert(appAlerts.genericValidationError(getErrorMessage(error)));
        }
      }
    }
  };

  const [form] = useForm({
    id: current ? current.key : undefined,
    shouldValidate: "onSubmit",
    defaultValue: current ? toFormInputs(current) : {},
    async onSubmit(event, { formData }) {
      event.preventDefault();
      const submission = parseWithZod(formData, { schema: FormInputsSchema });

      const reply = await submission.reply();

      if (reply.status === "error" && reply.error) {
        setFormErrors(reply.error);
        return;
      }

      const orgIds = Array.isArray(submission.payload.organisationIds)
        ? (submission.payload.organisationIds as string[]).map(Number)
        : submission.payload.organisationIds
          ? [Number(submission.payload.organisationIds as string)]
          : [];

      if (current) {
        try {
          await client.update_form_field_api_v1_form_fields__field_type__put(
            {
              key: current.key,
              eng_label: submission.payload.engLabel as string,
              ...(fieldType === "applicable_legislation" && {
                description: (submission.payload as ApplicableLegislationFormField).description,
                link: (submission.payload as ApplicableLegislationFormField).link,
              }),
              ...((fieldType === "keyword" || fieldType === "applicable_legislation") && {
                organisation_ids: orgIds,
              }),
            },
            {
              params: {
                field_type: fieldType,
              },
              withCredentials: true,
            },
          );

          setAlert(appAlerts.singularUpdated(formatting[fieldType].singular));
          setFormKey((prev) => prev + 1);
          setCurrent(null);
          setIsFormExpanded(false);
          setSidebarKey((prev) => prev + 1);
          onFieldUpdated();
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
          console.log(err);
          setAlert(appAlerts.genericValidationError(getErrorMessage(err)));
        }
      } else {
        try {
          await client.create_form_field_api_v1_form_fields__field_type__post(
            {
              eng_label: submission.payload.engLabel as string,
              ...(fieldType === "applicable_legislation" && {
                description: (submission.payload as ApplicableLegislationFormField).description,
                link: (submission.payload as ApplicableLegislationFormField).link,
              }),
              ...(fieldType === "keyword" || fieldType === "applicable_legislation"
                ? { organisation_ids: orgIds }
                : {}),
            },
            {
              params: {
                field_type: fieldType,
              },
              withCredentials: true,
            },
          );

          setAlert(appAlerts.singularCreated(formatting[fieldType].singular));
          setFormKey((prev) => prev + 1);
          setCurrent(null);
          setFormErrors({});
          setIsFormExpanded(false);
          setSidebarKey((prev) => prev + 1);
          onFieldUpdated();
          setLegislationData(null);
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
          console.log(err);
          setAlert(appAlerts.genericValidationError(getErrorMessage(err)));
        }
      }
    },
  });

  const handleCancel = () => {
    setCurrent(null);
    setFormErrors({});
    setFormKey((prev) => prev + 1);
    setIsFormExpanded(false);
    setLegislationData(null);
  };

  const handleLegislationSelect = (result: LegislationResult) => {
    setLegislationData(result);
  };

  return (
    <Card className='p-8' key={formKey}>
      <div
        className={`rounded-t flex flex-row justify-between items-center section-lnds-color ${
          isFormExpanded ? "mb-4" : ""
        }`}
      >
        <CardHeading
          label={`${current ? "Edit" : "Create"} ${formatting[fieldType].singular}`}
          Icon={PlusCircleIcon}
          className='flex'
        />
        {current && (
          <Button
            className='bg-lnds-red w-1/4'
            isFormSubmit={false}
            onClick={() => handleDelete()}
            Icon={TrashIcon}
            label={`Delete ${formatting[fieldType].singular}`}
          />
        )}
        {!current && (
          <Button
            btnType='transparent'
            label={isFormExpanded ? "Collapse Form" : "Expand Form"}
            onClick={() => setIsFormExpanded(!isFormExpanded)}
            Icon={isFormExpanded ? ChevronUpIcon : ChevronDownIcon}
          />
        )}
      </div>

      <div
        className={`transition-all duration-300 ${
          isFormExpanded ? "max-h-[1000px] opacity-100" : "max-h-0 opacity-0 overflow-hidden"
        }`}
      >
        <div className='flex flex-col gap-6'>
          <Form method='post' className='flex flex-col gap-6' {...getFormProps(form)} ref={formRef}>
            {fieldType === "applicable_legislation" && !current && (
              <LegislationSearch onSelect={handleLegislationSelect} />
            )}
            <InputField
              name='engLabel'
              label='Label'
              info={`Label is used as display name for the ${formatting[fieldType].singular}.`}
              errors={formErrors?.engLabel || []}
              defaultValue={current ? current.eng_label : legislationData?.label || ""}
              type='text'
              key={legislationData ? `label-${legislationData.id}` : "label-empty"}
            />
            {fieldType === "applicable_legislation" && (
              <TextArea
                name='description'
                label='Description'
                info={`Description is used to describe the ${formatting[fieldType].singular}.`}
                errors={formErrors?.description || []}
                defaultValue={
                  current
                    ? (current as ApplicableLegislationFormField).description
                    : legislationData?.description || ""
                }
                key={legislationData ? `description-${legislationData.id}` : "description-empty"}
              />
            )}
            {fieldType === "applicable_legislation" && (
              <InputField
                name='link'
                label='Link'
                type='url'
                info={`Link is used to provide a link to the  ${formatting[fieldType].singular}.`}
                errors={formErrors?.link || []}
                defaultValue={
                  current
                    ? (current as ApplicableLegislationFormField).link
                    : legislationData?.link || ""
                }
                key={legislationData ? `link-${legislationData.id}` : "link-empty"}
              />
            )}
            {showOrgDropdown && (
              <DropdownSelect
                name='organisationIds'
                label='Organisations'
                info='If you are assigned to only one organisation or no organisation, you can ignore this field.'
                options={filteredOrgOptions.map((o) => ({
                  label: o.label,
                  value: o.value.toString(),
                }))}
                defaultValue={
                  current &&
                  Array.isArray((current as { organisation_ids?: number[] }).organisation_ids)
                    ? (
                        (current as { organisation_ids?: number[] }).organisation_ids as number[]
                      ).map(String)
                    : []
                }
                errors={formErrors?.organisationIds || []}
                isClearable={true}
                isMulti={true}
              />
            )}
            <div className='flex flex-row gap-3 justify-end'>
              {current && (
                <Button
                  btnType='secondary'
                  Icon={XMarkIcon}
                  label='Cancel'
                  onClick={handleCancel}
                />
              )}
              <Button
                isFormSubmit={true}
                Icon={formatting[fieldType].Icon}
                label={`${current ? "Update" : "Create"} ${formatting[fieldType].singular}`}
              />
            </div>
          </Form>
        </div>
      </div>
    </Card>
  );
};

export default FormFieldsForm;
