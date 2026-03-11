---
slug: /roles-and-permissions
sidebar_position: 2
sidebar_label: "Understand roles and permissions"
description: "Learn about the default user roles and available permissions in Metadata Capture."
---

import FeatureFlag from '@site/src/components/FeatureFlag';

# Understand roles and permissions

Your access and capabilities within Metadata Capture are defined by your **organisation**, **role**, and **permissions**:

- **Organisation:** The entity you represent (such as a ministry or department). You can belong to multiple organisations.
- **Role:** Your function within an organisation that defines your responsibilities in Metadata Capture. You can hold multiple roles across different organisations.
- **Permission:** The specific actions you can perform on datasets based on your role. Each role grants a set of permissions, such as create, review, or publish.

:::info Organisation context

Roles operate within the context of an organisation. For example, a Metadata Editor role in *Organisation A* allows you to create datasets for that organisation, but not for *Organisation B* unless you hold the same role there.

:::

## User roles in Metadata Capture

The default roles in Metadata Capture align with the [dataset record lifecycle](/user-guide/key-concepts/the-dataset-record-lifecycle) stages. Each role has specific permissions to perform tasks required to move datasets through their lifecycle—from creation to publication.  This ensures governance and accountability in managing your organisation's dataset inventory.

The following diagram illustrates these roles and their relationships:

:::tip Default role names

This guide describes the default role names in Metadata Capture. Your organisation may use different names for these roles, but the core permissions remain the same. To view your actual role assignments and permissions, [**check your role directory**](/user-guide/check-your-permissions).

:::

<br/>

    ```mermaid
    ---
    title: Organisational roles in Metadata Capture
    ---
    graph TD
        CM[Catalogue Manager*<br/>#40;System-wide#41;]
        
        subgraph ORG[" **Organisation** "]
            IC[Inventory Coordinator]
            ME[Metadata Editor]
            MR[Metadata Reviewer]
            MA[Metadata Approver]
        end

    CM -->|Assigns| IC

    IC -->|Assigns within org| ME
    IC -->|Assigns within org| MR
    IC -->|Assigns within org| MA

    style CM fill:#6EC0A7,color:#FFFFFF,stroke:#4A8A73
    style IC fill:#4EAEDC,color:#FFFFFF,stroke:#4A8A73
    style ME fill:#4EAEDC,color:#FFFFFF,stroke:#3581B8
    style MR fill:#4EAEDC,color:#FFFFFF,stroke:#3581B8
    style MA fill:#4EAEDC,color:#FFFFFF,stroke:#3581B8
    style ORG fill:#FFF9E6,color:#B8941A,stroke:#F5C945,stroke-width:0.3px
```

*Catalogue Manager can also directly assign any organisation-level role.

<br/>




Here's a reference of each role and their responsibilities:

<FeatureFlag flag="enable_multi_tenants">

<!-- DGA -->
| Role | Scope | Responsibilities |
|------|-------|-----------------|
| **Catalogue Manager** | System-wide | • Publish datasets<br/>• Unpublish datasets<br/>• Deprecate datasets<br/>• Manage authentic source label proposals<br/>• Publish authentic source labels<br/>• Provide support to other roles<br/>• Manage controlled vocabularies |
| **Inventory Coordinator** | Organisation-level |  • Assign/Unassign Metadata Editors <br/> • Assign/Unassign Metadata Reviewers<br/>• Assign/Unassign Metadata Approvers<br/>• Manage organisation contact points |
| **Metadata Editor** | Organisation-level | • Create datasets<br/>• Update datasets<br/>• Submit datasets for review |
| **Metadata Reviewer** | Organisation-level | • Ensure dataset quality and accuracy<br/> • Review datasets for approval |
| **Metadata Approver** | Organisation-level | • Grant/remove publication authorisation<br/>• Final review and approval for publication |

</FeatureFlag>


<FeatureFlag flag="enable_multi_tenants" inverse>

