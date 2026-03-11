---
slug: /validate-a-dataset
sidebar_label: "Validate datasets"
sidebar_position: 2
description: "Ensure datasets are accurate and ready for approval."
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Validate datasets

In this guide

> [Overview](#overview)  
> [Validate a dataset](#validate-a-dataset)

## Overview

**Validate the accuracy of datasets** that have been submitted for review. During this stage, ensure that metadata fields are filled out correctly and that the information accurately represents the underlying data.

To understand how datasets record progress through different stages, see the [dataset record lifecycle](/user-guide/key-concepts/the-dataset-record-lifecycle).

## Validate a dataset

You must be an Approver or have the permission to **validate datasets**. Check your [permissions](/user-guide/check-your-permissions). Datasets awaiting validation are found in the **Completed** tab of the datasets panel.

1. Go to the **Completed** tab in the datasets panel.

2. Select **View** on the dataset you want to validate.

    <img src={useBaseUrl('/manage-datasets/completed-tab-view-button.png')} alt="Screenshot of the draft tab" width="600" />

3. Review the dataset details found in the different tabs: **Dataset**, **Distributions**, **Data Dictionary**, **Relations**, and **Comments**.

4. Select **Validate Dataset**. The comment field appears. 

5. (Optional) Enter your comments to provide context to other collaborators.

6. Select **Validate Dataset** again to confirm validation. After the dataset is validated, it appears in the **Validated** tab and is ready for [approval](/user-guide/approve-a-dataset).


    <img src={useBaseUrl('/manage-datasets/validate-dataset.png')} width="750" alt="A screenshot of the validate dataset button" />


:::tip What's next?

Need changes? Select **Revert to Draft** and provide comments to move the dataset back to the **Draft** tab for edits. Otherwise, the dataset is ready for [approval](/user-guide/approve-a-dataset).

:::
