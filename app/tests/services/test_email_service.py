import pytest
import os
from unittest.mock import Mock, patch, call
from models.user import User
from models.dataset import Dataset, DatasetGroupManagers
from models.organisation import Organisation
from models.user_assignment import UserOrganisationAssignment, Role
from repositories.organisation import OrganisationRepository
from repositories.role import RoleRepository
from repositories.user_assignment import UserAssignmentRepository
from services.user import UserService
from services.config import ConfigService
from email.message import EmailMessage
from services.email_service import EmailService
from test_factory import simple_dataset


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
    return ConfigService("./config.json")


@pytest.fixture
def email_service(
    user_service_mock,
    config_service,
    organisation_repository_mock,
    role_repository_mock,
    user_assignment_repository_mock,
):
    return EmailService(
        user_service=user_service_mock,
        config_service=config_service,
        organisation_repository=organisation_repository_mock,
        role_repository=role_repository_mock,
        user_assignment_repository=user_assignment_repository_mock,
    )


def test_notify_dataset_completed(email_service, user_service_mock, config_service):
    users = [User(id=1, email="user@example.com", name="Test User")]
    group_managers = [DatasetGroupManagers(user_id=users[0].id)]
    dataset = Dataset(
        id=1, title="Test Dataset", user_id=999, group_managers=set(group_managers)
    )

    config_service._config = {
        "enable_multi_tenants": False,
        "roles": [
            {
                "name": "GROUP_MANAGER",
                "permissions": ["datasets:status-change:validate:group"],
            },
            {
                "name": "DATA_MANAGER",
                "permissions": ["datasets:status-change:validate"],
            },
        ],
    }

    config_service.get_enable_multi_tenants = Mock(return_value=False)

    user_service_mock.find_by_iam_role.return_value = users

    with patch("smtplib.SMTP") as mock_smtp:
        smtp_instance = mock_smtp.return_value.__enter__.return_value
        email_service.notify_dataset_completed(dataset)

        user_service_mock.find_by_iam_role.assert_called()

        calls = smtp_instance.send_message.call_args_list
        assert len(calls) >= 1

        sent_email: EmailMessage = calls[0][0][0]

        assert sent_email["From"] == os.getenv("SENDER_EMAIL")
        assert sent_email["To"] == "user@example.com"
        assert "Test Dataset" in sent_email["Subject"]
        assert "http://localhost:5173/?datasetId=1" in sent_email.get_content()

        assert "Test Dataset" in sent_email.get_content()
        assert (
            "has been submitted and is ready for validation" in sent_email.get_content()
        )


def test_notify_dataset_completed_multi_tenant(
    email_service,
    user_service_mock,
    config_service,
    user_assignment_repository_mock,
    simple_dataset,
):
    org_user = User(id=1, email="org_user@example.com", name="Org User")
    manage_user = User(id=2, email="manage_user@example.com", name="Manage User")
    creator = User(id=999, email="creator@example.com", name="Creator")

    # Mock multi-tenant enabled
    config_service.get_enable_multi_tenants = Mock(return_value=True)

    # Mock the assignment repository for org users
    org_assignment = Mock()
    org_assignment.user = org_user
    user_assignment_repository_mock.get_user_organisation_assignments_by_roles.return_value = [
        org_assignment
    ]

    # Mock manage roles users
    user_service_mock.find_by_iam_role.return_value = [manage_user]
    user_service_mock.find_by_id.return_value = creator

    config_service._config = {
        "roles": [
            {
                "name": "ORG_VALIDATOR",
                "permissions": ["datasets:status-change:validate"],
            },
            {
                "name": "MANAGE_ROLE",
                "permissions": ["roles:manage"],
            },
        ]
    }

    with patch("smtplib.SMTP") as mock_smtp:
        smtp_instance = mock_smtp.return_value.__enter__.return_value
        email_service.notify_dataset_completed(simple_dataset)

        assert smtp_instance.send_message.call_count == 2
        first_call, second_call = smtp_instance.send_message.call_args_list

        org_user_email: EmailMessage = first_call[0][0]
        manage_user_email: EmailMessage = second_call[0][0]

        assert org_user_email["From"] == os.getenv("SENDER_EMAIL")
        assert org_user_email["To"] == "org_user@example.com"

        assert manage_user_email["To"] == "manage_user@example.com"


