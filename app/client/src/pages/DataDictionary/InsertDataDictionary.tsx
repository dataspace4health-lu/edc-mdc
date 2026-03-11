import { appAlerts } from "../../utils/appAlerts";
import {
  PlusCircleIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  TableCellsIcon,
  XMarkIcon,
  PencilIcon,
} from "@heroicons/react/24/solid";
import { useState, useEffect, useRef } from "react";
import { useAlert, Button, Card, CardHeading } from "@lnds-lu/design-system";
import { useForm, getFormProps } from "@conform-to/react";
import { Form } from "react-router-dom";
import { parseWithZod } from "@conform-to/zod/v4";
import client from "../../zodiosClient/client";
import { DataDictionaryEntrySchema } from "./dto";
import { ResourceDataDictionaryEntry } from "../../types";
import DismissibleAlert from "../../components/DismissibleAlert";
import DataDictionaryFormFields from "./DataDictionaryFormFields";

type InsertDataDictionaryProps = {
  datasetId: number;
  onEntryAdded: (newEntry: ResourceDataDictionaryEntry) => void;
  onEntryUpdated?: (updatedEntry: ResourceDataDictionaryEntry) => void;
  isDuplicate: (fieldName: string, currentEntryId?: number) => boolean;
  triggerActivityLogRefresh?: () => void;
  editingEntry?: ResourceDataDictionaryEntry | null;
  onCancelEdit?: () => void;
};

