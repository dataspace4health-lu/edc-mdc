import { useState, useEffect, useRef } from "react";
import { Button, InputField } from "@lnds-lu/design-system";
import { XMarkIcon, ServerIcon } from "@heroicons/react/24/solid";
import { Form } from "react-router-dom";
import { useForm, getFormProps } from "@conform-to/react";
import { useAlert } from "@lnds-lu/design-system";
import client from "../../zodiosClient/client";
import EndpointsList from "./EndpointsList";
import { ResourceDataService, ResourceDataServiceEndpoint } from "../../types";
import { DataServiceFormSchema } from "./dto";
import { parseWithZod } from "@conform-to/zod/v4";
import { appAlerts } from "../../utils/appAlerts";
import { isAxiosError } from "axios";

interface DataServiceFormProps {
  currentService: ResourceDataService | null;
  onServiceCreated: (service: ResourceDataService) => void;
  onServiceUpdated: (service: ResourceDataService) => void;
  onCancel: () => void;
  onDelete: (service: ResourceDataService) => void;
}

const DataServiceForm: React.FC<DataServiceFormProps> = ({
  currentService,
  onServiceCreated,
  onServiceUpdated,
  onCancel,
  // @ts-expect-error value is never used
  onDelete,
}) => {
  const [endpoints, setEndpoints] = useState<ResourceDataServiceEndpoint[]>(
    currentService?.endpoints || [],
  );
  const [formErrors, setFormErrors] = useState<Record<string, string[] | null>>({});
  const { setAlert, clearAlert } = useAlert();
  const formRef = useRef(null);

  const errorsInDebugMode =
    import.meta.env.DEV && formErrors && Object.keys(formErrors).length !== 0
      ? JSON.stringify(formErrors, null, 2)
      : null;
  const validationErrors =
    formErrors && Object.keys(formErrors).length !== 0 ? "Please fix the errors in the form" : null;

  useEffect(() => {
    if (errorsInDebugMode || validationErrors) {
      setAlert(appAlerts.genericValidationError(errorsInDebugMode || validationErrors!));
    } else {
      clearAlert();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [errorsInDebugMode, validationErrors]);

  const [form, fields] = useForm({
    shouldValidate: "onSubmit",
    defaultValue: currentService ? { title: currentService.title } : { title: "" },
    async onSubmit(event, { formData }) {
      event.preventDefault();
      const submission = parseWithZod(formData, { schema: DataServiceFormSchema });

      const reply = await submission.reply();

      if (reply.status === "error" && reply.error) {
        setFormErrors(reply.error);

        return;
      }

      try {
        if (currentService?.id) {
          const updatedService =
            await client.update_data_service_api_v1_data_services__data_service_id__put(
              // @ts-expect-error  Argument of type 'Record<string, SubmissionPayload<FormDataEntryValue>>' is not assignable
              submission.payload,
              {
                params: {
                  data_service_id: currentService.id,
                },
                withCredentials: true,
              },
            );

          onServiceUpdated(updatedService);
        } else {
          const createdService = await client.create_data_service_api_v1_data_services_post(
            // @ts-expect-error  Argument of type 'Record<string, SubmissionPayload<FormDataEntryValue>>' is not assignable
            submission.payload,
            {
              withCredentials: true,
            },
          );

          onServiceCreated(createdService);
        }
      } catch (error) {
        console.error("Error saving data service:", error);
        setAlert(
          appAlerts.genericValidationError(
            isAxiosError(error)
              ? error.response?.data?.detail || appAlerts.serverErrorTryLater().message
              : appAlerts.serverErrorTryLater().message,
          ),
        );
      }
      setFormErrors({});
    },
  });

  const handleAddEndpoint = () => {
    setEndpoints((prev) => [...prev, { endpoint_url: "", endpoint_description: "" }]);
  };

  const handleDeleteEndpoint = (index: number) => {
    setEndpoints((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className='flex flex-col gap-6'>
      <Form method='post' className='flex flex-col gap-6' {...getFormProps(form)} ref={formRef}>
        <InputField
          name='title'
          label='Service Title'
          info='Enter a descriptive title for this data service'
          errors={formErrors?.title || []}
          defaultValue={fields.title.value}
          type='text'
          required
        />

        <div className='mt-4 border-t pt-4'>
          <EndpointsList
            endpoints={endpoints}
            onAddEndpoint={handleAddEndpoint}
            onDeleteEndpoint={handleDeleteEndpoint}
            formErrors={formErrors}
          />
        </div>
        <div className='flex flex-row gap-3 justify-end'>
          {currentService && (
            <Button btnType='secondary' Icon={XMarkIcon} label='Cancel' onClick={onCancel} />
          )}
          <Button
            isFormSubmit={true}
            Icon={ServerIcon}
            label={`${currentService ? "Update" : "Create"} Data Service`}
          />
        </div>
      </Form>
    </div>
  );
};

export default DataServiceForm;
