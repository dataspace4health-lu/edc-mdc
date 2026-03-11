---
slug: /dashboard-overview
sidebar_label: "Navigate the dashboard"
sidebar_position: 4
description: "Understand the main components of the Metadata Capture dashboard and how to navigate them."
---
import FeatureFlag from '@site/src/components/FeatureFlag';
import useBaseUrl from '@docusaurus/useBaseUrl';


# Navigate the dashboard

The Metadata Capture interface consists of a **main menu** bar at the top of the page and a **working area** below it. The working area displays the content based on your selection from the main menu. 

:::tip Don't see any datasets?

If it's your first time signing in, you may see an empty panel. [Check your permissions](/user-guide/check-your-permissions) or [add your first dataset](/user-guide/add-a-dataset).

:::

<img src={useBaseUrl('/get-started/empty-dashboard.png')} alt="Filters panel with various filter options" />

## The main menu

The **main menu** is located at the top right corner of the page and provides quick access to global functions. 

<img src={useBaseUrl('/get-started/main-toolbar.png')} alt=" Screenshot of the main toolbar with global functions" width="800" />

- (<svg xmlns="http://www.w3.org/2000/svg" style={{display:"inline",verticalAlign:"middle",width:"1em",height:"1em"}} fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M4 16.5v-13h-.25a.75.75 0 010-1.5h12.5a.75.75 0 010 1.5H16v13h.25a.75.75 0 010 1.5h-3.5a.75.75 0 01-.75-.75v-2.5a.75.75 0 00-.75-.75h-2.5a.75.75 0 00-.75.75v2.5a.75.75 0 01-.75.75h-3.5a.75.75 0 010-1.5H4zm3-11a.5.5 0 01.5-.5h1a.5.5 0 01.5.5v1a.5.5 0 01-.5.5h-1a.5.5 0 01-.5-.5v-1zM7.5 9a.5.5 0 00-.5.5v1a.5.5 0 00.5.5h1a.5.5 0 00.5-.5v-1a.5.5 0 00-.5-.5h-1zM11 5.5a.5.5 0 01.5-.5h1a.5.5 0 01.5.5v1a.5.5 0 01-.5.5h-1a.5.5 0 01-.5-.5v-1zm.5 3.5a.5.5 0 00-.5.5v1a.5.5 0 00.5.5h1a.5.5 0 00.5-.5v-1a.5.5 0 00-.5-.5h-1z" clipRule="evenodd"/></svg>) 
**Switch org:** Switch between different organisations if you have access to more than one.  
- (<svg xmlns="http://www.w3.org/2000/svg" style={{display:"inline",verticalAlign:"middle",width:"1em",height:"1em"}} fill="none" viewBox="0 0 24 24" stroke="currentColor"><circle cx="12" cy="12" r="9" strokeWidth="1.5"/><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 8v8m4-4H8"/></svg>) 
**Add dataset:** Create a new dataset.  
- (<svg xmlns="http://www.w3.org/2000/svg" style={{display:"inline",verticalAlign:"middle",width:"1em",height:"1em"}} fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M9.293 2.293a1 1 0 011.414 0l7 7A1 1 0 0117 11h-1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-3a1 1 0 00-1-1H9a1 1 0 00-1 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-6H3a1 1 0 01-.707-1.707l7-7z" clipRule="evenodd"/></svg>)
**Home:** Go back to the dashboard from anywhere in the application.
- (<svg xmlns="http://www.w3.org/2000/svg" style={{display:"inline",verticalAlign:"middle",width:"1em",height:"1em"}} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 16V4m0 0l-4 4m4-4l4 4"/><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M20 16v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2"/></svg>) 
**Upload:** Upload datasets from a file.
- (<svg xmlns="http://www.w3.org/2000/svg" style={{display:"inline",verticalAlign:"middle",width:"1em",height:"1em"}} fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M2.5 3A1.5 1.5 0 0 0 1 4.5v4A1.5 1.5 0 0 0 2.5 10h6A1.5 1.5 0 0 0 10 8.5v-4A1.5 1.5 0 0 0 8.5 3h-6Zm11 2A1.5 1.5 0 0 0 12 6.5v7a1.5 1.5 0 0 0 1.5 1.5h4a1.5 1.5 0 0 0 1.5-1.5v-7A1.5 1.5 0 0 0 17.5 5h-4Zm-10 7A1.5 1.5 0 0 0 2 13.5v2A1.5 1.5 0 0 0 3.5 17h6a1.5 1.5 0 0 0 1.5-1.5v-2A1.5 1.5 0 0 0 9.5 12h-6Z" clipRule="evenodd"/></svg>) 
**Vocabulary and entities:** Manage controlled vocabularies like keywords and legislations.
- (<svg xmlns="http://www.w3.org/2000/svg" style={{display:"inline",verticalAlign:"middle",width:"1em",height:"1em"}} fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M7.84 1.804A1 1 0 018.82 1h2.36a1 1 0 01.98.804l.331 1.652a6.993 6.993 0 011.929 1.115l1.598-.54a1 1 0 011.186.447l1.18 2.044a1 1 0 01-.205 1.251l-1.267 1.113a7.047 7.047 0 010 2.228l1.267 1.113a1 1 0 01.206 1.25l-1.18 2.045a1 1 0 01-1.187.447l-1.598-.54a6.993 6.993 0 01-1.929 1.115l-.33 1.652a1 1 0 01-.98.804H8.82a1 1 0 01-.98-.804l-.331-1.652a6.993 6.993 0 01-1.929-1.115l-1.598.54a1 1 0 01-1.186-.447l-1.18-2.044a1 1 0 01.205-1.251l1.267-1.114a7.05 7.05 0 010-2.227L1.821 7.773a1 1 0 01-.206-1.25l1.18-2.045a1 1 0 011.187-.447l1.598.54A6.993 6.993 0 017.51 3.456l.33-1.652zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd"/></svg>) 
**Settings:** Access advanced actions like managing keywords, legislations, data services, and organisations.
- (<svg xmlns="http://www.w3.org/2000/svg" style={{display:"inline",verticalAlign:"middle",width:"1em",height:"1em"}} fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 0010 16a5.986 5.986 0 004.546-2.084A5 5 0 0010 11z" clipRule="evenodd"/></svg>) 
**Profile:** View your profile and roles.


## The dashboard (home page)

The Metadata Capture **dashboard** is the default view of the working area, where you can manage and view datasets. Everything you see in the dashboard is specific to the **organisation** you select and the **roles** assigned to you within that organisation.


The dashboard has the following components:

- **Filters panel** (left): Filter datasets based on key crieteria defined when the dataset was created.
- **Dataset panel** (right): Manage datasets throughout their lifecycle.
- **Search bar** (top of datasets panel): Search datasets by any keyword or phrase.


### Filters and search 

Use the **filters** and **search** to find datasets quickly. Datasets are displayed based on the filters you apply and the search terms you enter.

<img src={useBaseUrl('/get-started/search-and-filter.gif')} alt="A GIF demonstrating the search and filter functionality"  />

<br/>
<br/>

:::tip  Combine filters and search

Use **filters** and **search** together to progressively refine your results. For example, if you search for "transport", you'll see all datasets related to transport. Then, if you apply a **Keyword** filter, you'll find datasets related to transport that are tagged with the keyword. 

:::

### Dataset panel

The **dataset panel** is where you view and manage dataset metadata throughout their lifecycle.
<FeatureFlag flag="enable_multi_tenants">
Your access to metadata in this panel and their available actions depend on the role assigned to you and the organisation you are currently viewing.
</FeatureFlag>

<img src={useBaseUrl('/get-started/dataset-panel-tabs.gif')} alt="A GIF demonstrating the dataset panel tabs with the different lifecycle stages" />

Datasets are displayed in **tabs**, each representing a stage in the dataset record lifecycle:

- **Draft**: Datasets that have been added or are being edited.
- **Completed**: Datasets that are ready for review and validation.
- **Validated**: Datasets that have been reviewed and are awaiting approval.
- **Approved**: Datasets that have been approved and are ready for publication.
- **Published**: Datasets that are live and accessible to all organisations.
- **Internal Only**: Datasets that are live and accessible within your organisation.
- **Deprecated**: Datasets that are no longer in use or have been replaced by newer versions.

### View dataset details

Select **View** on any dataset to access its complete information across multiple tabs:

<img src={useBaseUrl('/get-started/view-dataset-details.gif')}  alt="A GIF showing how to navigate the tabs of the dataset details" />  <br/>

<br/>

- **Dataset**: Core metadata (title, description, keywords, themes, etc.)
- **Distributions**: Download and access options 
- **Data Dictionary**: Field-level documentation 
- **Relations**: Links to related datasets 
- **Comments**: Collaboration and feedback history
- **Activity Logs**: Complete change and audit trail

See [dataset enhancements](/user-guide/enhance-your-datasets) and [vocabulary management](/user-guide/manage-vocabularies) to learn more about these tabs.