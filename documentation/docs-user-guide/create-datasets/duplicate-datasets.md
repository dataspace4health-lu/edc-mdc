---
slug: /duplicate-datasets
sidebar_label: "Duplicate datasets"
sidebar_position: 2
description: "Templatise your datasets by creating independent copies with all metadata."
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Duplicate datasets

In this guide

> [Overview](#overview)  
> [Duplicate a dataset](#duplicate-a-dataset)  
> [What gets duplicated?](#what-gets-duplicated)

## Overview

**Duplicate datasets** to quickly create an independent copy of an existing dataset with all its metadata. Duplication is useful for creating templates or when you need to make similar datasets with minor variations. By duplicating, you save time by not having to re-enter all metadata from the start.

**How duplication works:**

- You can duplicate datasets at any stage in their lifecycle, from any status tab (Draft, Completed, Approved, Published, Internal Only, or Deprecated).
- No relationship exists between the original and the duplicate dataset, unless you manually link them
- A new unique identifier is automatically generated for the duplicate
- All metadata fields except for authentic source labels are copied to the duplicate. Read more: [What gets duplicated?](#what-gets-duplicated)

:::tip Duplication vs. versioning

- Use **duplication** to create independent datasets with no connection to the original—ideal for templates or similar datasets. 
- Use [**versioning**](/user-guide/create-dataset-versions) to create tracked updates of published datasets where changes are linked to the original.

:::

## Duplicate a dataset

To duplicate a dataset, you must be an Editor or have the permission to **edit datasets**. Check your [permissions](/user-guide/check-your-permissions). 

1. Browse or search for the dataset you want to duplicate anywhere in the datasets panel.

2. Select the options icon ( **⋮** ) on the dataset, and then select **Duplicate**. The system creates a copy of the dataset and automatically opens the dataset editor with the new dataset.

      <img src={useBaseUrl('/manage-datasets/duplicate-datasets.png')} alt="Screenshot showing the duplicated dataset opened in the dataset editor" width="750" />

3. Review and modify the duplicated dataset details:
   - **Title:** Prefixed with "**Clone -**" to distinguish it from the original
   - **All metadata fields:** distributions and data dictionary entries <br/> <br/>     
      <img src={useBaseUrl('/manage-datasets/duplicate-dataset-with-clone-title.png')} alt="Screenshot showing the duplicated dataset in the dataset editor" width="750" />


4. Update the fields as needed, then select **Preview & Save** to save the dataset as a draft. From here, you can continue editing, submit the dataset for approval.
## What gets duplicated?

The following properties are included when duplicating a dataset:

- **All metadata fields:** Title with "Clone -" prefix, description, temporal coverage, etc.
- **Distributions:** Access URLs, formats, and all distribution metadata
- **Data dictionary entries:** Field names, descriptions, and data types
- **Dataset relations:** Links to other datasets or external resources
- **Qualified attributions:** Role assignments for organisations
- **All other DCAT-AP-LU metadata properties**

The following properties are **not** included when duplicating a dataset:
- **Version relationships:** The duplicate is not linked to the original as a version
- **Authentic source labels:** Must be manually reassigned in data dictionaries
- **Activity logs:** The duplicate starts with a fresh activity log
- **Comments:** Comments from the original dataset are not copied

:::tip Remember

Duplicated datasets are **completely independent** from the original. If you want to create a tracked version of an existing published dataset, consider [**creating a new version**](/user-guide/create-dataset-versions) of the dataset instead.

:::

