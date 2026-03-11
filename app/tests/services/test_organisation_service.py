import pytest
from sqlalchemy.orm import Session
from models.organisation import Organisation, Contact
from schemas.organisation import OrganisationDto, ResourceOrganisation
from schemas.contact import ContactDto, ResourceContact
from services.organisation import OrganisationService
from services.organisation_cache import OrganisationCache
from services.permissions.organisation_permissions import OrganisationPermissionsService
from repositories.organisation import OrganisationRepository
from unittest.mock import Mock
from deepdiff import DeepDiff
from models.identity_context import IdentityContext
from unittest.mock import MagicMock


@pytest.fixture
def organisation_service() -> OrganisationService:
    return OrganisationService(
        organisation_repository=Mock(spec=OrganisationRepository),
        organisation_cache=Mock(spec=OrganisationCache),
        organisation_permissions_service=Mock(spec=OrganisationPermissionsService),
    )


@pytest.fixture
def identity() -> IdentityContext:
    return IdentityContext(user_id=1, permissions=[])


@pytest.fixture
def expected_organisation() -> ResourceOrganisation:
    return ResourceOrganisation(
        id=1,
        name="Organisation 1",
        email="contact@organisation.com",
        type="Company",
        is_deprecated=False,
        category=None,
        accessible_within_ctie=None,
        contacts=[
            ResourceContact(
                id=1,
                name="John Doe",
                email="john.doe@example.com",
                role="Manager",
                is_deprecated=False,
            )
        ],
    )


@pytest.fixture
def organisation() -> Organisation:
    contact1 = Contact(
        id=1,
        name="John Doe",
        email="john.doe@example.com",
        role="Manager",
        is_deprecated=False,
    )
    return Organisation(
        id=1,
        name="Organisation 1",
        email="contact@organisation.com",
        type="Company",
        is_deprecated=False,
        contacts=[contact1],
        user_assignments=set(),
    )


@pytest.fixture
def organisation_dto() -> OrganisationDto:
    return OrganisationDto(
        name="Organisation 1",
        email="contact@organisation.com",
        type="Company",
        category=None,
        accessible_within_ctie=None,
        contacts=[
            ContactDto(name="John Doe", email="john.doe@example.com", role="Manager")
        ],
    )


def test_get_organisation(
    organisation_service: OrganisationService,
    expected_organisation: ResourceOrganisation,
    organisation: Organisation,
    identity: IdentityContext,
):
    organisation_service._organisation_repository.get_organisation.return_value = (
        organisation
    )
    actual = organisation_service.get_organisation(organisation.id, identity)
    assert not DeepDiff(expected_organisation, actual, ignore_order=True)
    organisation_service._organisation_repository.get_organisation.assert_called_once_with(
        organisation.id
    )
    organisation_service._organisation_permissions_service.validate_get_organisation_permissions.assert_called_once_with(
        organisation.id, identity
    )


def test_create_organisation(
    organisation_service: OrganisationService,
    expected_organisation: ResourceOrganisation,
    organisation_dto: OrganisationDto,
    identity: IdentityContext,
):
    contact1 = Contact(
        id=1,
        name=organisation_dto.contacts[0].name,
        email=organisation_dto.contacts[0].email,
        role=organisation_dto.contacts[0].role,
        is_deprecated=False,
    )
    organisation = Organisation(
        id=1,
        name=organisation_dto.name,
        type=organisation_dto.type,
        is_deprecated=False,
        contacts=[contact1],
    )
    organisation_service._organisation_repository.exists_by_name.return_value = False
    organisation_service._organisation_repository.add.side_effect = lambda org: [
        setattr(org, "id", 1),
        setattr(org.contacts[0], "id", 1),
    ]

    organisation_service._organisation_repository.commit.return_value = None
    organisation_service._organisation_repository.refresh.return_value = None
    mock_activity_log_service = MagicMock()
    organisation_service._activity_log_service = mock_activity_log_service
    actual = organisation_service.create_organisation(organisation_dto, identity)
    mock_activity_log_service.log_organisation_activities.assert_called_once_with(
        identity.user_id,
        organisation.id,
        {},
        organisation_dto,
        "create",
    )

    assert not DeepDiff(expected_organisation, actual, ignore_order=True)
    organisation_service._organisation_repository.exists_by_name.assert_called_once_with(
        organisation_dto.name
    )
    organisation_service._organisation_repository.add.assert_called_once()
    organisation_service._organisation_repository.commit.assert_called_once()
    organisation_service._organisation_repository.refresh.assert_called_once()
    organisation_service._cache.invalidate.assert_called_once()


