import pytest
import os
from unittest.mock import Mock, patch
from models.user import User
from models.dataset import Dataset
from models.organisation import Organisation
from models.user_assignment import UserOrganisationAssignment, Role
from repositories.organisation import OrganisationRepository
from repositories.role import RoleRepository
from repositories.user_assignment import UserAssignmentRepository
from services.user import UserService
from services.config import ConfigService
from email.message import EmailMessage
from services.emails.authentic_source_email import AuthenticSourceEmailService


@pytest.fixture
def user_service_mock():
    return Mock(spec=UserService)


@pytest.fixture
def organisation_repository_mock():
    return Mock(spec=OrganisationRepository)


@pytest.fixture
def role_repository_mock():
    return Mock(spec=RoleRepository)


@pytest.fixture
def user_assignment_repository_mock():
    return Mock(spec=UserAssignmentRepository)


@pytest.fixture
def config_service():
    config_service = ConfigService("./config.json")
    config_service._config = {
        "disable_email_for_roles": ["LEADERSHIP_TEAM"],
        "roles": [
            {
                "name": "DATA_MANAGER",
                "permissions": ["roles:manage"],
            },
            {
                "name": "CATALOGUE_MANAGER",
                "permissions": ["roles:manage"],
            },
            {
                "name": "INVENTORY_COORDINATOR",
                "permissions": ["datasets:read:published"],
            },
            {
                "name": "METADATA_EDITOR",
                "permissions": ["datasets:read:published"],
            },
            {
                "name": "METADATA_REVIEWER",
                "permissions": ["datasets:read:published"],
            },
        ],
        "email_templates": {
            "AUTHENTIC_SOURCE_ASSIGNMENT_CHANGED": {
                "subject": "Authentic Source Assignment Changed: $dataset_title",
                "body": "Dear $recipient_name,\n\nAuthentic source label assignments have been modified for a dataset.\n\nDataset: $dataset_title\nLink: $dataset_link\n\nChanges made:\n$changes_summary\n\nModified by: $assigner_name\n\nThank you",
            }
        },
    }
    return config_service


@pytest.fixture
def authentic_source_email_service(
    user_service_mock,
    config_service,
    organisation_repository_mock,
    role_repository_mock,
    user_assignment_repository_mock,
):
    return AuthenticSourceEmailService(
        user_service=user_service_mock,
        config_service=config_service,
        organisation_repository=organisation_repository_mock,
        role_repository=role_repository_mock,
        user_assignment_repository=user_assignment_repository_mock,
    )


def test_notify_authentic_source_assignment_changed_basic(
    authentic_source_email_service, user_service_mock, user_assignment_repository_mock
):
    dataset = Dataset(
        id=123, title="Environmental Data 2024", user_id=100, publisher_id=200
    )
    creator = User(id=100, email="creator@example.com", name="Dataset Creator")
    assigner = User(id=999, email="assigner@example.com", name="John Assigner")

    assignment_changes = [
        {
            "label_name": "Government Records",
            "change_type": "assigned",
            "old_dataset_id": None,
            "new_dataset_id": 123,
        }
    ]

    user_service_mock.find_by_id.side_effect = lambda user_id: {
        100: creator,
        999: assigner,
    }.get(user_id)

    # Mock no other users with permissions
    authentic_source_email_service._get_users_with_permission_in_iam_roles = Mock(
        return_value=[]
    )
    authentic_source_email_service._get_users_with_permission_in_organisation = Mock(
        return_value=[]
    )

    # Mock organisation membership for creator
    creator_assignment = Mock()

    def mock_get_user_org_assignment(organisation_id, user_id):
        if user_id == 100 and organisation_id == 200:
            return creator_assignment
        return None

    user_assignment_repository_mock.get_user_organisation_assignment.side_effect = (
        mock_get_user_org_assignment
    )

    # Act & Assert
    with patch("smtplib.SMTP") as mock_smtp:
        smtp_instance = mock_smtp.return_value.__enter__.return_value

        authentic_source_email_service.notify_authentic_source_assignment_changed(
            dataset=dataset, assignment_changes=assignment_changes, assigner_user_id=999
        )

        # Verify email was sent
        assert smtp_instance.send_message.call_count == 1

        sent_email: EmailMessage = smtp_instance.send_message.call_args[0][0]
        assert sent_email["From"] == os.getenv("SENDER_EMAIL")
        assert sent_email["To"] == "creator@example.com"
        assert "Environmental Data 2024" in sent_email["Subject"]
        assert "Authentic Source Assignment Changed" in sent_email["Subject"]

        email_content = sent_email.get_content()
        assert "Environmental Data 2024" in email_content
        assert "Government Records: Assigned to this dataset" in email_content
        assert "John Assigner" in email_content
        assert "http://localhost:5173/?datasetId=123" in email_content


