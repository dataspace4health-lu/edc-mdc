import React from "react";
import { UsersIcon, KeyIcon } from "@heroicons/react/24/solid";

interface Role {
  name: string;
  permissions: string[];
}

interface RoleItemProps {
  role: Role;
}

const formatPermission = (permission: string): string => {
  const permissionMap: { [key: string]: string } = {
    "datasets:read": "View all datasets",
    "datasets:edit:draft:my": "Edit my draft datasets",
    "datasets:edit:draft:organisation": "Edit organisation draft datasets",
    "datasets:edit:draft:group": "Edit group draft datasets",
    "datasets:edit:draft": "Edit all draft datasets",
    "datasets:delete:draft:my": "Delete my draft datasets",
    "datasets:delete:draft:organisation": "Delete organisation draft datasets",
    "datasets:delete:draft": "Delete all draft datasets",
    "datasets:read:all-after-complete": "View all datasets after COMPLETED status",
    "datasets:read:all-after-draft": "View all datasets after DRAFT status (system-wide)",
    "datasets:read:all-after-draft:organisation":
      "View all datasets after DRAFT status (organisation-wide)",
    "datasets:read:completed": "View completed datasets",
    "datasets:read:validated": "View validated datasets",
    "datasets:read:approved": "View approved datasets",
    "datasets:read:published": "View published datasets",
    "datasets:status-change:complete:my": "Complete my datasets",
    "datasets:status-change:complete:group": "Complete group datasets",
    "datasets:status-change:complete:organisation": "Complete organisation datasets",
    "datasets:status-change:complete": "Complete all datasets",
    "datasets:status-change:validate:group": "Validate group datasets",
    "datasets:status-change:validate": "Validate all datasets",
    "datasets:status-change:draft:group": "Return group datasets to draft",
    "datasets:status-change:draft": "Return datasets to draft",
    "datasets:status-change:approve": "Approve datasets",
    "datasets:status-change:publish": "Publish datasets",
    "datasets:status-change:internal-only": "Set datasets as internal only",
    "datasets:status-change:deprecate": "Deprecate datasets",
    "authentic-source:assign": "Assign authentic source labels to datasets",

    "comments:delete": "Delete all comments",

    "form-fields:edit": "Edit form fields",
    "form-fields:edit:my": "Edit my form fields",
    "form-fields:edit:organisation": "Edit organisation form fields",

    "contacts:edit": "Edit contacts",
    "contacts:edit:organisation": "Edit organisation contacts",
    "organisations:edit": "Edit all organisations",
    "organisations:edit:organisation": "Edit only my organisation",

    "catalogue:generate-rdf": "Generate RDF catalogue",
    "catalogue:upload-rdf:s3": "Upload RDF to S3",

    "roles:manage": "Manage all roles",
    "roles:manage:organisation": "Manage organisation roles",
  };

  return (
    permissionMap[permission] ||
    permission.replace(/[_:]/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())
  );
};

const formatRoleName = (name: string): string => {
  return name.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
};

const RoleItem: React.FC<RoleItemProps> = ({ role }) => {
  return (
    <div className='border-b border-lnds-color last:border-b-0 p-4 transition-colors'>
      <div className='flex items-start gap-4'>
        <div className='flex-shrink-0 mt-1'>
          <UsersIcon className='h-6 w-6 text-lnds-purple' />
        </div>

        <div className='flex-grow'>
          <div className='flex items-center gap-2 mb-3'>
            <h3 className='text-lg font-semibold heading-lnds-color'>
              {formatRoleName(role.name)}
            </h3>
            <span className='text-sm bg-lnds-purple text-white px-2 py-0.5 rounded-full'>
              {role.permissions.length} permissions
            </span>
          </div>

          <div className='space-y-2'>
            <div className='flex items-center gap-2 mb-2'>
              <KeyIcon className='h-4 w-4 text-lnds-color' />
              <span className='text-sm font-medium text-lnds-color'>Permissions:</span>
            </div>

            <div className='grid grid-cols-1 md:grid-cols-2 gap-2 ml-6'>
              {role.permissions.map((permission) => (
                <div key={permission} className='flex items-center gap-2'>
                  <div className='w-2 h-2 bg-lnds-purple rounded-full flex-shrink-0'></div>
                  <span className='text-sm text-lnds-color'>{formatPermission(permission)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RoleItem;
