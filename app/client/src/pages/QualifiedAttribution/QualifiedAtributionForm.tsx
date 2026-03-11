import { useState, useRef, useEffect } from "react";
import { appAlerts } from "../../utils/appAlerts";
import { Button, Card, CardHeading, DropdownSelect } from "@lnds-lu/design-system";
import {
  PlusCircleIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  XMarkIcon,
  TrashIcon,
  BuildingOfficeIcon,
} from "@heroicons/react/24/solid";
import { Form } from "react-router-dom";
import { useForm, getFormProps } from "@conform-to/react";
import { parseWithZod } from "@conform-to/zod/v4";
import { useAlert } from "@lnds-lu/design-system";
import { QualifiedAttributionSchema } from "./dto";
import client from "../../zodiosClient/client";
import { ResourceQualifiedAttribution } from "../../types";
import { QualifiedAttributionRoleOptions } from "./dto";

interface QualifiedAttributionFormProps {
  datasetId: number;
  current: ResourceQualifiedAttribution | null;
  setCurrent: (attribution: ResourceQualifiedAttribution | null) => void;
  organisations: { value: string; label: string }[];
  onAttributionUpdated: () => void;
  triggerActivityLogRefresh?: () => void;
}

const QualifiedAttributionForm: React.FC<QualifiedAttributionFormProps> = ({
  datasetId,
  current,
  setCurrent,
  organisations,
  onAttributionUpdated,
  triggerActivityLogRefresh,
}) => {
  const [isFormExpanded, setIsFormExpanded] = useState(false);
  const [formKey, setFormKey] = useState(0);
  const [formErrors, setFormErrors] = useState<Record<string, string[] | null>>({});
  const { setAlert, clearAlert } = useAlert();
  const formRef = useRef(null);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const getErrorMessage = (err: any): string => {
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
        await client.delete_qualified_attribution_api_v1_datasets__dataset_id__qualified_attributions__attribution_id__delete(
          undefined,
          {
            params: {
              dataset_id: datasetId,
              attribution_id: current.id,
            },
            withCredentials: true,
          },
        );

        setAlert(appAlerts.qualifiedAttributionDeleted());
        setCurrent(null);
        setFormErrors({});
        setIsFormExpanded(false);
        onAttributionUpdated();
        triggerActivityLogRefresh?.();
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } catch (error: any) {
        setAlert(appAlerts.genericValidationError(getErrorMessage(error)));
      }
    }
  };

  const [form] = useForm({
    id: current ? String(current.id) : undefined,
    shouldValidate: "onSubmit",
    defaultValue: current
      ? {
          datasetId: String(datasetId),
          organisationId: String(current.organisation_id),
          role: current.role,
        }
      : {},
    async onSubmit(event, { formData }) {
      event.preventDefault();
      const submission = parseWithZod(formData, { schema: QualifiedAttributionSchema });

      const reply = await submission.reply();

      if (reply.status === "error" && reply.error) {
        setFormErrors(reply.error);
        return;
      }

      const payload = {
        organisation_id: Number(submission.payload.organisationId),
        role: submission.payload.role as string,
      };

      if (current) {
        try {
          await client.update_qualified_attribution_api_v1_datasets__dataset_id__qualified_attributions__attribution_id__put(
            payload,
            {
              params: {
                dataset_id: datasetId,
                attribution_id: current.id,
              },
              withCredentials: true,
            },
          );

          setAlert(appAlerts.qualifiedAttributionUpdated());
          setFormKey((prev) => prev + 1);
          setCurrent(null);
          setFormErrors({});
          setIsFormExpanded(false);
          onAttributionUpdated();
          triggerActivityLogRefresh?.();
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
          setAlert(appAlerts.genericValidationError(getErrorMessage(err)));
        }
      } else {
        try {
          await client.add_qualified_attribution_api_v1_datasets__dataset_id__qualified_attributions_post(
            payload,
            {
              params: {
                dataset_id: datasetId,
              },
              withCredentials: true,
            },
          );

          setAlert(appAlerts.qualifiedAttributionCreated());
          setFormKey((prev) => prev + 1);
          setCurrent(null);
          setFormErrors({});
          setIsFormExpanded(false);
          onAttributionUpdated();
          triggerActivityLogRefresh?.();
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
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
  };

  const handleExpandForCreate = () => {
    setCurrent(null);
    setFormKey((prev) => prev + 1);
    setIsFormExpanded(!isFormExpanded);
  };

  return (
    <Card className='p-8' key={formKey}>
      <div
        className={`rounded-t flex flex-row justify-between items-center section-lnds-color ${
          isFormExpanded ? "mb-4" : ""
        }`}
      >
        <CardHeading
          label={`${current ? "Edit" : "Add"} Qualified Attribution`}
          Icon={PlusCircleIcon}
          className='flex'
        />
        {current && (
          <Button
            className='bg-lnds-red w-1/4'
            isFormSubmit={false}
            onClick={handleDelete}
            Icon={TrashIcon}
            label='Delete Attribution'
          />
        )}
        {!current && (
          <Button
            btnType='transparent'
            label={isFormExpanded ? "Collapse Form" : "Expand Form"}
            onClick={handleExpandForCreate}
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
            <input type='hidden' name='datasetId' value={datasetId} />

            <DropdownSelect
              name='organisationId'
              label='Organisation'
              options={organisations}
              isMulti={false}
              required
              errors={formErrors?.organisationId || []}
              defaultValue={current ? String(current.organisation_id) : ""}
              placeholder='Select an organisation...'
            />
            <DropdownSelect
              name='role'
              label='Role'
              options={QualifiedAttributionRoleOptions}
              isMulti={false}
              required
              errors={formErrors?.role || []}
              defaultValue={current?.role || ""}
              placeholder='Select a role...'
            />
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
                Icon={BuildingOfficeIcon}
                label={`${current ? "Update" : "Add"} Attribution`}
              />
            </div>
          </Form>
        </div>
      </div>
    </Card>
  );
};

export default QualifiedAttributionForm;
