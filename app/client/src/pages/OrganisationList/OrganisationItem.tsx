import { ResourceOrganisation } from "../../types";
import { BuildingOfficeIcon, PencilIcon, UsersIcon } from "@heroicons/react/24/solid";
import { Card, Button, useAlert } from "@lnds-lu/design-system";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import ConfirmableActionButton from "../../components/ConfirmableActionButton";
import client from "../../zodiosClient/client";
import { isAxiosError } from "axios";
import Tooltip from "../../components/Tooltip";
import { DeprecatedTag, deprecatedBgClasses } from "../../components/DeprecatedTag";
import { appAlerts } from "../../utils/appAlerts";

export default function OrganizationItem({
  organisation,
  onEdit,
  onDeprecate,
}: Readonly<{
  organisation: ResourceOrganisation;
  onEdit: (organisation: ResourceOrganisation) => void;
  onDeprecate: (organisation: ResourceOrganisation, isDeprecated: boolean) => void;
}>) {
  const { user } = useAuth();
  const { setAlert } = useAlert();

  const canEditOrganisation =
    user?.permissions.includes("organisations:edit") ||
    user?.permissions.includes("organisations:edit:organisation");

  const handleToggleDeprecation = async () => {
    try {
      await client.toggle_organisation_deprecation_api_v1_organisations__organisation_id__toggle_deprecation_patch(
        undefined,
        {
          params: { organisation_id: organisation.id },
          withCredentials: true,
        },
      );
      setAlert(appAlerts.organisationDeprecationToggled(organisation.is_deprecated));
      onDeprecate(organisation, !organisation.is_deprecated);
    } catch (error) {
      if (isAxiosError(error)) {
        setAlert(
          appAlerts.genericValidationError(
            error.response?.data?.detail || appAlerts.organisationDeprecationToggleFailed().message,
          ),
        );
      } else {
        setAlert(appAlerts.unexpectedError());
      }
    }
  };

  return (
    <Card
      className={`flex w-full flex-col border-b-0 border-l-0 border-r-0 rounded-none ${organisation.is_deprecated ? deprecatedBgClasses : ""}`}
    >
      <div className='flex flex-col items-center justify-between md:flex-row h-full'>
        <div className='border-lnds-color flex w-full flex-1 items-center justify-between border border-b-0 border-l-0 border-t-0 border-none md:border-b md:border-l md:border-t'>
          <div className='flex w-full flex-col items-start'>
            <div className='flex w-full flex-col items-start'>
              <div className='heading-lnds-color mb-2 flex items-center space-x-2'>
                <BuildingOfficeIcon className='h-4 w-4 lg:h-6 lg:w-6' />
                <h1 className='text-sm lg:text-xl'>{organisation.name}</h1>
                {organisation.is_deprecated && <DeprecatedTag />}
              </div>
              <div className='mt-2 flex w-full flex-col text-xs md:flex-row md:space-x-8'>
                <div className='flex flex-col md:flex-row space-y-2 md:space-y-0 w-full'>
                  <div className='w-1/2'>
                    <div className='text-xs md:text-sm font-semibold label-lnds-color'>Type</div>
                    <p className='text-lnds-color text-sm'>
                      {organisation.type || "Not specified"}
                    </p>
                  </div>
                  <div className='w-1/2'>
                    <div className='text-xs md:text-sm font-semibold label-lnds-color'>Email</div>
                    <p className='text-lnds-color text-sm'>
                      {organisation.email || "Not specified"}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          {canEditOrganisation && (
            <div className='flex items-center space-x-4 px-4'>
              {organisation.is_deprecated ? (
                <ConfirmableActionButton action='restore' onConfirm={handleToggleDeprecation} />
              ) : (
                <>
                  <Tooltip text='Edit Organisation'>
                    <Button
                      btnType='transparent'
                      onClick={() => onEdit(organisation)}
                      className='p-2 w-10 h-10 rounded-md flex items-center justify-center icon-lnds-color cursor-pointer'
                      Icon={PencilIcon}
                    />
                  </Tooltip>
                  <ConfirmableActionButton action='deprecate' onConfirm={handleToggleDeprecation} />
                </>
              )}
            </div>
          )}
        </div>
        <div className='border-lnds-color border-l min-h-full self-stretch flex flex-col items-center justify-center pl-4 pr-4'>
          <div className='flex flex-col items-center mb-2'>
            <span className='text-3xl font-bold hover:text-lnds-dark-blue'>
              {organisation.contacts.length}
            </span>
          </div>
          <Button
            to={`/organisations/${organisation.id}`}
            Link={Link}
            Icon={UsersIcon}
            label='Contacts'
            size='small'
          />
        </div>
      </div>
    </Card>
  );
}