def test_notify_dataset_validated(
    email_service, user_service_mock, config_service, simple_dataset
):
    users = [User(id=1, email="user@example.com", name="Test User")]

    config_service.get_enable_multi_tenants = Mock(return_value=False)
    user_service_mock.find_by_iam_role.return_value = users

    with patch("smtplib.SMTP") as mock_smtp:
        smtp_instance = mock_smtp.return_value.__enter__.return_value
        email_service.notify_dataset_validated(simple_dataset)

        user_service_mock.find_by_iam_role.assert_any_call("DATA_MANAGER")

        args, _ = smtp_instance.send_message.call_args
        sent_email: EmailMessage = args[0]

        assert sent_email["From"] == os.getenv("SENDER_EMAIL")
        assert sent_email["To"] == "user@example.com"
        assert "Test Dataset" in sent_email["Subject"]
        assert "http://localhost:5173/?datasetId=1" in sent_email.get_content()

        assert "Test Dataset" in sent_email.get_content()
        assert (
            "has been validated and is ready for your approval"
            in sent_email.get_content()
        )


def test_notify_dataset_validated_failure(
    email_service, user_service_mock, config_service, simple_dataset
):
    users = [User(id=1, email="user@example.com", name="Test User")]

    config_service.get_enable_multi_tenants = Mock(return_value=False)
    user_service_mock.find_by_iam_role.return_value = users

    with patch("smtplib.SMTP") as mock_smtp:
        smtp_instance = mock_smtp.return_value.__enter__.return_value
        smtp_instance.send_message.side_effect = Exception("Failed to send email")

        email_service.notify_dataset_validated(simple_dataset)

        user_service_mock.find_by_iam_role.assert_any_call("DATA_MANAGER")
        smtp_instance.send_message.assert_called()


def test_notify_dataset_validated_multi_tenant(
    email_service,
    user_service_mock,
    config_service,
    user_assignment_repository_mock,
    simple_dataset,
):
    org_user = User(id=1, email="org_approver@example.com", name="Org Approver")
    manage_user = User(id=2, email="manage_user@example.com", name="Manage User")
    creator = User(id=999, email="creator@example.com", name="Creator")

    # Mock multi-tenant enabled
    config_service.get_enable_multi_tenants = Mock(return_value=True)

    # Mock the assignment repository for org users
    org_assignment = Mock()
    org_assignment.user = org_user
    user_assignment_repository_mock.get_user_organisation_assignments_by_roles.return_value = [
        org_assignment
    ]

    # Mock organisation membership for creator
    creator_assignment = Mock()

    def mock_get_user_org_assignment(organisation_id, user_id):
        if user_id == 999 and organisation_id == 100:
            return creator_assignment
        return None

    user_assignment_repository_mock.get_user_organisation_assignment.side_effect = (
        mock_get_user_org_assignment
    )

    # Mock manage roles users
    user_service_mock.find_by_iam_role.return_value = [manage_user]
    user_service_mock.find_by_id.return_value = creator

    config_service._config = {
        "roles": [
            {
                "name": "ORG_APPROVER",
                "permissions": ["datasets:status-change:approve"],
            },
            {
                "name": "MANAGE_ROLE",
                "permissions": ["roles:manage"],
            },
        ]
    }

    with patch("smtplib.SMTP") as mock_smtp:
        smtp_instance = mock_smtp.return_value.__enter__.return_value
        email_service.notify_dataset_validated(simple_dataset)

        # Should call org assignment repository for the approval permission
        user_assignment_repository_mock.get_user_organisation_assignments_by_roles.assert_called()

        assert smtp_instance.send_message.call_count == 3
        first_call, second_call, third_call = smtp_instance.send_message.call_args_list

        org_user_email: EmailMessage = first_call[0][0]
        manage_user_email: EmailMessage = second_call[0][0]
        creator_email: EmailMessage = third_call[0][0]

        assert org_user_email["To"] == "org_approver@example.com"
        assert manage_user_email["To"] == "manage_user@example.com"
        assert creator_email["To"] == "creator@example.com"


