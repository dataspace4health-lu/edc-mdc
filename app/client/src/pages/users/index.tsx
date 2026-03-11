import { useEffect, useState } from "react";
import { UsersIcon } from "@heroicons/react/24/solid";
import AssignRoleForm from "./AssignRoleForm";
import { Spinner } from "../../components/Spinner";
import { useLoaderData } from "react-router";
import Pagination from "../DatasetList/Pagination";
import EmptyScreen from "../../components/EmptyScreen";
import DismissibleAlert from "../../components/DismissibleAlert";
import { usersLoader } from "./loader";
import UserItem from "./UserItem";
import SearchPanel from "../DatasetList/SearchPanel";
import client from "../../zodiosClient/client";
import { useAuth } from "../../context/AuthContext";
import { useUrlState } from "../../hooks/useUrlState";
import { ResourceUserType, FilterTypes, ResourceRoleType } from "../../types";
import UserFilterList from "../../components/Filters/UserFilterList";
import { useMemo } from "react";
import { useAlert } from "@lnds-lu/design-system";
import { RightSidebar } from "../../components/RightSidebar";
import { ResourceOrganisation } from "../../types";
import { isAxiosError } from "axios";
import { usePageTitle } from "../../hooks/usePageTitle";
import { appAlerts } from "../../utils/appAlerts";