def test_notify_authentic_source_assignment_changed_multiple_recipients(
    authentic_source_email_service, user_service_mock, user_assignment_repository_mock
):
    contact = Mock()
    contact.id = 150
    contact.name = "Dataset Contact"
    contact.email = "contact@example.com"

    dataset_contact = Mock()
    dataset_contact.contact = contact
    dataset_contact.contact_id = 150

    dataset = Mock()
    dataset.id = 456
    dataset.title = "Financial Data Set"
    dataset.user_id = 100
    dataset.publisher_id = 200
    dataset.contacts = {dataset_contact}

    creator = User(id=100, email="creator@example.com", name="Dataset Creator")
    assigner = User(id=999, email="assigner@example.com", name="Jane Assigner")
    data_manager = User(id=200, email="data.manager@example.com", name="Data Manager")
    catalogue_manager = User(
        id=201, email="catalogue.manager@example.com", name="Catalogue Manager"
    )
    published_reader = User(
        id=400, email="published.reader@example.com", name="Published Reader"
    )

    assignment_changes = [
        {
            "label_name": "Financial Institution",
            "change_type": "unassigned",
            "old_dataset_id": 456,
            "new_dataset_id": None,
        },
        {
            "label_name": "Academic Research",
            "change_type": "reassigned",
            "old_dataset_id": 456,
            "new_dataset_id": 789,
        },
    ]

    user_service_mock.find_by_id.side_effect = lambda user_id: {
        100: creator,
        150: contact,
        999: assigner,
        200: data_manager,
        201: catalogue_manager,
        400: published_reader,
    }.get(user_id)

    # Mock users with different permissions
    def mock_get_users_with_permission_in_iam_roles(permission):
        if permission == "roles:manage":
            return [data_manager, catalogue_manager]
        return []

    def mock_get_users_with_permission_in_organisation(permission, org_id):
        if permission == "datasets:read:published":
            return [published_reader]
        return []

    authentic_source_email_service._get_users_with_permission_in_iam_roles = (
        mock_get_users_with_permission_in_iam_roles
    )
    authentic_source_email_service._get_users_with_permission_in_organisation = (
        mock_get_users_with_permission_in_organisation
    )

    # Mock organisation membership for creator
    creator_assignment = Mock()

    def mock_get_user_org_assignment(organisation_id, user_id):
        if user_id == 100 and organisation_id == 200:
            return creator_assignment
        return None

    user_assignment_repository_mock.get_user_organisation_assignment.side_effect = (
        mock_get_user_org_assignment
    )

    # Act & Assert
    with patch("smtplib.SMTP") as mock_smtp:
        smtp_instance = mock_smtp.return_value.__enter__.return_value

        authentic_source_email_service.notify_authentic_source_assignment_changed(
            dataset=dataset, assignment_changes=assignment_changes, assigner_user_id=999
        )

        # Verify 5 emails were sent (creator + contact + data_manager + catalogue_manager + published_reader)
        assert smtp_instance.send_message.call_count == 5

        # Get all email recipients
        calls = smtp_instance.send_message.call_args_list
        recipients = {call[0][0]["To"] for call in calls}

        expected_recipients = {
            "creator@example.com",
            "contact@example.com",
            "data.manager@example.com",
            "catalogue.manager@example.com",
            "published.reader@example.com",
        }
        assert recipients == expected_recipients

        # Check email content for one of the emails
        first_email: EmailMessage = calls[0][0][0]
        email_content = first_email.get_content()
        assert "Financial Institution: Removed from this dataset" in email_content
        assert (
            "Academic Research: Moved from this dataset to http://localhost:5173/?datasetId=789"
            in email_content
        )


