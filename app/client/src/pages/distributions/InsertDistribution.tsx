import { appAlerts } from "../../utils/appAlerts";
import {
  PencilIcon,
  PlusCircleIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  XMarkIcon,
} from "@heroicons/react/24/solid";
import { useState, useEffect, useRef } from "react";
import { Button, Card, CardHeading, useAlert } from "@lnds-lu/design-system";
import { useForm, getFormProps } from "@conform-to/react";
import { parseWithZod, getZodConstraint } from "@conform-to/zod/v4";
import client from "../../zodiosClient/client";
import { distributionSchema, toDistributionDTO } from "./dto";
import { ResourceDistributionType, FormType, ResourceUserType } from "../../types";
import DismissibleAlert from "../../components/DismissibleAlert";
import DistributionFormFields from "./DistributionFormFields";
import { NON_PUBLIC_RIGHTS_STATEMENT } from "../../schemas/distributionSchema";
import { useUIConfig } from "../../context/UIConfigContext";

type InsertDistributionProps = {
  datasetId: number;
  onDistributionAdded: (newDistribution: ResourceDistributionType) => void;
  onDistributionUpdated?: (updatedDistribution: ResourceDistributionType) => void;
  triggerActivityLogRefresh?: () => void;
  editingDistribution?: ResourceDistributionType | null;
  onCancelEdit?: () => void;
  formLoaderData: FormType;
  user: ResourceUserType | null;
  isHealthDataset?: boolean;
  datasetRightsStatement?: string;
  resetForm?: () => void;
  successMessage?: string | null;
  setSuccessMessage?: (message: string | null) => void;
};

const InsertDistribution = ({
  datasetId,
  onDistributionAdded,
  onDistributionUpdated,
  triggerActivityLogRefresh,
  editingDistribution = null,
  onCancelEdit,
  formLoaderData,
  user,
  isHealthDataset,
  datasetRightsStatement,
}: InsertDistributionProps) => {
  const [resetCounter, setResetCounter] = useState(0);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const componentKey = `distribution-form-${editingDistribution?.id || "new"}-${resetCounter}`;

  return (
    <InsertDistributionInner
      key={componentKey}
      datasetId={datasetId}
      onDistributionAdded={onDistributionAdded}
      onDistributionUpdated={onDistributionUpdated}
      triggerActivityLogRefresh={triggerActivityLogRefresh}
      editingDistribution={editingDistribution}
      onCancelEdit={onCancelEdit}
      formLoaderData={formLoaderData}
      user={user}
      isHealthDataset={isHealthDataset}
      datasetRightsStatement={datasetRightsStatement}
      resetForm={() => setResetCounter((prev) => prev + 1)}
      successMessage={successMessage}
      setSuccessMessage={setSuccessMessage}
    />
  );
};

