---
sidebar_position: 6
---

# Configure email notifications

Metadata Capture sends automated email notifications to users during key events in the dataset record lifecycle. Configure your SMTP server and customise email templates to enable effective communication within your organisation.

In this guide  
> [Set up SMTP server](#set-up-smtp-server)  
> [Customise email templates](#customise-email-templates)  
> [Available template variables](#available-template-variables)

## Set up SMTP server

Configure your SMTP server settings to enable the application to send email notifications.

1. Configure the SMTP environment variables in your [`.env` file](deploy-metadata-capture.md#configure-your-environment). Here's an example configuration:

   ```bash
   SMTP_SERVER=localhost
   SMTP_PORT=1025
   SMTP_USERNAME=smtp-username
   SMTP_PASSWORD=smtp-password
   SENDER_EMAIL=sender@email.com
   ```

2. Test your SMTP configuration. Run the application and trigger a test notification to verify email delivery.

    :::info SMTP requirements

    Your organisation must provide its own SMTP server as described in the [architecture overview](architecture-overview.md). Metadata Capture does not include a built-in email service.

    :::

## Customise email templates

Email templates determine the subject line and content of notifications sent during dataset record lifecycle events. Customise these templates in your `config.json` file to match your organisation's communication style.

1. Edit the configuration file as described in [configure the application](configure-the-application.md).

2. Modify the `email_templates` section with your custom messages:

   ```json
   {
     "email_templates": {
       "DATASET_COMPLETED": {
         "subject": "Dataset ready for validation: $dataset_title",
         "body": "Dear $recipient_name,\n\nA dataset has been submitted and is ready for validation.\n\nDataset: $dataset_title\nLink: $dataset_link\n\nPlease review and validate this dataset at your earliest convenience.\n\nThank you."
       },
       "DATASET_VALIDATED": {
         "subject": "Dataset ready for approval: $dataset_title", 
         "body": "Dear $recipient_name,\n\nA dataset has been validated and is ready for your approval.\n\nDataset: $dataset_title\nLink: $dataset_link\n\nPlease review and approve this dataset at your earliest convenience.\n\nThank you."
       },
       "DATASET_APPROVED": {
         "subject": "Dataset approved: $dataset_title",
         "body": "Dear $recipient_name,\n\nA dataset has been approved and is ready for publication.\n\nDataset: $dataset_title\nLink: $dataset_link\n\nThank you."
       },
       "DATASET_BACK_TO_DRAFT": {
         "subject": "Dataset returned to draft: $dataset_title",
         "body": "Dear $recipient_name,\n\nA dataset has been returned to draft status and requires further review.\n\nDataset: $dataset_title\nLink: $dataset_link\n\nPlease review the feedback and resubmit this dataset at your earliest convenience.\n\nThank you."
       }
     }
   }
   ```

    <br/>

    :::tip Email template design

    Design templates that provide clear, actionable messages to recipients. Include relevant dataset details and direct links to help your users complete their tasks efficiently.

    :::


## Available template variables

Use the following variables in your email templates to include dynamic content:

| Variable | Description |
|----------|-------------|
| `$dataset_title` | Title of the dataset |
| `$dataset_link` | Direct link to the dataset in the application |
| `$recipient_name` | Name of the email recipient |
| `$sender_name` | Name of the user who triggered the notification |
| `$organisation_name` | Name of the dataset's organisation |

<br/>

:::note Well done!

Now that you have configured email notifications, you can review your configurations and [deploy the application](deploy-metadata-capture.md#deploy-the-application).

:::