def test_notify_authentic_source_assignment_changed_excludes_assigner(
    authentic_source_email_service, user_service_mock, user_assignment_repository_mock
):
    dataset = Dataset(id=123, title="Test Dataset", user_id=100, publisher_id=200)
    creator_and_assigner = User(
        id=100, email="creator@example.com", name="Creator Assigner"
    )

    assignment_changes = [
        {
            "label_name": "Government Records",
            "change_type": "assigned",
            "old_dataset_id": None,
            "new_dataset_id": 123,
        }
    ]

    user_service_mock.find_by_id.return_value = creator_and_assigner

    # Mock no other users with permissions
    authentic_source_email_service._get_users_with_permission_in_iam_roles = Mock(
        return_value=[]
    )
    authentic_source_email_service._get_users_with_permission_in_organisation = Mock(
        return_value=[]
    )

    # Mock organisation membership for creator
    creator_assignment = Mock()

    def mock_get_user_org_assignment(organisation_id, user_id):
        if user_id == 100 and organisation_id == 200:
            return creator_assignment
        return None

    user_assignment_repository_mock.get_user_organisation_assignment.side_effect = (
        mock_get_user_org_assignment
    )

    # Act & Assert
    with patch("smtplib.SMTP") as mock_smtp:
        smtp_instance = mock_smtp.return_value.__enter__.return_value

        authentic_source_email_service.notify_authentic_source_assignment_changed(
            dataset=dataset,
            assignment_changes=assignment_changes,
            assigner_user_id=100,  # Same as creator
        )

        # Verify no emails were sent (assigner excluded)
        assert smtp_instance.send_message.call_count == 0


def test_format_assignment_changes_dataset_perspective(authentic_source_email_service):
    """Test formatting assignment changes from specific dataset perspective."""
    changes = [
        {
            "label_name": "Government Records",
            "change_type": "assigned",
            "old_dataset_id": None,
            "new_dataset_id": 123,
        },
        {
            "label_name": "Financial Institution",
            "change_type": "unassigned",
            "old_dataset_id": 123,
            "new_dataset_id": None,
        },
        {
            "label_name": "Academic Research",
            "change_type": "reassigned",
            "old_dataset_id": 123,
            "new_dataset_id": 456,
        },
        {
            "label_name": "Healthcare Data",
            "change_type": "reassigned",
            "old_dataset_id": 456,
            "new_dataset_id": 123,
        },
        {
            "label_name": "Internal System",
            "change_type": "reassigned",
            "old_dataset_id": 123,
            "new_dataset_id": 123,
        },
    ]

    result = authentic_source_email_service._format_assignment_changes(
        changes, dataset_id=123
    )

    expected_lines = [
        "- Government Records: Assigned to this dataset",
        "- Financial Institution: Removed from this dataset",
        "- Academic Research: Moved from this dataset to http://localhost:5173/?datasetId=456",
        "- Healthcare Data: Moved from http://localhost:5173/?datasetId=456 to this dataset",
        "- Internal System: Reassigned within this dataset",
    ]
    expected = "\n".join(expected_lines)

    assert result == expected


def test_format_assignment_changes_external_dataset_perspective(
    authentic_source_email_service,
):
    """Test formatting changes for datasets not directly involved."""
    changes = [
        {
            "label_name": "External Label",
            "change_type": "assigned",
            "old_dataset_id": None,
            "new_dataset_id": 456,
        },
        {
            "label_name": "Another External",
            "change_type": "unassigned",
            "old_dataset_id": 789,
            "new_dataset_id": None,
        },
    ]

    result = authentic_source_email_service._format_assignment_changes(
        changes, dataset_id=123
    )

    expected = (
        "- External Label: Assigned to dataset http://localhost:5173/?datasetId=456\n"
        "- Another External: Removed from dataset http://localhost:5173/?datasetId=789"
    )

    assert result == expected
