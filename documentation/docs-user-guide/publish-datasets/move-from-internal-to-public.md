---
slug: /make-internal-datasets-public
sidebar_label: "Publish from internal to public"
sidebar_position: 3
description: "Change internal datasets to public visibility to share with other organisations."
---

import useBaseUrl from '@docusaurus/useBaseUrl';
import FeatureFlag from '@site/src/components/FeatureFlag';

# Publish from internal to public

In this guide

> [Overview](#overview)  
> [Restore the dataset to Approved state](#restore-the-dataset-to-approved-state)  
> [Publish the dataset](publish-a-dataset)

## Overview

Change the visibility of datasets **from internal to public** when you're ready to share them with other organisations in the ecosystem. 

**When to publish internal datasets:**

<!-- DGA -->
<FeatureFlag flag="enable_multi_tenants">

- **Complete review workflow:** Move datasets from internal review to public availability after validation.
- **External sharing:** Make datasets visible to users from other organisations or through connected external data portals.

</FeatureFlag>

<!-- Public -->
<FeatureFlag flag="enable_multi_tenants" inverse>

If you're running your own instance of Metadata Capture, this process may work differently depending on your setup. In some standalone configurations, internal datasets may already be **fully available to all users** within your organisation (similar to published datasets). Contact your system administrator to understand how moving datasets from internal to public works in your configuration.

</FeatureFlag>

**How it works:** Internal datasets must be moved back to the Approved state before they can be published.  The following diagram shows the workflow for publishing internal datasets:

   ```mermaid
   ---
   title: Publishing internal datasets to public
   ---
   graph LR
      G[Internal Only]
      G --> |Approve for Publishing| E[Approved]
      E --> |Publish| F[Published]
      
      style G fill:#4EAEDC,color:#FFFFFF,stroke:#4A8A73
      style E fill:#4EAEDC,color:#FFFFFF,stroke:#3581B8
      style F fill:#6EC0A7,color:#FFFFFF,stroke:#52A68F
   ```

<br/>

To understand the full dataset record lifecycle, see the [dataset record lifecycle](/user-guide/key-concepts/the-dataset-record-lifecycle). 

## Restore the dataset to Approved state

To publish an internal dataset publicly, you'll first need to restore it to its Approved state. You must be a Catalogue Manager or have the permission to **approve datasets**. Check your [permissions](/user-guide/check-your-permissions).

1. Go to the **Internal Only** tab in the datasets panel.

2. Select **View** on the dataset you want to move to public publication.

3. Review the dataset details found in the different tabs: **Dataset**, **Distributions**, **Data Dictionary**, **Relations**, and **Comments** to ensure it's ready for public release.

4. Select **Approve for Publishing**. The comment field appears after you make your selection.

   <img src={useBaseUrl('/manage-datasets/restore-to-approved.png')} alt="Screenshot of the restore to approved button" width="550" />

5. (Optional) Enter your comments to provide context to other collaborators about moving to public publication.

6. Select **Approve for Publishing** to confirm. The dataset returns to the **Approved** tab where it can be published publicly.

:::tip Next step: Publish

Now that the dataset is back in the Approved state, you can proceed to [**publish it publicly**](/user-guide/publish-a-dataset).

:::
