import pytest
from unittest.mock import Mock
from fastapi import HTTPException
from models.identity_context import IdentityContext
from repositories.user_assignment import UserAssignmentRepository
from services.permissions.organisation_permissions import OrganisationPermissionsService


@pytest.fixture
def user_assignment_repository():
    return Mock(spec=UserAssignmentRepository)


@pytest.fixture
def service(user_assignment_repository):
    return OrganisationPermissionsService(
        user_assignment_repository=user_assignment_repository,
    )


def test_validate_get_organisation_permissions_contacts_edit_permission(service):
    organisation_id = 123
    identity = IdentityContext(user_id=456, permissions=["contacts:edit"])

    service.validate_get_organisation_permissions(organisation_id, identity)

    service._user_assignment_repository.get_user_organisation_assignment.assert_not_called()


def test_validate_get_organisation_permissions_organisations_edit_permission(service):
    organisation_id = 123
    identity = IdentityContext(user_id=456, permissions=["organisations:edit"])

    service.validate_get_organisation_permissions(organisation_id, identity)

    service._user_assignment_repository.get_user_organisation_assignment.assert_not_called()


def test_validate_get_organisation_permissions_contacts_edit_organisation_user_belongs_to_org(
    service,
):
    organisation_id = 123
    identity = IdentityContext(user_id=456, permissions=["contacts:edit:organisation"])

    service._user_assignment_repository.get_user_organisation_assignment.return_value = (
        Mock()
    )

    service.validate_get_organisation_permissions(organisation_id, identity)

    service._user_assignment_repository.get_user_organisation_assignment.assert_called_once_with(
        organisation_id=123, user_id=456
    )


def test_validate_get_organisation_permissions_organisations_edit_organisation_user_belongs_to_org(
    service,
):
    organisation_id = 123
    identity = IdentityContext(
        user_id=456, permissions=["organisations:edit:organisation"]
    )

    service._user_assignment_repository.get_user_organisation_assignment.return_value = (
        Mock()
    )

    service.validate_get_organisation_permissions(organisation_id, identity)

    service._user_assignment_repository.get_user_organisation_assignment.assert_called_once_with(
        organisation_id=123, user_id=456
    )


def test_validate_get_organisation_permissions_organisation_scoped_user_not_belongs_to_org(
    service,
):
    organisation_id = 123
    identity = IdentityContext(user_id=456, permissions=["contacts:edit:organisation"])

    service._user_assignment_repository.get_user_organisation_assignment.return_value = (
        None
    )

    with pytest.raises(HTTPException) as exc_info:
        service.validate_get_organisation_permissions(organisation_id, identity)

    assert exc_info.value.status_code == 403
    assert "You can only access organisations you belong to" == exc_info.value.detail

    # Should check user assignment
    service._user_assignment_repository.get_user_organisation_assignment.assert_called_once_with(
        organisation_id=123, user_id=456
    )


def test_validate_update_organisation_permissions_organisations_edit_permission(
    service,
):
    organisation_id = 123
    identity = IdentityContext(user_id=456, permissions=["organisations:edit"])

    service.validate_update_organisation_permissions(organisation_id, identity)

    service._user_assignment_repository.get_user_organisation_assignment.assert_not_called()


def test_validate_update_organisation_permissions_organisation_scoped_user_belongs_to_org(
    service,
):
    organisation_id = 123
    identity = IdentityContext(
        user_id=456, permissions=["organisations:edit:organisation"]
    )

    service._user_assignment_repository.get_user_organisation_assignment.return_value = (
        Mock()
    )

    service.validate_update_organisation_permissions(organisation_id, identity)

    service._user_assignment_repository.get_user_organisation_assignment.assert_called_once_with(
        organisation_id=123, user_id=456
    )


def test_validate_update_organisation_permissions_organisation_scoped_user_not_belongs_to_org(
    service,
):
    organisation_id = 123
    identity = IdentityContext(
        user_id=456, permissions=["organisations:edit:organisation"]
    )

    service._user_assignment_repository.get_user_organisation_assignment.return_value = (
        None
    )

    with pytest.raises(HTTPException) as exc_info:
        service.validate_update_organisation_permissions(organisation_id, identity)

    assert exc_info.value.status_code == 403
    assert "You can only update organisations you belong to" == exc_info.value.detail

    service._user_assignment_repository.get_user_organisation_assignment.assert_called_once_with(
        organisation_id=123, user_id=456
    )