const InsertDataDictionary = ({
  datasetId,
  onEntryAdded,
  onEntryUpdated,
  isDuplicate,
  triggerActivityLogRefresh,
  editingEntry = null,
  onCancelEdit,
}: InsertDataDictionaryProps) => {
  const isEditMode = !!editingEntry;
  const { setAlert, clearAlert } = useAlert();
  const [formKey, setFormKey] = useState(0);
  const [isFormExpanded, setIsFormExpanded] = useState(false);
  const [formErrors, setFormErrors] = useState<Record<string, string[] | null>>({});
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [serverErrorMessage, setServerErrorMessage] = useState<string | null>(null);
  // @ts-expect-error 'personallyIdentifiableVariable' is declared but its value is never read.
  const [personallyIdentifiableVariable, setPersonallyIdentifiableVariable] = useState(false); // NOSONAR
  const [dataType, setDataType] = useState<string | undefined>(undefined);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditMode && editingEntry) {
      setIsFormExpanded(true);
      setDataType(editingEntry.data_type);
      setFormKey((prev) => prev + 1);
      setFormErrors({});
    } else {
      setDataType(undefined);
      setFormErrors({});
    }
  }, [isEditMode, editingEntry]);

  useEffect(() => {
    if (formErrors && Object.keys(formErrors).length > 0) {
      window.scrollTo({ top: 0, behavior: "instant" });
      const errorsMessage = Object.entries(formErrors)
        .map(([field, messages]) => `${field}: ${(messages || []).join(", ")}`)
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
      window.scrollTo({ top: 0, behavior: "instant" });
      setAlert(appAlerts.alertMessageAsSuccess(successMessage));
      setServerErrorMessage(null);
      const timer = setTimeout(() => {
        clearAlert();
        setSuccessMessage(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [successMessage]);

  const validateFile = (file: File | undefined): boolean => {
    if (!file) {
      setAlert(appAlerts.noFileSelected());
      return false;
    }
    if (!file.name.endsWith(".csv")) {
      setAlert(appAlerts.csvFileRequired());
      return false;
    }
    return true;
  };

  const processBulkUploadResponse = (response: {
    entries?: ResourceDataDictionaryEntry[];
    skipped_entries?: { field_name: string }[];
    validation_errors?: { row: number; errors: string[] }[];
  }) => {
    if (response.entries?.length) {
      response.entries.forEach(onEntryAdded);
      setSuccessMessage(`Bulk upload successful! Added ${response.entries.length} entries.`);
      triggerActivityLogRefresh?.();
    }
    if (response.skipped_entries?.length) {
      const skippedNames = response.skipped_entries.map((e) => e.field_name).join(", ");
      setServerErrorMessage(`Skipped duplicate entries: ${skippedNames}`);
    }
    if (response.validation_errors?.length) {
      const validationMessages = response.validation_errors
        .map((e) => `Row ${e.row}: ${e.errors.join(", ")}`)
        .join("\n");
      setServerErrorMessage(`Validation errors occurred:\n${validationMessages}`);
    }
  };

  const handleBulkUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!validateFile(file) || !file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response =
        await client.bulk_upload_data_dictionaries_api_v1_datasets__dataset_id__data_dictionaries_bulk_upload_post(
          { file },
          { params: { dataset_id: datasetId }, withCredentials: true },
        );
      processBulkUploadResponse(response);
    } catch (error) {
      console.error("Bulk upload error:", error);
      setServerErrorMessage(
        (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
          "Bulk upload failed.",
      );
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const [form] = useForm({
    shouldValidate: "onSubmit",
    defaultValue:
      isEditMode && editingEntry
        ? {
            name: editingEntry.field_name,
            type: editingEntry.data_type,
            description: editingEntry.description || "",
            personallyIdentifiableVariable: editingEntry.personally_identifiable_variable || false,
            required: editingEntry.required || false,
            max_value: editingEntry.max_allowed_value || "",
            min_value: editingEntry.min_allowed_value || "",
            variable_unit: editingEntry.variable_unit || "",
            allowed_values: editingEntry.allowed_values || "",
            allowed_values_description: editingEntry.allowed_values_description || "",
          }
        : {},
    async onSubmit(event, { formData }) {
      event.preventDefault();
      clearAlert();

      const submission = parseWithZod(formData, { schema: DataDictionaryEntrySchema });
      const reply = submission.reply();

      if (reply.status === "error" && reply.error) {
        setFormErrors(reply.error);
        return;
      }

      if (isEditMode) {
        if (
          submission.payload.name !== editingEntry?.field_name &&
          isDuplicate(submission.payload.name as string, editingEntry?.id ?? undefined)
        ) {
          setFormErrors({ name: ["Already taken"] });
          setAlert(appAlerts.fieldNameAlreadyInUse());
          return;
        }
      } else {
        if (isDuplicate(submission.payload.name as string)) {
          setFormErrors({ name: ["Already taken"] });
          setAlert(appAlerts.fieldNameAlreadyInUse());
          return;
        }
      }

      try {
        const requestBody = {
          field_name: submission.payload.name as string,
          data_type: submission.payload.type as string,
          description: submission.payload.description as string,
          personally_identifiable_variable: !!submission.payload.personallyIdentifiableVariable,
          required: !!submission.payload.required,
          max_allowed_value: submission.payload.max_value
            ? parseFloat(submission.payload.max_value.toString())
            : null,
          min_allowed_value: submission.payload.min_value
            ? parseFloat(submission.payload.min_value.toString())
            : null,
          variable_unit: submission.payload.variable_unit as string,
          allowed_values: submission.payload.allowed_values as string,
          allowed_values_description: submission.payload.allowed_values_description as string,
          table_name: isEditMode ? editingEntry?.table_name || "" : "",
          dataset_id: datasetId,
          privacy_risk_type: isEditMode ? editingEntry?.privacy_risk_type || null : null,
        };

        if (isEditMode && editingEntry) {
          const response =
            await client.update_data_dictionary_api_v1_datasets__dataset_id__data_dictionaries__entry_id__put(
              requestBody,
              {
                params: { dataset_id: datasetId, entry_id: editingEntry.id! },
                withCredentials: true,
              },
            );

          onEntryUpdated?.(response);
          setSuccessMessage("Data Dictionary entry updated successfully!");
          setFormErrors({});
          setIsFormExpanded(false);
          triggerActivityLogRefresh?.();
          onCancelEdit?.();
          setFormKey((prev) => prev + 1);
          setDataType(undefined);
        } else {
          const response =
            await client.add_data_dictionary_api_v1_datasets__dataset_id__data_dictionaries_post(
              requestBody,
              { params: { dataset_id: datasetId }, withCredentials: true },
            );

          onEntryAdded(response);
          setSuccessMessage("Data Dictionary entry added successfully!");
          setFormKey((prev) => prev + 1);
          setFormErrors({});
          setIsFormExpanded(false);
          setPersonallyIdentifiableVariable(false);
          triggerActivityLogRefresh?.();
        }
      } catch (error) {
        console.error(isEditMode ? "Update error:" : "Insert error:", error);
        setServerErrorMessage(
          (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
            `Failed to ${isEditMode ? "update" : "add"} entry.`,
        );
      }
    },
  });

  const formRef = useRef<HTMLFormElement>(null);

  return (
    <div className='flex items-center justify-center h-full'>
      <Card key={formKey} className='w-full max-w-3xl p-8'>
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
            label={isEditMode ? "Edit Dataset Dictionary" : "Add Dataset Dictionary"}
            Icon={isEditMode ? PencilIcon : TableCellsIcon}
            className='md:text-center'
          />
          <div className='flex flex-col justify-center items-center gap-2'>
            {!isEditMode && (
              <Button
                label={isFormExpanded ? "Collapse Form" : "Expand Form"}
                onClick={() => {
                  if (isFormExpanded) {
                    // Reset form when collapsing
                    setFormKey((prev) => prev + 1);
                    setDataType(undefined);
                    setFormErrors({});
                  }
                  setIsFormExpanded(!isFormExpanded);
                }}
                Icon={isFormExpanded ? ChevronUpIcon : ChevronDownIcon}
              />
            )}

            {!isEditMode && (
              <div className='flex flex-col justify-center items-center gap-2'>
                <Button
                  label='Bulk Upload'
                  Icon={PlusCircleIcon}
                  onClick={() => fileInputRef.current?.click()}
                />
                <input
                  type='file'
                  accept='.csv'
                  ref={fileInputRef}
                  className='hidden'
                  onChange={handleBulkUpload}
                />
                <a
                  href='/data-dictionary-template.csv'
                  download
                  className='text-xs hover:underline'
                >
                  Download Template
                </a>
              </div>
            )}
          </div>
        </div>
        <div
          className={`transition-all duration-300 ${
            isFormExpanded ? "max-h-[1500px] opacity-100" : "max-h-0 opacity-0 overflow-hidden"
          }`}
        >
          <Form
            key={formKey}
            method='post'
            {...getFormProps(form)}
            className='w-full flex flex-col gap-6'
            ref={formRef}
          >
            <DataDictionaryFormFields
              formErrors={formErrors}
              dataType={dataType}
              onDataTypeChange={setDataType}
              defaultValues={
                isEditMode && editingEntry
                  ? {
                      name: editingEntry.field_name,
                      type: editingEntry.data_type,
                      description: editingEntry.description || "",
                      max_value: editingEntry.max_allowed_value?.toString() || "",
                      min_value: editingEntry.min_allowed_value?.toString() || "",
                      variable_unit: editingEntry.variable_unit || "",
                      allowed_values: editingEntry.allowed_values || "",
                      allowed_values_description: editingEntry.allowed_values_description || "",
                      personallyIdentifiableVariable:
                        editingEntry.personally_identifiable_variable || false,
                      required: editingEntry.required || false,
                    }
                  : undefined
              }
              onPersonallyIdentifiableChange={(value) =>
                setPersonallyIdentifiableVariable(value ?? false)
              }
            />
            <div className='flex justify-end gap-2'>
              {isEditMode && (
                <Button
                  label='Cancel'
                  btnType='secondary'
                  onClick={() => {
                    // Reset form, collapse, and clear editing state
                    setFormKey((prev) => prev + 1);
                    setDataType(undefined);
                    setFormErrors({});
                    setIsFormExpanded(false);
                    onCancelEdit?.();
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
          </Form>
        </div>
      </Card>
    </div>
  );
};

export default InsertDataDictionary;
