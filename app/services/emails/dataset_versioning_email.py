from typing import List, Optional
from fastapi import Depends
from services.email_service import EmailService, EmailRecipient
from models.dataset import Dataset


class DatasetVersioningEmailService(EmailService):

    def notify_old_dataset_deprecated(
        self,
        dataset: Dataset,
        newer_dataset: Dataset,
    ):
        recipients = self._get_notification_recipients(dataset)

        if not recipients:
            return

        dataset_link = self._create_dataset_link(dataset.id)
        newer_dataset_link = (
            self._create_dataset_link(newer_dataset.id) if newer_dataset else None
        )
        newer_dataset_title = newer_dataset.title if newer_dataset else None

        self._send_emails(
            recipients,
            "DATASET_DEPRECATED_WITH_NEW_VERSION",
            dataset_title=dataset.title,
            dataset_link=dataset_link,
            newer_dataset_link=newer_dataset_link,
            newer_dataset_title=newer_dataset_title,
        )

    def _get_notification_recipients(
        self,
        dataset: Dataset,
    ) -> List[EmailRecipient]:
        recipients = (
            self._get_dataset_contacts_and_roles_manager_and_all_and_all_org_roles(
                dataset
            )
        )

        unique_recipients = {r.email: r for r in recipients}.values()

        return list(unique_recipients)