def test_notify_dataset_approved(
    email_service, user_service_mock, config_service, simple_dataset
):
    users = [User(id=1, email="user@example.com", name="Test User:1")]

    user_service_mock.find_by_iam_role.return_value = users
    user_service_mock.find_by_id.return_value = User(
        id=999, email="creator@example.com", name="Test User:2"
    )
    config_service.get_enable_multi_tenants = Mock(return_value=False)

    with patch("smtplib.SMTP") as mock_smtp:
        smtp_instance = mock_smtp.return_value.__enter__.return_value
        email_service.notify_dataset_approved(simple_dataset)

        assert smtp_instance.send_message.call_count == 2

        first_call, second_call = smtp_instance.send_message.call_args_list
        user_email: EmailMessage = first_call[0][0]
        creator_email: EmailMessage = second_call[0][0]

        assert creator_email["From"] == os.getenv("SENDER_EMAIL")
        assert creator_email["To"] == "creator@example.com"
        assert "Test Dataset" in creator_email["Subject"]
        assert "has been approved" in creator_email.get_content()

        assert user_email["From"] == os.getenv("SENDER_EMAIL")
        assert user_email["To"] == "user@example.com"
        assert "Test Dataset" in user_email["Subject"]
        assert "http://localhost:5173/?datasetId=1" in user_email.get_content()


def test_notify_dataset_approved_multi_tenant(
    email_service,
    user_service_mock,
    config_service,
    user_assignment_repository_mock,
    simple_dataset,
):
    org_user = User(id=1, email="org_publisher@example.com", name="Org Publisher")
    manage_user = User(id=2, email="manage_user@example.com", name="Manage User")
    creator = User(id=999, email="creator@example.com", name="Creator")

    # Mock multi-tenant enabled
    config_service.get_enable_multi_tenants = Mock(return_value=True)

    # Mock the assignment repository for org users
    org_assignment = Mock()
    org_assignment.user = org_user
    user_assignment_repository_mock.get_user_organisation_assignments_by_roles.return_value = [
        org_assignment
    ]

    # Mock organisation membership for creator
    creator_assignment = Mock()

    def mock_get_user_org_assignment(organisation_id, user_id):
        if user_id == 999 and organisation_id == 100:
            return creator_assignment
        return None

    user_assignment_repository_mock.get_user_organisation_assignment.side_effect = (
        mock_get_user_org_assignment
    )

    # Mock manage roles users
    user_service_mock.find_by_iam_role.return_value = [manage_user]
    user_service_mock.find_by_id.return_value = creator

    config_service._config = {
        "roles": [
            {
                "name": "ORG_PUBLISHER",
                "permissions": ["datasets:status-change:publish"],
            },
            {
                "name": "MANAGE_ROLE",
                "permissions": ["roles:manage"],
            },
        ]
    }

    with patch("smtplib.SMTP") as mock_smtp:
        smtp_instance = mock_smtp.return_value.__enter__.return_value
        email_service.notify_dataset_approved(simple_dataset)

        # Should call org assignment repository for the publish permission
        user_assignment_repository_mock.get_user_organisation_assignments_by_roles.assert_called()

        # Should send emails including creator
        assert smtp_instance.send_message.call_count == 3
        first_call, second_call, third_call = smtp_instance.send_message.call_args_list

        org_user_email: EmailMessage = first_call[0][0]
        manage_user_email: EmailMessage = second_call[0][0]
        creator_email: EmailMessage = third_call[0][0]

        assert org_user_email["To"] == "org_publisher@example.com"
        assert manage_user_email["To"] == "manage_user@example.com"
        assert creator_email["To"] == "creator@example.com"


