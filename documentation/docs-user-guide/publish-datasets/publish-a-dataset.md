---
slug: /publish-a-dataset
sidebar_label: Publish datasets (public)
sidebar_position: 2
description: "Make approved datasets publicly discoverable to users beyond your organisation."
---

import useBaseUrl from '@docusaurus/useBaseUrl';
import FeatureFlag from '@site/src/components/FeatureFlag';

# Publish datasets (public)

In this guide

> [Overview](#overview)  
> [Publish a dataset](#publish-a-dataset)

## Overview

After a dataset is approved, you can either publish it publicly or [mark it as internal](/user-guide/mark-datasets-as-internal). **Publishing datasets publicly** makes them visible beyond your organisation. This allows users from other organisations in your ecosystem to search and discover the datasets.

<FeatureFlag flag="enable_multi_tenants" inverse>

If you're running your own instance of Metadata Capture, publishing may work differently—for example, making datasets available through connected external portals. Contact your system administrator to understand how publishing works in your setup.

</FeatureFlag>

 To understand how datasets records progress through different stages, see the [dataset record lifecycle](/user-guide/key-concepts/the-dataset-record-lifecycle).

## Publish a dataset

You must be a Catalogue Manager or have the permission to **publish datasets**. Check your [permissions](/user-guide/check-your-permissions). Datasets ready for publication are found in the **Approved** tab of the datasets panel.

1. Go to the **Approved** tab in the datasets panel. Don't see any datasets? Ensure the dataset has been [approved](/user-guide/key-concepts/the-dataset-record-lifecycle).

2. Select **View** on the dataset you want to publish.

   <img src={useBaseUrl('/manage-datasets/approved-tab-view-button.png')} alt="Screenshot of the draft tab" width="550" />

3. Review the dataset details found in the different tabs: **Dataset**, **Distributions**, **Data Dictionary**, **Relations**, and **Comments**.

4. Select **Publish Dataset**. The comment field appears after you make your selection.

5. (Optional) Enter your comments to provide context to other collaborators. 

6. Select **Publish Dataset** again to confirm publication.
   <img src={useBaseUrl('/manage-datasets/publish-dataset.png')} width="800" alt="A screenshot of the publish dataset button" />

   After the dataset is published, it appears in the **Published** tab and is available to users outside your organisation.

   <img src={useBaseUrl('/manage-datasets/published-tab.png')} width="800" alt="A screenshot of the published tab" /> <br/>

:::tip What's next?

Need to make changes? Select **Revert to Draft** to move the dataset back for further edits. You can also **Deprecate** the dataset if it's no longer in use or has been replaced.

:::
