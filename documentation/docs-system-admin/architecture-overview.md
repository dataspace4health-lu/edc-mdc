---
sidebar_position: 1
---

# Architecture overview

Metadata Capture is an open-source platform that you can deploy in your organisation's infrastructure. This self-hosted deployment model gives you complete control over the application. Before you begin deployment, understand the application architecture so you can prepare your environment.

The **Metadata Capture application** is a modular platform that integrates several components to enable secure, scalable dataset management. The following figure illustrates the high-level architecture of the system.

```mermaid
---
title: "Architecture overview of Metadata Capture"
---

flowchart LR
    User["User"]
    Browser["Web browser <br/> (Client)"]
    MetaApp["Metadata Capture application"]
    IAM["Identity and Access Management"]
    SMTP["SMTP server"]
    DB["Centralised database (PostgreSQL)"]

    User -- "Accesses" --> Browser
    Browser -- "Sends requests" --> MetaApp
    Browser -- "Authenticates" <--> IAM
    MetaApp -- "Validates identity" --> IAM
    MetaApp -- "Sends notifications" --> SMTP
    MetaApp -- "Reads/Writes data" --> DB

    style User fill:#D2D9DB,color:#24388C,stroke:#B5BFC4
    style MetaApp fill:#4EAEDC,color:#FFFFFF,stroke:#24388C
    style Browser fill:#FFFFFF,color:#414547,stroke:#B5BFC4
    style IAM fill:#6EC0A7,color:#FFFFFF,stroke:#24388C
    style SMTP fill:#6EC0A7,color:#FFFFFF,stroke:#24388C
    style DB fill:#FFE066,color:#414547,stroke:#B8941A,stroke-width:0.3px
```
<br/>

Metadata Capture integrates with your organisational infrastructure and is designed for flexible deployment. Here’s what you need to know before you begin deployment:

- **Core application:** The Metadata Capture application includes both a frontend (user interface) and backend services, designed to run on your infrastructure. Your users interact with the system through their web browser, which communicates directly with the application.

- **Authentication & access control:** The application relies on an external OpenID Connect **(OIDC)** provider to manage authentication and user permissions. Your organisation must have its own Identity and Access Management **(IAM)** system, which controls access and role assignments within Metadata Capture.

- **Centralised database:** Metadata Capture stores and retrieves all application data using a **PostgreSQL** database. Your organisation must provide its own PostgreSQL instance and grant Metadata Capture secure access to the database.

- **Email notifications:** Metadata Capture includes a notification feature that sends emails to relevant users during key events of the dataset record lifecycle. For example, it sends an email when a dataset is submitted for validation, or when it is approved for publication. Your organisation must configure its own **SMTP server** to deliver these notifications.

Now that you understand the architecture, you can prepare your environment and [deploy the Metadata Capture application](deploy-metadata-capture.md).