def test_update_organisation(
    organisation_service: OrganisationService,
    expected_organisation: ResourceOrganisation,
    organisation: Organisation,
    organisation_dto: OrganisationDto,
    identity: IdentityContext,
):
    organisation_service._organisation_repository.get_organisation.return_value = (
        organisation
    )
    organisation_service._organisation_repository.commit.return_value = None
    organisation_service._organisation_repository.refresh.return_value = None
    mock_activity_log_service = MagicMock()
    organisation_service._activity_log_service = mock_activity_log_service
    actual = organisation_service.update_organisation(
        organisation.id, organisation_dto, identity
    )
    mock_activity_log_service.log_organisation_activities.assert_called_once_with(
        identity.user_id,
        organisation.id,
        organisation.to_dict_for_diff(),
        organisation_dto,
        "update",
    )

    assert not DeepDiff(expected_organisation, actual, ignore_order=True)

    organisation_service._organisation_repository.commit.assert_called_once()
    organisation_service._organisation_repository.refresh.assert_called_once()
    organisation_service._cache.invalidate.assert_called_once()
    organisation_service._organisation_permissions_service.validate_update_organisation_permissions.assert_called_once_with(
        organisation.id, identity
    )


def test_toggle_organisation_deprecation_to_deprecated():
    contact = Contact(
        id=1, name="John", email="john@example.com", role="Manager", is_deprecated=False
    )
    organisation = Organisation(
        id=1,
        name="Test Org",
        email="test@org.com",
        type="Company",
        is_deprecated=False,
        contacts=[contact],
        user_assignments=set(),
    )
    identity = IdentityContext(user_id=1, permissions=[])

    mock_repo = Mock()
    mock_repo.get_organisation.return_value = organisation
    mock_repo.set_deprecation_status.side_effect = lambda org_id, status: setattr(
        organisation, "is_deprecated", status
    )
    mock_repo.commit.return_value = None
    mock_repo.refresh.return_value = None

    mock_cache = Mock()
    mock_activity_log = Mock()
    mock_permission_service = Mock()
    mock_contact_service = Mock()

    organisation_service = OrganisationService(
        organisation_repository=mock_repo,
        organisation_cache=mock_cache,
        activity_log_service=mock_activity_log,
        organisation_permissions_service=mock_permission_service,
        contact_service=mock_contact_service,
    )

    result: ResourceOrganisation = organisation_service.toggle_organisation_deprecation(
        organisation.id, identity
    )

    assert organisation.is_deprecated is True
    assert result.is_deprecated is True

    mock_permission_service.validate_update_organisation_permissions.assert_called_once_with(
        organisation.id, identity
    )
    mock_repo.get_organisation.assert_called_once_with(organisation.id)
    mock_repo.set_deprecation_status.assert_called_once_with(organisation.id, True)
    mock_repo.commit.assert_called_once()
    mock_repo.refresh.assert_called_once_with(organisation)
    mock_cache.invalidate.assert_called_once()

    mock_activity_log.log_organisation_activities.assert_called_once_with(
        identity.user_id,
        organisation.id,
        {"is_deprecated": False},
        {"is_deprecated": True},
        "deprecate",
    )


def test_toggle_organisation_deprecation_to_restored():
    contact = Contact(
        id=1, name="John", email="john@example.com", role="Manager", is_deprecated=False
    )
    organisation = Organisation(
        id=1,
        name="Test Org",
        email="test@org.com",
        type="Company",
        is_deprecated=True,  # Start with deprecated
        contacts=[contact],
        user_assignments=set(),
    )
    identity = IdentityContext(user_id=1, permissions=[])

    mock_repo = Mock()
    mock_repo.get_organisation.return_value = organisation
    mock_repo.set_deprecation_status.side_effect = lambda org_id, status: setattr(
        organisation, "is_deprecated", status
    )
    mock_repo.commit.return_value = None
    mock_repo.refresh.return_value = None

    mock_cache = Mock()
    mock_activity_log = Mock()
    mock_permission_service = Mock()
    mock_contact_service = Mock()

    organisation_service = OrganisationService(
        organisation_repository=mock_repo,
        organisation_cache=mock_cache,
        activity_log_service=mock_activity_log,
        organisation_permissions_service=mock_permission_service,
        contact_service=mock_contact_service,
    )

    result: ResourceOrganisation = organisation_service.toggle_organisation_deprecation(
        organisation.id, identity
    )

    assert organisation.is_deprecated is False
    assert result.is_deprecated is False

    mock_permission_service.validate_update_organisation_permissions.assert_called_once_with(
        organisation.id, identity
    )
    mock_repo.get_organisation.assert_called_once_with(organisation.id)
    mock_repo.set_deprecation_status.assert_called_once_with(organisation.id, False)
    mock_repo.commit.assert_called_once()
    mock_repo.refresh.assert_called_once_with(organisation)
    mock_cache.invalidate.assert_called_once()

    mock_activity_log.log_organisation_activities.assert_called_once_with(
        identity.user_id,
        organisation.id,
        {"is_deprecated": True},
        {"is_deprecated": False},
        "restore",
    )
