import { BuildingOfficeIcon, XMarkIcon, StarIcon } from "@heroicons/react/24/solid";
import { Button, Card, useAlert } from "@lnds-lu/design-system";
import InitialsAvatar from "../../components/InitialsAvatar";
import ConfirmableActionButton from "../../components/ConfirmableActionButton";
import { ResourceUserType } from "../../types";
import client from "../../zodiosClient/client";
import { isAxiosError } from "axios";
import StatusBadge from "../../components/StatusBadge";
import Tooltip from "../../components/Tooltip";
import { DeprecatedTag, deprecatedBgClasses } from "../../components/DeprecatedTag";
import { DateUtils } from "../../utils/dateTimeHelpers";
import { appAlerts } from "../../utils/appAlerts";

type UserItemProps = {
  user: ResourceUserType;
  availableOrganisationIds: number[];
  onRemoveOrganization: (userId: number, organizationId: number) => void;
  onRemoveRole: (userId: number, organizationId: number, role: number) => void;
  canDeleteUsers?: boolean;
  isLoggedInUser?: boolean;
  onDeleteUser?: (userId: number) => void;
  onDeprecateUser?: (user: ResourceUserType) => void;
  onRemoveIamRoles?: (userId: number) => void;
};

export default function UserItem(props: Readonly<UserItemProps>) {
  const {
    user,
    availableOrganisationIds,
    onRemoveOrganization,
    onRemoveRole,
    canDeleteUsers,
    isLoggedInUser,
    onDeleteUser,
    onDeprecateUser,
    onRemoveIamRoles,
  } = props;
  const organizations = user.assignments || [];

  const { setAlert } = useAlert();
  const isCatalogueManager = user.iam_roles?.includes("CATALOGUE_MANAGER") || false;

  const handleDeprecate = async () => {
    try {
      await client.change_deprecation_status_api_v1_users__user_id__toggle_deprecation_patch(
        undefined,
        {
          params: { user_id: user.id },
          withCredentials: true,
        },
      );
      setAlert(appAlerts.userDeprecated());
      onDeprecateUser?.(user);
    } catch (error) {
      if (isAxiosError(error)) {
        setAlert(
          appAlerts.genericValidationError(
            error.response?.data?.detail || appAlerts.failedToDeprecateUser().message,
          ),
        );
      } else {
        setAlert(appAlerts.unexpectedError());
      }
    }
  };
  const handleDelete = async () => {
    if (!canDeleteUsers) {
      setAlert(appAlerts.userDeletePermissionDenied());
      return;
    }

    try {
      await client.delete_unassigned_user_api_v1_users__user_id__delete(undefined, {
        params: { user_id: user.id },
        withCredentials: true,
      });
      setAlert(appAlerts.userDeleted());
      onDeleteUser?.(user.id);
    } catch (error) {
      if (isAxiosError(error)) {
        setAlert(
          appAlerts.genericValidationError(
            error.response?.data?.detail || appAlerts.failedToDeleteUser().message,
          ),
        );
      } else {
        setAlert(appAlerts.unexpectedError());
      }
    }
  };

  const handleRemoveIamRoles = async () => {
    if (!canDeleteUsers) {
      setAlert(appAlerts.iamRoleRemovePermissionDenied());
      return;
    }

    try {
      await client.remove_user_iam_roles_api_v1_users__user_id__iam_roles_delete(undefined, {
        params: { user_id: user.id },
        withCredentials: true,
      });
      setAlert(appAlerts.iamRolesRemoved());
      onRemoveIamRoles?.(user.id);
    } catch (error) {
      if (isAxiosError(error)) {
        setAlert(
          appAlerts.genericValidationError(
            error.response?.data?.detail || appAlerts.failedToRemoveIamRoles().message,
          ),
        );
      } else {
        setAlert(appAlerts.unexpectedError());
      }
    }
  };

  return (
    <Card
      className={`mb-4 ${isCatalogueManager ? "ring-2 ring-yellow-400 bg-yellow-50" : ""} ${isLoggedInUser ? "ring-2 ring-lnds-purple" : ""} ${user.is_deprecated ? deprecatedBgClasses : ""}`}
    >
      <div className='flex items-center space-x-3 border-b pb-4 border-lnds-color'>
        <InitialsAvatar name={user.name} showTooltip={true} />
        <div className='flex-1'>
          <div className='font-semibold text-lg heading-lnds-color flex items-center'>
            {user.name}
            {isCatalogueManager && (
              <div className='flex items-center ml-2'>
                <StarIcon className='w-5 h-5 text-yellow-500 mr-1' />
                <span className='px-2 py-0.5 text-xs font-bold bg-gradient-to-r from-yellow-400 to-yellow-600 text-white rounded-full shadow-sm'>
                  CATALOGUE MANAGER
                </span>
              </div>
            )}
            {user.is_deprecated && <DeprecatedTag />}
            {isLoggedInUser && (
              <span className='ml-2 px-2 py-0.5 text-xs font-medium bg-lnds-purple text-white rounded-full'>
                You
              </span>
            )}
            {organizations.length === 0 && !isCatalogueManager && (
              <span className='ml-2 px-2 py-0.5 text-xs font-medium bg-lnds-green text-white rounded-full'>
                New
              </span>
            )}
          </div>
          <div className='text-sm text-lnds-color'>{user.email}</div>
          {user.last_login_at && (
            <div className='text-xs text-gray-500 dark:text-gray-400 mt-1'>
              Last login: {DateUtils.formatRelativeTime(user.last_login_at)}
            </div>
          )}
        </div>

        {!isLoggedInUser && isCatalogueManager && canDeleteUsers && (
          <ConfirmableActionButton
            onConfirm={() => handleRemoveIamRoles()}
            action='remove-iam-roles'
          />
        )}
        {!isLoggedInUser && !user.iam_roles.includes("CATALOGUE_MANAGER") && canDeleteUsers && (
          <ConfirmableActionButton onConfirm={() => handleDelete()} action='delete' />
        )}
        {!isLoggedInUser &&
          !user.iam_roles.includes("CATALOGUE_MANAGER") &&
          canDeleteUsers &&
          (!user.is_deprecated ? (
            <ConfirmableActionButton onConfirm={() => handleDeprecate()} action='deprecate' />
          ) : (
            <ConfirmableActionButton onConfirm={() => handleDeprecate()} action='restore' />
          ))}
      </div>

      <div className='mt-4'>
        {isCatalogueManager && organizations.length === 0 && (
          <div className='text-center py-4 text-yellow-700 rounded-lg mb-4'>
            <StarIcon className='w-6 h-6 mx-auto mb-2 text-yellow-600' />
            <div className='font-medium'>Catalogue Manager</div>
            <div className='text-sm'>Has system-wide access to all organizations</div>
          </div>
        )}

        {organizations.length === 0 && !isCatalogueManager ? (
          <div className='text-center py-4 text-lnds-color'>
            No organisations assigned to this user
          </div>
        ) : (
          organizations.map((org, index) => (
            <div
              key={org.organisation_id}
              className={`pb-4 border-lnds-color ${
                index + 1 === organizations.length ? "border-none" : "border-b mb-4"
              }`}
            >
              <div className='flex justify-between items-center mb-2'>
                <div className='font-medium text-lnds-color flex items-center'>
                  <BuildingOfficeIcon className='w-5 h-5 mr-2' />
                  {org.organisation_name}
                  {org.is_deprecated && (
                    <div className='ml-2'>
                      <StatusBadge isDeprecated />
                    </div>
                  )}
                </div>
                {availableOrganisationIds.includes(org.organisation_id) && (
                  <Tooltip text='Remove Organization'>
                    <Button
                      btnType='danger'
                      size='small'
                      Icon={XMarkIcon}
                      onClick={() => onRemoveOrganization(user.id, org.organisation_id)}
                      label='Remove'
                    />
                  </Tooltip>
                )}
              </div>
              <div className={index + 1 === organizations.length ? "" : "mb-4"}>
                <div className='flex flex-wrap gap-2'>
                  {org.roles.map((role) => (
                    <span
                      key={role.id}
                      className={`inline-flex items-center px-2 py-1 text-xs font-semibold text-white rounded-full mr-1 ${availableOrganisationIds.includes(org.organisation_id) ? "bg-lnds-purple" : "bg-lnds-light-gray"}`}
                    >
                      {role.name}
                      {availableOrganisationIds.includes(org.organisation_id) && (
                        <Tooltip text='Remove Role'>
                          <button
                            type='button'
                            className='inline-flex items-center p-1 ms-2 text-sm bg-transparent rounded-sm hover:bg-lnds-dark-blue'
                            aria-label='remove'
                            onClick={() => onRemoveRole(user.id, org.organisation_id, role.id)}
                          >
                            <XMarkIcon className='h-3 w-3 cursor-pointer' />
                          </button>
                        </Tooltip>
                      )}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </Card>
  );
}
