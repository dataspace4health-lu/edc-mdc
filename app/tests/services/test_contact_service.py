import pytest
from sqlalchemy.orm import Session
from models.contact import Contact
from models.organisation import Organisation
from repositories.contact import ContactRepository
from schemas.contact import ContactDto, ResourceContact
from services.contact import ContactService
from unittest.mock import Mock
from deepdiff import DeepDiff
from test_factory import sample_organisation
from services.database_session_manager import DatabaseSessionManager
from models.identity_context import IdentityContext
from fastapi import HTTPException
from unittest.mock import MagicMock
from repositories.contact import ContactRepository
from schemas.contact import contact_entity_to_resource
from services.organisation_cache import OrganisationCache, get_organisation_cache
from services.activity_logs.organisation_activity_log import (
    OrganisationActivityLogService,
)
from services.permissions.contact_permissions import ContactPermissionsService
from repositories.organisation import OrganisationRepository


@pytest.fixture
def contact_service() -> ContactService:
    return ContactService(
        contact_repository=Mock(spec=ContactRepository),
        activity_log_service=Mock(spec=OrganisationActivityLogService),
        organisation_cache=Mock(spec=OrganisationCache),
        contact_permissions_service=Mock(spec=ContactPermissionsService),
        organisation_repository=Mock(spec=OrganisationRepository),
    )


@pytest.fixture
def identity() -> IdentityContext:
    return IdentityContext(user_id=1, permissions=[])


@pytest.fixture
def expected_contact() -> ResourceContact:
    """Fixture to create a sample expected ResourceContact."""
    return ResourceContact(
        id=1,
        name="John Doe",
        email="john.doe@example.com",
        role="Manager",
        is_deprecated=False,
    )


@pytest.fixture
def contact() -> Contact:
    return Contact(
        id=1,
        name="John Doe",
        email="john.doe@example.com",
        role="Manager",
        is_deprecated=False,
    )


@pytest.fixture
def contact_dto() -> ContactDto:
    """Fixture to define a contact DTO."""
    return ContactDto(
        name="John Doe",
        email="john.doe@example.com",
        role="Manager",
    )


@pytest.fixture
def organisation_id(sample_organisation: Organisation) -> int:
    return sample_organisation.id


def test_add_contact_duplicate(
    contact_service: ContactService,
    contact_dto: ContactDto,
    sample_organisation: Organisation,
    identity: IdentityContext,
):
    organisation_id = sample_organisation.id

    contact_service._contact_repository.exists_by_name_or_email.return_value = True

    with pytest.raises(HTTPException) as excinfo:
        contact_service.add_contact(organisation_id, contact_dto, identity)

    assert excinfo.value.status_code == 400
    assert "already exists" in str(excinfo.value.detail)

    contact_service._contact_repository.exists_by_name_or_email.assert_called_once_with(
        organisation_id, contact_dto.name, contact_dto.email
    )


def test_add_contact_success(
    contact_service: ContactService,
    contact_dto: ContactDto,
    identity: IdentityContext,
    organisation_id: int,
):
    contact_service._contact_repository.exists_by_name_or_email.return_value = False
    contact_service._contact_repository.add.side_effect = lambda c: setattr(c, "id", 1)
    contact_service._contact_repository.commit.return_value = None

    mock_activity_log_service = MagicMock()
    contact_service._activity_log_service = mock_activity_log_service

    actual = contact_service.add_contact(organisation_id, contact_dto, identity)

    assert actual.id == 1
    assert actual.name == contact_dto.name
    assert actual.email == contact_dto.email
    assert actual.role == contact_dto.role

    args, _ = mock_activity_log_service.log_contact_added_to_organisation.call_args
    assert args[0] == identity.user_id
    assert args[1] == organisation_id
    assert args[2].name == contact_dto.name
    assert args[2].email == contact_dto.email

    contact_service._contact_repository.exists_by_name_or_email.assert_called_once_with(
        organisation_id, contact_dto.name, contact_dto.email
    )
    contact_service._contact_repository.add.assert_called_once()
    contact_service._contact_repository.commit.assert_called_once()
    contact_service._cache.invalidate.assert_called_once()


