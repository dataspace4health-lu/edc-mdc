---
slug: /add-distributions
sidebar_label: "Add distributions"
description: "Specify how users can access datasets in different formats or methods."
sidebar_position: 2
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Add distributions

In this guide

> [Overview](#overview)  
> [Add a distribution](#add-a-distribution)  
> [Manage existing distributions](#manage-existing-distributions)

## Overview

**Distributions** are the different formats or methods for accessing a dataset. By adding distributions to your datasets, you provide Data Users with options for downloading, accessing, or interacting with the data. A distribution can include details such as the format, access URL, and technical specifications like file size or compression type. 

**For example:** A dataset may have multiple distributions such as a CSV file for download, an API endpoint for programmatic access, and a PDF report. 

**How distributions work:**

- You can add multiple distributions to a single dataset
- If a dataset is published in multiple formats, you must add a distribution for each format
- Distribution information appears in the published dataset metadata

## Add a distribution

To add distributions to a dataset, you must be an Editor or have the permission to **edit datasets**. Check your [permissions](/user-guide/check-your-permissions).

1. Ensure the dataset is in Draft, or [revert it to draft](/user-guide/revert-a-dataset-to-draft) if needed.

2. Open the dataset in the **Draft** tab using one of the following methods:
   - Select the options icon ( **⋮** ) on the dataset and select **Edit**
   - When [adding a new dataset](/user-guide/add-a-dataset), select **Add Distribution** at the bottom of the form
3. Select **Add Distribution** in the dataset form. The distribution form appears.

    <figure>
      <img src={useBaseUrl('/enhance-datasets/add-distribution.png')} alt="Screenshot of the add distribution button" width="700" />
      <figcaption></figcaption>
    </figure>



4. Fill out the distribution form. For guidance on filling out the form, see the definition of properties in the [DCAT-AP-LU vocabulary](https://mindig_lu.gitlab.io/DCAT-AP-LU/#Distribution).
   

5. Select **Add Distribution** to save the entry. Repeat for each distribution.

   :::tip Multiple distributions

   You can add multiple distributions to provide different access methods for the same dataset. For example, provide both a CSV file for download and an API endpoint for programmatic access.

   :::

## Manage existing distributions

After you add distribution entries, you can edit or delete them as needed.

1. Open the dataset editor and locate the distribution section.

2. Find the distribution you want to manage in the form.

3. Select your action:
   - **Edit**: Update the distribution details.
   - **Delete**: Remove the distribution entry if it's no longer relevant. 

4. Select **Preview & Save** to save your changes to the dataset.

:::tip Well done

After you add distributions, Data Users can view the access methods and technical specifications in the published dataset metadata. This helps users understand how to access and use your data effectively.

:::