def test_notify_dataset_back_to_draft(
    email_service, user_service_mock, config_service, simple_dataset
):
    user_service_mock.find_by_id.return_value = User(
        id=999, email="creator@example.com", name="Test User:2"
    )
    config_service.get_enable_multi_tenants = Mock(return_value=False)

    with patch("smtplib.SMTP") as mock_smtp:
        smtp_instance = mock_smtp.return_value.__enter__.return_value
        email_service.notify_dataset_back_to_draft(simple_dataset)

        user_service_mock.find_by_id.assert_called_once_with(999)

        assert smtp_instance.send_message.call_count == 1

        call = smtp_instance.send_message.call_args
        sent_email: EmailMessage = call[0][0]

        assert sent_email["From"] == os.getenv("SENDER_EMAIL")
        assert sent_email["To"] == "creator@example.com"
        assert "Test Dataset" in sent_email["Subject"]
        assert "has been returned to draft status" in sent_email.get_content()


def test_notify_dataset_back_to_draft_multi_tenant(
    email_service,
    user_service_mock,
    config_service,
    user_assignment_repository_mock,
    simple_dataset,
):
    creator = User(id=999, email="creator@example.com", name="Creator")
    org_editor = User(id=10, email="org_editor@example.com", name="Org Editor")

    config_service.get_enable_multi_tenants = Mock(return_value=True)
    user_service_mock.find_by_id.return_value = creator
    user_service_mock.find_by_iam_role.return_value = []  # No global editors

    # Mock organisation editors
    org_assignment = Mock()
    org_assignment.user = org_editor
    user_assignment_repository_mock.get_user_organisation_assignments_by_roles.return_value = [
        org_assignment
    ]

    # Mock organisation membership for creator
    creator_assignment = Mock()

    def mock_get_user_org_assignment(organisation_id, user_id):
        if user_id == 999 and organisation_id == 100:
            return creator_assignment
        return None

    user_assignment_repository_mock.get_user_organisation_assignment.side_effect = (
        mock_get_user_org_assignment
    )

    config_service._config = {
        "roles": [
            {
                "name": "ORG_EDITOR",
                "permissions": ["datasets:edit:draft:organisation"],
            }
        ]
    }

    with patch("smtplib.SMTP") as mock_smtp:
        smtp_instance = mock_smtp.return_value.__enter__.return_value
        email_service.notify_dataset_back_to_draft(simple_dataset)

        # Should send to both creator and org editor
        assert smtp_instance.send_message.call_count == 2
        calls = smtp_instance.send_message.call_args_list
        emails = [call[0][0] for call in calls]
        email_tos = {email["To"] for email in emails}

        assert email_tos == {"creator@example.com", "org_editor@example.com"}
        assert all(
            "has been returned to draft status" in email.get_content()
            for email in emails
        )


def test_notify_dataset_published(
    email_service, user_service_mock, config_service, simple_dataset
):
    user_service_mock.find_by_id.return_value = User(
        id=999, email="creator@example.com", name="Test User:2"
    )
    config_service.get_enable_multi_tenants = Mock(return_value=False)

    users = [User(id=1, email="catalogue_manager@example.com", name="Test User")]
    user_service_mock.find_by_iam_role.return_value = users

    email_service._user_assignment_repository.get_user_organisation_assignments_by_roles.return_value = (
        []
    )

    with patch("smtplib.SMTP") as mock_smtp:
        smtp_instance = mock_smtp.return_value.__enter__.return_value
        email_service.notify_dataset_published(simple_dataset)

        user_service_mock.find_by_id.assert_called_once_with(999)

        assert smtp_instance.send_message.call_count == 2
        # Check both emails were sent
        calls = smtp_instance.send_message.call_args_list
        emails = [call[0][0] for call in calls]
        email_tos = {email["To"] for email in emails}

        assert email_tos == {"creator@example.com", "catalogue_manager@example.com"}

        # Verify one of the emails
        assert any("Test Dataset" in email["Subject"] for email in emails)
        assert any("has been published" in email.get_content() for email in emails)


