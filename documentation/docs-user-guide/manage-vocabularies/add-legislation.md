---
slug: /add-legislation
sidebar_label: "Add legislations"
sidebar_position: 3
description: "Provide legal context by adding applicable legislations to datasets."
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Add applicable legislations

In this guide

> [Overview](#overview)  
> [Add a legislation](#add-a-legislation)  
> [Manage existing legislations](#manage-existing-legislations)

## Overview

**Legislations** are legal frameworks or regulations that govern the collection, storage, and sharing of data. By adding legislations to the system, you enable Editors to associate datasets with relevant legal requirements—ensuring compliance and providing clear legal context for Data Users.

**For example:** A dataset for *Healthcare Records* may need to comply with the General Data Protection Regulation (GDPR) and national health data protection laws. By adding these legislations to the system, Editors can associate them with datasets to show legal compliance when published.

**How legislations work:**

- Catalogue Managers (or equivalent roles) add legislation entries from official legal databases to the system. The platform integrates with [Legilux<sup>↗</sup>](https://legilux.public.lu/) for Luxembourg legislation and [EUR-Lex<sup>↗</sup>](https://eur-lex.europa.eu/) for European Union legislation
- Editors associate legislations with datasets when [adding or editing datasets](/user-guide/add-a-dataset)
- Legislation details appear in published dataset metadata

## Add a legislation

Add legislations to the system to enable Editors to associate them with datasets. You must be a Catalogue Manager or have the permission to **manage controlled vocabularies**. Check your [permissions](/user-guide/check-your-permissions).

To add a legislation that can be applied to datasets:

1. Select the entities icon (<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" style={{display:"inline",verticalAlign:"middle",width:"1em",height:"1em"}}><path fillRule="evenodd" d="M4.25 2A2.25 2.25 0 0 0 2 4.25v2.5A2.25 2.25 0 0 0 4.25 9h2.5A2.25 2.25 0 0 0 9 6.75v-2.5A2.25 2.25 0 0 0 6.75 2h-2.5Zm0 9A2.25 2.25 0 0 0 2 13.25v2.5A2.25 2.25 0 0 0 4.25 18h2.5A2.25 2.25 0 0 0 9 15.75v-2.5A2.25 2.25 0 0 0 6.75 11h-2.5Zm9-9A2.25 2.25 0 0 0 11 4.25v2.5A2.25 2.25 0 0 0 13.25 9h2.5A2.25 2.25 0 0 0 18 6.75v-2.5A2.25 2.25 0 0 0 15.75 2h-2.5Zm0 9A2.25 2.25 0 0 0 11 13.25v2.5A2.25 2.25 0 0 0 13.25 18h2.5A2.25 2.25 0 0 0 18 15.75v-2.5A2.25 2.25 0 0 0 15.75 11h-2.5Z" clipRule="evenodd" /></svg>) beside your profile icon.  

2. Select **Applicable Legislations**. The list of existing legislation entries appears.

   <img src={useBaseUrl('/manage-vocabularies/add-legislations.png')} alt="Screenshot of the Applicable legislations option" width="600" />

3. Select **Expand Form**, then select the legislation body (Legilux or EUR-Lex).

4. Fill out the legislation form: 
   - **Search**: Search for the legislation in the database by label, description, or link
   - **Label**: The name of the legislation
   - **Description**: The description of the legislation
   - **Link**: Direct link to the legislation in the official database
   - **Organisation**: Select the organisations that can use this legislation, or leave blank to make it globally available

5. Select **Create Applicable Legislation**. The new legislation entry appears in the list.

   The legislation now appears in your vocabulary list:

   <img src={useBaseUrl('/manage-vocabularies/example-list-of-added-legislations.png')} alt="Screenshot showing the list of added legislations" width="750" />

   Editors can now select this legislation when creating or editing datasets:

   <img src={useBaseUrl('/manage-vocabularies/example-legislation-in-dataset-editor.png')} alt="Screenshot showing legislation options in the dataset editor" width="750" />

## Manage existing legislations

After you create legislation entries, you can edit or delete them as needed.

1. In the legislation list, search and locate the legislation you want to manage. Use the filters to help find specific entries.

2. Select the edit icon (<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style={{display:"inline",verticalAlign:"middle",width:"1em",height:"1em"}}><path d="M21.731 2.269a2.625 2.625 0 0 0-3.712 0l-1.157 1.157 3.712 3.712 1.157-1.157a2.625 2.625 0 0 0 0-3.712ZM19.513 8.199l-3.712-3.712-8.4 8.4a5.25 5.25 0 0 0-1.32 2.214l-.8 2.685a.75.75 0 0 0 .933.933l2.685-.8a5.25 5.25 0 0 0 2.214-1.32l8.4-8.4Z" /><path d="M5.25 5.25a3 3 0 0 0-3 3v10.5a3 3 0 0 0 3 3h10.5a3 3 0 0 0 3-3V13.5a.75.75 0 0 0-1.5 0v5.25a1.5 1.5 0 0 1-1.5 1.5H5.25a1.5 1.5 0 0 1-1.5-1.5V8.25a1.5 1.5 0 0 1 1.5-1.5h5.25a.75.75 0 0 0 0-1.5H5.25Z" /></svg>) next to the legislation entry.

3. Choose your action:
   - **Edit**: Update the legislation details.
   - **Delete**: Permanently remove the legislation from the system. You can only delete legislations that are not associated with any datasets.

:::tip Well done

After you add legislations, Editors can associate them with datasets when they [add or edit datasets](/user-guide/add-a-dataset). This supports regulatory compliance and provides legal context across your data catalogue.

:::
