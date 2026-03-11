---
slug: /view-version-history
sidebar_label: "View version history"
sidebar_position: 3
description: "Track the lineage and evolution of datasets over time."
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# View version history

In this guide

> [Overview](#overview)  
> [View version history](#view-version-history-1)

## Overview

**View version history** to track how datasets have evolved over time. Version history shows you the lineage of a dataset, including all previous and subsequent versions, along with a comparison of what changed between versions.

When [a new version is published](/user-guide/create-dataset-versions), the system automatically deprecates the old version and updates the version chain. Email notifications are sent to stakeholders of the old dataset, informing them about the availability of the newer version.

## View version history

To view the version history of a dataset:

1. Browse or search for the dataset you want to view. You can identify versioned datasets by the info panel on the dataset card.

    For the current **(published)** version, the info panel indicates that newer version exists with a link to it. 
 
      <img src={useBaseUrl('/manage-datasets/versioned-dataset-info-panel.png')} alt="Screenshot showing the info panel on a current published version" width="600" />

    For the previous **(deprecated)** version, the info panel indicates that newer version exists with a link to it.
 
      <img src={useBaseUrl('/manage-datasets/deprecated-dataset-after-versioning-info-panel.png')} alt="Screenshot showing the info panel on a deprecated version" width="600" />

2. Select **View** on the dataset card, and then select **View Changes**. 

      <img src={useBaseUrl('/manage-datasets/view-changes.png')} alt="Screenshot showing the View Changes button" width="800" />

    Alternatively, you can select **More**, and then **Versions**. The version history appears on the Versions tab.

3. Select **Show Changes** to expand the version comparison panel. 


      <img src={useBaseUrl('/manage-datasets/show-changes.png')} alt="Screenshot showing the More menu with Versions option" width="800"/>


    Green highlights indicate the current version (what's added), while red highlights indicate the previous version (what's removed). 


      <img src={useBaseUrl('/manage-datasets/green-and-red-highlights.png')} alt="Screenshot showing the More menu with Versions option" width="800"/>


