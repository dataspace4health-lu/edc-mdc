import pytest
from sqlalchemy.orm import Session
from models.organisation import Organisation
from repositories.organisation import OrganisationRepository
from test_factory import sample_organisation
from fastapi import HTTPException


@pytest.fixture
def organisation_repository(db_session: Session) -> OrganisationRepository:
    return OrganisationRepository(db_session)


def test_add_organisation(organisation_repository: OrganisationRepository):
    new_organisation = Organisation(
        name="New Organisation",
        email="new.org@example.com",
        type="Company",
    )
    organisation_repository.add(new_organisation)
    organisation_repository.commit()

    retrieved_organisation = organisation_repository.get_organisation(
        new_organisation.id
    )

    assert retrieved_organisation is not None
    assert retrieved_organisation.name == new_organisation.name
    assert retrieved_organisation.email == new_organisation.email


def test_get_organisation_exists(organisation_repository: OrganisationRepository):
    sample_org = Organisation(
        name="Existing Organisation",
        email="existing@organisation.com",
        type="NGO",
    )
    organisation_repository.add(sample_org)
    organisation_repository.commit()

    result = organisation_repository.get_organisation(sample_org.id)
    assert result is not None
    assert result.name == sample_org.name
    assert result.email == sample_org.email


def test_get_organisation_not_found(organisation_repository: OrganisationRepository):
    with pytest.raises(HTTPException) as excinfo:
        organisation_repository.get_organisation(9999)
    assert excinfo.value.status_code == 404


def test_update_organisation(organisation_repository: OrganisationRepository):
    sample_org = Organisation(
        name="Update Organisation",
        email="update@organisation.com",
        type="Company",
    )
    organisation_repository.add(sample_org)
    organisation_repository.commit()

    sample_org.name = "Updated Name"
    organisation_repository.update(sample_org)
    organisation_repository.commit()

    updated_org = organisation_repository.get_organisation(sample_org.id)
    assert updated_org.name == "Updated Name"


def test_organisation_exists_by_name(
    organisation_repository: OrganisationRepository,
):
    organisation = Organisation(
        name="Sample Organisation",
        email="contact@organisation.com",
        type="Company",
    )
    organisation_repository.add(organisation)
    organisation_repository.commit()

    assert organisation_repository.exists_by_name("Sample Organisation") is True
    assert organisation_repository.exists_by_name("Nonexistent Org") is False


def test_set_deprecation_status_true(organisation_repository: OrganisationRepository):
    organisation = Organisation(
        name="Test Organisation",
        email="test@organisation.com",
        type="Company",
        is_deprecated=False,
    )
    organisation_repository.add(organisation)
    organisation_repository.commit()

    # Set deprecation status to True
    organisation_repository.set_deprecation_status(organisation.id, True)
    organisation_repository.commit()

    # Verify deprecation
    deprecated_org = organisation_repository.get_organisation(organisation.id)
    assert deprecated_org.is_deprecated is True


def test_set_deprecation_status_false(organisation_repository: OrganisationRepository):
    organisation = Organisation(
        name="Test Organisation",
        email="test@organisation.com",
        type="Company",
        is_deprecated=True,  # Start as deprecated
    )
    organisation_repository.add(organisation)
    organisation_repository.commit()

    # Set deprecation status to False (restore)
    organisation_repository.set_deprecation_status(organisation.id, False)
    organisation_repository.commit()

    # Verify restoration
    restored_org = organisation_repository.get_organisation(organisation.id)
    assert restored_org.is_deprecated is False


def test_set_deprecation_status_organisation_not_found(
    organisation_repository: OrganisationRepository,
):
    # Try to set deprecation status on non-existent organisation
    with pytest.raises(HTTPException) as excinfo:
        organisation_repository.set_deprecation_status(9999, True)
    assert excinfo.value.status_code == 404
