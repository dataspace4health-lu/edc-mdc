import { Button, Card } from "@lnds-lu/design-system";
import Filter from "./Filter";
import { XMarkIcon } from "@heroicons/react/20/solid";
import { FormType, FilterTypes, DatasetStatusEnum } from "../../types";
import { rightStatementsOptions } from "../../utils/rightStatementsLabels";
import { useUrlState } from "../../hooks/useUrlState";
import { useAuth } from "../../context/AuthContext";

type FilterListProps = {
  formFields: FormType;
  status: string;
};

type FilterType = {
  key: FilterTypes;
  label: string;
  options: Array<{ eng_label: string; value: string }>;
  isMulti: boolean;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  hide?: (user: any) => boolean;
};

export default function FilterList(props: Readonly<FilterListProps>) {
  const { formFields, status } = props;
  const { generateUrl } = useUrlState();
  const { user } = useAuth();

  const filters: FilterType[] = [
    {
      key: FilterTypes.DatasetTypes,
      label: "Dataset Types",
      options: formFields.dataset.dataset_types,
      isMulti: true,
    },
    {
      key: FilterTypes.RightsStatment,
      label: "Rights Statement",
      options: rightStatementsOptions,
      isMulti: true,
    },
    {
      key: FilterTypes.Organisations,
      label: "Publishers",
      options: formFields.organisation.organisations,
      isMulti: true,
    },
    {
      key: FilterTypes.Keywords,
      label: "Keywords",
      options: formFields.dataset.keywords,
      isMulti: true,
    },
    {
      key: FilterTypes.Themes,
      label: "Themes",
      options: formFields.dataset.themes,
      isMulti: true,
    },
    {
      key: FilterTypes.ApplicableLegislations,
      label: "Applicable Legislations",
      options: formFields.dataset.applicable_legislations || [],
      isMulti: true,
    },
    {
      key: FilterTypes.Frequency,
      label: "Frequency",
      options: formFields.dataset.periodicities,
      isMulti: true,
    },
  ];

  if (status === DatasetStatusEnum.PUBLISHED) {
    filters.unshift({
      key: FilterTypes.authenticSource,
      label: "Authentic Source",
      options: [
        {
          eng_label: "Needs Review",
          value: "authentic_source_review_pending",
        },
        {
          eng_label: "Needs Labeling",
          value: "has_unlabeled_authentic_source",
        },
      ],
      isMulti: false,
    });
  }

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
        {filters.map((f) => {
          if (!f.options.length || (f.hide && f.hide(user))) {
            return null;
          }

          return (
            <Filter
              key={f.key}
              filterKey={f.key}
              label={f.label}
              options={f.options}
              isMulti={f.isMulti}
            />
          );
        })}
      </div>
    </Card>
  );
}
