import React, { useState } from "react";
import { ChevronDownIcon, BuildingOfficeIcon, CheckIcon } from "@heroicons/react/24/solid";
import { QuestionMarkCircleIcon } from "@heroicons/react/24/outline";
import { ResourceUserType } from "../types";
import client from "../zodiosClient/client";
import { getNonDeprecatedAssignments } from "../utils/organisations";

interface OrganizationSwitcherProps {
  user: ResourceUserType | null;
}

const OrganizationSwitcher: React.FC<OrganizationSwitcherProps> = ({ user }) => {
  const [isOpen, setIsOpen] = useState(false);
  if (!user?.feature_options.enable_multi_tenants || !user) {
    return null;
  }

  const currentOrg = user.current_organisation;
  const availableOrgs = getNonDeprecatedAssignments(user);
  const isRolesManager = user.permissions?.includes("roles:manage");
  const canSwitch = availableOrgs.length > 1;

  if (!currentOrg || isRolesManager || availableOrgs.length === 1) {
    return null;
  }

  const handleOrgSwitch = async (orgId: number) => {
    try {
      await client.switch_organisation_api_v1_switch_organisation__org_id__post(undefined, {
        params: { org_id: orgId },
        withCredentials: true,
      });
      window.location.reload();
    } catch (error) {
      console.error("Error switching organization:", error);
    } finally {
      setIsOpen(false);
    }
  };

  return (
    <div className='relative'>
      {/* Desktop/Tablet Version */}
      <div className='hidden sm:block'>
        <button
          onClick={() => canSwitch && setIsOpen(!isOpen)}
          disabled={!canSwitch}
          className={`
            flex items-center space-x-2 px-3 py-2 rounded-md border transition-colors duration-200
            ${
              canSwitch
                ? "border-lnds-color hover:border-lnds-dark-blue cursor-pointer"
                : "border-gray-300 cursor-default"
            }
            bg-white dark:bg-gray-800 dark:border-gray-600
          `}
        >
          <BuildingOfficeIcon className='h-4 w-4 text-lnds-color flex-shrink-0' />
          <span className='text-sm font-medium'>Switch Org</span>
          {canSwitch && (
            <ChevronDownIcon
              className={`h-4 w-4 icon-lnds-color flex-shrink-0 transition-transform duration-200 ${
                isOpen ? "rotate-180" : ""
              }`}
            />
          )}
        </button>
      </div>

      <div className='sm:hidden'>
        <button
          onClick={() => canSwitch && setIsOpen(!isOpen)}
          disabled={!canSwitch}
          className={`
            flex items-center space-x-1 px-2 py-1 rounded border transition-colors duration-200
            ${canSwitch ? "border-lnds-color cursor-pointer" : "border-gray-300 cursor-default"}
            bg-white dark:bg-gray-800 dark:border-gray-600
          `}
        >
          <BuildingOfficeIcon className='h-3 w-3 text-lnds-color flex-shrink-0' />
          <span className='text-xs font-medium'>Switch</span>
          {canSwitch && (
            <ChevronDownIcon
              className={`h-3 w-3 icon-lnds-color flex-shrink-0 transition-transform duration-200 ${
                isOpen ? "rotate-180" : ""
              }`}
            />
          )}
        </button>
      </div>

      {/* Dropdown Menu */}
      {isOpen && canSwitch && (
        <div className='absolute top-full left-0 mt-1 w-80 bg-white dark:bg-gray-800 border border-lnds-color rounded-md z-50 max-h-96 overflow-y-auto'>
          <div className='py-1'>
            <div className='px-3 py-2 flex items-center justify-between border-b border-lnds-color'>
              <span className='text-xs font-semibold text-lnds-color uppercase tracking-wide'>
                Switch Organization
              </span>

              <a
                href='/roles'
                className='text-xs text-lnds-color hover:text-lnds-dark-blue hover:underline transition-colors duration-200 flex items-center space-x-1'
                title='View roles and permissions'
              >
                <QuestionMarkCircleIcon className='h-5 w-5' />
                <span>Roles Info</span>
              </a>
            </div>

            {availableOrgs.map((assignment, index) => (
              <button
                key={assignment.organisation_id}
                onClick={() => handleOrgSwitch(assignment.organisation_id)}
                className={`
                  w-full text-left px-3 py-2 group hover:text-white hover:bg-lnds-dark-blue transition-colors duration-200 border-lnds-color
                  ${
                    currentOrg?.id === assignment.organisation_id
                      ? ""
                      : "text-gray-700 dark:text-gray-200"
                  }
                  ${index === availableOrgs.length - 1 ? "" : "border-b"}
                `}
              >
                <div className='flex items-center justify-between'>
                  <div className='flex-1 min-w-0'>
                    <div className='font-medium text-sm label-lnds-color group-hover:text-white'>
                      {assignment.organisation_name}
                    </div>
                    <div className='text-sm font-bold text-lnds-color mt-1 group-hover:text-white'>
                      {assignment.roles.map((role) => role.name.replace(/_/g, " ")).join(", ")}
                    </div>
                  </div>
                  {currentOrg?.id === assignment.organisation_id && (
                    <div className='text-lnds-color dark:text-white group-hover:text-white'>
                      <CheckIcon className='h-4 w-4' />
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default OrganizationSwitcher;
