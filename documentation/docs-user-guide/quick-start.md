---
slug: /quick-start-guide
sidebar_label: "Quick start guide"
sidebar_position: 2
description: "Get started with managing datasets based on your role."
---

import FeatureFlag from '@site/src/components/FeatureFlag';
import useBaseUrl from '@docusaurus/useBaseUrl';

# Quick start guide

Get started with managing datasets based on your role in the workflow.

In this guide  
> [Identify your role](#identify-your-role)  
> [**Editors:** Create and submit datasets](#editors-create-and-submit-datasets)  
> [**Reviewers:** Validate datasets](#reviewers-validate-datasets)  
> [**Approvers:** Approve datasets](#approvers-approve-datasets)  
> [**Catalogue Managers:** Publish and manage datasets](#catalogue-managers-publish-and-manage-datasets)

## Identify your role

Your role determines what actions you can perform with datasets. **Role names may vary** in your organisation—[check your permissions](/user-guide/check-your-permissions) if you're unsure. Common roles and their responsibilities include:

| Your role | What you do |
|-----------|-------------|
| **Metadata Editor** | Create datasets, add enhancements, submit for review |
| **Metadata Reviewer** | Validate submitted datasets, ensure accuracy and standards |
| **Metadata Approver** | Approve validated datasets, ensure governance compliance |
| **Catalogue Manager** | Publish datasets, manage public access, handle deprecation |

:::tip Role names vary

These roles reflect a typical setup in Metadata Capture. Your organisation may use different names—contact your [Inventory Coordinator](/user-guide/roles-and-permissions) or [System Administrator](/user-guide/roles-and-permissions) if you need clarification.

:::

## Editors: Create and submit datasets

**Your task:** Document your organisation's data holdings and submit them for review.

**Your workflow:**

1. **Create a dataset:** [Add a dataset](/user-guide/add-a-dataset) or use the [bulk upload](/user-guide/bulk-upload-datasets) feature to start documenting your data.

2. **Enhance your dataset:** (Optional) Add details to improve discoverability
   - [Add distributions](/user-guide/add-distributions) – describe how users can access the data
   - [Add a data dictionary](/user-guide/add-a-data-dictionary) – document data structure and fields
   - [Manage dataset relations](/user-guide/manage-dataset-relations) – link to related datasets
   - [Add qualified attributions](/user-guide/add-qualified-attributions) – credit data sources

3. **[Submit for review](/user-guide/submit-datasets-for-review):** Submit your dataset to initiate the review process.

:::tip Save your progress

Select **Save as Draft** at any time to save your work, and come back to it from the **Draft** tab when you're ready.

:::

## Reviewers: Validate datasets

**Your task:** Ensure submitted datasets meet technical standards and accuracy requirements.

**Your workflow:**

1. **Find submitted datasets:** Find datasets awaiting validation in the **Completed** tab. 
2. **[Validate the dataset](/user-guide/validate-a-dataset):** Ensure metadata is accurate and complete and validate the dataset.
3. **[Or revert for changes:](/user-guide/revert-a-dataset-to-draft)** If the dataset needs corrections, revert to draft and add comments about what needs fixing.

:::tip Add context

Always include comments when reverting datasets—this helps Editors understand what needs changing.

:::

## Approvers: Approve datasets

**Your task:** Confirm validated datasets meet governance policies and compliance standards before publication.

**Your workflow:** 

1. **Find validated datasets:** Find datasets awaiting approval in the **Validated** tab.
2. **[Approve the dataset](/user-guide/approve-a-dataset):** Ensure the dataset meets your publication standards and approve the dataset.
3. **[Or revert for changes:](/user-guide/revert-a-dataset-to-draft)** If the dataset needs corrections, revert to draft and add comments about what needs fixing.

:::tip Final checkpoint

This is the final review before publication—ensure all governance, legal, and quality requirements are satisfied.

:::

## Catalogue Managers: Publish and manage datasets

**Your task:** Publish approved datasets and manage their lifecycle, including deprecation and access control.

**Your workflow:**

1. **Find approved datasets:** Find datasets ready for publication in the **Approved** tab.
2. **Choose publication type:**
   - **[Publish publicly](/user-guide/publish-a-dataset)** – make datasets discoverable beyond your organisation
   - **[Mark as internal](/user-guide/mark-datasets-as-internal)** – restrict access to your organisation only
3. **[Or revert for changes:](/user-guide/revert-a-dataset-to-draft)** If the dataset needs corrections, revert to draft and add comments about what needs fixing.

**Other data management tasks:**

- **[Unpublish](/user-guide/unpublish-a-dataset):** Temporarily remove datasets from public access
- **[Revert to draft](/user-guide/revert-a-dataset-to-draft):** Move datasets back to draft for further edits
- **[Deprecate](/user-guide/deprecate-datasets):** Mark datasets as outdated or superseded


:::tip Related guides

- **New to datasets?** Learn the [dataset record lifecycle](/user-guide/key-concepts/the-dataset-record-lifecycle) to understand the complete lifecycle.
- **Need more control?** Review [roles and permissions](/user-guide/roles-and-permissions) to understand what actions are available to you.

:::