const InsertDistributionInner = ({
  datasetId,
  onDistributionAdded,
  onDistributionUpdated,
  triggerActivityLogRefresh,
  editingDistribution = null,
  onCancelEdit,
  formLoaderData,
  user,
  isHealthDataset,
  datasetRightsStatement,
  resetForm,
  successMessage,
  setSuccessMessage,
}: InsertDistributionProps) => {
  const isEditMode = !!editingDistribution;
  const { setAlert, clearAlert } = useAlert();
  const { config } = useUIConfig();
  const [isFormExpanded, setIsFormExpanded] = useState(false);
  const [formErrors, setFormErrors] = useState<Record<string, string[] | null>>({});
  const [serverErrorMessage, setServerErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (isEditMode && editingDistribution) {
      setIsFormExpanded(true);
      setFormErrors({});
      // Scroll to the form when entering edit mode
      setTimeout(() => {
        cardRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
    } else {
      setFormErrors({});
    }
  }, [isEditMode, editingDistribution]);

  useEffect(() => {
    if (formErrors && Object.keys(formErrors).length > 0) {
      window.scrollTo({ top: 0, behavior: "auto" });
      const errorsMessage = Object.entries(formErrors)
        .map(([field, messages]) => {
          if (Array.isArray(messages)) {
            return `${field}: ${messages.join(", ")}`;
          } else if (messages) {
            return `${field}: ${String(messages)}`;
          }
          return "";
        })
        .filter(Boolean)
        .join(" | ");
      setAlert(appAlerts.pleaseFixErrors(errorsMessage));
      const timer = setTimeout(() => {
        clearAlert();
      }, 5000);
      return () => clearTimeout(timer);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formErrors]);

  useEffect(() => {
    if (successMessage) {
      window.scrollTo({ top: 0, behavior: "auto" });
      setAlert(appAlerts.alertMessageAsSuccess(successMessage));
      setServerErrorMessage(null);
      const timer = setTimeout(() => {
        clearAlert();
        setSuccessMessage?.(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [successMessage]);

  const [form, fields] = useForm({
    shouldValidate: "onSubmit",
    constraint: getZodConstraint(distributionSchema),
    onValidate({ formData }) {
      const submission = parseWithZod(formData, { schema: distributionSchema });

      // Extract and set errors for display
      if (submission.status === "error" && submission.error) {
        const errors: Record<string, string[] | null> = {};
        Object.entries(submission.error).forEach(([key, value]) => {
          if (Array.isArray(value)) {
            errors[key] = value;
          } else if (value) {
            errors[key] = [String(value)];
          }
        });
        setFormErrors(errors);
      } else {
        setFormErrors({});
      }

      return submission;
    },
    defaultValue: editingDistribution
      ? {
          title: editingDistribution.title,
          description: editingDistribution.description || "",
          accessURLs: editingDistribution.access_urls || [],
          downloadURLs: editingDistribution.download_urls || [],
          distributionRightsStatement: editingDistribution.rights_statement || "",
          fileFormat: editingDistribution.file_type?.value || "",
          license: editingDistribution.license?.value || "",
          languages: editingDistribution.languages?.map((l) => l.value) || [],
          applicableLegislations: editingDistribution.applicable_legislations || [],
          linkedSchemas: editingDistribution.linked_schemas || [],
          availability: editingDistribution.availability || "",
          distributionDCATStatus: editingDistribution.distribution_dcat_status || "",
          releaseDate: editingDistribution.release_date || "",
          modificationDate: editingDistribution.modification_date || "",
          documentation: editingDistribution.documentation || [],
          distributionPath: editingDistribution.distribution_path || null,
          mediaType: editingDistribution.media_type || "",
          compressionFormat: editingDistribution.compression_format || "",
          packagingFormat: editingDistribution.packaging_format || "",
          byteSize: editingDistribution.byte_size || undefined,
          checksum: editingDistribution.checksum || "",
          spatialResolution: editingDistribution.spatial_resolution || undefined,
          temporalResolution: editingDistribution.temporal_resolution || "",
          internalOnly: editingDistribution.internal_only || false,
          isAnalytics: editingDistribution.is_analytics || false,
          accessServices:
            editingDistribution.access_services?.map((s) => parseInt(s.id.toString())) || [],
          policyActions:
            editingDistribution.policy_actions?.map((action) => {
              const policyConstraintType = action.policy_constraint_type ?? undefined;
              const policyConstraintValue = action.policy_constraint_value ?? undefined;
              const temporalRestrictionStart = action.temporal_restriction_start ?? undefined;
              const temporalRestrictionEnd = action.temporal_restriction_end ?? undefined;

              const spatialRestrictions = Array.isArray(action.spatial_restrictions)
                ? action.spatial_restrictions.map((sr: string | { value: string }) =>
                    typeof sr === "string" ? sr : sr.value,
                  )
                : [];

              return {
                policyActionType: action.policy_action_type,
                policyConstraintType,
                policyConstraintValue,
                temporalRestrictionStart,
                temporalRestrictionEnd,
                spatialRestrictions,
              };
            }) || [],
        }
      : {
          policyActions: [],
          distributionRightsStatement: datasetRightsStatement || "",
          accessURLs:
            datasetRightsStatement === NON_PUBLIC_RIGHTS_STATEMENT && config?.default_access_url
              ? [config.default_access_url]
              : [],
        },
    async onSubmit(event, { submission }) {
      event.preventDefault();
      clearAlert();

      // submission is already validated by onValidate
      if (!submission || submission.status !== "success") {
        // Validation failed - extract errors
        const errors: Record<string, string[] | null> = {};
        if (submission && submission.status === "error") {
          const errorObj = submission.error || {};
          Object.entries(errorObj).forEach(([key, value]) => {
            if (Array.isArray(value)) {
              errors[key] = value;
            } else if (value) {
              errors[key] = [String(value)];
            }
          });
        }
        setFormErrors(errors);
        return;
      }

      try {
        const payload = submission.value;
        const requestBody = toDistributionDTO(payload);

        if (isEditMode && editingDistribution) {
          const response =
            await client.update_distribution_api_v1_datasets__dataset_id__distributions__distribution_id__put(
              requestBody,
              {
                params: { dataset_id: datasetId, distribution_id: editingDistribution.id! },
                withCredentials: true,
              },
            );

          onDistributionUpdated?.(response);
          setSuccessMessage?.("Distribution updated successfully!");
          setFormErrors({});
          setIsFormExpanded(false);
          triggerActivityLogRefresh?.();
          onCancelEdit?.();
          resetForm?.();
        } else {
          const response =
            await client.add_distribution_api_v1_datasets__dataset_id__distributions_post(
              requestBody,
              { params: { dataset_id: datasetId }, withCredentials: true },
            );

          onDistributionAdded(response);
          setSuccessMessage?.("Distribution added successfully!");
          setFormErrors({});
          setIsFormExpanded(false);
          triggerActivityLogRefresh?.();
          resetForm?.();
        }
      } catch (error) {
        console.error(isEditMode ? "Update error:" : "Insert error:", error);
        window.scrollTo({ top: 0, behavior: "auto" });
        const errorResponse = (
          error as {
            response?: { data?: { detail?: string | Array<{ loc?: string[]; msg: string }> } };
          }
        )?.response?.data?.detail;

        let errorMessage = `Failed to ${isEditMode ? "update" : "add"} distribution.`;

        if (typeof errorResponse === "string") {
          errorMessage = errorResponse;
        } else if (Array.isArray(errorResponse)) {
          // FastAPI validation errors
          errorMessage = errorResponse
            .map(
              (err: { loc?: string[]; msg: string }) =>
                `${err.loc?.join(".") || "Field"}: ${err.msg}`,
            )
            .join(", ");
        }

        setServerErrorMessage(errorMessage);
      }
    },
  });

  const formRef = useRef<HTMLFormElement>(null);
  const cardRef = useRef<HTMLDivElement>(null);

  return (
    <div ref={cardRef} className='flex items-center justify-center h-full'>
      <Card className='w-full max-w-3xl p-8'>
        {serverErrorMessage && (
          <DismissibleAlert
            message={serverErrorMessage || ""}
            type='error'
            className='mt-0 mb-4'
            overrideClose={() => setServerErrorMessage(null)}
          />
        )}
        <div
          className={`flex flex-col md:flex-row justify-between items-end md:items-baseline ${
            isFormExpanded ? "mb-4" : ""
          } gap-2 md:gap-none`}
        >
          <CardHeading
            label={isEditMode ? "Edit Distribution" : "Add Distribution"}
            Icon={isEditMode ? PencilIcon : PlusCircleIcon}
            className='md:text-center'
          />
          <div className='flex flex-col justify-center items-center gap-2'>
            {!isEditMode && (
              <Button
                label={isFormExpanded ? "Collapse Form" : "Expand Form"}
                onClick={() => {
                  if (isFormExpanded) {
                    resetForm?.();
                    setFormErrors({});
                  }
                  setIsFormExpanded(!isFormExpanded);
                }}
                Icon={isFormExpanded ? ChevronUpIcon : ChevronDownIcon}
              />
            )}
          </div>
        </div>
        <div
          className={`transition-all duration-300 ${
            isFormExpanded ? "opacity-100" : "max-h-0 opacity-0 overflow-hidden"
          }`}
        >
          <form
            {...getFormProps(form)}
            onSubmit={(e) => {
              e.preventDefault();
              form.onSubmit(e as React.FormEvent<HTMLFormElement>);
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && e.target instanceof HTMLInputElement) {
                e.preventDefault();
              }
            }}
            className='w-full flex flex-col gap-6'
            ref={formRef}
          >
            <DistributionFormFields
              formErrors={formErrors}
              defaultValues={isEditMode ? editingDistribution : undefined}
              fields={fields}
              formLoaderData={formLoaderData}
              user={user}
              form={form}
              isHealthDataset={isHealthDataset}
            />
            <div className='flex justify-end gap-2'>
              {isEditMode && (
                <Button
                  label='Cancel'
                  btnType='secondary'
                  onClick={() => {
                    onCancelEdit?.();
                    resetForm?.();
                    setFormErrors({});
                    setIsFormExpanded(false);
                  }}
                  Icon={XMarkIcon}
                  className='mt-4'
                />
              )}
              <Button
                label={isEditMode ? "Update" : "Insert"}
                isFormSubmit={true}
                Icon={isEditMode ? PencilIcon : PlusCircleIcon}
                className='mt-4'
              />
            </div>
          </form>
        </div>
      </Card>
    </div>
  );
};

export default InsertDistribution;
