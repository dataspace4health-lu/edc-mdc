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
import { ResourceOrganisation } from "../../types";
import { Form } from "react-router-dom";
import { useForm, getFormProps } from "@conform-to/react";
import { parseWithZod } from "@conform-to/zod/v4";
import { useAlert } from "@lnds-lu/design-system";
import { AssignRoleFormSchema } from "./dto";
import client from "../../zodiosClient/client";
import { isAxiosError } from "axios";
import { useUIConfig } from "../../context/UIConfigContext";
import { useAuth } from "../../context/AuthContext";
import { filterOrganisationsByAccess } from "../../utils/organisations";

type AssignRoleFormProps = {
  organisations: ResourceOrganisation[];
  roles: { label: string; value: string }[];
  onRoleAssigned?: (
    email: string,
    organisationId: number,
    role: { id: number; name: string },
  ) => void;
};

export default function AssignRoleForm(props: Readonly<AssignRoleFormProps>) {
  const { organisations, roles, onRoleAssigned } = props;
  const { config: uiConfig } = useUIConfig();
  const { user } = useAuth();
  const [isFormExpanded, setIsFormExpanded] = useState(false);

  const handleCancel = () => {
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
      const submission = parseWithZod(formData, { schema: AssignRoleFormSchema });

      const reply = await submission.reply();

      if (reply.status === "error" && reply.error) {
        setFormErrors(reply.error);

        return;
      }

      try {
        await client.create_organisation_assignment_api_v1_organisations__organisation_id__assignments_post(
          {
            email: submission.payload.email as string,
            role_id: parseInt(submission.payload.roleId as string),
          },
          {
            params: { organisation_id: parseInt(submission.payload.organisationId as string) },
            withCredentials: true,
          },
        );
        setAlert(appAlerts.roleAssigned());
        setFormKey((prev) => prev + 1);
        setFormErrors({});

        if (onRoleAssigned) {
          const role = roles.find((r) => r.value === submission.payload.roleId);
          if (role) {
            onRoleAssigned(
              submission.payload.email as string,
              parseInt(submission.payload.organisationId as string),
              { id: parseInt(submission.payload.roleId as string), name: role.label },
            );
          }
        }
      } catch (error: unknown) {
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

  return (
    <Card className='p-4 md:p-8' key={formKey}>
      <div
        className={`rounded-t flex flex-row justify-between items-center section-lnds-color ${isFormExpanded ? "mb-4" : ""}`}
      >
        <CardHeading label={"Assign Role"} Icon={PlusCircleIcon} className='flex' />
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
          <Form method='post' className='flex flex-col gap-6' {...getFormProps(form)} ref={formRef}>
            <InputField
              name='email'
              label='Email'
              info='The user with this email must exist in the system'
              errors={formErrors?.email || []}
              type='text'
            />
            <DropdownSelect
              name='organisationId'
              label='Organisation'
              options={filterOrganisationsByAccess(
                organisations,
                uiConfig?.is_ctie_instance,
                user?.feature_options?.enable_multi_tenants,
                user?.feature_options?.enable_dual_instance,
              ).map((org) => ({
                label: org.name,
                value: org.id.toString(),
              }))}
              isMulti={false}
              className='w-full'
              defaultValue={organisations.length === 1 ? organisations[0].id : undefined}
              errors={formErrors?.organisationId || []}
            />
            <DropdownSelect
              name='roleId'
              label='Role'
              options={roles}
              isMulti={false}
              className='w-full'
              errors={formErrors?.roleId || []}
            />
            <div className='flex flex-row gap-3 justify-end'>
              <Button btnType='secondary' Icon={XMarkIcon} label='Cancel' onClick={handleCancel} />
              <Button isFormSubmit={true} Icon={BuildingOfficeIcon} label='Assign Role' />
            </div>
          </Form>
        </div>
      </div>
    </Card>
  );
}
