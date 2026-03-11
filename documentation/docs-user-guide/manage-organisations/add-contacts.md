---
slug: /add-contacts
sidebar_label: "Add contacts to organisations"
sidebar_position: 2
description: "Facilitate communication by adding contacts to organisations."
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Add contacts to organisations

In this guide

> [Overview](#overview)  
> [Add a contact](#add-a-contact)  
> [Manage existing contacts](#manage-existing-contacts)

## Overview

Add **contacts** to organisations to provide specific persons who can be contacted about datasets. When Editors associate these contacts with datasets, Data Users know who to reach out to for questions or support.

**How contacts work:** 

- Contacts belong to specific organisations and can only be added to existing organisations. See: [Add organisations](/user-guide/add-organisations)
- Editors assign contacts as contact points for datasets associated with that organisation
- Contact names appear in published dataset metadata as links to their email addresses

## Add a contact

To add contacts to organisations, you must be a Catalogue Manager or have the permission to **manage organisations**. Check your [permissions](/user-guide/check-your-permissions).

1. Select the entities icon (<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" style={{display:"inline",verticalAlign:"middle",width:"1em",height:"1em"}}><path fillRule="evenodd" d="M4.25 2A2.25 2.25 0 0 0 2 4.25v2.5A2.25 2.25 0 0 0 4.25 9h2.5A2.25 2.25 0 0 0 9 6.75v-2.5A2.25 2.25 0 0 0 6.75 2h-2.5Zm0 9A2.25 2.25 0 0 0 2 13.25v2.5A2.25 2.25 0 0 0 4.25 18h2.5A2.25 2.25 0 0 0 9 15.75v-2.5A2.25 2.25 0 0 0 6.75 11h-2.5Zm9-9A2.25 2.25 0 0 0 11 4.25v2.5A2.25 2.25 0 0 0 13.25 9h2.5A2.25 2.25 0 0 0 18 6.75v-2.5A2.25 2.25 0 0 0 15.75 2h-2.5Zm0 9A2.25 2.25 0 0 0 11 13.25v2.5A2.25 2.25 0 0 0 13.25 18h2.5A2.25 2.25 0 0 0 18 15.75v-2.5A2.25 2.25 0 0 0 15.75 11h-2.5Z" clipRule="evenodd" /></svg>) beside your profile icon.

2. Select **Org & Contacts**. The list of existing organisations appears.

3. In the organisations list, locate the organisation you want to add contacts to.

4. Select the **Contacts** option for that organisation. The contact form appears.

5. Fill out the contact form:
   - **Name**: The contact person's full name
   - **Email**: The contact person's email address
   - **Role**: Their role or job title within the organisation. This does **not** assign any specific permissions within the system.

6. Select **Add**. The new contact appears in the organisation's contact list.

:::tip Multiple contacts

You can add multiple contacts to each organisation. As an Editor, you can select them as contact points when you [add or edit datasets](/user-guide/add-a-dataset).

:::


## Manage existing contacts

After you create contacts, you can edit or delete them as needed.

1. Open the **Org & Contacts** list. 

2. In the organisations list, select **Contacts** for the relevant organisation.

3. Locate the contact you want to manage in the contacts list and select the edit icon (✏️) next to the contact.

4. Choose your action:
   - **Edit:** Update the contact details.
   - **Delete:** Permanently remove the contact from the system. You can only delete contacts that are not referenced by any datasets.
   <!-- - **Deprecate:** Deprecate contacts that are no longer active, but are still referenced by datasets. Deprecated contacts remain in the system for historical reference but cannot be selected for new datasets. -->


:::tip Well done

After you add contacts to organisations, Editors can select them as contact points when they [add or edit datasets](/user-guide/add-a-dataset). This ensures Data Users have accurate contact information for each dataset in your data catalogue.

:::
