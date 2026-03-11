---
slug: /unpublish-a-dataset
sidebar_label: "Unpublish datasets"
sidebar_position: 17
description: "Remove datasets from public visibility while maintaining their approved status."
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Unpublish datasets

In this guide

> [Overview](#overview)  
> [Unpublish a dataset](#unpublish-a-dataset)

## Overview

**Unpublish datasets** to remove them from public visibility whilst maintaining their approved status. This action moves datasets back to the Approved state, allowing you to take down published datasets whilst keeping them ready for re-publication or marking as internal without requiring re-approval. Use this for temporary removal, policy changes, or when preparing datasets to be marked as internal.

**For example:** A dataset for *Budget Allocations 2024* may need to be temporarily removed from public access due to policy changes. By unpublishing it, the dataset returns to the Approved state and can be quickly republished or marked as internal once the issues are resolved.

**How unpublishing works:**

- Catalogue Managers (or equivalent roles) can unpublish datasets in Published state
- Unpublished datasets move to the Approved tab and are no longer publicly visible
- Datasets can be republished, marked as internal, or reverted to draft from the Approved state
- No re-approval is required to republish an unpublished dataset


## Unpublish a dataset

To unpublish a dataset, you must be a Catalogue Manager or have the permission to **unpublish datasets**. Check your [permissions](/user-guide/check-your-permissions).

1. Go to the **Published** tab in the datasets panel.

2. Select **View** on the dataset you want to unpublish.

3. Select **Unpublish**. The comment field appears.

   <figure>
      <img src={useBaseUrl('/manage-datasets/unpublish.png')} alt="Screenshot of the unpublish dataset button" />
   </figure>

4. (Optional) Enter your comments explaining why you are unpublishing the dataset to provide context to other collaborators.

5. Select **Unpublish** to confirm. The dataset appears in the **Approved** tab and is no longer publicly visible.

   :::tip Next steps

   From the Approved tab, you have three options:
   - **[Publish the dataset](/user-guide/publish-a-dataset)**: Make it publicly available again
   - **[Mark as internal](/user-guide/mark-datasets-as-internal)**: Keep it visible only within your organisation
   - **[Revert to draft](/user-guide/revert-a-dataset-to-draft)**: Move it back to Draft state for further edits and reapproval

   :::


