---
slug: /manage-user-assignments
sidebar_label: "Manage user assignments"
sidebar_position: 4
description: "View, update, and remove user role assignments within organisations."
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Manage user assignments

In this guide

> [Overview](#overview)  
> [View user assignments](#view-user-assignments)  
> [Add roles to existing users](#add-roles-to-existing-users)  
> [Remove a role from a user](#remove-a-role-from-a-user)  
> [Remove a user from an organisation](#remove-a-user-from-an-organisation)


## Overview

After [adding users to organisations](/user-guide/add-users-to-organisations), you can view and manage their role assignments. Users can have multiple roles within the same organisation, and you can add or remove roles as needed to match their changing responsibilities.

**What you can do:**

- View all user assignments across organisations
- Filter users by organisation, role, or assignment status
- Add additional roles to users who already have assignments
- Remove specific roles from users while maintaining their organisation membership
- Remove users completely from an organisation

## View user assignments

1. Select the profile icon (<svg xmlns="http://www.w3.org/2000/svg" style={{display:"inline",verticalAlign:"middle",width:"1em",height:"1em"}} fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 0010 16a5.986 5.986 0 004.546-2.084A5 5 0 0010 11z" clipRule="evenodd"/></svg>) beside your name in the main menu.

2. Select **Users**. The list displays all users with their current organisation and role assignments.

3. Use the filters on the left panel to narrow down the list:
   - **Organisation**: Show only users assigned to specific organisations
   - **Role**: Show only users with specific roles
   - **Only Unassigned**: Show only users who haven't been assigned to any organisation
   - **Deprecated Users**: Show only users marked as deprecated

4. Use the search bar to find users by name or email address.

:::tip Understanding the users list

Each user entry shows their name, email, and all their organisation-role combinations. Users with multiple roles in the same organisation will have multiple role badges displayed under that organisation.

:::


## Add roles to existing users

You can assign additional roles to users who already have assignments within an organisation. This is useful when a user's responsibilities expand or change.

1. Open the **Users** list by selecting the profile icon and then **Users**.

2. Select **Expand Form** to show the assignment form.

3. Fill out the form:
   - **Email**: Enter the email address of the user who already has an assignment
   - **Organisation**: Select the organisation where you want to add a role
   - **Role**: Select the additional role to assign

4. Select **Assign Role**. The new role is added to the user's existing assignments within that organisation.

:::info Adding roles to existing assignments

When you assign a role to a user who already has other roles in the same organisation, the system adds the new role without affecting their existing roles. Each role grants its own set of permissions, and the user will have access to all capabilities from all their assigned roles.

:::


## Remove a role from a user

Remove specific roles from users while keeping their organisation membership active. This is useful when a user's responsibilities change but they still need access to the organisation.

1. In the **Users** list, locate the user whose role you want to remove.

2. Find the organisation and role assignment you want to remove.

3. Select the delete icon (🗑️) next to the specific role.

4. Confirm the removal. The role is removed from the user's organisation membership.

:::warning Removing all roles

If you remove all roles from a user within an organisation, the user will no longer have access to that organisation's resources. The user will remain in the system but will be unassigned from that organisation.

:::


## Remove a user from an organisation

Remove a user completely from an organisation by deleting all their role assignments at once.

1. In the **Users** list, locate the user you want to remove from an organisation.

2. Select the delete icon (🗑️) next to the organisation name (not individual roles).

3. Confirm the removal. All role assignments for that user within the organisation are removed.

:::tip User account preservation

Removing a user from an organisation does not delete their user account. The user remains in the system and can be assigned to other organisations or re-assigned to the same organisation later if needed.

:::

