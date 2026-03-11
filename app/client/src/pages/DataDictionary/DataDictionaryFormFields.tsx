import { InputField, DropdownSelect } from "@lnds-lu/design-system";
import { options } from "./dto";
import { SingleValue } from "react-select";

type DataDictionaryFormFieldsProps = {
  formErrors: Record<string, string[] | null>;
  dataType?: string;
  onDataTypeChange: (value: string) => void;
  defaultValues?: {
    name?: string;
    type?: string;
    description?: string;
    max_value?: string;
    min_value?: string;
    variable_unit?: string;
    allowed_values?: string;
    allowed_values_description?: string;
    personallyIdentifiableVariable?: boolean | null;
    required?: boolean | null;
  };
  currentPersonallyIdentifiable?: boolean | null;
  currentRequired?: boolean | null;
  onPersonallyIdentifiableChange?: (value: boolean | null) => void;
  onRequiredChange?: (value: boolean | null) => void;
};

const DataDictionaryFormFields = ({
  formErrors,
  dataType,
  onDataTypeChange,
  defaultValues = {},
  currentPersonallyIdentifiable,
  currentRequired,
  onPersonallyIdentifiableChange,
  onRequiredChange,
}: DataDictionaryFormFieldsProps) => {
  const personallyIdentifiableValue =
    currentPersonallyIdentifiable !== undefined
      ? currentPersonallyIdentifiable
      : (defaultValues?.personallyIdentifiableVariable ?? null);
  const requiredValue =
    currentRequired !== undefined ? currentRequired : (defaultValues?.required ?? null);

  return (
    <>
      <div className='grid grid-cols-1 gap-6'>
        <InputField
          label='Name'
          name='name'
          type='text'
          required
          placeholder='Name'
          className='w-full'
          defaultValue={defaultValues.name}
          errors={formErrors.name || undefined}
        />
        <DropdownSelect
          label='Type'
          name='type'
          className='w-full'
          options={options}
          isMulti={false}
          required
          defaultValue={defaultValues.type}
          errors={formErrors.type || undefined}
          onChange={(value) =>
            onDataTypeChange(
              ((value as SingleValue<{ label: string; value: string }>)?.value ?? "") as string,
            )
          }
        />
        <InputField
          label='Description'
          name='description'
          type='text'
          required
          placeholder='Description'
          className='w-full'
          defaultValue={defaultValues.description}
          errors={formErrors.description || undefined}
        />
      </div>
      <div className='grid grid-cols-1 gap-6'>
        {dataType !== "String" ? (
          <>
            <InputField
              label='Max Allowed Value'
              name='max_value'
              type='number'
              placeholder='Max Allowed Value'
              className='w-full'
              defaultValue={defaultValues.max_value}
              errors={formErrors.max_value || undefined}
            />
            <InputField
              label='Min Allowed Value'
              name='min_value'
              type='number'
              placeholder='Min Allowed Value'
              className='w-full'
              defaultValue={defaultValues.min_value}
              errors={formErrors.min_value || undefined}
            />
          </>
        ) : null}
        <InputField
          label='Variable Unit'
          name='variable_unit'
          type='text'
          placeholder='Variable Unit'
          className='w-full'
          defaultValue={defaultValues.variable_unit}
          errors={formErrors.variable_unit || undefined}
        />
        <InputField
          label='Allowed Values'
          name='allowed_values'
          type='text'
          placeholder='Allowed Values'
          className='w-full'
          defaultValue={defaultValues.allowed_values}
          errors={formErrors.allowed_values || undefined}
        />
        <InputField
          label='Allowed Values Description'
          name='allowed_values_description'
          type='text'
          placeholder='Allowed Values Description'
          className='w-full'
          defaultValue={defaultValues.allowed_values_description}
          errors={formErrors.allowed_values_description || undefined}
        />
        <DropdownSelect
          key={`personally-identifiable-${personallyIdentifiableValue}`}
          name='_personallyIdentifiableVariable_ignore'
          label='Personally Identifiable Variable'
          className='w-full'
          options={[
            { value: "true", label: "Yes" },
            { value: "false", label: "No" },
          ]}
          isMulti={false}
          defaultValue={
            personallyIdentifiableValue === true
              ? "true"
              : personallyIdentifiableValue === false
                ? "false"
                : undefined
          }
          onChange={(value) =>
            onPersonallyIdentifiableChange?.(
              value
                ? (value as SingleValue<{ label: string; value: string }>)?.value === "true"
                : null,
            )
          }
          errors={formErrors.personallyIdentifiableVariable || undefined}
        />
        <DropdownSelect
          key={`required-${requiredValue}`}
          name='_required_ignore'
          label='Required'
          className='w-full'
          options={[
            { value: "true", label: "Yes" },
            { value: "false", label: "No" },
          ]}
          isMulti={false}
          defaultValue={
            requiredValue === true ? "true" : requiredValue === false ? "false" : undefined
          }
          onChange={(value) =>
            onRequiredChange?.(
              value
                ? (value as SingleValue<{ label: string; value: string }>)?.value === "true"
                : null,
            )
          }
          errors={formErrors.required || undefined}
        />
      </div>
    </>
  );
};

export default DataDictionaryFormFields;
