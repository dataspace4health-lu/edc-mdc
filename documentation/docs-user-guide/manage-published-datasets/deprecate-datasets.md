---
slug: /deprecate-datasets
sidebar_label: "Deprecate datasets"
sidebar_position: 18
description: "Maintain dataset integrity by deprecating outdated or irrelevant datasets."
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Deprecate datasets

In this guide

> [Overview](#overview)  
> [Deprecate a dataset](#deprecate-a-dataset)

## Overview

**Deprecate datasets** that are no longer relevant or accurate. Deprecation indicates to users that the dataset should not be used for new analyses, while still preserving its historical context for reference. Use this option when datasets have been superseded by newer versions or when their content is outdated. To understand the dataset record lifecycle, see the [dataset record lifecycle](/user-guide/key-concepts/the-dataset-record-lifecycle).

**For example:** A dataset for *Employment Statistics 2020* may become outdated when newer data is available. By deprecating it, Data Users can see it's no longer current whilst still accessing historical information.

**How deprecation works:**

- Catalogue Managers (or equivalent roles) can deprecate datasets in Published or Internal Only stage
- Once deprecated, datasets remain viewable but cannot be restored to previous states
- Deprecated datasets appear in the Deprecated tab for historical reference
- To make a deprecated dataset available again, you mus t recreate it as a new dataset. 

:::info Remember
Once a dataset is deprecated, you can still view its details but **you can no longer restore it** to its previous states. If you need to make the dataset available again, you must recreate it as a [new dataset](/user-guide/add-a-dataset). If you want to edit and republish a dataset, **consider the [Unpublish](/user-guide/unpublish-a-dataset) option instead**.
:::

## Deprecate a dataset

To deprecate a dataset, you must be a Catalogue Manager or have the permission to **deprecate datasets**. Check your [permissions](/user-guide/check-your-permissions).

1. Go to the **Published** or **Internal Only** tab in the datasets panel.

2. Select **View** on the dataset you want to deprecate.

3. Select **Deprecate Dataset**. The comment box appears.

   <figure>
      <img src={useBaseUrl('/manage-datasets/deprecate.png')} alt="Screenshot of the deprecate dataset button" width="550" />
   </figure>

4. (Optional) Enter a comment explaining why you are deprecating the dataset to provide context to other collaborators.

5. Select **Deprecate Dataset** to confirm. The dataset appears in the **Deprecated** tab.

   :::tip Deprecate vs unpublish

   - **Deprecate**: Use when a dataset is outdated or no longer relevant, but you want to keep it accessible for historical reference. No further edits or publications can be made.
   - **Unpublish**: Use when a dataset contains errors or sensitive information and should be removed from public access. The dataset moves back to the Approved stage for further review and correction.

   :::

