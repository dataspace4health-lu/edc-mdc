import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
from models.organisation import Organisation
from models.user import User
from models.user_assignment import UserOrganisationAssignment, RoleAssignment
from schemas.user_assignment import UserAssignmentDto
from schemas.organisation import ResourceOrganisation
from services.user_assignment import UserAssignmentService
from services.user_assignment_permissions import UserAssignmentPermissionsService
from repositories.organisation import OrganisationRepository
from repositories.user_assignment import UserAssignmentRepository
from services.activity_logs.user_assignment_activity_log_service import (
    UserAssignmentActivityLogService,
)
from services.email_service import EmailService
from repositories.user import UserRepository
from models.identity_context import IdentityContext
from fastapi import HTTPException


@pytest.fixture
def mock_repositories():
    return {
        "organisation_repository": Mock(spec=OrganisationRepository),
        "user_assignment_repository": Mock(spec=UserAssignmentRepository),
        "user_repository": Mock(spec=UserRepository),
        "permissions_service": Mock(spec=UserAssignmentPermissionsService),
        "activity_log_service": Mock(spec=UserAssignmentActivityLogService),
        "email_service": Mock(spec=EmailService),
    }


@pytest.fixture
def mock_resource_organisation():
    return ResourceOrganisation(
        id=1,
        name="Test Organisation",
        type="Organisation",
        is_deprecated=False,
        email="test@organisation.com",
        category=None,
        accessible_within_ctie=None,
        contacts=[],
    )


@pytest.fixture
def user_assignment_service(mock_repositories, mock_resource_organisation):
    # Create service with mocked repositories
    service = UserAssignmentService(
        organisation_repository=mock_repositories["organisation_repository"],
        user_assignment_repository=mock_repositories["user_assignment_repository"],
        user_repository=mock_repositories["user_repository"],
        permissions_service=mock_repositories["permissions_service"],
        activity_log_service=mock_repositories["activity_log_service"],
        email_service=mock_repositories["email_service"],
    )

    # Patch the organization_entity_to_resource function to return our mocked ResourceOrganisation
    with patch(
        "schemas.organisation.organisation_entity_to_resource"
    ) as mock_converter:
        mock_converter.return_value = mock_resource_organisation
        yield service


@pytest.fixture
def identity():
    return IdentityContext(user_id=1, permissions=["organisations:edit"])


@pytest.fixture
def test_organisation():
    org = MagicMock(spec=Organisation)
    org.id = 1
    org.name = "Test Organisation"
    org.email = "test@organisation.com"
    org.type = "Organisation"
    org.is_deprecated = False
    org.contacts = []
    org.user_assignments = []
    return org


@pytest.fixture
def test_user():
    return User(
        id=2,
        name="Test User",
        email="testuser@example.com",
        external_id="ext-id-1234",
        iam_roles="user",
    )


@pytest.fixture
def test_assignment_dto(test_user):
    return UserAssignmentDto(email=test_user.email, role_id=1, organisation_id=1)


@pytest.fixture
def test_user_assignment():
    assignment = UserOrganisationAssignment(user_id=2, organisation_id=1)
    assignment.roles.add(RoleAssignment(role_id=1))
    return assignment


def test_create_user_organisation_assignment(
    user_assignment_service,
    mock_repositories,
    test_organisation,
    test_user,
    test_assignment_dto,
    identity,
    mock_resource_organisation,
):
    mock_repositories[
        "user_assignment_repository"
    ].get_user_organisation_assignment.return_value = None

    mock_repositories["user_repository"].get_user_by_email.return_value = test_user

    mock_organisation = Mock()
    mock_organisation.id = test_organisation.id
    mock_organisation.name = test_organisation.name
    mock_organisation.type = test_organisation.type
    mock_organisation.email = test_organisation.email
    mock_organisation.is_deprecated = False
    mock_organisation.category = None
    mock_organisation.accessible_within_ctie = None
    mock_organisation.contacts = []

    mock_repositories["organisation_repository"].get_organisation.return_value = (
        mock_organisation
    )

    # Call method under test
    result = user_assignment_service.create_user_organisation_assignment(
        test_organisation.id, test_assignment_dto, identity
    )

    mock_repositories["user_repository"].get_user_by_email.assert_called_once_with(
        test_user.email
    )
    mock_repositories[
        "user_assignment_repository"
    ].get_user_organisation_assignment.assert_called_once_with(
        organisation_id=test_organisation.id, user_id=test_user.id
    )
    mock_repositories[
        "user_assignment_repository"
    ].add_user_organisation_assignment.assert_called_once()
    mock_repositories["user_assignment_repository"].commit.assert_called_once()
    mock_repositories["user_assignment_repository"].refresh.assert_called_once()
    mock_repositories["email_service"].notify_role_assigned.assert_called_once()