<!-- Public -->
| Role | Scope | Responsibilities |
|------|-------|-----------------|
| **Catalogue Manager** | System-wide | • Publish datasets<br/>• Unpublish datasets<br/>• Deprecate datasets<br/>• Manage authentic source label proposals<br/>• Publish authentic source labels<br/>• Provide support to other roles<br/>• Manage controlled vocabularies |
| **Inventory Coordinator** | Organisation-level |  • Assign/Unassign Metadata Editors <br/> • Assign/Unassign Metadata Reviewers<br/>• Assign/Unassign Metadata Approvers<br/>• Manage organisation contact points |
| **Metadata Approver** | Organisation-level | • Grant/remove publication authorisation<br/>• Final review and approval for publication |
| **Metadata Reviewer** | Organisation-level | • Ensure dataset quality and accuracy<br/> • Review datasets for approval |
| **Metadata Editor** | Organisation-level | • Create datasets<br/>• Update datasets<br/>• Submit datasets for review |

</FeatureFlag>

### Catalogue Manager

<FeatureFlag flag="enable_multi_tenants">

<!-- DGA -->
The **Catalogue Manager** is a member of the Ministry for Digitalisation or an approved sub-contractor who serves as the system-wide administrator of the platform. They oversee the dataset governance across all organisations, and operate in three key areas:

</FeatureFlag>


<FeatureFlag flag="enable_multi_tenants" inverse>

<!-- Public -->
The **Catalogue Manager** serves as the system-wide administrator of the platform. They oversee the dataset governance across all organisations, and operate in three key areas:

</FeatureFlag>

- **User management:** Assigns Inventory Coordinators and supports all roles.
- **Publication control:** Publishes, unpublishes, and deprecates records; and manage authentic source labels.
- **Vocabulary management:** Maintains controlled vocabularies (keywords, legal basis, organisations).

### Inventory Coordinator

The **Inventory Coordinator** is a member of your organisation appointed by a Catalogue Manager. They ensure datasets are properly documented and reviewed through:

- **Role management:** Assigns Metadata Editors, Reviewers, and Approvers within your organisation.
- **Contact management:** Manages the contact points in your organisation for proper communication.

### Metadata Approver

The **Metadata Approver** has authority to legally bind your organisation to publication decisions. Appointed by the Inventory Coordinator, they focus on:

<FeatureFlag flag="enable_multi_tenants">

<!-- DGA -->
- **Publication authorisation:** Grants or removes publication authorisation.
- **Final validation:** Approves metadata records for publication.

</FeatureFlag>


<FeatureFlag flag="enable_multi_tenants" inverse>

<!-- Public -->
- **Publication authorisation:** Grants or removes publication authorisation for datasets. This signifies your organisation's consent to publish the metadata and, and can include reviewing legal requirements or other organisational policies.
- **Final validation:** Approves metadata records for publication.

</FeatureFlag>


<FeatureFlag flag="enable_multi_tenants">

<!-- DGA -->
:::info Important

Although **Catalogue Managers** can view and interact with all records, **only Metadata Approvers** have the authority to approve records for their organisation. This approval signifies your organisation's consent to publish the metadata and, if given, their publication authorisation.

:::

</FeatureFlag>

### Metadata Reviewer

The **Metadata Reviewer** is a member of your organisation who ensures the quality and accuracy of metadata records before they reach the approval stage. Appointed by the Inventory Coordinator, they focus on:

- **Quality control:** Review metadata records submitted by Metadata Editors for completeness and accuracy.
- **Validation:** Verify that dataset descriptions accurately represent the underlying data resources.

### Metadata Editor

The **Metadata Editor** is a member of your organisation who creates and maintains metadata records. Appointed by the Inventory Coordinator, they work on:

- **Dataset creation:** Create new metadata records for datasets held by their organisation.
- **Content maintenance:** Update existing metadata records to reflect changes in datasets.
- **Workflow initiation:** Submit completed metadata records for review to begin the publication process.


<FeatureFlag flag="enable_multi_tenants">

<!-- DGA -->
:::info Required Roles

To maintain a data inventory, your organisation must have **all organisation-level roles** described in this document: Metadata Editor, Metadata Reviewer, and Metadata Approver. These roles have the necessary permissions to move datasets through the stages of their lifecycle.

:::

</FeatureFlag>

<!-- Public -->
<FeatureFlag flag="enable_multi_tenants" inverse>
:::info Required Roles

To maintain a data inventory, your organisation must have **all organisation-level roles** described in this document. If you customise the default roles, ensure that the new roles cover all necessary permissions required for each stage (editing, reviewing, approving, and publishing).

:::
</FeatureFlag>
