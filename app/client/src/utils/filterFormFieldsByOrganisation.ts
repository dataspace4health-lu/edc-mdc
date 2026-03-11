import { ResourceUserType } from "../types";

type FormFieldWithOrganisations = {
  eng_label: string;
  value: string;
  organisation_ids?: number[] | null;
};

type FilterOptions = {
  user: ResourceUserType | null;
  selectedPublisherId?: string | null;
};

export function filterFormFieldsByOrganisation<T extends FormFieldWithOrganisations>(
  fields: T[],
  options: FilterOptions,
): T[] {
  const { user, selectedPublisherId } = options;

  return fields.filter((field) => {
    const isGlobal = !field.organisation_ids || field.organisation_ids.length === 0;

    // If multi-tenants is disabled, show all fields
    if (!user?.feature_options.enable_multi_tenants) {
      return true;
    }

    // Users with roles:manage permission
    if (user?.permissions?.includes("roles:manage")) {
      // If a publisher is selected, show global + publisher's org fields
      if (selectedPublisherId) {
        return (
          isGlobal ||
          field.organisation_ids?.map((id) => id.toString()).includes(selectedPublisherId)
        );
      }
      // If no publisher selected, show all fields
      return true;
    }

    // Regular users (multi-tenant enabled, no roles:manage)
    // Show global fields + fields from user's organisation
    return (
      isGlobal ||
      (user?.current_organisation?.id &&
        field.organisation_ids
          ?.map((id) => id.toString())
          .includes(user.current_organisation.id.toString())) ||
      false
    );
  });
}

export function sortFormFieldsByLabel<T extends { label: string }>(fields: T[]): T[] {
  return fields.sort((a, b) => a.label.toLowerCase().localeCompare(b.label.toLowerCase()));
}
