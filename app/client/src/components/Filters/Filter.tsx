import { Checkbox, DropdownSelect } from "@lnds-lu/design-system";
import { SingleValue } from "react-select";
import { useUrlState } from "../../hooks/useUrlState";
import { FilterTypes } from "../../types";

type FilterProps = {
  filterKey: FilterTypes;
  label: string;
  options: Array<{ eng_label: string; value: string }>;
  isMulti: boolean;
};

export default function Filter(props: Readonly<FilterProps>) {
  const { filterKey, label, options, isMulti } = props;
  const { getFilter, updateFilter, clearFilter } = useUrlState();

  const selectedValues = getFilter(filterKey) || [];

  const handleOptionChangeOnDropdown = (
    options:
      | ReadonlyArray<{ label: string; value: string }>
      | { label: string; value: string }
      | null,
  ) => {
    const noOptionSelected = !options || (Array.isArray(options) && options.length === 0);

    if (noOptionSelected) {
      clearFilter(filterKey);
    } else if (Array.isArray(options)) {
      updateFilter(
        filterKey,
        options.map((o) => o.value),
      );
    } else {
      updateFilter(filterKey, [(options as SingleValue<{ label: string; value: string }>)!.value]);
    }
  };

  const handleOptionChangeOnCheckbox = (selectedValues: string[]) => {
    if (selectedValues.length > 0) {
      updateFilter(filterKey, selectedValues);
    } else {
      clearFilter(filterKey);
    }
  };

  return (
    <div className='flex flex-col gap-y-2'>
      <h1 className='text-lnds-gray dark:text-gray-400'>{label}</h1>
      {options.length > 3 ? (
        <DropdownSelect
          options={options.map((o) => ({ label: o.eng_label, value: o.value }))}
          isMulti={isMulti}
          name={label}
          onChange={handleOptionChangeOnDropdown}
          defaultValue={selectedValues}
        />
      ) : (
        <Checkbox
          label=''
          name={label}
          layout='vertical'
          options={options.map((o) => ({ label: o.eng_label, value: o.value }))}
          selectedValue={selectedValues}
          onChange={handleOptionChangeOnCheckbox}
        />
      )}
    </div>
  );
}
