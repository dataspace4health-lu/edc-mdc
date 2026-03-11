---
slug: /revert-a-dataset-to-draft
sidebar_label: "Revert datasets to draft"
sidebar_position: 4
description: "Make corrections or updates by reverting datasets back to draft state."
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Revert datasets to draft

In this guide
> [Overview](#overview)  
> [Revert a dataset to draft](#revert-a-dataset-to-draft) 
## Overview

Revert datasets to their draft state at any stage in the workflow to make corrections or updates before continuing through the approval process. Use this option when you need to make significant changes or address issues identified during review. This allows you to address feedback, add missing information, or fix errors identified during review.

**How it works:**

- Datasets can be reverted from Completed, Validated, or Approved stages
- Published and Internal Only datasets cannot be reverted to draft
- For internal datasets, first approve them for publishing to move them to the Approved state, then revert
- Reverting sends the dataset back to the Draft tab where you can make edits

The following diagram illustrates which stages allow reverting to draft:

```mermaid
---
title: Revert to draft
---
graph TD
    B[Draft]
    C[Completed]
    D[Validated]
    E[Approved]
    G[Internal Only]
    F[Published]
    
    C -. Revert .-> B
    D -. Revert .-> B
    E -. Revert .-> B
    G -. Cannot Revert .-> G
    F -. Cannot Revert .-> F
    
    style B fill:#4EAEDC,color:#FFFFFF,stroke:#3581B8
    style C fill:#4EAEDC,color:#FFFFFF,stroke:#3581B8
    style D fill:#4EAEDC,color:#FFFFFF,stroke:#3581B8
    style E fill:#4EAEDC,color:#FFFFFF,stroke:#3581B8
    style G fill:#4EAEDC,color:#FFFFFF,stroke:#4A8A73
    style F fill:#6EC0A7,color:#FFFFFF,stroke:#52A68F
```

To understand the full dataset record lifecycle, see the [dataset record lifecycle](/user-guide/key-concepts/the-dataset-record-lifecycle).

## Revert a dataset to draft

To revert a dataset to draft, you must be a Catalogue Manager or have the permission to **return datasets to draft**. Check your [permissions](/user-guide/check-your-permissions).

1. Search for the dataset you want to revert, or manually locate them in the datasets panel.

2. Select **View** on the dataset you want to revert. 

   <img src={useBaseUrl('/manage-datasets/completed-tab-view-button.png')} alt="Screenshot of the draft tab" width="600" />

3. Select **Revert to Draft**. The comment box appears.

4. (Optional) Enter a comment explaining why you are reverting the dataset to draft state.

5. Select **Revert to Draft** to confirm. After the dataset is reverted, it appears on the **Draft** tab, and is ready for further edits.

   <img src={useBaseUrl('/manage-datasets/revert-datasets.png')} width="700" alt="A screenshot of the revert to draft button" />

