---
slug: /create-dataset-versions
sidebar_label: "Create dataset versions"
sidebar_position: 3
description: "Maintain historical records of your datasets by creating new versions."
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Create dataset versions

In this guide

> [Overview](#overview)  
> [Create a new dataset version](#create-a-new-dataset-version)  
> [Version constraints and relationships](#version-constraints-and-relationships)  
> [Best practices for versioning](#best-practices-for-versioning)  


## Overview

**Create dataset versions** to maintain a historical record of how published datasets evolve over time. Versioning creates a new draft dataset that is linked to the original through a version chain, allowing you to track the lineage and evolution of your data while the old version is automatically deprecated.

**Create a new version when:**
- You want to publish an updated dataset that supersedes an existing published version
- You want to maintain a historical record of dataset changes over time
- You want to ensure stakeholders are notified about newer versions of datasets they use

**For example:**  Annual Employment Statistics are released as a stand-alone dataset, with data on one year each. These datasets relate to each other using a dataset series and enable users to easily find similar releases but retain each year of data as an independent and valid dataset.

**How versioning works:**

- New versions can only be created from **published datasets** that don't already have newer versions. 
- The new version maintains the same identifier as the previous version to ensure continuity.
- The new version starts as a **draft** with a link to its previous version.
- The original dataset is **automatically deprecated** when you publish the new version.
- The new version inherits all metadata from the previous version, including **authentic source** labels

## Create a new dataset version

To create a dataset version, you must be a Catalogue Manager or have the permission to **publish datasets**. Check your [permissions](/user-guide/check-your-permissions).

1. Go to the **Published** tab in the datasets panel.

2. Select the options icon ( **⋮** ) on the dataset you want to version.

3. Select **Create a Version** from the menu. The system creates a new draft version and opens the dataset editor.

<figure>
      <img src={useBaseUrl('/manage-datasets/create-a-new-version.png')} alt="Screenshot showing the create version button in the actions menu" width="630" />
</figure>

   :::info Restrictions

   You can only create a new version from a published dataset that does not already have a newer version. If the dataset already has a newer version, the **Create a Version** button is disabled.

   :::

4. Update the new version with your changes:
   - The title and other metadata are copied from the previous version
   - All distributions and data dictionary entries are included
   - Dataset relations and qualified attributions are preserved
   - Authentic source assignments remain intact
   - The status is set to **Draft**

5. Make your updates, then select **Preview & Save** to review your changes.

6. Select **Save as Draft** to save the new version. From here, you can continue editing, submit it for approval, and publish it. See: [Dataset record lifecycle](/user-guide/key-concepts/the-dataset-record-lifecycle).

    To view the previous version of the dataset, select the **previous dataset** link in the dataset card. 

<figure>
      <img src={useBaseUrl('/manage-datasets/link-to-previous-version.png')} alt="Screenshot showing the link to previous version" width="630" />
</figure>

:::tip What's next?

After publishing the new version, you can [view the version history](/user-guide/view-version-history) to see how the dataset has evolved over time.

:::

## Version constraints and relationships

Versioning follows specific rules to maintain clarity and consistency in dataset lineage:

- **Same identifier:** New versions retain the same identifier as the previous version to ensure continuity
- **One active version**: Only one version in a chain can be published without being deprecated
- **Linear chain**: Each dataset can have only one previous version and one next version
- **No version of versions**: You cannot create a version of a dataset that is already a newer version of another published dataset (wait until you publish the new version first)

**What's included in the new version:**
- All metadata fields: Title, description, temporal coverage, rights statement, etc.
- Distributions: Access URLs, formats, and all distribution metadata
- Data dictionary: Entries with **authentic source assignments preserved**
- Dataset relations: Links to other datasets or external resources
- Qualified attributions: Role assignments for organisations

**What's not included in the new version:**
- Activity logs (the new version starts with a fresh activity log)
- Comments (comments from the previous version are not copied)
- Status (the new version always starts as Draft)
- Approval and publication dates (these are set when the new version goes through the workflow)

## Best practices for versioning

- **Use clear version identifiers**: Update the `version` field to make versions easily distinguishable. For further guidance on good versioning practices for data. For more details, see the [data versioning guide](https://www.ands.org.au/working-with-data/data-management/data-versioning).
- **Add version notes**: Use the `version_notes` field to document what changed in this version
- **Update temporal coverage**: Adjust time periods to reflect the data covered by the new version
- **Review all metadata**: Ensure all metadata fields are current and accurate for the new version
- **Verify data dictionaries**: Check that field definitions remain relevant or update them as needed
- **Test distributions**: Ensure all distribution links and access methods work correctly
- **Add comments during workflow**: Use comments when submitting, approving, and publishing to document the versioning rationale

<!-- ## Stakeholder notifications

When a new version is published and the old version is deprecated, the following people receive email notifications:

- **Dataset creator**: The person who originally created the old dataset
- **Dataset contacts**: All contacts associated with the old dataset
- **Role-based recipients**: Users with "Manager" and "All" roles for the publisher organisation
 -->
