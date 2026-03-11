---
slug: /add-a-dataset
sidebar_label: "Create new datasets"
sidebar_position: 1
description: "Document your organisation's data holdings by creating new datasets."
---
import FeatureFlag from '@site/src/components/FeatureFlag';
import useBaseUrl from '@docusaurus/useBaseUrl';

# Create new datasets

In this guide  
> [Overview](#overview)  
> [Create a dataset](#create-a-dataset)

## Overview

**Create datasets** to document and catalogue information about your organisation's data holdings. Providing rich metadata through well-structured datasets improves data discoverability, understanding, and reuse among data consumers.
 
There are two ways to create datasets:

- **Individually:** (This guide) Add datasets one at a time through the dataset editor. 
- **Using bulk upload:** Add multiple datasets at once using an Excel file. See [bulk upload](/user-guide/bulk-upload-datasets).

If you're new to creating datasets, start with understanding the [dataset record lifecycle](/user-guide/category/understand-datasets). 


## Create a dataset

To create a dataset, you must be an Editor or have the permission to **add datasets**. 

1. Select **Add dataset** on the main menu. 

   <img src={useBaseUrl('/manage-datasets/add-dataset.png')} alt="Screenshot of the add dataset button" width="750" />

2. Fill out the dataset form. For guidance on filling out the form, see the definition of properties in the [DCAT-AP-LU Vocabulary<sup>↗</sup>](https://mindig_lu.gitlab.io/DCAT-AP-LU/#Dataset).

:::caution
All mandatory fields (marked with * ) must be filled in to successfully proceed to step 3.
:::

 :::tip Dropdown lists

   **All dropdown lists** are pre-defined based on the [DCAT-AP-LU Vocabulary<sup>↗</sup>](https://mindig_lu.gitlab.io/DCAT-AP-LU/#controlled-vocs) or your organisation's [controlled vocabularies](/user-guide/manage-vocabularies). To suggest additional options in the lists, contact your Catalogue Manager or system administrator.

   ::: 

   <img src={useBaseUrl('/manage-datasets/create-dataset-form.png')} alt="Screenshot showing the create dataset form" width="750" />

   
3. Select **Preview & Save** and review the dataset details.

4. Select **Save as Draft**. The dataset is now saved in the **Draft** tab, while the dataset editor remains open. 

:::tip Continue later

Your dataset is now saved. To continue editing later, select **Cancel** to close the dataset editor and come back to it from the **Draft** tab when you're ready. 

:::

5. (Optional) On the left panel, select any option to enhance your dataset. 

   <img src={useBaseUrl('/manage-datasets/enhancement-options-in-dataset-editor.png')} alt="Screenshot showing enhancement options in the dataset editor" width="750" />


      For a step-by-step guide on adding these details, see:

         - [Add distributions](/user-guide/add-distributions) (Select **Edit Dataset** to access this option)
         - [Add a data dictionary](/user-guide/add-a-data-dictionary)
         - [Manage dataset relations](/user-guide/manage-dataset-relations)
         - [Add qualified attributions](/user-guide/add-qualified-attributions)
   
6. After completing your dataset enhancements, go back to the **Edit Dataset** page and select **Preview & Save**. The dataset preview appears. Edits made in other sections are saved automatically, also you may exist the process using Home button. 

7. Review your dataset details in the preview. When you're ready, [submit the dataset for review](/user-guide/submit-datasets-for-review).

:::tip What's next?

Now that you've created your dataset,  [**submit it for review**](/user-guide/submit-datasets-for-review) or continue [**adding enhancements**](/user-guide/category/enhance-datasets).

:::






