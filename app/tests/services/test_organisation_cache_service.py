import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from schemas.organisation import ResourceOrganisation
from repositories.organisation import OrganisationRepository
from services.organisation_cache import OrganisationCache, get_organisation_cache
from models.organisation import Organisation


@pytest.fixture
def organisation_repository():
    return Mock(spec=OrganisationRepository)


@pytest.fixture
def organisation_cache(organisation_repository):
    return OrganisationCache(organisation_repository)


@pytest.fixture
def sample_organisations():
    return [
        Organisation(
            id=1,
            name="Organisation 1",
            email="org1@example.com",
            type="Company",
            contacts=[],
            user_assignments=set(),
        ),
        Organisation(
            id=2,
            name="Organisation 2",
            email="org2@example.com",
            type="NGO",
            contacts=[],
            user_assignments=set(),
        ),
    ]


@pytest.fixture
def sample_resource_organisations():
    return [
        ResourceOrganisation(
            id=1,
            name="Organisation 1",
            email="org1@example.com",
            type="Company",
            is_deprecated=False,
            category=None,
            accessible_within_ctie=None,
            contacts=[],
        ),
        ResourceOrganisation(
            id=2,
            name="Organisation 2",
            email="org2@example.com",
            type="NGO",
            is_deprecated=False,
            category=None,
            accessible_within_ctie=None,
            contacts=[],
        ),
    ]


def test_initial_state(organisation_cache):
    assert organisation_cache.data is None
    assert organisation_cache.last_updated is None
    assert organisation_cache.expiry_time == timedelta(hours=10)


def test_is_valid_when_empty(organisation_cache):
    assert not organisation_cache.is_valid()


def test_is_valid_when_data_exists(organisation_cache, sample_resource_organisations):
    organisation_cache.data = sample_resource_organisations
    organisation_cache.last_updated = datetime.now()
    assert organisation_cache.is_valid()


def test_is_valid_when_expired(organisation_cache, sample_resource_organisations):
    organisation_cache.data = sample_resource_organisations
    organisation_cache.last_updated = datetime.now() - timedelta(hours=11)
    assert not organisation_cache.is_valid()


def test_set(organisation_cache, sample_resource_organisations):
    with patch("services.organisation_cache.datetime") as mock_datetime:
        mock_now = datetime.now()
        mock_datetime.now.return_value = mock_now

        organisation_cache.set(sample_resource_organisations)

        assert organisation_cache.data == sample_resource_organisations
        assert organisation_cache.last_updated == mock_now


def test_invalidate(organisation_cache, sample_resource_organisations):
    organisation_cache.data = sample_resource_organisations
    organisation_cache.last_updated = datetime.now()

    organisation_cache.invalidate()

    assert organisation_cache.data is None
    assert organisation_cache.last_updated is None


def test_get_all_with_cache_hit(organisation_cache, sample_resource_organisations):
    organisation_cache.data = sample_resource_organisations
    organisation_cache.last_updated = datetime.now()

    result = organisation_cache.get_all()
    assert result == sample_resource_organisations
    organisation_cache._repository.get_organisations.assert_not_called()


def test_get_all_with_cache_miss(
    organisation_cache, sample_organisations, sample_resource_organisations
):
    organisation_cache.data = None
    organisation_cache.last_updated = None
    organisation_cache._repository.get_organisations.return_value = sample_organisations

    with patch(
        "services.organisation_cache.organisation_entity_to_resource"
    ) as mock_transform:
        mock_transform.side_effect = lambda org: ResourceOrganisation(
            id=org.id,
            name=org.name,
            email=org.email,
            type=org.type,
            is_deprecated=False,
            category=None,
            accessible_within_ctie=None,
            contacts=[],
        )

        result = organisation_cache.get_all()

        organisation_cache._repository.get_organisations.assert_called_once()
        assert len(result) == len(sample_organisations)
        assert organisation_cache.data is not None
        assert organisation_cache.last_updated is not None
