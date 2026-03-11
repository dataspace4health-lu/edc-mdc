---
title: The dataset record lifecycle
sidebar_position: 2
description: "Understand the dataset record lifecycle for managing datasets in Metadata Capture."
redirect_from:
  - /docs/user-guide/key-concepts/the-dataset-workflow
  - /user-guide/key-concepts/the-dataset-workflow



---

import FeatureFlag from '@site/src/components/FeatureFlag';

# The dataset record lifecycle

Use this guide to understand the workflow for managing datasets in Metadata Capture. Also see: [What is a dataset?](/user-guide/what-is-a-dataset)

Dataset records in Metadata capture go through a multi‑stage lifecycle focusing on approvals to ensure datasets are properly documented before publication. This lifecycle defines the workflow for managing datasets from creation to publication and eventual deprecation.  

The following diagram illustrates the dataset record lifecycle in Metadata Capture. The boxes represent the lifecycle **stages**, and the arrows indicate the **actions** required to move the datasets to the next stage. Each stage represents a tab in the [dataset panel](/user-guide/dashboard-overview#dataset-panel), where you can manage datasets based on their current state.


```mermaid
---
title: dataset record lifecycle in Metadata Capture
---
graph LR
    B[Draft]
    B --> |Submit| C[Completed]
    C --> |Validate| D[Validated]
    D --> |Approve| E[Approved]
    
    E --> |Publish| F[Published]
    E --> |Mark as Internal| G[Internal Only]
    
    F -. Unpublish .-> E
    G -. Approve for Publishing .-> E
    
    F --> |Deprecate| H[Deprecated]
    G --> |Deprecate| H[Deprecated]
    
    style B fill:#4EAEDC,color:#FFFFFF,stroke:#3581B8
    style C fill:#4EAEDC,color:#FFFFFF,stroke:#3581B8
    style D fill:#4EAEDC,color:#FFFFFF,stroke:#3581B8
    style E fill:#4EAEDC,color:#FFFFFF,stroke:#3581B8
    style F fill:#6EC0A7,color:#FFFFFF,stroke:#52A68F
    style G fill:#4EAEDC,color:#FFFFFF,stroke:#4A8A73
    style H fill:#B5BFC4,color:#000000,stroke:#8A9499
```
<br/>

:::tip Other actions

- You can [revert datasets to draft](/user-guide/revert-a-dataset-to-draft) at any stage except for Published and Internal Only stages. 
- You can only publish datasets from [Internal Only to Public](/user-guide/make-internal-datasets-public) by first moving them back to the Approved state.

:::

<br/>

The following table describes how datasets progress through each stage from creation (draft) to publication and deprecation, and the steps involved in each stage:

<FeatureFlag flag="enable_multi_tenants">

| Action | Stage  | Resulting State  |
|--------|-------|-------------|
| Add a dataset  | **Draft** | Dataset is being added or edited.|
| Submit the dataset  | **Completed** | Dataset has been submitted for review. |
| Validate the dataset   | **Validated** | The accuracy of dataset has been confirmed, and is awaiting approval. |
| Approve the dataset  | **Approved** | The dataset meets relevant publication standards, and is awaiting publication. |
| Publish the dataset as public  | **Published** | Dataset is published and accessible to all organisations. |
| Mark the dataset as internal  | **Internal Only** | Dataset is published and only accessible within the organisation. |
| Deprecate the dataset   | **Deprecated** | Dataset is no longer used or has been replaced by newer versions. |

</FeatureFlag>

<!-- Public -->
<FeatureFlag flag="enable_multi_tenants" inverse>

| Action | Stage  | Resulting State  |
|--------|-------|-------------|
| Add a dataset  | **Draft** | Dataset is being added or edited.|
| Submit the dataset  | **Completed** | Dataset has been submitted for review. |
| Validate the dataset   | **Validated** | The accuracy of dataset has been confirmed, and is awaiting approval. |
| Approve the dataset  | **Approved** | The dataset meet the publication standards, and is awaiting publication. This can include fulfilling legal requirements or other organisational policies. |
| Publish the dataset as public  | **Published** | Dataset is published and accessible to all organisations. |
| Mark the dataset as internal  | **Internal Only** | Dataset is published and only accessible within the organisation. |
| Deprecate the dataset   | **Deprecated** | Dataset is no longer used or has been replaced by newer versions. |

</FeatureFlag>

:::info Roles and permissions

Your role determines the actions you can perform and how you can interact with a dataset. Some actions are only available to specific roles. To learn about the available roles and the actions you can perform, see: [Roles and permissions](/user-guide/roles-and-permissions).
