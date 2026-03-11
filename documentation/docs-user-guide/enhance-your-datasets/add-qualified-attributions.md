---
slug: /add-qualified-attributions
sidebar_label: "Add qualified attributions"
description: "Provide transparency and accountability by crediting data sources with specific roles."
sidebar_position: 5
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Add qualified attributions

In this guide

> [Overview](#overview)  
> [Add a qualified attribution](#add-a-qualified-attribution)   
> [Manage existing qualified attributions](#manage-existing-qualified-attributions)

## Overview

**Qualified attributions**  allow the association of an organisation with a specific aspect of the dataset’s creation, maintenance, or distribution, beyond the “Publisher” and “Creator” roles explicitly defined in the metadata model. By adding qualified attributions to your datasets, you provide transparency about who is responsible for various aspects of the dataset—improving provenance tracking, accountability and trust for Data Users.

**For example:** A dataset for *Transport Infrastructure* may involve the Ministry of Transport as the **Publisher** and a certain data centre as the **Custodian**. By adding these attributions, Data Users can understand each organisation's role when the dataset is published.

**How qualified attributions work:**

- You can add multiple attributions to document all parties involved with a dataset
- The same organisation can have multiple roles (e.g., both Author and Custodian)
- Attribution details appear in published dataset metadata

## Add a qualified attribution

Add qualified attributions to link organisations and their specific roles to your dataset. You must be an Editor or have the permission to **edit datasets**, check your [permissions](/user-guide/check-your-permissions).

To add attributions to a dataset:

1. Ensure the dataset is in Draft, or [revert it to draft](/user-guide/revert-a-dataset-to-draft) if needed

2. Open the dataset in the **Draft** tab using one of the following methods:
   - Select the options icon ( **⋮** ) on the dataset and select **Edit**, then select **Qualified Attributions** in the left panel. 
   - Select **View** on the dataset, go to the **Qualified Attributions** tab, and select **Manage Qualified Attributions**

    <figure>
      <img src={useBaseUrl('/enhance-datasets/manage-attributions.png')} alt="Screenshot of the manage attributions button" width="700" />
      <figcaption></figcaption>
    </figure>

3. Select **Expand Form** to add a new entry.

4. Fill out the attribution form:
   - **Organisation**: Select the organisation name
   - **Role**: Select the appropriate role that best describes this organisation's relationship to the dataset. For guidance, see: [Available attribution roles](#available-attribution-roles).
   
   In this example, we select *LNDS* as the **Custodian** of the dataset.
   
   <figure>
      <img src={useBaseUrl('/enhance-datasets/sample-attribution.png')} alt="Example screenshot of adding LNDS as a custodian" width="700" />
      <figcaption></figcaption>
   </figure>

5. Select **Add Attribution** to save the entry. Repeat for each attribution.

   :::tip Multiple roles for one organisation

   The same organisation can have multiple roles. For example, an organisation might be both the **Author** and **Custodian** of a dataset. Add separate attributions for each role.

   :::

### Available attribution roles

The roles are based on the [INSPIRE Responsible Party Role<sup>↗</sup>](http://inspire.ec.europa.eu/metadata-codelist/ResponsiblePartyRole) codelist:

- **Author**: Party who authored the dataset or its documentation
- **Custodian**: Party responsible for accepting accountability for the data and ensuring appropriate care and maintenance
- **Distributor**: Party who distributes the dataset to others
- **Originator**: Party who created the original data or dataset
- **Owner**: Party who owns the dataset or has ownership rights
- **Point of contact**: Party who can be contacted for acquiring knowledge about or acquisition of the dataset
- **Principal investigator**: Key party responsible for gathering information and conducting research
- **Processor**: Party who has processed the data in a manner such that the dataset has been modified
- **Resource provider**: Party that supplies the dataset or resource
- **User**: Party who uses the dataset

## Manage existing qualified attributions

After you add attribution entries, you can edit or delete them as needed.

1. Open the dataset editor and select **Qualified Attributions** in the left panel.

2.  Locate the entry you want to manage in the table and select the edit icon (✏️).

   <figure> 
      <img src={useBaseUrl('/enhance-datasets/attribution-list.png')} alt="Screenshot showing an example of the qualified attributions list" width="700" />
      <figcaption> </figcaption>
   </figure>

3. In the **Edit Qualified Attribution screen**, choose one of the following actions:
   - **Edit**: Update the details and select **Update Attribution**.
   - **Delete**: Select **Delete Attribution** to permanently remove the entry.

   <figure>
      <img src={useBaseUrl('/enhance-datasets/edit-or-delete-attribution.png')} alt="Screenshot of editing or deleting attributions" width="700" />
      <figcaption> </figcaption>
   </figure>

:::tip Well done

After you add qualified attributions, Data Users can view the organisations and their roles in the published dataset metadata. This improves transparency and accountability.

:::


