---
slug: /view-and-manage-comments
sidebar_label: "View and manage comments"
sidebar_position: 2
description: "Collaborate and enhance dataset context with comments."
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# View and manage dataset comments

In this guide

> [Overview](#overview)  
> [View dataset comments](#view-dataset-comments)  
> [Delete a comment](#delete-a-comment)  

## Overview 

**Comments** in datasets provide context and communication throughout the dataset record lifecycle. They help you collaborate with others by documenting decisions, asking questions, and providing feedback at each stage of the dataset record lifecycle.

**For example:** As an Approver who is reverting a dataset to draft instead of approving it, you might leave a comment explaining the reason for the decision. Or if you are marking a dataset as internal only, you might leave a comment to inform others why the dataset is restricted.

**How dataset comments work:**

- You can add comments when performing dataset actions (validate, publish, revert to draft, and so on) 
- All comments appear in the **Comments** tab of the dataset details page in chronological order
- Users with the permission to **delete comments** can delete any comment (not just their own)  
- Comments cannot be delete for datasets in the Published and Internal Only states

### View dataset comments

1. Search for the dataset and select **View**. Datasets with comments show a comment icon with the number of comments on the lower left of the dataset card.

<figure>
  <img src={useBaseUrl('/enhance-datasets/comment-icon.png')} alt="Comment icon on dataset card" width="600" />
    <figcaption> </figcaption>
</figure>

2. Select **More** and then **Comments**. The comments tab displays all comments associated with the dataset with the most recent comments at the top.

<figure>
  <img src={useBaseUrl('/enhance-datasets/view-comments.png')} alt="Screenshot showing how to view comments" width="800" />
    <figcaption> </figcaption>
</figure>

## Delete a comment

You can delete comments for datatsets in Draft, Completed, Validated, or Approved status. You must have the permission to **delete comments** to delete dataset comments. Check your [permissions](/user-guide/check-your-permissions).

To delete a comment:

1. Select **View** on the dataset.

2. Locate the comment you want to delete and select the delete icon (🗑️).

3. Select **Confirm** to confirm deletion.

:::warning Delete with caution

Deleted comments cannot be recovered. Comment deletions are logged in the Activity Log for audit purposes.

:::
