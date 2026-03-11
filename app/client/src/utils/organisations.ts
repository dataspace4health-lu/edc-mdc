type Assignment = {
  organisation_id: number;
  organisation_name: string;
  roles: { id: number; name: string }[];
  is_deprecated?: boolean;
};

type UserWithAssignments = {
  assignments?: Assignment[];
};

export function getNonDeprecatedAssignments(user?: UserWithAssignments | null) {
  return (user?.assignments || []).filter((org) => !org.is_deprecated);
}

export function filterOrganisationsByAccess<T extends Record<string, unknown>>(
  organisations: T[],
  isCTIEInstance: boolean | undefined,
  enableMultiTenants: boolean | undefined,
  enableDualInstance: boolean = false,
): T[] {
  return organisations.filter((org) => {
    if (org.is_deprecated === true) {
      return false;
    }

    if (!enableDualInstance) {
      return true;
    }

    if (!enableMultiTenants) {
      return true;
    }

    const accessible = org.accessible_within_ctie as boolean | null | undefined;
    if (isCTIEInstance && accessible === false) {
      return false;
    }

    if (!isCTIEInstance && accessible === true) {
      return false;
    }

    return true;
  });
}
