import { useEffect, useRef, useState } from "react";
import { appAlerts } from "../../utils/appAlerts";
import { useAuth } from "../../context/AuthContext";
import { useAlert } from "@lnds-lu/design-system";
import { loginUrl } from "../../utils/authUrls";
import { Form, useActionData, useOutletContext } from "react-router-dom";
import { SingleValue } from "react-select";
import RelationCard from "./RelationCard";
import { useForm, getFormProps } from "@conform-to/react";
import { PlusCircleIcon, LinkIcon } from "@heroicons/react/24/solid";
import { relationsDisplayFields } from "../../utils/DatasetFieldDisplayName";
import { RelationsTypesOptions, reciprocalMapping, ExternalRelationsRoleOptions } from "./dto";
import type { SubmissionResult } from "@conform-to/react";
import { DatasetRelation, ResourceDatasetType, DatasetStatusEnum } from "../../types";
import {
  DropdownSelect,
  Button,
  Card,
  CardHeading,
  TextArea,
  InputField,
} from "@lnds-lu/design-system";
import EmptyScreen from "../../components/EmptyScreen";
import DatasetSearchSelector from "../../components/DatasetSearchSelector";
import { usePageTitle } from "../../hooks/usePageTitle";

const datasetStatuses = [
  "DRAFT",
  "COMPLETED",
  "VALIDATED",
  "APPROVED",
  "INTERNAL_ONLY",
  "PUBLISHED",
  "DEPRECATED",
];

const relationKindOptions = [
  { value: "dataset", label: "Link to Other Dataset" },
  { value: "external", label: "Link to Other External Resource" },
];

