---
slug: /assign-authentic-source
sidebar_label: "Assign authentic source"
sidebar_position: 6
description: "Establish data trustworthiness by assigning authentic source labels to dataset fields."
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Assign authentic source

In this guide

> [Overview](#overview)  
> [Assign an authentic source](#assign-an-authentic-source)  
> [Manage authentic source labels](#manage-authentic-source-labels)


## Overview

Assign **authentic source** labels to specific fields in your dataset's data dictionary to indicate which source is the most reliable and authoritative for that information. This establishes clear data governance standards and helps Data Users identify the most trustworthy source when the same data element appears in multiple datasets. 


**When to use authentic source:** When data is collected from multiple sources, certain sources may be more reliable than others for specific fields. By assigning an authentic source label, you provide clear guidance to Data Users about which source to trust for particular information. This helps prevent data duplication and inconsistencies.

**For example:** A researcher needs demographic data including age, gender, and address. Address information may appear in multiple datasets—a clinic registration database, a government ID database, and an employment database. Each may contain different addresses depending on when and how the data was collected. By assigning the government ID database as the authentic source for the address field, you indicate to the researcher that this is the most reliable source for address information.

**How authentic source works:**
- Can only be assigned to [published](/user-guide/publish-a-dataset) datasets
- Applied at the **field level** within the [data dictionary](/user-guide/add-a-data-dictionary) of a dataset
- Persists even if a dataset is unpublished (reverted to its Approved state) or deprecated—authentic source labels remain until you manually remove them while the dataset is in Published state.

## Assign an authentic source

To assign authentic source labels, you must be a Catalogue Manager or have the permission to **assign authentic source**. Check your [permissions](/user-guide/check-your-permissions).

1. Ensure the dataset is in **Published** state, or [publish it](/user-guide/publish-a-dataset) if needed.

2. Select **View** on the dataset you want to assign an authentic source to.

3. Select the **Data Dictionary** tab. The data fields appear in table form.

4. Select the toggle under the **Authentic Source** column of the field you want to assign an authentic source to. The label field for entering the authentic source appears.

5. Enter the name and description of the organisation or entity that is the authentic source for this field. In this example, we enter *National Telecom Registry* as the authentic source for the *Phone number* field. 

<figure>
      <img src={useBaseUrl('/enhance-datasets/assign-authentic-source.png')} alt="Screenshot of assigning an authentic source label to a data dictionary field" width="700" />
      <figcaption> </figcaption>
</figure>

You can assign different authentic sources to **different fields** within the same dataset. In this example, you can assign a different authentic source for the *Entity code* field.

   
6. Select **Create Label**. The authentic source label is now assigned to the field and appears in the data dictionary.

:::info Label persistence

**Authentic source labels remain** even if the dataset is unpublished or deprecated. Deprecated datasets are no longer usable, while unpublished datasets can only be reverted to the Approved state, preserving the label and overall dataset integrity. To remove authentic source labels, you must [manually turn them off](#manage-authentic-source-labels) in the data dictionary **while they are in Published state**.
:::


## Manage authentic source labels

After you create authentic source labels, you can edit them or turn them on or off as needed.

1. Go to the **Published** tab and open the dataset containing the authentic source label you want to manage.

2. Select the **Data Dictionary** tab.

3. Locate the field with the authentic source label you want to manage.

4. Select the toggle to turn off or turn on the authentic source assignment for that field.

:::tip Well done

After you assign authentic source labels, Data Users can identify which sources provide the most reliable information for specific data elements. This supports better **data governance** and helps users make informed decisions about which datasets to use for their research or analysis.

:::
