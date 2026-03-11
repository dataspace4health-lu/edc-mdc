---
slug: /track-changes
sidebar_label: "Track changes"
sidebar_position: 1
description: "Track and manage changes made to datasets and organisations using activity logs."
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Track changes (Activity logs)

In this guide

> [Overview](#overview)  
> [View activity logs on datasets](#view-activity-logs-on-datasets)  
> [View activity logs on organisations](#view-activity-logs-on-organisations)  
> [Understanding the activity log entries](#understanding-the-activity-log-entries)

## Overview

**Activity logs** provide an automated audit trail of changes and actions performed on datasets. They track who did what and when, ensuring transparency, accountability, and compliance throughout the dataset record lifecycle.

**For example:** If a dataset was unexpectedly reverted to draft without any comments or explanation, you can check the activity log to see who reverted it, when, and review any comments they provided for context.

**How activity logs work:**

- Activity logs are **automatically generated** for every changes made to a dataset or organisation
- Activity logs are permanently stored and cannot be deleted
- Logs include details such as the user who performed the action, timestamp, action type, and specific changes made

## View activity logs on datasets

To view the activity log for a dataset:

1. Search for the dataset and select **View**.

2. Select **More** and then the **Activity Log** tab. The activity log displays all recorded actions for the dataset with the most recent activity at the top.

<figure>
  <img src={useBaseUrl('/manage-datasets/view-activity-logs.png')} alt="Screenshot showing how to view activity logs" width="800" />
    <figcaption> </figcaption>
</figure>

## View activity logs on organisations

1. Select the entity icon in the top right corner, and select Orgs & Contacts.

2. Select the organisation you want to view.

3. Select the **Log** on the upper right side of the page. The activity log displays all recorded actions for the organisation with the most recent activity at the top.

<figure>
  <img src={useBaseUrl('/manage-datasets/view-organisation-logs.png')} alt="Screenshot showing how to view organisation activity logs" width="800" />
    <figcaption> </figcaption>
</figure>

## Understanding the activity log entries

Each log entry provides the following details:

- **Timestamp**: Date and time when the action occurred
- **User**: Name or identifier of the person who performed the action
- **Action type**: What was done (e.g., "Created", "Updated", "Published", "Status changed")
- **Details**: Specific changes made or additional context

Common action types include:

- **Created**: Dataset was initially created
- **Status changed**: Dataset moved to a different workflow stage (for example, from Draft to Completed)
- **Published / Unpublished**: Dataset was published or removed from publication
- **Updated**: Metadata fields were modified
- **Distribution added/updated/deleted**: Changes to dataset distributions
- **Data dictionary modified**: Changes to data dictionary entries
- **Validated / Approved**: Dataset passed validation or approval stages
- **Reverted to draft**: Dataset was moved back to draft state for further edits



