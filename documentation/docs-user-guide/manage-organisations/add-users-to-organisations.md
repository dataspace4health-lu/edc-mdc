---
slug: /add-users-to-organisations
sidebar_label: "Add users to organisations"
sidebar_position: 3
description: "Assign users to organisations and manage their roles within each organisation."
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Add users to organisations

In this guide

> [Overview](#overview)  
> [Add a user to an organisation](#add-a-user-to-an-organisation)


## Overview

Assign **users** to organisations and define their roles to control access and permissions within your data catalogue. Each user can be assigned to one or more organisations with specific roles that determine what actions they can perform.

**How user assignments work:**

- You identify and assign users by their email address
- Each assignment links a user to an organisation with a specific role
- Users can have multiple roles within the same organisation or multiple organisation assignments
- User roles determine their permissions within that organisation

:::info User accounts vs. user assignments

Adding a user to an organisation is different from creating a user account. User accounts are created automatically when users sign in for the first time through the authentication system. This guide covers how to **assign existing users** to organisations and roles.

:::

## Add a user to an organisation

To assign users to organisations, you must be a Catalogue Manager or have the permission to **manage roles**. Check your [permissions](/user-guide/check-your-permissions).

1. Select the profile icon (<svg xmlns="http://www.w3.org/2000/svg" style={{display:"inline",verticalAlign:"middle",width:"1em",height:"1em"}} fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 0010 16a5.986 5.986 0 004.546-2.084A5 5 0 0010 11z" clipRule="evenodd"/></svg>) beside your name in the main menu.

2. Select **Users**. The list of existing users and the Assign Role form appears.

3. Select **Expand Form** to show the user assignment form.

4. Fill out the assignment form:

    <img src={useBaseUrl('/manage-orgs/add-users-to-orgs.png')} alt="User assignment form screenshot" width="700" />
    

   - **Email**: Enter the email address of the user you want to assign. The user must already exist in the system (they must have signed in at least once).
   - **Organisation**: Select the organisation to which you want to assign the user.
   - **Role**: Select the role you want to assign to the user within that organisation.

5. Select **Assign Role**. The user is now assigned to the organisation with the selected role.

6. To assign multiple roles to the same user, repeat steps 4-5 with different roles as needed.

:::info Available roles

The roles available for assignment depend on your system configuration. To learn more about roles in your organisation, contact your Inventory Coordinator or System Administrator. Also see: [Roles and Permissions](/user-guide/roles-and-permissions).

:::


:::tip What's next?

After you assign users to organisations with appropriate roles, they will have access to manage datasets and other resources within those organisations according to their role permissions. 

To view and manage existing user assignments, see: [Manage user assignments](/user-guide/manage-user-assignments).

:::