def test_notify_dataset_marked_as_interal(
    email_service, user_service_mock, config_service, simple_dataset
):
    user_service_mock.find_by_id.return_value = User(
        id=999, email="creator@example.com", name="Test User:2"
    )
    config_service.get_enable_multi_tenants = Mock(return_value=False)

    with patch("smtplib.SMTP") as mock_smtp:
        smtp_instance = mock_smtp.return_value.__enter__.return_value
        email_service.notify_dataset_marked_as_internal(simple_dataset)

        user_service_mock.find_by_id.assert_called_once_with(999)

        assert smtp_instance.send_message.call_count == 1
        call = smtp_instance.send_message.call_args
        sent_email: EmailMessage = call[0][0]
        assert sent_email["From"] == os.getenv("SENDER_EMAIL")
        assert sent_email["To"] == "creator@example.com"
        assert "Test Dataset" in sent_email["Subject"]
        assert "has been marked as internal" in sent_email.get_content()


def test_notify_dataset_marked_as_internal_multi_tenant(
    email_service,
    user_service_mock,
    config_service,
    user_assignment_repository_mock,
    simple_dataset,
):
    creator = User(id=999, email="creator@example.com", name="Creator")
    org_editor = User(id=10, email="org_editor@example.com", name="Org Editor")

    config_service.get_enable_multi_tenants = Mock(return_value=True)
    user_service_mock.find_by_id.return_value = creator
    user_service_mock.find_by_iam_role.return_value = []  # No global editors

    # Mock organisation editors
    org_assignment = Mock()
    org_assignment.user = org_editor
    user_assignment_repository_mock.get_user_organisation_assignments_by_roles.return_value = [
        org_assignment
    ]

    # Mock organisation membership for creator
    creator_assignment = Mock()

    def mock_get_user_org_assignment(organisation_id, user_id):
        if user_id == 999 and organisation_id == 100:
            return creator_assignment
        return None

    user_assignment_repository_mock.get_user_organisation_assignment.side_effect = (
        mock_get_user_org_assignment
    )

    config_service._config = {
        "roles": [
            {
                "name": "ORG_EDITOR",
                "permissions": ["datasets:edit:draft:organisation"],
            }
        ]
    }

    with patch("smtplib.SMTP") as mock_smtp:
        smtp_instance = mock_smtp.return_value.__enter__.return_value
        email_service.notify_dataset_marked_as_internal(simple_dataset)

        # Should send to both creator and org editor
        assert smtp_instance.send_message.call_count == 2
        calls = smtp_instance.send_message.call_args_list
        emails = [call[0][0] for call in calls]
        email_tos = {email["To"] for email in emails}

        assert email_tos == {"creator@example.com", "org_editor@example.com"}
        assert all(
            "has been marked as internal" in email.get_content() for email in emails
        )


def test_notify_dataset_deprecated_multi_tenant(
    email_service,
    user_service_mock,
    config_service,
    user_assignment_repository_mock,
    simple_dataset,
):
    creator = User(id=999, email="creator@example.com", name="Creator")
    org_editor = User(id=10, email="org_editor@example.com", name="Org Editor")

    config_service.get_enable_multi_tenants = Mock(return_value=True)
    user_service_mock.find_by_id.return_value = creator
    user_service_mock.find_by_iam_role.return_value = []  # No global editors

    # Mock organisation editors
    org_assignment = Mock()
    org_assignment.user = org_editor
    user_assignment_repository_mock.get_user_organisation_assignments_by_roles.return_value = [
        org_assignment
    ]

    # Mock organisation membership for creator
    creator_assignment = Mock()

    def mock_get_user_org_assignment(organisation_id, user_id):
        if user_id == 999 and organisation_id == 100:
            return creator_assignment
        return None

    user_assignment_repository_mock.get_user_organisation_assignment.side_effect = (
        mock_get_user_org_assignment
    )

    config_service._config = {
        "roles": [
            {
                "name": "ORG_EDITOR",
                "permissions": ["datasets:edit:draft:organisation"],
            }
        ]
    }

    with patch("smtplib.SMTP") as mock_smtp:
        smtp_instance = mock_smtp.return_value.__enter__.return_value
        email_service.notify_dataset_deprecated(simple_dataset)

        # Should send to both creator and org editor
        assert smtp_instance.send_message.call_count == 2
        calls = smtp_instance.send_message.call_args_list
        emails = [call[0][0] for call in calls]
        email_tos = {email["To"] for email in emails}

        assert email_tos == {"creator@example.com", "org_editor@example.com"}
        assert all("has been deprecated" in email.get_content() for email in emails)


