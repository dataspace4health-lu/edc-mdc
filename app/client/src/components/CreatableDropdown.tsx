import { MultiValue, SingleValue } from "react-select";
import React, { useState } from "react";
import CreatableSelect from "react-select/creatable";
import FieldInfoHeader from "./FieldInfoHeader";

export type CreatableDropdownSelectProps = {
  label?: string;
  info?: string;
  explanation?: string;
  popoverInfo?: string;
  name: string;
  isMulti: boolean;
  options: Array<{ label: string; value: string }>;
  defaultValue?: string | number | readonly string[] | (string | undefined)[];
  errors?: string[] | null;
  required?: boolean;
  recommended?: boolean;
  onChange?: (
    value:
      | MultiValue<{ label: string; value: string }>
      | SingleValue<{ label: string; value: string }>,
  ) => void;
  className?: string;
  placeholder?: string;
};

const clientRendering = typeof window !== "undefined";

const CreatableDropdownSelect: React.FC<CreatableDropdownSelectProps> = ({
  label,
  info,
  explanation,
  popoverInfo,
  name,
  isMulti,
  options,
  defaultValue,
  errors,
  required,
  recommended,
  onChange,
  className,
  placeholder = "Type and press enter to add...",
}) => {
  const [duplicateAlert, setDuplicateAlert] = useState<string | null>(null);
  const defaultOptions = options.filter((option) =>
    Array.isArray(defaultValue)
      ? defaultValue.includes(option.value)
      : option.value === defaultValue,
  );
  const normalizedErrors = Array.isArray(errors) ? errors.filter(Boolean) : [];

  return (
    <div className={`flex flex-col gap-2 ${className}`}>
      {label && (
        <InputLabel
          name={name}
          required={required}
          recommended={recommended}
          info={info}
          popoverInfo={popoverInfo ?? explanation}
          label={label}
        />
      )}
      <CreatableSelect
        isMulti={isMulti}
        name={name}
        inputId={name}
        options={options}
        defaultValue={defaultOptions}
        onChange={onChange}
        onKeyDown={(e) => {
          if (e.key === "Enter" && isMulti) {
            const inputValue = (e.target as HTMLInputElement).value?.trim();
            if (inputValue) {
              const normalizedInput = inputValue.toLowerCase();
              const isDuplicate = options.some((o) => o.value.toLowerCase() === normalizedInput);
              if (isDuplicate) {
                e.preventDefault();
                e.stopPropagation();
                setDuplicateAlert("Duplicates are not allowed.");
                setTimeout(() => setDuplicateAlert(null), 5000);
              }
            }
          }
        }}
        placeholder={placeholder}
        menuPortalTarget={clientRendering ? document.querySelector("body") : null}
        styles={{
          menuPortal: (base) => ({ ...base, zIndex: 9999 }),
          // Hide dropdown indicators
          dropdownIndicator: (base) => ({ ...base, display: "none" }),
          indicatorSeparator: (base) => ({ ...base, display: "none" }),
          // Make input look more like a tags input
          control: (base) => ({
            ...base,
            minHeight: "44px",
            borderRadius: "0.5rem",
            boxShadow: "none",
            "&:hover": { borderColor: "var(--lnds-light-gray)" },
          }),
          // Customize how the container wraps tags
          valueContainer: (base) => ({
            ...base,
            padding: "2px 8px",
            flexWrap: "wrap",
            gap: "4px",
          }),
        }}
        classNames={{
          input: () => "!text-lnds-gray dark:!text-white",
          control: () =>
            "w-full text-lnds-gray dark:text-white rounded-lg focus:border-lnds-blue focus:outline-none border border-lnds-light-gray dark:border-gray-600 hover:border-lnds-light-gray dark:hover:border-gray-500 !shadow-none bg-white dark:bg-gray-700",
          valueContainer: () => "!focus:border-lnds-blue !focus:outline-none",
          multiValue: () => "!bg-lnds-purple rounded-lg",
          multiValueLabel: () => "!text-white !rounded-l-lg px-2 py-1 text-sm",
          multiValueRemove: () =>
            "!text-white hover:!bg-lnds-dark-blue hover:!text-white !rounded-r-lg !rounded-l-none px-1",
          menu: () => "hidden", // Hide the dropdown menu completely
        }}
        // Hide the menu when typing
        components={{
          DropdownIndicator: null,
          IndicatorSeparator: null,
        }}
        // Allow creation immediately
        formatCreateLabel={(inputValue) => `Add "${inputValue}"`}
        isValidNewOption={(inputValue, selectValue) => {
          if (!inputValue.trim()) return false;
          // Prevent duplicates (case-insensitive)
          const normalizedInput = inputValue.trim().toLowerCase();
          const existingValues = selectValue?.map((option) => option.value.toLowerCase()) || [];
          return !existingValues.includes(normalizedInput);
        }}
        isClearable={false}
        blurInputOnSelect={false}
        closeMenuOnSelect={true}
      />
      {duplicateAlert && <small className='font-bold text-lnds-red'>{duplicateAlert}</small>}
      {normalizedErrors.length > 0 && (
        <small className='font-bold text-lnds-red'>{normalizedErrors.join(" ")}</small>
      )}
    </div>
  );
};

export default CreatableDropdownSelect;

export type InputLabelProps = {
  label: string;
  name?: string;
  info?: string | React.ReactNode;
  popoverInfo?: string;
  required?: boolean;
  recommended?: boolean;
  labelClassName?: string;
};

const InputLabel: React.FC<InputLabelProps> = ({
  label,
  name,
  info,
  popoverInfo,
  required,
  recommended,
  labelClassName,
}) => {
  return (
    <div>
      <FieldInfoHeader
        label={label}
        popoverInfo={popoverInfo}
        required={required}
        as={name ? "label" : "span"}
        htmlFor={name}
        labelClassName={`label-lnds-color text-lg ${labelClassName || ""}`}
        containerClassName='flex items-center gap-1'
      />
      {info && (
        <p
          className={`mb-2 mt-1 text-sm italic ${
            recommended ? "text-teal-500" : "text-lnds-gray dark:text-gray-400"
          }`}
        >
          {info}
        </p>
      )}
    </div>
  );
};
