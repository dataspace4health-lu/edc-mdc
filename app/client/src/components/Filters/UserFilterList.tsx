import { Card, Button } from "@lnds-lu/design-system";
import Filter from "./Filter";
import { useUrlState } from "../../hooks/useUrlState";
import { XMarkIcon } from "@heroicons/react/20/solid";
import { FilterTypes } from "../../types";

type Props = {
  organisations: Array<{ id: number; name: string }>;
  roles: Array<{ id: number; name: string }>;
  showNoRoleFilter: boolean;
};

export default function UserFilterList(props: Readonly<Props>) {
  const { organisations, roles, showNoRoleFilter } = props;
  const { generateUrl } = useUrlState();

  const filters = [
    {
      key: FilterTypes.UserOrganisations,
      label: "Organisations",
      options: organisations.map((org) => ({
        value: String(org.id),
        eng_label: org.name,
      })),
      isMulti: true,
    },
    {
      key: FilterTypes.UserRoles,
      label: "Roles",
      options: roles.map((role) => ({
        value: String(role.id),
        eng_label: role.name,
      })),
      isMulti: true,
    },
  ];

  if (showNoRoleFilter) {
    filters.push(
      {
        key: FilterTypes.OnlyUnassigned,
        label: "Without Any Role",
        options: [{ value: "true", eng_label: "Users with no organisation and role" }],
        isMulti: false,
      },
      {
        key: FilterTypes.deprecatedUsers,
        label: "Deprecated users",
        options: [{ value: "true", eng_label: "Deprecate users" }],
        isMulti: false,
      },
    );
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
        {filters.map((f) => (
          <Filter
            key={f.key}
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