export default function Relations() {
  const { isLoading, user } = useAuth();
  const { setAlert, clearAlert } = useAlert();
  const [relationKind, setRelationKind] = useState<"dataset" | "external" | null>(null);
  const [selectedRelationType, setSelectedRelationType] = useState<string | null>(null);
  const [selectedExternalRole, setSelectedExternalRole] = useState<string | null>(null);
  const [relations, setRelations] = useState<DatasetRelation[]>([]);
  const [formKey, setFormKey] = useState(0);
  const [selectedStatus, setSelectedStatus] = useState("PUBLISHED");
  const [selectedTargetDataset, setSelectedTargetDataset] = useState<ResourceDatasetType | null>(
    null,
  );

  if (!isLoading && !user) {
    window.location.href = loginUrl();
  }

  const { dataset, triggerActivityLogRefresh } = useOutletContext() as {
    dataset: ResourceDatasetType;
    triggerActivityLogRefresh: () => void;
  };

  usePageTitle(`${dataset?.title || "Dataset"} - Relations`);

  const actionData = useActionData() as SubmissionResult<string[]>;

  const formErrors = actionData?.status === "error" ? actionData?.error : null;

  const errorsInDebugMode =
    import.meta.env.DEV && formErrors && Object.keys(formErrors).length !== 0
      ? JSON.stringify(formErrors, null, 2)
      : null;

  const validationErrors =
    formErrors && Object.keys(formErrors).length !== 0 ? "Please fix the errors in the form" : null;

  const [form] = useForm({
    lastResult: actionData ? actionData : undefined,
    shouldValidate: "onSubmit",
    defaultValue: {},
  });

  const onDelete = async (relationId: number) => {
    setRelations((relations) => relations.filter((relation) => relation.id !== relationId));
    triggerActivityLogRefresh();
  };

  useEffect(() => {
    if (dataset && dataset.source_relations) {
      setRelations(
        dataset.source_relations.map((relation) => ({
          id: relation.id,
          relationKind: relation.relation_kind as "dataset" | "external",
          datasetId: relation.dataset_id ?? undefined,
          title: relation.title ?? undefined,
          status: relation.status ?? undefined,
          relationType: relation.relation_type ?? undefined,
          externalUrl: relation.external_url ?? undefined,
          externalRole: relation.external_role ?? undefined,
          externalDescription: relation.external_description ?? undefined,
        })),
      );
    }
  }, [dataset]);

  useEffect(() => {
    if (actionData?.status === "success" && actionData.initialValue) {
      const newRelation = actionData.initialValue;

      if (newRelation.relationKind === "dataset") {
        const target = selectedTargetDataset;
        setRelations([
          ...relations,
          {
            id: Number(newRelation.id),
            relationKind: "dataset",
            title: target!.title,
            status: target!.status,
            datasetId: Number(newRelation.targetId),
            relationType: newRelation.relationType as string,
          },
        ]);
      } else {
        setRelations([
          ...relations,
          {
            id: Number(newRelation.id),
            relationKind: "external",
            externalUrl: String(newRelation.externalUrl ?? ""),
            externalRole: newRelation.externalRole ? String(newRelation.externalRole) : undefined,
            externalDescription: newRelation.externalDescription
              ? String(newRelation.externalDescription)
              : undefined,
          },
        ]);
      }

      setAlert(appAlerts.relationAdded());
      setFormKey((prev) => prev + 1);
      setRelationKind(null);
      setSelectedRelationType(null);
      setSelectedExternalRole(null);
      setSelectedTargetDataset(null);
      triggerActivityLogRefresh();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [actionData]);

  useEffect(() => {
    if (errorsInDebugMode || validationErrors) {
      window.scrollTo({ top: 0, behavior: "instant" });
      setAlert(appAlerts.genericValidationError(errorsInDebugMode || validationErrors!));
    } else {
      clearAlert();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [errorsInDebugMode, validationErrors]);

  const formRef = useRef<HTMLFormElement>(null);

  const getNewerVersionRelation = (relation: DatasetRelation) => {
    if (relation.relationKind !== "dataset") return null;

    const r = dataset.source_relations?.find(
      (other) =>
        other.previous_version_dataset_id === relation.datasetId &&
        relation.status === DatasetStatusEnum.PUBLISHED,
    );

    if (!r) return null;

    return {
      id: r.id,
      relationKind: "dataset" as const,
      datasetId: r.dataset_id,
      title: r.title,
      status: r.status,
      relationType: r.relation_type,
    } as DatasetRelation;
  };

  return (
    <div className='flex flex-col w-full' key={formKey}>
      <Card className='p-8 mb-6 w-full max-w-3xl flex flex-col self-center'>
        <div className='rounded-t flex flex-row justify-between items-center section-lnds-color mb-8'>
          <CardHeading label={"Add Relation"} Icon={PlusCircleIcon} className='flex w-full mb-4' />
        </div>
        <Form method='post' {...getFormProps(form)} className='flex flex-col gap-6' ref={formRef}>
          <input type='hidden' name='sourceId' value={dataset?.id} />

          <DropdownSelect
            name='relationKind'
            label='Choose if you want to add a dataset relation or an external resource relation to this dataset'
            options={relationKindOptions}
            isMulti={false}
            required
            onChange={(option) =>
              setRelationKind(
                (option as SingleValue<{ label: string; value: "dataset" | "external" }>)?.value ??
                  null,
              )
            }
          />

          {relationKind === "dataset" && (
            <>
              <DropdownSelect
                name='relationType'
                label={relationsDisplayFields["relationType"].longLabel}
                options={RelationsTypesOptions}
                isMulti={false}
                errors={formErrors?.relationType}
                required
                onChange={(option) =>
                  setSelectedRelationType(
                    (option as SingleValue<{ label: string; value: string }>)!.value,
                  )
                }
              />

              <div className='flex flex-col gap-2'>
                <label className='text-lg font-medium text-lnds-dark-blue dark:text-gray-400'>
                  Dataset <span className='text-lnds-red'>*</span>
                </label>
                <div className='flex flex-row gap-4 items-start'>
                  <div className='w-1/3 min-w-[180px]'>
                    <DropdownSelect
                      name='status'
                      label=''
                      isMulti={false}
                      options={datasetStatuses.map((status) => ({
                        value: status,
                        label: status,
                      }))}
                      onChange={(option) => {
                        const selected = option as SingleValue<{
                          value: string;
                          label: string;
                        }> | null;
                        if (selected) setSelectedStatus(selected.value);
                      }}
                      className='w-full'
                      required
                    />
                  </div>

                  <div className='flex-1'>
                    <DatasetSearchSelector
                      status={selectedStatus}
                      selectedIds={relations
                        .filter((relation) =>
                          relation.relationKind === "dataset" && selectedRelationType
                            ? relation.relationType === selectedRelationType ||
                              relation.relationType === reciprocalMapping[selectedRelationType]
                            : true,
                        )
                        .map((r) => r.datasetId!)}
                      onSelect={(dataset) => {
                        setSelectedTargetDataset(dataset);
                        const input =
                          formRef.current?.querySelector<HTMLInputElement>(
                            'input[name="targetId"]',
                          );
                        if (input) input.value = dataset.id.toString();
                      }}
                      addButtonLabel='Select'
                      alwaysShowSearch={false}
                    />
                  </div>
                </div>
              </div>
              <input type='hidden' name='targetId' />
            </>
          )}
          {relationKind === "external" && (
            <>
              <InputField
                name='externalUrl'
                label='External URL'
                type='url'
                placeholder='https://example.com/resource'
                required
                errors={formErrors?.externalUrl ?? undefined}
              />
              <DropdownSelect
                name='externalRole'
                label={relationsDisplayFields["externalRole"].longLabel}
                options={ExternalRelationsRoleOptions}
                isMulti={false}
                errors={formErrors?.externalRole}
                info='This field is optional.'
                onChange={(option) =>
                  setSelectedExternalRole(
                    (option as SingleValue<{ label: string; value: string }>)?.value ?? null,
                  )
                }
              />
              {selectedExternalRole !== "is-referenced-by" && (
                <TextArea
                  name='externalDescription'
                  label='Description'
                  placeholder='Describe this external resource...'
                  errors={formErrors?.externalDescription ?? undefined}
                  info='This field is optional.'
                />
              )}
            </>
          )}
          <div className='flex flex-row gap-3 justify-end'>
            <Button isFormSubmit={true} Icon={LinkIcon} label='Add Relation' />
          </div>
        </Form>
      </Card>
      {relations.length === 0 && <EmptyScreen message='No relations available' Icon={LinkIcon} />}
      {relations.length > 0 && (
        <div className='space-y-8 w-full max-w-3xl self-center'>
          {relations.filter((r) => r.relationKind === "dataset").length > 0 && (
            <div>
              <h3 className='label-lnds-color text-xl font-semibold mb-4 pb-2 border-b-2 border-lnds-color'>
                Dataset Relations
              </h3>
              <div className='space-y-4'>
                {relations
                  .filter((relation) => relation.relationKind === "dataset")
                  .map((relation) => (
                    <RelationCard
                      key={relation.id}
                      sourceId={dataset.id}
                      relation={relation}
                      onDelete={onDelete}
                      getNewerVersionRelation={getNewerVersionRelation}
                    />
                  ))}
              </div>
            </div>
          )}
          {relations.filter((r) => r.relationKind === "external").length > 0 && (
            <div>
              <h3 className='label-lnds-color text-xl font-semibold mb-4 pb-2 border-b-2 border-lnds-color'>
                Links to External Resources
              </h3>
              <div className='space-y-4'>
                {relations
                  .filter((relation) => relation.relationKind === "external")
                  .map((relation) => (
                    <RelationCard
                      key={relation.id}
                      sourceId={dataset.id}
                      relation={relation}
                      onDelete={onDelete}
                      getNewerVersionRelation={getNewerVersionRelation}
                    />
                  ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