def test_notify_dataset_published_with_assignments(
    email_service,
    user_service_mock,
    config_service,
    user_assignment_repository_mock,
    simple_dataset,
):

    contact = Mock()
    contact.id = 100
    contact.name = "Contact Name"
    contact.email = "contact@example.com"

    dataset_contact = Mock()
    dataset_contact.contact = contact
    dataset_contact.contact_id = 100

    mock_dataset = Mock()
    mock_dataset.id = simple_dataset.id
    mock_dataset.title = simple_dataset.title
    mock_dataset.user_id = simple_dataset.user_id
    mock_dataset.publisher_id = 42
    mock_dataset.contacts = {dataset_contact}

    simple_dataset = mock_dataset
    creator = User(id=999, email="creator@example.com", name="Creator Name")
    user_service_mock.find_by_id.return_value = creator

    # Mock multi-tenants disabled for simpler test
    config_service.get_enable_multi_tenants = Mock(return_value=False)

    # config: only two roles have the published‐read permission
    config_service._config = {
        "disable_email_for_roles": [],
        "roles": [
            {
                "name": "INVENTORY_COORDINATOR",
                "permissions": ["datasets:read:published"],
            },
            {"name": "METADATA_EDITOR", "permissions": ["datasets:read:published"]},
        ],
        "email_templates": {
            "DATASET_PUBLISHED": {
                "subject": 'Dataset "$dataset_title" published',
                "body": 'Hi $recipient_name,\n\nYour dataset "$dataset_title" is live: $dataset_link',
            }
        },
    }

    config_service.get_roles = lambda: config_service._config["roles"]
    config_service.get_roles_with_disable_email = lambda: config_service._config[
        "disable_email_for_roles"
    ]

    # two organisation assignments
    inv = User(id=10, email="inv@example.com", name="Inv Coord")
    ed = User(id=11, email="edit@example.com", name="Meta Edit")
    a1 = Mock()
    a1.user = inv
    a2 = Mock()
    a2.user = ed
    user_assignment_repository_mock.get_user_organisation_assignments_by_roles.return_value = [
        a1,
        a2,
    ]

    # act
    with patch("smtplib.SMTP") as mock_smtp:
        smtp = mock_smtp.return_value.__enter__.return_value
        email_service.notify_dataset_published(simple_dataset)

    # assert we fetched exactly the two expected roles
    expected_roles = ["INVENTORY_COORDINATOR", "METADATA_EDITOR"]
    user_assignment_repository_mock.get_user_organisation_assignments_by_roles.assert_called_once_with(
        42, expected_roles
    )

    # we should have sent to contact, creator, inv, ed → 4 emails
    assert smtp.send_message.call_count == 4
    tos = {call_args[0][0]["To"] for call_args in smtp.send_message.call_args_list}
    assert tos == {
        "contact@example.com",
        "creator@example.com",
        "inv@example.com",
        "edit@example.com",
    }

    # spot‐check subject/body of the first one
    first: EmailMessage = smtp.send_message.call_args_list[0][0][0]
    assert "Test Dataset" in first["Subject"]
    assert "http://localhost:5173/?datasetId=1" in first.get_content()


