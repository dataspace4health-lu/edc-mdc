---
slug: /bulk-upload-datasets
sidebar_label: "Bulk upload datasets"
sidebar_position: 2
description: "Save time by uploading multiple datasets at once using an Excel template."
---

import FeatureFlag from '@site/src/components/FeatureFlag';
import useBaseUrl from '@docusaurus/useBaseUrl';

# Bulk upload datasets

In this guide

> [Overview](#overview)  
> [Understand the Excel template](#understand-the-excel-template)  
> [Bulk upload datasets](#bulk-upload-datasets-1)

## Overview

**Upload multiple datasets** at once using a single Excel file. A template file is available for you to fill out with your dataset information. Bulk upload saves time especially when:

- **Migrating datasets** into Metadata Capture
- **Creating new keywords** that are not yet in your organisation's [controlled vocabularies](/user-guide/manage-vocabularies). 

To understand the dataset record lifecycle after creation, see: [The dataset record lifecycle](/user-guide/key-concepts/the-dataset-record-lifecycle).


## Bulk upload datasets

To add datasets in bulk, you must be an Editor or have the permission to **add datasets**. Check your [permissions](/user-guide/check-your-permissions).


1. Select the upload icon (<svg xmlns="http://www.w3.org/2000/svg" style={{display:"inline",verticalAlign:"middle",width:"1em",height:"1em"}} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 16V4m0 0l-4 4m4-4l4 4"/><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M20 16v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2"/></svg>) on the main menu. 

   <img src={useBaseUrl('/manage-datasets/upload-datasets.png')} alt="Screenshot of the upload dataset button" width="750" />

2. Select **Download Sample Excel Template**. The template downloads as an `.xlsm` file that you can open in Excel.

   <img src={useBaseUrl('/manage-datasets/download-template.png')} alt="Screenshot of the download excel template button" width="750" />

3. Review the README sheet for guidance and template conventions, or see: [Understand the Excel template](#understand-the-excel-template).
   
   <img src={useBaseUrl('/manage-datasets/template-sheets.png')} alt="Screenshot of the readme sheet in the bulk upload template" width="750" />

4. Fill out the **DatasetTemplate** sheet with your dataset information. Use the **ControlledVocabularies** sheet to find valid values for formatted fields (green headers). 

4. (Optional) Fill out the **DistributionTemplate** sheet:
   - Link distributions to datasets using the **DataSet Title** column (must match exactly)
   - Each row represents one distribution (access method) for a dataset
   - A single dataset can have multiple distributions—for example, one for raw data and another for statistical analysis
   - Provide the **Access URL** (mandatory) and **Format** (recommended) for each distribution

5. (Optional) Fill out the **DataDictionaryTemplate** sheet:
   - Link data dictionary entries to datasets using the **DataSet Title** column (must match exactly)
   - Document each field or column that exists in your actual data source—for example, if your data contains fields like *Employee ID*, *Name*, *Department*, and *Hire Date*, list each one with its description and data type
   - Specify data type (Integer, String, Boolean, Date, etc.) for each field
   - Mark personally identifiable variables using `TRUE` or `FALSE`
   - Data dictionary entries help Data Users understand what fields they'll see when accessing your dataset

6. Save your completed file.

    :::info Keyword management

    Any **new keywords** you include in the upload file are automatically created as part of the upload process. While this simplifies keyword management, **ensure keywords are well-defined and relevant** to improve dataset discoverability. Learn more about [keywords](/user-guide/add-a-keyword) and vocabulary management.

    :::  

7. Return to Metadata Capture and select **Upload Excel file**, then select your completed file.

8. Select **Create Dataset**. The system processes your file and creates the datasets with their associated distributions and data dictionaries.

9. After processing completes, the dashboard opens and your new datasets appear in the **Draft** tab. 

:::tip What's next?

Well done! Now that you have created the datasets, you must [**submit them for review**](/user-guide/submit-datasets-for-review) to move them through the publication process. 
 
:::


## Understand the Excel template

Before you begin, download and review the bulk upload Excel template to familiarise yourself with its structure and requirements. The template file contains **three template sheets** designed to capture different aspects of your datasets (and two reference sheets):

<img src={useBaseUrl('/manage-datasets/template-sheets-all.png')} alt="Screenshot of the different sheets in the bulk upload template" width="750" />

- **README:** Contains guidance and conventions for filling out the template
- **DatasetTemplate:** Use this sheet to enter core dataset metadata fields (title, keywords, etc.)
- **DistributionTemplate:** Use this sheet to enter information about how users can access your datasets
- **DataDictionaryTemplate:** Use this sheet to describe the structure and meaning of your dataset fields
- **ControlledVocabularies:** Reference sheet with DCAT-AP-LU controlled vocabularies for formatted fields. Use this to find valid values when filling out the "Template" columens with green headers.

:::tip Template conventions

- **Green headers:** Cells with controlled vocabularies or formatting rules—efer to the ControlledVocabularies sheet for values.
- **Fields with `**`:** Mandatory—imports fail without these values
- **Fields with `*`:** Recommended for metadata quality
- **Use the pipe character (`|`):** To separate multiple values in a single cell. For example: `health|society|policy`
- **Light grey texts:** Shows examples for reference

:::