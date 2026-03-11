import { useAlert } from "@lnds-lu/design-system";
import { useEffect, useState, useRef } from "react";
import { ResourceContact } from "../../../types";
import { PlusCircleIcon, XMarkIcon } from "@heroicons/react/24/solid";
import { Button, InputField } from "@lnds-lu/design-system";
import { Form } from "react-router-dom";
import { useForm, getFormProps } from "@conform-to/react";
import { parseWithZod } from "@conform-to/zod/v4";
import { ContactFormInputSchema } from "./dto";
import client from "../../../zodiosClient/client";
import { isAxiosError } from "axios";
import { appAlerts } from "../../../utils/appAlerts";

export default function ContactForm({
  organisationId,
  onAddContact,
  onUpdateContact,
  clearContact,
  contact,
}: Readonly<{
  organisationId: number;
  onAddContact: (response: ResourceContact) => void;
  onUpdateContact: (response: ResourceContact) => void;
  clearContact: () => void;
  contact?: ResourceContact | null;
}>) {
  const { setAlert, clearAlert } = useAlert();
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
      const submission = parseWithZod(formData, { schema: ContactFormInputSchema });

      const reply = await submission.reply();

      if (reply.status === "error" && reply.error) {
        setFormErrors(reply.error);

        return;
      }

      try {
        if (contact) {
          const response =
            await client.update_contact_api_v1_organisations__organisation_id__contacts__contact_id__put(
              {
                name: submission.payload.name as string,
                email: submission.payload.email as string,
                role: submission.payload.role as string,
              },
              {
                params: {
                  organisation_id: organisationId,
                  contact_id: contact.id,
                },
                withCredentials: true,
              },
            );
          setAlert(appAlerts.contactUpdated());
          setFormKey((prev) => prev + 1);
          setFormErrors({});
          onUpdateContact(response);
          return;
        }

        const response =
          await client.add_contact_api_v1_organisations__organisation_id__contacts_post(
            {
              name: submission.payload.name as string,
              email: submission.payload.email as string,
              role: submission.payload.role as string,
            },
            {
              params: { organisation_id: organisationId },
              withCredentials: true,
            },
          );
        setAlert(appAlerts.contactAdded());
        setFormKey((prev) => prev + 1);
        setFormErrors({});
        onAddContact(response);
      } catch (error: unknown) {
        if (isAxiosError(error)) {
          if (error.response?.status === 400) {
            setAlert(appAlerts.contactDuplicate());
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

  useEffect(() => {
    if (errorsInDebugMode || validationErrors) {
      setAlert(appAlerts.genericValidationError(errorsInDebugMode || validationErrors!));
    } else {
      clearAlert();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [errorsInDebugMode, validationErrors]);

  useEffect(() => {
    if (contact) {
      setFormKey((prev) => prev + 1);
    }
  }, [contact]);

  const formRef = useRef(null);

  return (
    <Form
      key={formKey}
      {...getFormProps(form)}
      ref={formRef}
      method='post'
      className='w-full flex flex-col lg:flex-row space-y-4 lg:space-y-0 lg:space-x-4 items-start'
    >
      <InputField
        className='lg:w-1/4 w-full'
        name='name'
        type='text'
        required
        placeholder='Name'
        errors={formErrors?.name || []}
        defaultValue={contact?.name || ""}
      />
      <InputField
        name='email'
        type='text'
        required
        placeholder='Email'
        className='lg:w-1/4 w-full'
        errors={formErrors?.email || []}
        defaultValue={contact?.email || ""}
      />
      <InputField
        name='role'
        type='text'
        required
        placeholder='Role'
        className='lg:w-1/4 w-full'
        errors={formErrors?.role || []}
        defaultValue={contact?.role || ""}
      />
      <Button
        label={contact ? "Update" : "Add"}
        isFormSubmit={true}
        Icon={PlusCircleIcon}
        className='mr-4 mt-2'
      />
      {contact && (
        <Button
          btnType='secondary'
          Icon={XMarkIcon}
          label='Clear'
          onClick={() => {
            clearContact();
            setFormErrors({});
            setFormKey((prev) => prev + 1);
          }}
          className='mt-2'
        />
      )}
    </Form>
  );
}