def test_notify_role_assigned(
    email_service,
    user_service_mock,
    config_service,
    organisation_repository_mock,
    role_repository_mock,
    user_assignment_repository_mock,
):
    target_user = User(id=1, email="target@example.com", name="Target User")
    assigner_user = User(id=2, email="assigner@example.com", name="Assigner User")
    org_manager = User(id=3, email="manager@example.com", name="Org Manager")
    data_manager = User(id=4, email="datamanager@example.com", name="Data Manager")

    organisation = Organisation(id=100, name="Test Organisation")
    role = Role(id=10, name="CONTRIBUTOR")

    # Setup config with roles
    config_service._config = {
        "disable_email_for_roles": ["LEADERSHIP_TEAM"],
        "roles": [
            {
                "name": "DATA_MANAGER",
                "permissions": ["roles:manage"],
            },
            {
                "name": "INVENTORY_COORDINATOR",
                "permissions": ["roles:manage:organisation"],
            },
        ],
        "email_templates": {
            "ROLE_ASSIGNED": {
                "subject": "Role Assignment: $role_name for $target_user_name",
                "body": "Dear $recipient_name,\n\nRole $role_name has been assigned to $target_user_name ($target_user_email) in $organisation_name by $assigner_name.\n\nApp URL: $app_url",
            }
        },
    }
    org_assignment = Mock()
    org_assignment.user = org_manager

    # Setup mocks
    user_service_mock.find_by_id.side_effect = lambda user_id: {
        1: target_user,
        2: assigner_user,
        3: org_manager,
        4: data_manager,
    }.get(user_id)

    user_service_mock.find_by_iam_role.side_effect = lambda role_name: {
        "DATA_MANAGER": [data_manager],
        "INVENTORY_COORDINATOR": [],
    }.get(role_name, [])

    organisation_repository_mock.get_organisation.return_value = organisation
    role_repository_mock.get_by_id.return_value = role
    user_assignment_repository_mock.get_user_organisation_assignments_by_roles.return_value = [
        org_assignment
    ]

    # Execute the method
    with patch("smtplib.SMTP") as mock_smtp:
        smtp_instance = mock_smtp.return_value.__enter__.return_value

        email_service.notify_role_assigned(
            target_user_id=1, organisation_id=100, role_id=10, assigner_user_id=2
        )

        # Verify repository calls
        user_service_mock.find_by_id.assert_any_call(1)  # target user
        user_service_mock.find_by_id.assert_any_call(2)  # assigner user
        organisation_repository_mock.get_organisation.assert_called_once_with(100)
        role_repository_mock.get_by_id.assert_called_once_with(10)

        # Verify emails were sent
        assert (
            smtp_instance.send_message.call_count == 3
        )  # target + org_manager + data_manager

        # Check email content
        calls = smtp_instance.send_message.call_args_list

        # Verify target user email
        target_email: EmailMessage = calls[0][0][0]
        assert target_email["From"] == os.getenv("SENDER_EMAIL")
        assert target_email["To"] == "target@example.com"
        assert "CONTRIBUTOR for Target User" in target_email["Subject"]
        assert "Target User" in target_email.get_content()
        assert "target@example.com" in target_email.get_content()
        assert "CONTRIBUTOR" in target_email.get_content()
        assert "Test Organisation" in target_email.get_content()
        assert "Assigner User" in target_email.get_content()

        # Verify data manager email (has roles:manage permission)
        data_manager_email: EmailMessage = calls[1][0][0]
        assert data_manager_email["To"] == "datamanager@example.com"
        assert "CONTRIBUTOR for Target User" in data_manager_email["Subject"]

        # Verify org manager email (has roles:manage:organisation permission)
        org_manager_email: EmailMessage = calls[2][0][0]
        assert org_manager_email["To"] == "manager@example.com"
        assert "CONTRIBUTOR for Target User" in org_manager_email["Subject"]
