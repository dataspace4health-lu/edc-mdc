import os
from unittest.mock import Mock, patch
import pytest
from models.user import User
from services.config import ConfigService
from services.emails.organisation_specific_email import (
    OrganisationSpecificEmailsService,
)
from repositories.organisation import OrganisationRepository
from repositories.role import RoleRepository
from repositories.user_assignment import UserAssignmentRepository
from services.user import UserService


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
    return OrganisationSpecificEmailsService(
        user_service=user_service_mock,
        config_service=config_service,
        organisation_repository=organisation_repository_mock,
        role_repository=role_repository_mock,
        user_assignment_repository=user_assignment_repository_mock,
    )


def test_notify_keyword_promoted_to_global_automatic(email_service, config_service):
    keyword_name = "ClimateChange"
    old_org_id = 123
    org_user = User(id=20, name="Alice OrgUser", email="alice@org.com")
    promoter_user = User(id=99, name="Bob Promoter", email="bob@promoter.com")

    email_service._get_users_with_permission_in_organisation = Mock(
        side_effect=[[org_user, promoter_user], []]
    )

    email_service._get_manage_roles_users = Mock(return_value=[])
    email_service._get_roles_with_permission = Mock(return_value=[])
    email_service._get_users_by_iam_role = Mock(return_value=[])

    config_service._config = {
        "email_templates": {
            "KEYWORD_PROMOTED": {
                "subject": "Keyword Promoted to Global: $keyword_name",
                "body": (
                    "Dear $recipient_name,\n\n"
                    'The keyword "$keyword_name" from your organisation has been promoted to global status by $promoter_name.\n\nThank you'
                ),
            }
        }
    }

    with patch("smtplib.SMTP") as mock_smtp:
        smtp = mock_smtp.return_value.__enter__.return_value

        email_service.notify_keyword_promoted_to_global(
            old_organisation_id=old_org_id,
            keyword_name=keyword_name,
            promoter=promoter_user.id,
        )

        assert smtp.send_message.call_count == 2

        sent_emails = [
            call_args[0][0] for call_args in smtp.send_message.call_args_list
        ]

        to_addresses = [email["To"] for email in sent_emails]
        assert "alice@org.com" in to_addresses
        assert "bob@promoter.com" in to_addresses

        for email in sent_emails:
            assert email["From"] == os.getenv("SENDER_EMAIL")
            assert email["Subject"] == "Keyword Promoted to Global: ClimateChange"
            content = email.get_content()
            assert "ClimateChange" in content
            assert "has been promoted to global status by Bob Promoter" in content
