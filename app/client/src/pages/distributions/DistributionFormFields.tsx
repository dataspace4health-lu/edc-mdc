import { useEffect, useState, useMemo } from "react";
import {
  InputField,
  DropdownSelect,
  TextArea,
  RadioButton,
  ToggleButton,
  Button,
} from "@lnds-lu/design-system";
import CreatableDropdownSelect from "../../components/CreatableDropdown";
import distributionSchemaConfig from "../../schemas/distributionSchema";
import { FormType, ResourceUserType } from "../../types";
import { PlusCircleIcon, TrashIcon, DocumentTextIcon } from "@heroicons/react/24/solid";
import {
  actionTypeOptions,
  constraintTypeOptions,
  purposeOptions,
} from "../../schemas/distributionSchema";
import { getFieldErrors } from "../../utils/formFieldErrors";

type DistributionFormFieldsProps = {
  formErrors: Record<string, string[] | null>;
  defaultValues?: Record<string, unknown>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  fields: any;
  formLoaderData: FormType;
  user: ResourceUserType | null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  form: any;
  isHealthDataset?: boolean;
};

const DistributionFormFields = ({
  formErrors,
  fields,
  formLoaderData,
  user,
  form,
  isHealthDataset,
}: DistributionFormFieldsProps) => {
  const policyActionsList = useMemo(() => {
    const list = fields.policyActions?.getFieldList() ?? [];
    return list;
  }, [fields.policyActions]);

  const [hasPolicy, setHasPolicy] = useState(policyActionsList.length > 0);
  const [constraintTypes, setConstraintTypes] = useState<Record<number, string>>({});

  useEffect(() => {
    const next: Record<number, string> = {};
    policyActionsList.forEach(
      (
        action: { getFieldset: () => { policyConstraintType?: { value?: string } } },
        index: number,
      ) => {
        const v = action.getFieldset().policyConstraintType?.value as string | undefined;
        if (v) next[index] = v;
      },
    );

    setConstraintTypes((prev) => {
      const prevKeys = Object.keys(prev);
      const nextKeys = Object.keys(next);
      const sameSize = prevKeys.length === nextKeys.length;
      const sameVals = sameSize && nextKeys.every((k) => prev[+k] === next[+k]);
      return sameVals ? prev : next;
    });
  }, [policyActionsList]);

  // Safety check for formLoaderData
  if (!formLoaderData || !formLoaderData.distribution) {
    return (
      <div className='text-lnds-color p-4'>
        <p>Loading form configuration...</p>
      </div>
    );
  }

  const renderConstraintValueField = (
    actionIndex: number,
    actionFields: Record<string, { name?: string; value?: unknown; errors?: string[] }>,
  ) => {
    const constraintType = constraintTypes[actionIndex];

    switch (constraintType) {
      case "purpose":
        return (
          <DropdownSelect
            name={actionFields.policyConstraintValue?.name ?? ""}
            label='Purpose Restriction'
            options={purposeOptions}
            defaultValue={actionFields.policyConstraintValue?.value as string}
            errors={actionFields.policyConstraintValue?.errors}
            isMulti={false}
            info='Select a purpose restriction from the DUO codes.'
            required
          />
        );
      case "temporal":
        return (
          <div className='flex flex-col gap-4'>
            <InputField
              name={actionFields.temporalRestrictionStart?.name ?? ""}
              label='Temporal Restriction Start'
              type='date'
              defaultValue={(actionFields.temporalRestrictionStart?.value as string) || ""}
              errors={actionFields.temporalRestrictionStart?.errors}
              info='Specify the start of the temporal restriction date.'
            />
            <InputField
              name={actionFields.temporalRestrictionEnd?.name ?? ""}
              label='Temporal Restriction End'
              type='date'
              defaultValue={(actionFields.temporalRestrictionEnd?.value as string) || ""}
              errors={actionFields.temporalRestrictionEnd?.errors}
              info='Specify the end of the temporal restriction date.'
            />
          </div>
        );
      case "spatial":
        console.log("Spatial restrictions field value:", actionFields.spatialRestrictions?.value);
        console.log("Spatial restrictions field name:", actionFields.spatialRestrictions?.name);
        return (
          <DropdownSelect
            name={actionFields.spatialRestrictions?.name ?? ""}
            label='Spatial Restrictions'
            options={(Array.isArray(formLoaderData.distribution.spatial_restrictions)
              ? formLoaderData.distribution.spatial_restrictions
              : []
            ).map((opt: { value: string; eng_label: string }) => ({
              value: opt.value,
              label: opt.eng_label,
            }))}
            defaultValue={actionFields.spatialRestrictions?.value as string[]}
            errors={actionFields.spatialRestrictions?.errors}
            isMulti={true}
            info='Select spatial restrictions.'
            required
          />
        );
      case "industry":
        return (
          <InputField
            name={actionFields.policyConstraintValue?.name || ""}
            label='Industry Restriction'
            type='text'
            defaultValue={(actionFields.policyConstraintValue?.value as string) || ""}
            errors={actionFields.policyConstraintValue?.errors}
            info='Specify an industry restriction.'
            required
          />
        );
      default:
        return null;
    }
  };

  const handleAddPolicyAction = (e?: React.MouseEvent) => {
    e?.preventDefault();
    e?.stopPropagation();

    form.insert({
      name: fields.policyActions.name,
      defaultValue: { policyActionType: "permission" },
    });
  };

  const handleDeletePolicyAction = (actionIndex: number) => {
    form.remove({ name: fields.policyActions.name, index: actionIndex });
  };

  // Handle hasPolicy toggle - insert first action when enabled
  const handleHasPolicyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const checked = e.target.checked;
    setHasPolicy(checked);

    if (checked && policyActionsList.length === 0) {
      form.insert({
        name: fields.policyActions.name,
        defaultValue: { policyActionType: "permission" },
      });
    }
  };

  const getCreatedOptions = (values: (string | undefined)[] | string | undefined) => {
    if (typeof values === "string" && values.trim().length > 0) {
      return [{ value: values, label: values }];
    }

    if (!Array.isArray(values)) {
      return [];
    }

    return values.map((v) => ({ value: v!, label: v! }));
  };

  return (
    <>
      {distributionSchemaConfig.map((field) => {
        if (field.hide && field.hide(user)) {
          return null;
        }

        if (field.name === "internalOnly") {
          return (
            <ToggleButton
              yesLabel='Yes'
              noLabel='No'
              key={fields[field.name as keyof typeof fields].name}
              name={fields[field.name as keyof typeof fields].name}
              defaultValue={!!fields[field.name].value}
              label={field.longLabel}
              popoverInfo={field.explanation}
              info={field.info}
              errors={formErrors?.[field.name] || undefined}
            />
          );
        } else if (field.name === "isAnalytics") {
          if (!isHealthDataset) {
            return null;
          }
          return (
            <ToggleButton
              yesLabel='Yes'
              noLabel='No'
              key={fields[field.name as keyof typeof fields].name}
              name={fields[field.name as keyof typeof fields].name}
              defaultValue={!!fields[field.name].value}
              label={field.longLabel}
              popoverInfo={field.explanation}
              errors={formErrors?.[field.name] || undefined}
            />
          );
        } else if (field.name === "hasPolicy") {
          return (
            <div key={field.name} className='mt-2'>
              <ToggleButton
                yesLabel='Yes'
                noLabel='No'
                name='hasPolicy'
                defaultValue={hasPolicy}
                label='Enable data use policy for this distribution'
                popoverInfo={field.explanation}
                onChange={handleHasPolicyChange}
              />

              {hasPolicy && (
                <div className='mt-4 pl-4 border-l-2 border-lnds-blue'>
                  {policyActionsList.map(
                    (
                      policyAction: {
                        key: string;
                        getFieldset: () => Record<
                          string,
                          { name?: string; value?: unknown; errors?: string[] }
                        >;
                      },
                      actionIndex: number,
                    ) => {
                      const actionFields = policyAction.getFieldset();

                      return (
                        <div
                          key={policyAction.key}
                          className='mb-6 p-4 bg-gray-100 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-md'
                        >
                          <div className='flex items-center justify-between pb-2 mb-3 border-b-2 border-gray-200 dark:border-gray-600'>
                            <div className='flex items-center'>
                              <DocumentTextIcon className='h-5 w-5 mr-2 text-gray-600 dark:text-gray-300' />
                              <h5 className='font-medium text-gray-900 dark:text-gray-100'>
                                Policy Action {actionIndex + 1}
                              </h5>
                            </div>
                            <Button
                              Icon={TrashIcon}
                              btnType='danger'
                              size='small'
                              label='Delete'
                              onClick={() => handleDeletePolicyAction(actionIndex)}
                            />
                          </div>

                          <div className='space-y-4'>
                            <DropdownSelect
                              name={actionFields.policyActionType?.name || ""}
                              label='Action Type'
                              options={actionTypeOptions}
                              defaultValue={
                                (actionFields.policyActionType?.value as string) || "permission"
                              }
                              errors={actionFields.policyActionType?.errors}
                              isMulti={false}
                              required
                            />

                            <DropdownSelect
                              name={actionFields.policyConstraintType?.name || ""}
                              label='Constraint Type'
                              options={constraintTypeOptions}
                              defaultValue={actionFields.policyConstraintType?.value as string}
                              errors={actionFields.policyConstraintType?.errors}
                              isMulti={false}
                              required
                              onChange={(op) => {
                                const value = Array.isArray(op)
                                  ? op[0]?.value
                                  : (op as { value?: string } | null)?.value;
                                setConstraintTypes({
                                  ...constraintTypes,
                                  [actionIndex]: value || "",
                                });
                              }}
                            />

                            {constraintTypes[actionIndex] &&
                              renderConstraintValueField(actionIndex, actionFields)}
                          </div>
                        </div>
                      );
                    },
                  )}

                  <Button
                    Icon={PlusCircleIcon}
                    btnType='secondary'
                    label='Add Another Policy Action'
                    onClick={handleAddPolicyAction}
                  />
                </div>
              )}
            </div>
          );
        } else if (field.name === "policyActions") {
          return null;
        } else if (field.type === "InputField") {
          const inputDefaultValue = fields[field.name as keyof typeof fields].value as string;
          return (
            <InputField
              key={fields[field.name as keyof typeof fields].name}
              name={fields[field.name as keyof typeof fields].name}
              label={field.longLabel}
              popoverInfo={field.explanation}
              type={field.inputType!}
              defaultValue={inputDefaultValue}
              errors={formErrors?.[field.name] || undefined}
              required={field.required}
              maxLength={field.maxLength}
              info={field.info}
            />
          );
        } else if (field.type === "TextArea") {
          return (
            <TextArea
              key={fields[field.name as keyof typeof fields].name}
              name={fields[field.name as keyof typeof fields].name}
              label={field.longLabel}
              popoverInfo={field.explanation}
              defaultValue={fields[field.name as keyof typeof fields].value as string}
              errors={formErrors?.[field.name] || undefined}
              required={field.required}
              recommended={field.recommended}
              minLength={field.minLength}
              info={field.info}
            />
          );
        } else if (field.type === "RadioButton") {
          return (
            <RadioButton
              name={fields[field.name as keyof typeof fields].name}
              defaultValue={fields[field.name as keyof typeof fields].value as string}
              label={field.longLabel}
              popoverInfo={field.explanation}
              options={field.options!(formLoaderData, user)}
              errors={formErrors?.[field.name] || undefined}
              required={field.required}
              key={field.name}
            />
          );
        } else if (field.type === "DropdownSelect") {
          return (
            <DropdownSelect
              key={fields[field.name as keyof typeof fields].name}
              name={fields[field.name as keyof typeof fields].name}
              label={field.longLabel}
              popoverInfo={field.explanation}
              options={field.options!(formLoaderData, user)}
              defaultValue={fields[field.name as keyof typeof fields].value as string | string[]}
              errors={formErrors?.[field.name] || undefined}
              isMulti={field.isMulti!}
              info={field.info}
              required={field.required}
              recommended={field.recommended}
            />
          );
        } else if (field.type === "CreatableSelect") {
          return (
            <CreatableDropdownSelect
              key={fields[field.name as keyof typeof fields].name}
              name={fields[field.name as keyof typeof fields].name}
              label={field.longLabel}
              explanation={field.explanation}
              popoverInfo={field.explanation}
              isMulti={field.isMulti ?? false}
              options={getCreatedOptions(
                fields[field.name as keyof typeof fields].value as string[],
              )}
              defaultValue={fields[field.name as keyof typeof fields].value}
              info={field.info}
              errors={getFieldErrors(formErrors, field.name)}
              required={field.required}
            />
          );
        }
        return null;
      })}
    </>
  );
};

export default DistributionFormFields;
