---
slug: /what-is-mdc
sidebar_position: 100
sidebar_label:  "About Metadata Capture"
description: "Learn about Metadata Capture, its purpose, features, and how it supports data holders and data consumers."
---

import FeatureFlag from '@site/src/components/FeatureFlag';

# About Metadata Capture

**Metadata Capture** is a platform that helps organisations catalogue, manage, and publish datasets. Each **dataset** is a metadata record that describes a specific data asset held by your organisation. By documenting your data holdings as datasets, Metadata Capture makes your information discoverable and ready for sharing or reuse.

Metadata Capture is designed for **data holders**—organisations that collect and maintain data—such as government agencies, healthcare providers, and private sector entities. By documenting your data holdings as datasets, Metadata Capture makes your information discoverable and ready for sharing or reuse.

<FeatureFlag flag="enable_multi_tenants">
The platform was created as part of the **Data Government Act (DGA)** initiative, which requires public organisations to make their data available for reuse across the public ecosystem. It enables you to systematically prepare your data holdings for sharing through rich metadata documentation, while ensuring compliance with the Data Catalogue Vocabulary Application Profile - Luxembourg ([DCAT-AP-LU](https://mindig_lu.gitlab.io/DCAT-AP-LU/)).
</FeatureFlag>

<FeatureFlag flag="enable_multi_tenants" inverse>
The platform helps you establish effective data governance within your organisation. It enables you to catalogue and manage metadata about your data assets, supporting internal discovery and preparing datasets for potential external sharing—all while ensuring compliance with the Data Catalogue Vocabulary Application Profile - Luxembourg ([DCAT-AP-LU](https://mindig_lu.gitlab.io/DCAT-AP-LU/)).
</FeatureFlag>

## How it works

The platform supports a collaborative workflow for preparing your data for sharing. As a dta holder, you can use Metadata Capture to:

- **Document your data:** Create datasets that describe your data holdings with structured metadata, including details about content, format, and access requirements.
- **Collaborate across teams:** Work with colleagues in different roles to review, validate, and approve datasets before publication.
- **Publish for discovery:** Make datasets available within your organisation or across organisations, enabling data consumers to find and request the data they need.

:::tip Data access

**Metadata Capture** does *not* access or store your underlying data. Instead, it enables you to describe your available data so others can find and request what they need.

:::

## Data holders and data consumers

Metadata Capture acts as a bridge between these two groups: data holders and data consumers.

**Data holders** are organisations that collect and maintain data. If you're a data holder, you use Metadata Capture to document your data holdings and make them discoverable for sharing.

**Data consumers** are organisations or individuals looking for specific data to support their work. As a data consumer, you search for available datasets—either directly through Metadata Capture or through connected data portals, depending on your organisation's setup.


## Accessing Metadata Capture

As an organisation, you can use Metadata Capture in two ways:

- **Managed access:** If your organisation is part of a larger ecosystem (such as government agencies under the Ministry for Digitalisation), you may have specific access requirements. Contact your system administrator for more information.
- **Self-hosting:** If your organisation prefers to manage its own instance of Metadata Capture, you can deploy it in your private environment. This option provides greater control over data and configurations.

## Key features

Metadata Capture provides comprehensive functionality to support your data catalogue management:

### dataset record lifecycle management
Manage datasets through their complete lifecycle with a structured approval workflow. Create draft datasets, submit them for review, validate accuracy, approve for publication, and publish to make them discoverable. You can also unpublish or deprecate datasets when they're no longer needed, ensuring your catalogue stays current.

### Collaborative workflows
Enable seamless teamwork across different roles in your organisation. Multiple team members can contribute at different stages—editors create datasets, reviewers validate accuracy, and approvers authorise publication. Built-in commenting allows teams to provide feedback and context at each stage, while the ability to revert datasets ensures corrections can be made when needed.

### Rich metadata documentation
Create comprehensive dataset descriptions that go beyond basic information. Add data dictionaries to document individual fields with their meanings, data types, and constraints. Link related datasets together, specify multiple distribution formats, identify authentic sources for specific data fields, and provide detailed attribution for contributors and data sources.

### Controlled vocabularies
Maintain consistency across your catalogue with standardised terminology. Tag datasets with keywords for better discoverability, link them to applicable legislation and regulations, and manage a central registry of organisations that serve as publishers, creators, and contact points for your datasets.

### Access controls and permissions  
Control who can view and modify datasets with role-based permissions. Assign specific capabilities to editors, reviewers, and approvers. In multi-organisation setups, control dataset visibility across organisations, or restrict sensitive datasets to internal-only access while maintaining full documentation.

### Bulk operations
Save time with efficient bulk operations. Upload multiple datasets at once using Excel templates, making it easy to migrate existing catalogues or add large numbers of datasets quickly while maintaining data quality and consistency.

### Search and discoverability
Help users find the data they need with powerful search capabilities. Filter datasets by keywords, organisations, publication status, and other criteria. View datasets organised by their workflow stage (draft, validated, published), and in multi-organisation setups, discover datasets across different organisations.

### Standards compliance
Ensure your metadata meets international and national data standards. All datasets are structured according to the DCAT-AP-LU standard (Data Catalogue Vocabulary Application Profile - Luxembourg), ensuring consistency and interoperability with other data catalogues. Track all changes with comprehensive activity logging for accountability and audit purposes.

### System integration
Work seamlessly with your existing infrastructure. Integrate with your organisation's identity management system through single sign-on (SSO) for streamlined user authentication. Upload multiple datasets efficiently using Excel templates, and deploy the application either as a managed service or in your own environment for complete control over configurations and data.
