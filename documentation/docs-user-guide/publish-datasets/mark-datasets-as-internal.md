---
slug: /mark-datasets-as-internal
sidebar_label: "Mark as internal only"
sidebar_position: 1
description: "Restrict approved datasets to your organisation without making them publicly visible."
---

import useBaseUrl from '@docusaurus/useBaseUrl';
import FeatureFlag from '@site/src/components/FeatureFlag';

# Mark datasets as internal only

In this guide

> [Overview](#overview)  
> [Mark a dataset as internal](#mark-a-dataset-as-internal)

## Overview

After a dataset is approved, you can either [publish it publicly](/user-guide/publish-a-dataset) or mark it as internal. **Marking datasets as internal** keeps their visibility within your organisation, restricting access from other organisations in the ecosystem. 

<!-- DGA -->
<FeatureFlag flag="enable_multi_tenants">

**When to mark datasets as internal:**

- **Internal cataloguing:** Keep sensitive datasets permanently restricted to your organisation only.
- **Internal review workflow:** Maintain datasets in an internal state for review and validation before making them publicly available to other organisations in the ecosystem.

 To understand how datasets records progress through different stages after marking them as internal, see the [dataset record lifecycle](/user-guide/key-concepts/the-dataset-record-lifecycle).

</FeatureFlag>

<!-- Public -->
<FeatureFlag flag="enable_multi_tenants" inverse>

**When to mark datasets as internal:** If you're running your own instance of Metadata Capture, marking datasets as internal may work differently. In some standalone setups, internal datasets are fully available to all users within your organisation (similar to publishing publicly), while in others it may prevent datasets from being shared through connected external portals. Contact your system administrator to understand how internal datasets work in your setup.

 To understand how datasets records progress through different stages after marking them as internal, see the [dataset record lifecycle](/user-guide/key-concepts/the-dataset-record-lifecycle).


</FeatureFlag>


## Mark a dataset as internal

To mark datasets as internal, you must be a Catalogue Manager or have the permission to **set datasets as internal**. Check your [permissions](/user-guide/check-your-permissions).

1. Go to the **Approved** tab in the datasets panel. 

2. Select **View** on the dataset you want to mark as internal.

3. Review the dataset details found in the different tabs: **Dataset**, **Distributions**, **Data Dictionary**, **Relations**, and **Comments**.

4. Select **Mark as Internal**. The comment field appears after you make your selection.

5. (Optional) Enter your comments explaining why you are marking the dataset as internal, to provide context to other collaborators.

6. Select **Mark as Internal** to confirm. The dataset now appears in the **Internal Only** tab.

   <img src={useBaseUrl('/manage-datasets/mark-as-internal.png')} width="600" alt="A screenshot of the mark as internal button" />

:::tip Changed your mind?

- To publish the dataset publicly, first select **Approve for Publishing** to return the dataset to the **Approved** state. 
- Select **Revert to Draft** if you need to make further edits.

:::
