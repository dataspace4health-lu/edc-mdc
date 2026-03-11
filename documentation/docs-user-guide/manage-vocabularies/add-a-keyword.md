---
slug: /add-a-keyword
sidebar_label: "Add keywords"
sidebar_position: 2
description: "Enable consistent dataset tagging by adding controlled keywords."
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Add keywords

In this guide

> [Overview](#overview)  
> [Add a keyword](#add-a-keyword)  
> [Manage existing keywords](#manage-existing-keywords)

## Overview

**Keywords** are controlled terms or phrases that describe the content or subject matter of datasets. By adding keywords to the system, you provide consistent terminology that Editors can use to tag datasets when they create or edit them. This tagging helps Data Users discover relevant datasets through keyword search and filtering.

**How keywords work:**

- Catalogue Managers (or equivalent roles) create keywords that Editors can use to tag datasets
- Keywords can be made globally available or restricted to specific organisations, if your setup applies
- Editors tag datasets with existing keywords when they [add or edit datasets](/user-guide/add-a-dataset)
- Editors can also create new keywords through the [dataset bulk upload](/user-guide/bulk-upload-datasets) feature 


:::info Manage keywords

This guide is for **Catalogue Managers** (or equivalent roles) who want to manage or add new keywords to the system. If you're an **Editor** who wants to tag datasets with existing keywords, see [Add or edit a dataset](/user-guide/add-a-dataset).

:::

## Add a keyword

Add keywords to the system so Editors can use them to tag datasets. You must be a Catalogue Manager or have the permission to **manage controlled vocabularies**. Check your [permissions](/user-guide/check-your-permissions).

To add keywords that can be assocated with datasets:

1. Select the entities icon (<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" style={{display:"inline",verticalAlign:"middle",width:"1em",height:"1em"}}><path fillRule="evenodd" d="M4.25 2A2.25 2.25 0 0 0 2 4.25v2.5A2.25 2.25 0 0 0 4.25 9h2.5A2.25 2.25 0 0 0 9 6.75v-2.5A2.25 2.25 0 0 0 6.75 2h-2.5Zm0 9A2.25 2.25 0 0 0 2 13.25v2.5A2.25 2.25 0 0 0 4.25 18h2.5A2.25 2.25 0 0 0 9 15.75v-2.5A2.25 2.25 0 0 0 6.75 11h-2.5Zm9-9A2.25 2.25 0 0 0 11 4.25v2.5A2.25 2.25 0 0 0 13.25 9h2.5A2.25 2.25 0 0 0 18 6.75v-2.5A2.25 2.25 0 0 0 15.75 2h-2.5Zm0 9A2.25 2.25 0 0 0 11 13.25v2.5A2.25 2.25 0 0 0 13.25 18h2.5A2.25 2.25 0 0 0 18 15.75v-2.5A2.25 2.25 0 0 0 15.75 11h-2.5Z" clipRule="evenodd" /></svg>) beside your profile icon. 

2. Select **Keywords**. The list of existing keywords appears.

   <img src={useBaseUrl('/manage-vocabularies/add-keywords.png')} alt="Screenshot of the Keywords option" width="600" />

3. Select **Expand Form** and fill out the keyword form:
   - **Label**: The name of the keyword
   - **Organisation**: Select the organisations that can use this keyword, or leave blank to make it globally available
   
4. Select **Create Keyword**. After the keyword is create, it appear on both the Key word list and in the dataset editor for tagging datasets.

   The new keyword now appears in the keywords list. In this example, we added *connection speed*:
   <img src={useBaseUrl('/manage-vocabularies/example-list-of-added-keywords.png')} alt="Screenshot showing the list of added keywords" width="700" />

   Editors can now select the new keyword when creating or editing datasets. In this example, we see *connection speed*.
   <img src={useBaseUrl('/manage-vocabularies/example-keyword-in-dataset-editor.png')} alt="Screenshot showing keyword options in the dataset editor" width="700" />

:::tip Bulk upload keywords

Editors can also add new keywords using the [bulk upload](/user-guide/bulk-upload-datasets) feature when adding datasets. New keywords are automatically created if they don't already exist in the system.

:::

## Manage existing keywords

After you create keywords, you can edit or delete them as needed.

1. In the keywords list, search and locate the keyword you want to manage. Use the filters to help find specific keywords.

2. Select the edit icon (<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style={{display:"inline",verticalAlign:"middle",width:"1em",height:"1em"}}><path d="M21.731 2.269a2.625 2.625 0 0 0-3.712 0l-1.157 1.157 3.712 3.712 1.157-1.157a2.625 2.625 0 0 0 0-3.712ZM19.513 8.199l-3.712-3.712-8.4 8.4a5.25 5.25 0 0 0-1.32 2.214l-.8 2.685a.75.75 0 0 0 .933.933l2.685-.8a5.25 5.25 0 0 0 2.214-1.32l8.4-8.4Z" /><path d="M5.25 5.25a3 3 0 0 0-3 3v10.5a3 3 0 0 0 3 3h10.5a3 3 0 0 0 3-3V13.5a.75.75 0 0 0-1.5 0v5.25a1.5 1.5 0 0 1-1.5 1.5H5.25a1.5 1.5 0 0 1-1.5-1.5V8.25a1.5 1.5 0 0 1 1.5-1.5h5.25a.75.75 0 0 0 0-1.5H5.25Z" /></svg>) next to the keyword.

3. Choose your action:
   - **Edit**: Update the keyword details.
   - **Delete**: Permanently remove the keyword from the system. You can only delete keywords that are not associated with any datasets.

:::tip Well done

After you add keywords, Editors can use them to tag datasets when they [add or edit datasets](/user-guide/add-a-dataset). This improves dataset discoverability across your data catalogue.
