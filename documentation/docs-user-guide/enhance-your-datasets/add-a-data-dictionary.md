---
slug: /add-a-data-dictionary
sidebar_label: "Add data dictionaries"
description: "Improve dataset clarity by documenting field meanings, data types, and constraints."
sidebar_position: 3
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Add data dictionaries

In this guide

> [Overview](#overview)  
> [Add a data dictionary](#add-a-data-dictionary)  
> [Manage existing data dictionaries](#manage-existing-data-dictionaries)

## Overview

**Data dictionaries** describe the structure and meaning of the fields (or columns) within your dataset. By documenting this information, you help users understand the data they are working with, reducing the risk of misinterpretation or misuse. Data dictionaries typically include details such as field names, their purpose, data types, allowed values, and any constraints.

**For example:** A dataset for *Patient Information* may include fields like *Test Results* whose values are limited to `Positive`, `Negative`, or `Inconclusive`. Another field could be *Patient ID* which is defined as a unique allnumeric identifier. 

**How data dictionaries work:**

- You can add multiple entries to a data dictionary to describe each field in the dataset.
- The same field can have multiple attributes. For example a field can have both a data type and allowed values.
- Dictionary details appear in published dataset metadata. 

## Add a data dictionary

Add data dictionaries to document the structure and meaning of dataset fields. You must be an Editor or have the permission to **edit datasets**, check your [permissions](/user-guide/check-your-permissions).

To add a data dictionary to a dataset:

1. Ensure the dataset is in Draft, or [revert it to draft](/user-guide/revert-a-dataset-to-draft) if needed. 

2. Open the dataset in the **Draft** tab using one of the following methods:

   - Select the options icon ( **⋮** ) on the dataset and select **Edit** then select **Data Dictionary** in the left panel. 
   - Select **View** on the dataset, go to the **Data Dictionary** tab, and select **Manage dictionaries**

    <figure>
      <img src={useBaseUrl('/enhance-datasets/manage-dictionaries.png')} alt="Screenshot of the manage dictionary button" width="700" />
      <figcaption> </figcaption>
    </figure>

3. Add your data dictionary entries using one of the following methods:

   <figure>
      <img src={useBaseUrl('/enhance-datasets/expand-or-upload.png')} alt="Screenshot of the add dictionary entry section or upload option" width="700" />
      <figcaption> </figcaption>
    </figure>

   - **Add entries manually:** Select **Expand Form**, fill out the form. For guidance on filling out the form, see the definition of properties in the [https://mindig_lu.gitlab.io/DCAT-AP-LU/#Dataset].
   - **Upload a file:** Select **Download Template**, complete the template, and select **Bulk Upload** to upload the file

4. Review the entries in the table. To delete an entry, select the trash icon (🗑️) under **Actions**.

   <figure>
      <img src={useBaseUrl('/enhance-datasets/view-dictionary.png')} alt="Screenshot of the data dictionary entries table" width="700" />
      <figcaption> </figcaption>
    </figure>
   
   
   :::tip Show or hide columns

   Select **Filter Columns** to customise which columns appear in the table.

   :::

## Manage existing data dictionaries

After you add data dictionary entries, you can edit or delete them as needed.

1. Open the dataset editor and select **Data Dictionary** in the left panel.

2. Locate the entry you want to manage in the table.

3. Choose your action:
   - **Edit**: Update the entry details by selecting it from the table
   - **Delete**: Select the trash icon (🗑️) to permanently remove the entry

:::tip Well done

After you add a data dictionary, Data Users can view the field definitions in the published dataset metadata. This improves data understanding and reduces misuse.

:::