def test_update_contact(
    contact_service: ContactService,
    expected_contact: ResourceContact,
    contact: Contact,
    contact_dto: ContactDto,
    identity: IdentityContext,
    organisation_id: int,
):
    contact_service._contact_repository.get_contact_by_id.return_value = contact
    contact_service._contact_repository.commit.return_value = None

    mock_activity_log_service = MagicMock()
    contact_service._activity_log_service = mock_activity_log_service

    old_contact_dict = contact.to_dict()

    actual = contact_service.update_contact(
        organisation_id, contact.id, contact_dto, identity
    )

    mock_activity_log_service.log_contact_updated_in_organisation.assert_called_once_with(
        identity.user_id, organisation_id, old_contact_dict, contact
    )

    assert not DeepDiff(expected_contact, actual, ignore_order=True)

    contact_service._contact_repository.commit.assert_called_once()


def test_delete_contact_success(
    contact_service: ContactService,
    contact: Contact,
    identity: IdentityContext,
    organisation_id: int,
):
    contact_service._contact_repository.get_contact_by_id.return_value = contact
    contact_service._contact_repository.is_contact_assigned_to_dataset.return_value = (
        False
    )
    contact_service._contact_repository.delete.return_value = None
    contact_service._contact_repository.commit.return_value = None

    mock_activity_log_service = MagicMock()
    contact_service._activity_log_service = mock_activity_log_service

    # Mock the to_dict method for the contact
    contact.to_dict = MagicMock(
        return_value={
            "id": contact.id,
            "name": contact.name,
            "email": contact.email,
            "role": contact.role,
        }
    )

    # Call delete_contact - should not raise any exception
    contact_service.delete_contact(organisation_id, contact.id, identity)

    # Verify all the expected calls were made
    contact_service._contact_permissions_service.validate_contact_permissions.assert_called_once_with(
        organisation_id, identity
    )
    contact_service._contact_repository.get_contact_by_id.assert_called_once_with(
        organisation_id, contact.id
    )
    contact_service._contact_repository.is_contact_assigned_to_dataset.assert_called_once_with(
        contact.id
    )
    contact_service._contact_repository.delete.assert_called_once_with(contact)
    contact_service._contact_repository.commit.assert_called_once()
    contact_service._cache.invalidate.assert_called_once()

    # Verify activity logging
    mock_activity_log_service.log_contact_deleted_from_organisation.assert_called_once_with(
        identity.user_id, organisation_id, contact.to_dict.return_value
    )


def test_update_deprecation_status_deprecate(
    contact_service: ContactService,
    contact: Contact,
    identity: IdentityContext,
    organisation_id: int,
):
    contact.is_deprecated = False
    contact_service._contact_repository.get_contact_by_id.return_value = contact

    mock_updated_contact = Contact(
        id=contact.id,
        name=contact.name,
        email=contact.email,
        role=contact.role,
        is_deprecated=True,
    )
    contact_service._contact_repository.get_contact_by_id.side_effect = [
        contact,
        mock_updated_contact,
    ]

    result = contact_service.update_deprecation_status(
        organisation_id, contact.id, identity
    )

    assert result.is_deprecated is True
    contact_service._contact_repository.set_deprecation_status.assert_called_once_with(
        contact.id, organisation_id, True
    )


def test_update_deprecation_status_restore(
    contact_service: ContactService,
    contact: Contact,
    identity: IdentityContext,
    organisation_id: int,
):
    contact.is_deprecated = True
    contact_service._contact_repository.get_contact_by_id.return_value = contact

    mock_updated_contact = Contact(
        id=contact.id,
        name=contact.name,
        email=contact.email,
        role=contact.role,
        is_deprecated=False,
    )
    contact_service._contact_repository.get_contact_by_id.side_effect = [
        contact,
        mock_updated_contact,
    ]

    result = contact_service.update_deprecation_status(
        organisation_id, contact.id, identity
    )

    assert result.is_deprecated is False
    contact_service._contact_repository.set_deprecation_status.assert_called_once_with(
        contact.id, organisation_id, False
    )
