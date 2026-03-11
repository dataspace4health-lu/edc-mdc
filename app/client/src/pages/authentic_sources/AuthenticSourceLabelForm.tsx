import { useEffect, useState } from "react";
import { useAlert } from "@lnds-lu/design-system";
import { PencilIcon, XMarkIcon } from "@heroicons/react/24/solid";
import { Button, InputField, TextArea } from "@lnds-lu/design-system";
import { Form } from "react-router-dom";
import { useForm, getFormProps } from "@conform-to/react";
import { parseWithZod } from "@conform-to/zod/v4";
import { AuthenticSouceLabelFormSchema } from "./dto";
import client from "../../zodiosClient/client";
import { isAxiosError } from "axios";
import { ResourceAuthenticSourceLabel } from "../../types";
import { appAlerts } from "../../utils/appAlerts";

interface AuthenticSourceLabelFormProps {
  isCondensed?: boolean;
  label?: ResourceAuthenticSourceLabel | null;
  onCreate?: (label: ResourceAuthenticSourceLabel) => void;
  onUpdate?: (label: ResourceAuthenticSourceLabel) => void;
  onCancel: () => void;
}

const AuthenticSourceLabelForm = ({
  isCondensed,
  label,
  onCreate,
  onUpdate,
  onCancel,
}: AuthenticSourceLabelFormProps) => {
  const [formKey, setFormKey] = useState(0);
  const { setAlert, clearAlert } = useAlert();
  const [formErrors, setFormErrors] = useState<Record<string, string[] | null>>({});

  const errorsInDebugMode =
    import.meta.env.DEV && formErrors && Object.keys(formErrors).length !== 0
      ? JSON.stringify(formErrors, null, 2)
      : null;
  const validationErrors =
    formErrors && Object.keys(formErrors).length !== 0 ? "Please fix the errors in the form" : null;

  const [form] = useForm({
    id: label ? `edit-label-${label.id}` : "create-label",
    shouldValidate: "onSubmit",
    defaultValue: label
      ? {
          name: label.name,
          description: label.description,
        }
      : {},
    async onSubmit(event, { formData }) {
      event.preventDefault();
      const submission = parseWithZod(formData, { schema: AuthenticSouceLabelFormSchema });
      const reply = await submission.reply();

      if (reply.status === "error" && reply.error) {
        setFormErrors(reply.error);
        return;
      }

      if (!label && onCreate) {
        try {
          const response =
            await client.create_authentic_source_label_api_v1_authentic_source_labels_post(
              {
                name: submission.payload.name as string,
                description: submission.payload.description as string,
              },
              {
                withCredentials: true,
              },
            );
          setAlert(appAlerts.authenticSourceLabelAdded());
          setFormKey((prev) => prev + 1);
          setFormErrors({});
          onCreate(response);
        } catch (error: unknown) {
          console.log("Error creating label:", error);
          if (isAxiosError(error)) {
            // @ts-expect-error error response structure
            setAlert(appAlerts.genericValidationError(error.response.data.detail));
          } else {
            setAlert(appAlerts.unknownError());
          }
        }
        return;
      }

      try {
        const response =
          await client.update_authentic_source_label_api_v1_authentic_source_labels__label_id__put(
            {
              name: submission.payload.name as string,
              description: submission.payload.description as string,
            },
            {
              params: { label_id: label!.id },
              withCredentials: true,
            },
          );

        setAlert(appAlerts.authenticSourceLabelUpdated());
        setFormKey((prev) => prev + 1);
        setFormErrors({});
        onUpdate && onUpdate(response);
      } catch (error: unknown) {
        console.log("Error updating label:", error);
        if (isAxiosError(error)) {
          // @ts-expect-error error response structure
          setAlert(appAlerts.genericValidationError(error.response.data.detail));
        } else {
          setAlert(appAlerts.unknownError());
        }
      }
    },
  });

  useEffect(() => {
    if (errorsInDebugMode || validationErrors) {
      setAlert(appAlerts.genericValidationError(errorsInDebugMode || validationErrors!));
    } else {
      clearAlert();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [errorsInDebugMode, validationErrors]);

  useEffect(() => {
    setFormKey((prev) => prev + 1);
  }, [label]);

  return (
    <div className='p-4'>
      <Form
        key={formKey}
        {...getFormProps(form)}
        method='post'
        className={`w-full ${isCondensed ? "space-y-2" : "flex flex-col gap-6"}`}
      >
        <InputField
          name='name'
          label='Name'
          type='text'
          required
          placeholder='Name'
          defaultValue={label?.name}
          errors={formErrors?.name || []}
        />
        <TextArea
          name='description'
          label='Description'
          defaultValue={label?.description || ""}
          errors={formErrors?.description || []}
          required
        />
        <div className='mt-4 flex justify-end gap-3'>
          <Button onClick={onCancel} btnType='secondary' label='Cancel' Icon={XMarkIcon} />
          <Button
            label={label ? "Update Label" : "Create Label"}
            isFormSubmit={true}
            Icon={PencilIcon}
          />
        </div>
      </Form>
    </div>
  );
};

export default AuthenticSourceLabelForm;
