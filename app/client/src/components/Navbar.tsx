import { useEffect, useState, useRef } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  HomeIcon,
  PlusCircleIcon,
  ArrowUpTrayIcon,
  ArrowRightOnRectangleIcon,
  BuildingOfficeIcon,
  TagIcon,
  Cog6ToothIcon,
  ScaleIcon,
  ServerIcon,
  UsersIcon,
  ShieldCheckIcon,
  RectangleGroupIcon,
  CloudIcon,
} from "@heroicons/react/24/solid";
import { ResourceUserType } from "../types";
import { logoutUrl } from "../utils/authUrls";
import { Navbar, Button, NavigationDropdown } from "@lnds-lu/design-system";
import DarkModeLink from "./DarkModeLink";
import { useLeftSidebar } from "../context/LeftSidebarContext";
import InitialsAvatar from "./InitialsAvatar";
import OrganizationSwitcher from "./OrganizationSwitcher";
import Tooltip from "./Tooltip";
import { DRAFT_EDIT_PERMISSIONS } from "../utils/permissions";

interface MetadataNavbarProps {
  user: ResourceUserType | null;
}

export default function MetadataNavbar(props: Readonly<MetadataNavbarProps>) {
  const { user } = props;
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const { isSidebarOpen, setSidebarOpen } = useLeftSidebar();
  const path = useLocation().pathname;
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const theme = localStorage.getItem("theme");
    const prefersDarkMode = window.matchMedia("(prefers-color-scheme: dark)").matches;
    if (theme === "dark" || (prefersDarkMode && !theme)) {
      window.document.documentElement.classList.add("dark");
      setIsDarkMode(true);
    }
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    };

    if (dropdownOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [dropdownOpen]);

  const onChangeDarkMode = () => {
    if (isDarkMode) {
      window.document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    } else {
      localStorage.setItem("theme", "dark");
      window.document.documentElement.classList.add("dark");
    }
    setIsDarkMode(!isDarkMode);
    setDropdownOpen(false);
  };

  const showUsersLink =
    user?.feature_options?.enable_multi_tenants &&
    ["roles:manage", "roles:manage:organisation"].some((p) => user?.permissions?.includes(p));

  const showFrontOfficeLink = user?.feature_options?.enable_upload_datasets_to_front_office;

  const showAuthenticSourcesLink = user?.feature_options?.enable_authentic_source;

  const showOrganisationsLink = [
    "organisations:edit",
    "organisations:edit:organisation",
    "contacts:edit:organisation",
    "contacts:edit",
  ].some((p) => user?.permissions?.includes(p));

  const showDatasetActions = DRAFT_EDIT_PERMISSIONS.some((p) => user?.permissions?.includes(p));

  const renderUserRoles = () => {
    if (!user) return null;

    if (user?.feature_options.enable_multi_tenants) {
      return (
        <div className='flex flex-col space-y-1 mt-1'>
          {user.iam_roles
            .filter((role: string) => role.toLowerCase().includes("catalogue_manager"))
            .map((role: string) => (
              <div key={`iam-${role}`} className='text-xs'>
                <Link
                  to='/roles'
                  className='text-lnds-color hover:text-lnds-dark-blue underline hover:no-underline transition-colors duration-200 cursor-pointer'
                >
                  {role.split("_").join(" ")}
                </Link>
              </div>
            ))}

          {user.assignments
            ?.filter((assignment) => !assignment.is_deprecated)
            .map((assignment, assignmentIndex) => (
              <div key={`org-${assignment.organisation_id}`}>
                {(assignmentIndex > 0 ||
                  user.iam_roles.filter((role: string) =>
                    role.toLowerCase().includes("catalogue_manager"),
                  ).length > 0) && (
                  <div className='border-t border-gray-200 dark:border-gray-600 my-2'></div>
                )}

                <div className='space-y-2'>
                  {assignment.roles?.map((role) => (
                    <div
                      key={`assignment-${assignment.organisation_id}-${role.id}`}
                      className='text-xs bg-gray-50 dark:bg-gray-800 p-2 rounded border-l-2 border-gray-400'
                    >
                      <div className='text-gray-500 dark:text-gray-400 font-medium text-[10px] uppercase tracking-wide mb-1 leading-tight'>
                        {assignment.organisation_name}
                      </div>
                      <Link
                        to='/roles'
                        className='text-lnds-color font-medium uppercase tracking-wide hover:text-lnds-dark-blue underline hover:no-underline transition-colors duration-200 cursor-pointer'
                      >
                        {role.name.split("_").join(" ")}
                      </Link>
                    </div>
                  ))}
                </div>
              </div>
            ))}
        </div>
      );
    } else {
      return (
        <div className='flex flex-col justify-center text-xs text-lnds-color'>
          {(user?.iam_roles || []).map((role: string) => (
            <Link
              to='/roles'
              key={role}
              className='hover:text-lnds-dark-blue underline hover:no-underline transition-colors duration-200 cursor-pointer'
            >
              {role.split("_").join(" ")}
            </Link>
          ))}
        </div>
      );
    }
  };

  return (
    <Navbar
      /* @ts-expect-error: The expected type comes from property 'appName' which is declared here on type 'IntrinsicAttributes & NavbarProps' */
      appName={
        <div className='flex flex-col'>
          <div className='flex items-center gap-2'>
            <Link to='/' className='flex items-center space-x-1'>
              <span className='text-base font-semibold'>
                {import.meta.env.DEV ? "Dataset Metadata Capture (DEV)" : document.title}
              </span>
            </Link>
          </div>
          {user?.feature_options?.enable_multi_tenants && user?.current_organisation && (
            <span className='text-xs text-lnds-color font-light flex items-center mt-0.5 !normal-case'>
              <BuildingOfficeIcon className='h-2.5 w-2.5 mr-1 opacity-60' />
              {user.current_organisation.name}
            </span>
          )}
        </div>
      }
      onLeftMenuClick={
        path.includes("/datasets/") ? () => setSidebarOpen(!isSidebarOpen) : undefined
      }
      logoNode={<div />}
      mobileMenuItems={
        <div className='absolute w-full z-40 md:hidden section-lnds-color'>
          <div className='px-6 py-2 flex flex-col space-y-1 border-b border-t border-lnds-color'>
            <span id='user-name'>{user?.name}</span>
            {user?.feature_options.enable_multi_tenants && (
              <div className='mt-2 mb-1'>
                <OrganizationSwitcher user={user} />
              </div>
            )}
            {renderUserRoles()}
          </div>
          <div className='px-2 pt-2 pb-3 space-y-1 sm:px-3'>
            <Link
              to='/'
              className='hover:bg-lnds-dark-blue hover:text-white px-3 py-2 rounded-md flex items-center'
            >
              <HomeIcon className='h-6 w-6' />
              <span className='ml-1'>Home</span>
            </Link>
            {showDatasetActions && (
              <>
                <Link
                  to='/datasets/bulk-upload'
                  className='hover:bg-lnds-dark-blue hover:text-white px-3 py-2 rounded-md flex items-center'
                >
                  <ArrowUpTrayIcon className='h-6 w-6' />
                  <span className='ml-1'>Bulk Import Datasets</span>
                </Link>
                <Link
                  to='/datasetform'
                  className='hover:bg-lnds-dark-blue hover:text-white px-3 py-2 rounded-md flex items-center'
                >
                  <PlusCircleIcon className='h-6 w-6' />
                  <span className='ml-1'>Add Dataset</span>
                </Link>
              </>
            )}
            <DarkModeLink isDarkMode={isDarkMode} onChangeDarkMode={onChangeDarkMode} />
            {user && user.can_edit_form_fields && (
              <>
                <Link
                  to='/keywords'
                  className='hover:bg-lnds-dark-blue hover:text-white px-3 py-2 rounded-md flex items-center'
                >
                  <TagIcon className='h-6 w-6' />
                  <span className='ml-1'>Keywords</span>
                </Link>
                <Link
                  to='/applicable_legislations'
                  className='hover:bg-lnds-dark-blue hover:text-white px-3 py-2 rounded-md flex items-center'
                >
                  <ScaleIcon className='h-6 w-6' />
                  <span className='ml-1'>Applicable Legislations</span>
                </Link>
                <Link
                  to='/data_services'
                  className='hover:bg-lnds-dark-blue hover:text-white px-3 py-2 rounded-md flex items-center'
                >
                  <ServerIcon className='h-6 w-6' />
                  <span className='ml-1'>Data Services</span>
                </Link>
                {showAuthenticSourcesLink && (
                  <Link
                    to='/authentic_sources'
                    className='hover:bg-lnds-dark-blue hover:text-white px-3 py-2 rounded-md flex items-center'
                  >
                    <ShieldCheckIcon className='h-6 w-6' />
                    <span className='ml-1'>Authentic Sources</span>
                  </Link>
                )}
                {showOrganisationsLink && (
                  <Link
                    to='/organisations'
                    className='hover:bg-lnds-dark-blue hover:text-white px-3 py-2 rounded-md flex items-center'
                  >
                    <BuildingOfficeIcon className='h-6 w-6' />
                    <span className='ml-1'>Orgs & Contacts</span>
                  </Link>
                )}
                {showUsersLink && (
                  <Link
                    to='/users'
                    className='hover:bg-lnds-dark-blue hover:text-white px-3 py-2 rounded-md flex items-center'
                  >
                    <UsersIcon className='h-6 w-6' />
                    <span className='ml-1'>Users</span>
                  </Link>
                )}
                {showFrontOfficeLink && (
                  <a
                    href='/admin/front-office-directory'
                    className='block px-4 py-2 hover:bg-lnds-dark-blue hover:text-white flex items-center space-x-1'
                  >
                    <CloudIcon className='h-6 w-6' />
                    <span className='ml-1'>Front Office Directory</span>
                  </a>
                )}
              </>
            )}
            {user && (
              <a
                href={logoutUrl()}
                className='hover:bg-lnds-dark-blue hover:text-white px-3 py-2 rounded-md flex items-center'
              >
                <ArrowRightOnRectangleIcon className='h-6 w-6' />
                <span className='ml-1'>Logout</span>
              </a>
            )}
          </div>
        </div>
      }
    >
      <div className='flex flex-wrap items-center space-x-4'>
        <OrganizationSwitcher user={user} />
        {showDatasetActions && (
          <Button
            label='Add dataset'
            to='/datasetform'
            Icon={PlusCircleIcon}
            className='mr-4'
            Link={Link}
          />
        )}
        <Link to='/' className='flex items-center space-x-1'>
          <Tooltip text='Home' preferredPosition='bottom'>
            <HomeIcon className={`h-6 w-6 icon-lnds-color`} />
          </Tooltip>
        </Link>
        {showDatasetActions && (
          <Link to='/datasets/bulk-upload' className='flex items-center space-x-1'>
            <Tooltip text='Bulk Import Datasets' preferredPosition='bottom'>
              <ArrowUpTrayIcon className='h-6 w-6 icon-lnds-color' />
            </Tooltip>
          </Link>
        )}
        {user?.can_edit_form_fields && (
          <Tooltip text='Vocabularies and Entities' preferredPosition='bottom'>
            <NavigationDropdown
              NavButton={<RectangleGroupIcon className='cursor-pointer h-6 w-6 icon-lnds-color' />}
            >
              <>
                <Link
                  to='/keywords'
                  className='block px-4 py-2 hover:bg-lnds-dark-blue hover:text-white flex items-center space-x-1'
                >
                  <TagIcon className='h-5 w-5 flex-shrink-0' />
                  <span>Keywords</span>
                </Link>
                <Link
                  to='/applicable_legislations'
                  className='block px-4 py-2 hover:bg-lnds-dark-blue hover:text-white flex items-center space-x-1'
                >
                  <ScaleIcon className='h-5 w-5 flex-shrink-0' />
                  <span>Applicable Legislations</span>
                </Link>
                <Link
                  to='/data_services'
                  className='block px-4 py-2 hover:bg-lnds-dark-blue hover:text-white flex items-center space-x-1'
                >
                  <ServerIcon className='h-5 w-5 flex-shrink-0' />
                  <span>Data Services</span>
                </Link>
                {showAuthenticSourcesLink && (
                  <Link
                    to='/authentic_sources'
                    className='block px-4 py-2 hover:bg-lnds-dark-blue hover:text-white flex items-center space-x-1'
                  >
                    <ShieldCheckIcon className='h-5 w-5 flex-shrink-0' />
                    <span>Authentic Sources</span>
                  </Link>
                )}
                {showOrganisationsLink && (
                  <Link
                    to='/organisations'
                    className='block px-4 py-2 hover:bg-lnds-dark-blue hover:text-white flex items-center space-x-1'
                  >
                    <BuildingOfficeIcon className='h-5 w-5 flex-shrink-0' />
                    <span>Orgs & Contacts</span>
                  </Link>
                )}
              </>
            </NavigationDropdown>
          </Tooltip>
        )}
        {showUsersLink && !showFrontOfficeLink && (
          <Link to='/users' className='flex items-center space-x-1'>
            <Tooltip text='Users' preferredPosition='bottom'>
              <UsersIcon className={`h-6 w-6 icon-lnds-color`} />
            </Tooltip>
          </Link>
        )}
        {showUsersLink && showFrontOfficeLink && (
          <Tooltip text='Admin Settings' preferredPosition='bottom'>
            <NavigationDropdown
              NavButton={<Cog6ToothIcon className='cursor-pointer h-6 w-6 icon-lnds-color' />}
            >
              <>
                <Link
                  to='/users'
                  className='block px-4 py-2 hover:bg-lnds-dark-blue hover:text-white flex items-center space-x-1'
                >
                  <UsersIcon className='h-5 w-5 flex-shrink-0' />
                  <span>Users</span>
                </Link>
                <Link
                  to='/admin/front-office-directory'
                  className='block px-4 py-2 hover:bg-lnds-dark-blue hover:text-white flex items-center space-x-1'
                >
                  <CloudIcon className='h-5 w-5 flex-shrink-0' />
                  <span>Front Office Directory</span>
                </Link>
              </>
            </NavigationDropdown>
          </Tooltip>
        )}
        {user && (
          <div className='relative' ref={dropdownRef}>
            <button
              id='user-menu'
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className={`flex items-center justify-center h-7 w-7 ${
                dropdownOpen
                  ? "bg-lnds-dark-blue dark:bg-white dark:text-lnds-blue"
                  : "bg-lnds-gray dark:bg-gray-400 hover:bg-lnds-dark-blue dark:hover:bg-white dark:hover:text-lnds-blue"
              } rounded-full text-white cursor-pointer hover:bg-lnds-dark-blue`}
            >
              <InitialsAvatar name={user.name} showTooltip={false} />
            </button>
            {dropdownOpen && (
              <div className='absolute right-0 mt-2 py-2 w-64 section-lnds-color rounded border border-1 border-lnds-color z-10'>
                <div className='block px-4 py-2 flex flex-col space-y-1'>
                  <span id='user-name'>{user.name}</span>
                  {renderUserRoles()}
                </div>
                <hr className='my-1 border-lnds-color' />
                <DarkModeLink isDarkMode={isDarkMode} onChangeDarkMode={onChangeDarkMode} />
                <a
                  href={logoutUrl()}
                  className='px-4 py-2 hover:bg-lnds-dark-blue hover:text-white flex items-center space-x-1'
                >
                  <ArrowRightOnRectangleIcon className='h-5 w-5' />
                  <span>Logout</span>
                </a>
              </div>
            )}
          </div>
        )}
      </div>
    </Navbar>
  );
}
