---
slug: /approve-a-dataset
sidebar_label: "Approve datasets"
sidebar_position: 3
description: "Confirm datasets meet publication standards before making them available."
---

import FeatureFlag from '@site/src/components/FeatureFlag';
import useBaseUrl from '@docusaurus/useBaseUrl';

# Approve datasets

In this guide

> [Overview](#overview)  
> [Approve a dataset](#approve-a-dataset)

## Overview


**Approve datasets** that have been validated to confirm they meet relevant publication standards before making them available for publication. This can include legal, ethical, and quality requirements.

To understand how datasets records progress through different stages after approval, see the [dataset record lifecycle](/user-guide/key-concepts/the-dataset-record-lifecycle).

## Approve a dataset

To approve datasets, you must be an Approver or have the permission to **approve datasets**. Check your [permissions](/user-guide/check-your-permissions). Datasets ready for approval are found in the **Validated** tab of the datasets panel.

1. Go to the  **Validated** tab in the datasets panel.

2. Select **View** on the dataset you want to validate.

   <img src={useBaseUrl('/manage-datasets/validated-tab-view-button.png')} alt="Screenshot of the draft tab" width="600" />


3. Review the dataset details found in the different tabs: **Dataset**, **Distributions**, **Data Dictionary**, **Relations**, **Qualified Attributions** and **Comments**.

4. Review the dataset details and attributions to ensure they are complete and accurate, then select Approve Dataset. The comment field appears.

5. (Optional) Enter your comments to provide context to other collaborators.

6. Select **Approve Dataset** again to confirm approval. The dataset moves to the **Approved** tab and is ready for publication.

   <img src={useBaseUrl('/manage-datasets/approve-dataset.png')} width="750" alt="A screenshot of the approve dataset button" />

:::tip Need changes?

If you need changes to the dataset, select **Revert to Draft** and provide comments so the Metadata Editor understands the required updates. The dataset moves back to the **Draft** tab, where the Metadata Editor can make the necessary updates.

:::