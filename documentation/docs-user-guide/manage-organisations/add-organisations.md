---
slug: /add-organisations
sidebar_label: "Add organisations"
sidebar_position: 1
description: "Attribute datasets accurately by adding organisations to the system."
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Add organisations

In this guide

> [Overview](#overview)  
> [Add an organisation](#add-an-organisation)  
> [Manage existing organisations](#manage-existing-organisations)


## Overview

Add **organisations** to the system to properly attribute dataset ownership and provide accurate contact information. These organisations can serve as publishers or creators of datasets and their names appear in published dataset metadata, ensuring clear attribution and accountability.

**How organisations work:** Once you add organisations, Editors can reference them when they [add or edit datasets](/user-guide/add-a-dataset).
- **As publisher**: The organisation responsible for making the dataset available
- **As creator**: The organisation that originally created or compiled the dataset
- **As contact point:** You can add contacts to organisations and Editors can set them as contact points for datasets. See: [Add contacts](/user-guide/add-contacts)

## Add an organisation

To add organisations that can be referenced in datasets, you must be a Catalogue Manager or have the permission to **manage organisations**. Check your [permissions](/user-guide/check-your-permissions).

1. Select the entities icon (<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" style={{display:"inline",verticalAlign:"middle",width:"1em",height:"1em"}}><path fillRule="evenodd" d="M4.25 2A2.25 2.25 0 0 0 2 4.25v2.5A2.25 2.25 0 0 0 4.25 9h2.5A2.25 2.25 0 0 0 9 6.75v-2.5A2.25 2.25 0 0 0 6.75 2h-2.5Zm0 9A2.25 2.25 0 0 0 2 13.25v2.5A2.25 2.25 0 0 0 4.25 18h2.5A2.25 2.25 0 0 0 9 15.75v-2.5A2.25 2.25 0 0 0 6.75 11h-2.5Zm9-9A2.25 2.25 0 0 0 11 4.25v2.5A2.25 2.25 0 0 0 13.25 9h2.5A2.25 2.25 0 0 0 18 6.75v-2.5A2.25 2.25 0 0 0 15.75 2h-2.5Zm0 9A2.25 2.25 0 0 0 11 13.25v2.5A2.25 2.25 0 0 0 13.25 18h2.5A2.25 2.25 0 0 0 18 15.75v-2.5A2.25 2.25 0 0 0 15.75 11h-2.5Z" clipRule="evenodd" /></svg>) beside your profile icon. 

2. Select **Org & Contacts**. The list of existing organisations appears.

3. Select **Expand Form** and fill out the organisation form:
   - **Name**: Enter the official name of the organisation. This name will appear in dataset metadata.
   - **Type**: Select the organisation type (e.g., National Authority, Private Company, Academic Institution, etc.)
   - **Email**: Enter the organisation's contact email. Editors can select this email as the contact point for datasets when no specific contact person is available.
   
4. Select **Create Organisation**. The new organisation appears in the list below.

:::tip Add contacts

After creating an organisation, you can [add contacts to it](/user-guide/add-contacts) to provide specific contact persons for datasets.

:::


## Manage existing organisations

After you create organisations, you can edit or delete them as needed.

1. In the organisations list, search for the organisation you want to manage.

2. Select the edit icon (✏️) next to the organisation.

3. Choose your action:
   - **Edit:** Make changes to the organisation details. 
   - **Deprecate:** Deprecate organisations that are no longer active, but are still referenced by datasets. Deprecated organisations remain in the system for historical reference but cannot be selected for new datasets. 
   - **Delete:** Permanently remove the organisation from the system. You can only delete organisations that are not referenced by any datasets.

:::tip Well done

After you add an organisation, Editors can reference it when they [add or edit datasets](/user-guide/add-a-dataset). The organisation can be selected as the publisher or creator, ensuring accurate attribution in your data catalogue.

:::
