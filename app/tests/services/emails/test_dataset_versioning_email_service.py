import os
from unittest.mock import Mock, patch
import pytest
from email.message import EmailMessage

from services.emails.dataset_versioning_email import DatasetVersioningEmailService
from services.email_service import EmailRecipient
from models.dataset import Dataset
from models.user import User
from services.config import ConfigService
from repositories.organisation import OrganisationRepository
from repositories.role import RoleRepository
from repositories.user_assignment import UserAssignmentRepository


@pytest.fixture
def config_service_mock():
    mock = Mock(spec=ConfigService)

    mock.get_email_templates.return_value = {
        "DATASET_DEPRECATED_WITH_NEW_VERSION": {
            "subject": "Dataset Deprecated: $dataset_title",
            "body": (
                "Hello $recipient_name,\n\n"
                'The dataset "$dataset_title" has been deprecated as a new version is now available.\n\n'
                "Deprecated Dataset: $dataset_title\n"
                "Link: $dataset_link\n\n"
                "New Version: $newer_dataset_title\n"
                "Link: $newer_dataset_link\n\n"
                "Thank you"
            ),
        }
    }

    mock.get_roles.return_value = [
        {"name": "admin", "permissions": ["datasets:read:published"]},
        {"name": "editor", "permissions": ["datasets:read:published"]},
    ]
    mock.get_roles_with_disable_email.return_value = []

    return mock


@pytest.fixture
def versioning_email_service(config_service_mock):
    service = DatasetVersioningEmailService(
        user_service=Mock(),
        config_service=config_service_mock,
        organisation_repository=Mock(spec=OrganisationRepository),
        role_repository=Mock(spec=RoleRepository),
        user_assignment_repository=Mock(spec=UserAssignmentRepository),
    )
    service.sender_email = os.getenv("SENDER_EMAIL", "noreply@example.com")
    service.base_url = "http://localhost:5173"
    return service


def test_notify_old_dataset_deprecated(versioning_email_service):
    old_dataset = Dataset(id=1, title="Old Dataset", user_id=42)
    new_dataset = Dataset(id=2, title="New Dataset", user_id=99)
    creator = User(id=42, email="creator@example.com", name="Creator User")

    versioning_email_service._get_dataset_creator = Mock(return_value=creator)
    versioning_email_service._get_dataset_contacts_and_roles_manager_and_all_and_all_org_roles = Mock(
        return_value=[EmailRecipient(name=creator.name, email=creator.email)]
    )

    with patch("smtplib.SMTP") as mock_smtp:
        smtp_instance = mock_smtp.return_value.__enter__.return_value

        versioning_email_service.notify_old_dataset_deprecated(
            old_dataset, newer_dataset=new_dataset
        )

        assert smtp_instance.send_message.call_count == 1

        sent_email: EmailMessage = smtp_instance.send_message.call_args[0][0]

        assert sent_email["From"] == versioning_email_service.sender_email
        assert sent_email["To"] == creator.email
        assert f"Dataset Deprecated: {old_dataset.title}" in sent_email["Subject"]

        body = sent_email.get_content()

        assert f"Hello {creator.name}" in body
        assert (
            f'The dataset "{old_dataset.title}" has been deprecated as a new version is now available.'
            in body
        )
        assert f"Deprecated Dataset: {old_dataset.title}" in body
        assert (
            f"Link: {versioning_email_service._create_dataset_link(old_dataset.id)}"
            in body
        )
        assert f"New Version: {new_dataset.title}" in body
        assert (
            f"Link: {versioning_email_service._create_dataset_link(new_dataset.id)}"
            in body
        )
        assert "Thank you" in body
