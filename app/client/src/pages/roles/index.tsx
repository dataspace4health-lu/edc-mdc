import React, { useState } from "react";
import { Card } from "@lnds-lu/design-system";
import { UsersIcon } from "@heroicons/react/24/solid";
import { useLoaderData } from "react-router";
import EmptyScreen from "../../components/EmptyScreen";
import { SearchInput } from "@lnds-lu/design-system";
import RoleItem from "./RoleItem";
import { usePageTitle } from "../../hooks/usePageTitle";

interface Role {
  name: string;
  permissions: string[];
}

const RolesInformation: React.FC = () => {
  usePageTitle("Roles");
  const roles = (useLoaderData() as Awaited<Role[]>) || [];
  const [searchTerm, setSearchTerm] = useState("");

  const filteredRoles = roles.filter(
    (role: Role) =>
      role.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      role.permissions.some((permission) =>
        permission.toLowerCase().includes(searchTerm.toLowerCase()),
      ),
  );

  const sortedRoles = [...filteredRoles];
  sortedRoles.sort((a, b) => a.name.localeCompare(b.name));

  return (
    <div className='my-6 mx-6 max-w-2xl lg:max-w-6xl md:mx-auto'>
      <Card className='flex flex-col h-full px-0'>
        <div className='p-4 flex justify-between items-center border-b border-lnds-color'>
          <div className='flex items-center gap-2'>
            <UsersIcon className='h-5 w-5 heading-lnds-color' />
            <h2 className='text-2xl font-semibold heading-lnds-color'>
              Roles Directory{" "}
              <span className='text-sm bg-lnds-purple text-white px-2 py-0.5 rounded-full ml-2'>
                {filteredRoles.length}
              </span>
            </h2>
          </div>
        </div>

        <div className='p-4 border-b border-lnds-color'>
          <SearchInput
            className='md:w-full'
            withoutBtn={true}
            placeholder='Search roles and permissions...'
            query={searchTerm}
            onSearch={setSearchTerm}
            size='small'
          />
        </div>

        <div className='flex-grow overflow-y-auto' style={{ height: "calc(60vh)" }}>
          {filteredRoles.length > 0 ? (
            <div>
              {sortedRoles.map((role) => (
                <RoleItem key={role.name} role={role} />
              ))}
            </div>
          ) : (
            <div className='p-4'>
              <EmptyScreen message='No roles found' Icon={UsersIcon} />
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default RolesInformation;
