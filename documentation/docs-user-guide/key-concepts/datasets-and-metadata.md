---
slug: /what-is-a-dataset
sidebar_label: "What is a dataset?"
sidebar_position: 1
description: "Learn the concept of datasets and how you manage them with Metadata Capture."
---

# What is a dataset?

Metadata Capture is designed around the concepts of **datasets**, **metadata**, and **data lifecycle management**.  These concepts shape your interactions within Metadata Capture.

## What is a dataset?

To understand what a **dataset** means in Metadata Capture, you must first understand metadata. **Metadata** is information that describes a certain data asset, providing context and meaning to raw data. For example:

- A *patient record* in a hospital system may have metadata describing the *record date* and *data sensitivity level*.
- A *transport schedule dataset* may have metadata describing the *route coverage* and *vehicle types*.

Within Metadata Capture, a **dataset** is a catalogued record of this metadata, structured according to the [DCAT-AP-LU standards](https://mindig_lu.gitlab.io/DCAT-AP-LU/). Datasets describe the content, context, and accessibility of your data assets. It includes various properties and attributes about the data, such as the title, description, publisher, keywords, and access rights. 

:::tip Know your terms

**Metadata** as a set of details that describes your data, while a **dataset** is a structured record of this metadata. Datasets contain information about the data, **not** the data itself.

:::

## Why datasets matter

Datasets are essential for effective data management, sharing, and reuse. 

Organisations across domains—such as in health, environment, and government—need access to accurate and comprehensive data for research, policy making, and other purposes. For example, health organisations may need access to specific health data to control disease outbreaks.

For organisations to effectively share and reuse data among themselves, they must have a clear understanding of the data's context, quality, and accessibility. The first step to sharing data is documenting it so that others can find and understand it. This is where documenting datasets becomes crucial. 

## Data holders and data consumers

**Data holders** (or data providers) are organisations or entities that collect raw data directly from sources. For example, a *hospital* may collect health information directly from a patient. As a data holder, you are responsible for securely maintaining and disseminating data within your domain.  

**Data users** (or data consumers) are organisations or individuals that reuse data collected by data holders. For example, a *researcher* may use patient health data collected by hospitals for analysis.  As a data consumer, you are responsible for using data in compliance with applicable laws and regulations.


## Managing datasets with Metadata Capture

**Metadata Capture** acts as a bridge between **data holders** and **data consumers**, enabling data holders to document well-structured datasets (metadata records) without accessing the underlying data—ensuring information is discoverable and shared in line with data governance and compliance. The platform supports the full [dataset record lifecycle](/user-guide/key-concepts/the-dataset-record-lifecycle), allowing you to update, version, or retire datasets as your data changes. Read more [about Metadata Capture](/user-guide/what-is-mdc).
