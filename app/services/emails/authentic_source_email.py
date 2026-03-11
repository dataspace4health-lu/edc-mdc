from typing import List, Dict
from fastapi import Depends
from services.email_service import EmailService, EmailRecipient
from models.dataset import Dataset


class AuthenticSourceEmailService(EmailService):
    def notify_authentic_source_assignment_changed(
        self,
        dataset: Dataset,
        assignment_changes: List[dict],
        assigner_user_id: int,
    ):
        recipients = self._get_authentic_source_notification_recipients(
            dataset, assigner_user_id
        )

        if not recipients:
            return

        # Get assigner information
        assigner_user = self._user_service.find_by_id(assigner_user_id)
        if not assigner_user:
            return

        # Format assignment changes for email (specific to this dataset's perspective)
        changes_summary = self._format_assignment_changes(
            assignment_changes, dataset.id
        )

        # Create dataset link
        dataset_link = self._create_dataset_link(dataset.id)

        # Send emails
        self._send_emails(
            recipients,
            "AUTHENTIC_SOURCE_ASSIGNMENT_CHANGED",
            dataset_title=dataset.title,
            dataset_link=dataset_link,
            changes_summary=changes_summary,
            assigner_name=assigner_user.name,
            app_url=self._get_app_url(),
        )

    def _get_authentic_source_notification_recipients(
        self, dataset: Dataset, assigner_user_id: int
    ) -> List[EmailRecipient]:
        recipients = (
            self._get_dataset_contacts_and_roles_manager_and_all_and_all_org_roles(
                dataset
            )
        )
        assigner_user = self._user_service.find_by_id(assigner_user_id)
        assigner_email = assigner_user.email if assigner_user else None

        recipients = [r for r in recipients if r.email != assigner_email]

        unique_recipients = {r.email: r for r in recipients}.values()

        return list(unique_recipients)

    def _format_assignment_changes(
        self, assignment_changes: List[dict], dataset_id: int
    ) -> str:
        changes_text = []

        for change in assignment_changes:
            label_name = change["label_name"]
            change_type = change["change_type"]
            old_dataset_id = change.get("old_dataset_id")
            new_dataset_id = change.get("new_dataset_id")

            if change_type == "assigned":
                if new_dataset_id == dataset_id:
                    changes_text.append(f"- {label_name}: Assigned to this dataset")
                else:
                    dataset_link = self._create_dataset_link(new_dataset_id)
                    changes_text.append(
                        f"- {label_name}: Assigned to dataset {dataset_link}"
                    )

            elif change_type == "unassigned":
                if old_dataset_id == dataset_id:
                    changes_text.append(f"- {label_name}: Removed from this dataset")
                else:
                    dataset_link = self._create_dataset_link(old_dataset_id)
                    changes_text.append(
                        f"- {label_name}: Removed from dataset {dataset_link}"
                    )

            elif change_type == "reassigned":
                if old_dataset_id == dataset_id and new_dataset_id != dataset_id:
                    new_dataset_link = self._create_dataset_link(new_dataset_id)
                    changes_text.append(
                        f"- {label_name}: Moved from this dataset to {new_dataset_link}"
                    )
                elif new_dataset_id == dataset_id and old_dataset_id != dataset_id:
                    old_dataset_link = self._create_dataset_link(old_dataset_id)
                    changes_text.append(
                        f"- {label_name}: Moved from {old_dataset_link} to this dataset"
                    )
                elif old_dataset_id == dataset_id and new_dataset_id == dataset_id:
                    changes_text.append(
                        f"- {label_name}: Reassigned within this dataset"
                    )

        return "\n".join(changes_text) if changes_text else "No changes made"
