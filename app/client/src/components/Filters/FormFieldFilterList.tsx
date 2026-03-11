import { Card, Button } from "@lnds-lu/design-system";
import Filter from "./Filter";
import { useUrlState } from "../../hooks/useUrlState";
import { XMarkIcon } from "@heroicons/react/20/solid";
import { FilterTypes } from "../../types";

type Props = {
  organisations: Array<{ label: string; value: number }>;
  fieldTypeName: string;
};

export default function FormFieldFilterList(props: Readonly<Props>) {
  const { organisations, fieldTypeName } = props;
  const { generateUrl } = useUrlState();

  const filters = [
    {
      key: FilterTypes.FormFieldOrganisations,
      label: "Global",
      options: [
        {
          value: "global",
          eng_label: `Show Global ${fieldTypeName}`,
        },
      ],
      isMulti: false,
    },
    {
      key: FilterTypes.FormFieldOrganisations,
      label: "Organisations",
      options: organisations.map((org) => ({
        value: String(org.value),
        eng_label: org.label,
      })),
      isMulti: true,
    },
  ];

  const onClearAllFilters = () => {
    window.location.href = generateUrl({}, { removeAllFilters: true });
  };

  return (
    <Card className='w-full flex flex-col gap-y-6'>
      <div className='flex justify-between items-center'>
        <h1 className='font-bold text-xl dark:text-white'>Filters</h1>
        <Button
          label='Reset all'
          Icon={XMarkIcon}
          btnType='transparent'
          onClick={onClearAllFilters}
        />
      </div>
      <div className='flex flex-col gap-y-6'>
        {filters.map((f) => (
          <Filter
            key={f.key + f.label}
            filterKey={f.key}
            label={f.label}
            options={f.options}
            isMulti={f.isMulti}
          />
        ))}
      </div>
    </Card>
  );
}