def test_create_multiple_roles_for_same_user_org(
    user_assignment_service,
    mock_repositories,
    test_organisation,
    test_user,
    identity,
):
    role_ids = [1, 2, 3]

    user_assignment = UserOrganisationAssignment(
        user_id=test_user.id, organisation_id=test_organisation.id
    )
    user_assignment.roles = set()

    assignment_created = {"count": 0}

    def get_user_assignment_mock(organisation_id, user_id):
        if assignment_created["count"] == 0:
            return None
        return user_assignment

    def add_assignment_mock(assignment):
        assignment_created["count"] += 1
        user_assignment.roles.update(assignment.roles)

    mock_repositories["user_repository"].get_user_by_email.return_value = test_user
    mock_repositories[
        "user_assignment_repository"
    ].get_user_organisation_assignment.side_effect = get_user_assignment_mock
    mock_repositories[
        "user_assignment_repository"
    ].add_user_organisation_assignment.side_effect = add_assignment_mock
    mock_repositories["user_assignment_repository"].commit.return_value = None
    mock_repositories["user_assignment_repository"].refresh.return_value = None

    fake_org = Mock()
    fake_org.id = test_organisation.id
    fake_org.name = test_organisation.name
    fake_org.email = test_organisation.email
    fake_org.type = test_organisation.type
    fake_org.contacts = []
    fake_org.is_deprecated = False
    fake_org.category = None
    fake_org.accessible_within_ctie = None
    mock_repositories["organisation_repository"].get_organisation.return_value = (
        fake_org
    )

    for role_id in role_ids:
        dto = UserAssignmentDto(
            email=test_user.email,
            role_id=role_id,
            organisation_id=test_organisation.id,
        )
        user_assignment_service.create_user_organisation_assignment(
            test_organisation.id, dto, identity
        )

    assigned_role_ids = {role.role_id for role in user_assignment.roles}
    assert assigned_role_ids == set(role_ids)

    assert assignment_created["count"] == 1
    assert mock_repositories["email_service"].notify_role_assigned.call_count == 3


def test_delete_user_organisation_assignment(
    user_assignment_service,
    mock_repositories,
    test_organisation,
    test_user,
    test_user_assignment,
    identity,
):
    mock_repositories[
        "user_assignment_repository"
    ].get_user_organisation_assignment.return_value = test_user_assignment

    # Call method under test
    user_assignment_service.delete_user_organisation_assignment(
        test_organisation.id, test_user.id, identity
    )

    mock_repositories[
        "user_assignment_repository"
    ].get_user_organisation_assignment.assert_called_once_with(
        organisation_id=test_organisation.id, user_id=test_user.id
    )
    mock_repositories[
        "user_assignment_repository"
    ].delete_user_organisation_assignment.assert_called_once_with(test_user_assignment)
    mock_repositories["user_assignment_repository"].commit.assert_called_once()


def test_delete_nonexistent_user_organisation_assignment(
    user_assignment_service, mock_repositories, test_organisation, test_user, identity
):
    # Setup mock returns
    mock_repositories["organisation_repository"].get_organisation.return_value = (
        test_organisation
    )
    mock_repositories[
        "user_assignment_repository"
    ].get_user_organisation_assignment.return_value = None

    # Call method under test and expect exception
    with pytest.raises(HTTPException) as exc_info:
        user_assignment_service.delete_user_organisation_assignment(
            test_organisation.id, test_user.id, identity
        )

    # Assertions
    assert exc_info.value.status_code == 404
    assert (
        f"User[{test_user.id}] is not assigned to Organisation[{test_organisation.id}]"
        in str(exc_info.value.detail)
    )


def test_delete_user_role_assignment_removes_role(
    user_assignment_service,
    mock_repositories,
    test_organisation,
    test_user,
    test_user_assignment,
    identity,
):
    test_user_assignment.roles = {RoleAssignment(role_id=1), RoleAssignment(role_id=2)}
    mock_repositories[
        "user_assignment_repository"
    ].get_user_organisation_assignment.return_value = test_user_assignment

    user_assignment_service.delete_user_role_assignment(
        organisation_id=test_organisation.id,
        user_id=test_user.id,
        role_id=1,
        identity=identity,
    )

    assert all(role.role_id != 1 for role in test_user_assignment.roles)
    mock_repositories["user_assignment_repository"].commit.assert_called_once()


def test_delete_user_role_assignment_removes_last_role_and_deletes_assignment(
    user_assignment_service,
    mock_repositories,
    test_organisation,
    test_user,
    identity,
):
    assignment = UserOrganisationAssignment(
        user_id=test_user.id, organisation_id=test_organisation.id
    )
    assignment.roles = {RoleAssignment(role_id=1)}

    mock_repositories[
        "user_assignment_repository"
    ].get_user_organisation_assignment.return_value = assignment

    user_assignment_service.delete_user_role_assignment(
        organisation_id=test_organisation.id,
        user_id=test_user.id,
        role_id=1,
        identity=identity,
    )

    mock_repositories[
        "user_assignment_repository"
    ].delete_user_organisation_assignment.assert_called_once_with(assignment)
    mock_repositories["user_assignment_repository"].commit.assert_called_once()


def test_delete_user_role_assignment_raises_if_assignment_not_found(
    user_assignment_service,
    mock_repositories,
    test_organisation,
    test_user,
    identity,
):
    mock_repositories[
        "user_assignment_repository"
    ].get_user_organisation_assignment.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        user_assignment_service.delete_user_role_assignment(
            organisation_id=test_organisation.id,
            user_id=test_user.id,
            role_id=1,
            identity=identity,
        )

    assert exc_info.value.status_code == 404
    assert (
        f"User[{test_user.id}] is not assigned to Organisation[{test_organisation.id}]"
        in str(exc_info.value.detail)
    )


def test_delete_user_role_assignment_raises_if_role_not_found(
    user_assignment_service,
    mock_repositories,
    test_organisation,
    test_user,
    test_user_assignment,
    identity,
):
    mock_repositories[
        "user_assignment_repository"
    ].get_user_organisation_assignment.return_value = test_user_assignment

    with pytest.raises(HTTPException) as exc_info:
        user_assignment_service.delete_user_role_assignment(
            organisation_id=test_organisation.id,
            user_id=test_user.id,
            role_id=999,
            identity=identity,
        )

    assert exc_info.value.status_code == 404
    assert (
        f"User does not have Role[999] in Organisation[{test_organisation.id}]"
        in str(exc_info.value.detail)
    )