export default function UserList() {
  usePageTitle("Users");
  const { user } = useAuth();
  const { getPageParam, getFilter } = useUrlState(user?.permissions || []);
  const { setAlert } = useAlert();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [sidebarKey, setSidebarKey] = useState(0);

  const query = getPageParam("query");
  const page = getPageParam("page");
  const pageSize = getPageParam("pageSize");
  const [allRoles, setAllRoles] = useState<ResourceRoleType[]>([]);
  const organisation = (useLoaderData() as Awaited<ResourceOrganisation>) || [];

  const [users, setUsers] = useState<ResourceUserType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(0);
  const [error, setError] = useState<Error | null>(null);
  const [filtersApplied, setFiltersApplied] = useState(false);

  const allOrganisations = (useLoaderData() as Awaited<ReturnType<typeof usersLoader>>) || [];

  const canManageRoles = user?.permissions?.includes("roles:manage");

  const active_organisations = allOrganisations
    .filter((org) => !org.is_deprecated)
    .filter((org) => canManageRoles || user?.current_organisation?.id === org.id);

  const organisations = allOrganisations.filter(
    (org) => canManageRoles || user?.current_organisation?.id === org.id,
  );

  const allFilters = [
    FilterTypes.UserOrganisations,
    FilterTypes.UserRoles,
    FilterTypes.OnlyUnassigned,
    FilterTypes.deprecatedUsers,
  ];

  const filterMap = useMemo(() => {
    return new Map<FilterTypes, string[]>(allFilters.map((filter) => [filter, getFilter(filter)]));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [allFilters.map((f) => getFilter(f).join(",")).join(",")]);

  const serializedFilterMap = JSON.stringify(Array.from(filterMap.values()));

  const fetchUsers = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const organisationIds = (filterMap.get(FilterTypes.UserOrganisations) ?? []).map(Number);
      const roleIds = (filterMap.get(FilterTypes.UserRoles) ?? []).map(Number);
      const onlyUnassigned = filterMap.get(FilterTypes.OnlyUnassigned) ?? [];
      const deprecatedOnly = (filterMap.get(FilterTypes.deprecatedUsers) ?? []).map(Number);

      const response = await client.users_api_v1_users_post(
        {
          page: Number(page),
          page_size: Number(pageSize),
          query,
          organisation_ids: organisationIds.length ? organisationIds.map(Number) : undefined,
          role_ids: roleIds.length ? roleIds.map(Number) : undefined,
          only_unassigned: onlyUnassigned.includes("true") ? true : undefined,
          is_deprecated: deprecatedOnly.length ? true : false,
        },
        { withCredentials: true },
      );
      setUsers(response.items);
      setTotalCount(response.meta.total_items);
    } catch (error) {
      console.error("Failed to fetch users:", error);
      // @ts-expect-error custom error handling
      if (error.response?.status === 403) {
        const customError = new Error("You do not have permission to view this page.");
        // @ts-expect-error custom error handling
        customError.status = 403; // Add status property
        // @ts-expect-error custom error handling
        customError.response = error.response; // Preserve original response
        setError(customError);
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const organisationIds = (filterMap.get(FilterTypes.UserOrganisations) ?? []).map(Number);
    const roleIds = (filterMap.get(FilterTypes.UserRoles) ?? []).map(Number);
    const onlyUnassigned = filterMap.get(FilterTypes.OnlyUnassigned) ?? [];
    const isAnyFilterApplied =
      organisationIds.length > 0 ||
      roleIds.length > 0 ||
      onlyUnassigned.includes("true") ||
      (!!query && query.trim() !== "");
    setFiltersApplied(isAnyFilterApplied);

    fetchUsers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [serializedFilterMap, query, page, pageSize]);

  useEffect(() => {
    async function fetchRoles() {
      try {
        const response = await client.get_roles_api_v1_roles_post(undefined, {
          withCredentials: true,
        });
        setAllRoles(response);
      } catch (error) {
        console.error("Failed to fetch all roles", error);
      }
    }
    fetchRoles();
  }, []);

  if (error) {
    throw error;
  }

  const handleRemoveOrganization = async (userId: number, organisationId: number) => {
    try {
      await client.delete_organisation_assignment_api_v1_organisations__organisation_id__assignments__user_id__delete(
        undefined,
        {
          params: {
            organisation_id: organisationId,
            user_id: userId,
          },
          withCredentials: true,
        },
      );
      setUsers((prevUsers) =>
        prevUsers.map((user) =>
          user.id === userId
            ? {
                ...user,
                assignments: user.assignments?.filter((a) => a.organisation_id !== organisationId),
              }
            : user,
        ),
      );
      setSidebarKey((prev) => prev + 1);
      setAlert(appAlerts.organisationRemoved());
    } catch (error) {
      console.error("Error while removing the assignment between user and organisation :", error);
      if (isAxiosError(error)) {
        // @ts-expect-error error response structure
        setAlert(appAlerts.genericValidationError(error.response.data.detail));
      } else {
        setAlert(appAlerts.unknownError());
      }
    }
  };

  const handleRemoveRole = async (userId: number, organisationId: number, roleId: number) => {
    try {
      await client.delete_user_role_assignment_api_v1_organisations__organisation_id__assignments__user_id__roles__role_id__delete(
        undefined,
        {
          params: {
            organisation_id: organisationId,
            user_id: userId,
            role_id: roleId,
          },
          withCredentials: true,
        },
      );

      setUsers((prevUsers) =>
        prevUsers.map((user) => {
          if (user.id !== userId) return user;

          const updatedAssignments =
            user.assignments?.map((assignment) => {
              if (assignment.organisation_id !== organisationId) return assignment;

              const filteredRoles = assignment.roles.filter((role) => role.id !== roleId);

              return {
                ...assignment,
                roles: filteredRoles,
              };
            }) ?? [];

          const filteredAssignments = updatedAssignments.filter(
            (assignment) => assignment.roles.length > 0,
          );

          return {
            ...user,
            assignments: filteredAssignments,
          };
        }),
      );
      setSidebarKey((prev) => prev + 1);
      setAlert(appAlerts.roleRemoved());
    } catch (error) {
      console.error("Failed to remove role assignment:", error);
      if (isAxiosError(error)) {
        // @ts-expect-error error response structure
        setAlert(appAlerts.genericValidationError(error.response.data.detail));
      } else {
        setAlert(appAlerts.unknownError());
      }
    }
  };

  const handleRoleAssigned = (
    email: string,
    organisationId: number,
    role: { id: number; name: string },
  ) => {
    const userExists = users.some((u) => u.email === email);

    if (!userExists) {
      fetchUsers();
      setTimeout(() => {
        setAlert(appAlerts.roleAssigned());
      }, 100);
      return;
    }

    setUsers((prevUsers) => {
      const userIndex = prevUsers.findIndex((u) => u.email === email);
      if (userIndex === -1) return prevUsers;

      const user = prevUsers[userIndex];

      const updatedAssignments = user.assignments ? [...user.assignments] : [];

      const assignmentIndex = updatedAssignments.findIndex(
        (a) => a.organisation_id === organisationId,
      );

      if (assignmentIndex === -1) {
        updatedAssignments.push({
          organisation_id: organisationId,
          organisation_name:
            active_organisations.find((org) => org.id === organisationId)?.name || "",
          roles: [role],
          is_deprecated: organisation.is_deprecated,
        });
      } else {
        const assignment = updatedAssignments[assignmentIndex];
        const roleExists = assignment.roles.some((r) => r.id === role.id);

        if (!roleExists) {
          assignment.roles = [...assignment.roles, role];
        }
        updatedAssignments[assignmentIndex] = assignment;
      }

      const updatedUser = {
        ...user,
        assignments: updatedAssignments,
      };

      const newUsers = [...prevUsers];
      newUsers[userIndex] = updatedUser;
      setSidebarKey((prev) => prev + 1);
      return newUsers;
    });
  };

  const showNoRoleFilter = user?.permissions?.includes("roles:manage") || false;

  const canAssignRoleToOrganisation =
    user?.permissions?.includes("roles:manage:organisation") || false;

  const handleDeleteUser = (deletedUserId: number) => {
    setUsers((prev) => prev.filter((u) => u.id !== deletedUserId));
    setAlert(appAlerts.userDeleted());
  };

  const handleDeprecateUser = (user: ResourceUserType) => {
    setUsers((prev) => prev.filter((u) => u.id !== user.id));
    const alertMsg = user.is_deprecated
      ? "User has been restored successfully"
      : "User has been deprecated successfully";
    setAlert(appAlerts.alertMessageAsSuccess(alertMsg));
  };

  const handleRemoveIamRoles = (userId: number) => {
    setUsers((prevUsers) =>
      prevUsers.map((user) =>
        user.id === userId
          ? {
              ...user,
              iam_roles: [],
            }
          : user,
      ),
    );
  };

  return (
    <div className='flex flex-col gap-y-6 lg:gap-y-0 lg:flex-row lg:gap-x-4 mx-4 2xl:mx-24 my-4'>
      <div className='w-full lg:w-1/4 mt-6'>
        <UserFilterList
          organisations={organisations}
          roles={allRoles}
          showNoRoleFilter={showNoRoleFilter}
        />
      </div>
      <div className='w-full lg:w-3/4'>
        <div className='mt-6'>
          {isLoading ? (
            <div className='flex justify-center items-center h-48'>
              <Spinner />
            </div>
          ) : (
            <div className='flex flex-col gap-y-4'>
              <AssignRoleForm
                organisations={active_organisations}
                roles={allRoles.map((role) => ({ label: role.name, value: role.id.toString() }))}
                onRoleAssigned={handleRoleAssigned}
              />
              <div className='mb-4'>
                <SearchPanel query={query} placeholder='Search users by name or email' />
                {canAssignRoleToOrganisation && (
                  <DismissibleAlert
                    message={`New users without roles won't appear in this list. Enter their email in the "Assign Role" form to assign a role - they'll appear here once assigned.
`}
                    type='info'
                  />
                )}
              </div>
              {!isLoading && (filtersApplied || query) && users.length > 0 && (
                <div className='mt-3 mb-4 px-4 py-3 section-lnds-color border-l-4 border-lnds-blue rounded-md text-lnds-color text-sm font-medium'>
                  <strong className='text-base'>{totalCount}</strong>{" "}
                  {totalCount === 1 ? "result" : "results"} found with filters or query
                </div>
              )}
              {users.length === 0 ? (
                <EmptyScreen message='No users available' Icon={UsersIcon} />
              ) : (
                users.map((us) => {
                  return (
                    <UserItem
                      key={us.id}
                      user={us}
                      availableOrganisationIds={active_organisations

                        .filter((org) => !org.is_deprecated)
                        .map((org) => org.id)}
                      onRemoveOrganization={handleRemoveOrganization}
                      onRemoveRole={handleRemoveRole}
                      canDeleteUsers={canManageRoles}
                      onDeleteUser={handleDeleteUser}
                      onDeprecateUser={handleDeprecateUser}
                      onRemoveIamRoles={handleRemoveIamRoles}
                      isLoggedInUser={user?.id === us.id}
                    />
                  );
                })
              )}
              <Pagination
                currentPage={Number(page)}
                totalPages={Math.ceil(totalCount / Number(pageSize))}
                pageSize={Number(pageSize)}
                query={query}
              />
            </div>
          )}
        </div>
      </div>
      <div
        className={`transition-all duration-300 ease-in-out ${
          isSidebarOpen ? "w-[28rem]" : "w-0"
        } overflow-hidden`}
      >
        {users && (
          <RightSidebar
            refreshTrigger={sidebarKey}
            entityId={organisation.id}
            entityType='user_assignment'
            className='border-l border-lnds-color'
            defaultIsOpen={false}
            onSidebarToggle={(isOpen: boolean) => setIsSidebarOpen(isOpen)}
            organisations={active_organisations}
            roles={allRoles}
          />
        )}
      </div>
    </div>
  );
}
