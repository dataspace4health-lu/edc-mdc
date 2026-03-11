import pytest
from sqlalchemy.orm import Session
from models.contact import Contact
from models.dataset import Dataset, DatasetContact
from repositories.contact import ContactRepository
from test_factory import sample_organisation, sample_dataset
from factories.contact import create_sample_contact
from fastapi import HTTPException


@pytest.fixture
def contact_repository(db_session: Session) -> ContactRepository:
    return ContactRepository(db_session)


def test_add_contact(contact_repository: ContactRepository, sample_organisation):
    new_contact = create_sample_contact(organisation_id=sample_organisation.id)
    contact_repository.add(new_contact)
    contact_repository.commit()

    retrieved_contact = contact_repository.get_contact_by_id(
        sample_organisation.id, new_contact.id
    )

    assert retrieved_contact is not None
    assert retrieved_contact.name == new_contact.name
    assert retrieved_contact.email == new_contact.email


def test_get_contact_exists(contact_repository: ContactRepository, sample_organisation):
    contact_id = sample_organisation.contacts[0].id
    contact = contact_repository.get_contact_by_id(sample_organisation.id, contact_id)

    assert contact is not None
    assert contact.name == sample_organisation.contacts[0].name
    assert contact.email == sample_organisation.contacts[0].email


def test_get_contact_not_found(
    contact_repository: ContactRepository, sample_organisation
):
    contact_id = 9999
    contact = contact_repository.get_contact_by_id(sample_organisation.id, contact_id)

    assert contact is None


def test_get_contact_by_email_exists(
    contact_repository: ContactRepository, sample_organisation
):
    existing_contact = sample_organisation.contacts[0]
    contact = contact_repository.get_contact_by_email(
        sample_organisation.id, existing_contact.email
    )

    assert contact is not None
    assert contact.id == existing_contact.id
    assert contact.name == existing_contact.name
    assert contact.email == existing_contact.email


def test_get_contact_by_email_case_insensitive(
    contact_repository: ContactRepository, sample_organisation
):
    new_contact = create_sample_contact(organisation_id=sample_organisation.id)
    new_contact.email = "test@example.com"
    contact_repository.add(new_contact)
    contact_repository.commit()

    # Test with uppercase
    contact_upper = contact_repository.get_contact_by_email(
        sample_organisation.id, "TEST@EXAMPLE.COM"
    )
    assert contact_upper is not None
    assert contact_upper.email == "test@example.com"

    # Test with mixed case
    contact_mixed = contact_repository.get_contact_by_email(
        sample_organisation.id, "TeSt@ExAmPlE.CoM"
    )
    assert contact_mixed is not None
    assert contact_mixed.email == "test@example.com"


def test_get_contact_by_email_not_found(
    contact_repository: ContactRepository, sample_organisation
):
    contact = contact_repository.get_contact_by_email(
        sample_organisation.id, "nonexistent@example.com"
    )

    assert contact is None


def test_get_contact_by_email_wrong_organisation(
    contact_repository: ContactRepository, sample_organisation
):
    existing_contact = sample_organisation.contacts[0]
    wrong_org_id = 9999

    contact = contact_repository.get_contact_by_email(
        wrong_org_id, existing_contact.email
    )

    assert contact is None


def test_update_contact(contact_repository: ContactRepository, sample_organisation):
    contact_to_update = sample_organisation.contacts[0]
    contact_to_update.role = "Updated Role"
    contact_repository.update(contact_to_update)
    contact_repository.commit()

    updated_contact = contact_repository.get_contact_by_id(
        sample_organisation.id, contact_to_update.id
    )
    assert updated_contact.role == "Updated Role"


def test_contact_exists_by_name_or_email(
    contact_repository: ContactRepository, sample_organisation
):
    contact = create_sample_contact(organisation_id=sample_organisation.id)
    contact_repository.add(contact)
    contact_repository.commit()

    assert (
        contact_repository.exists_by_name_or_email(
            sample_organisation.id, "Napoleon Bonaparte", "nonexistent@example.com"
        )
        is True
    )
    assert (
        contact_repository.exists_by_name_or_email(
            sample_organisation.id, "Nonexistent Name", "napoleon@lnds.lu"
        )
        is True
    )
    assert (
        contact_repository.exists_by_name_or_email(
            sample_organisation.id, "Nonexistent Name", "nonexistent@example.com"
        )
        is False
    )


def test_is_contact_assigned_to_dataset_when_assigned(
    contact_repository: ContactRepository,
    sample_organisation,
    db_session: Session,
    sample_dataset: Dataset,
):
    contact = create_sample_contact(organisation_id=sample_organisation.id)
    contact_repository.add(contact)
    contact_repository.commit()

    dataset_contact = DatasetContact(
        dataset_id=sample_dataset.id, contact_id=contact.id
    )
    db_session.add(dataset_contact)
    db_session.commit()

    is_assigned = contact_repository.is_contact_assigned_to_dataset(contact.id)
    assert is_assigned is True


def test_set_deprecation_status_deprecate(
    contact_repository: ContactRepository, sample_organisation
):
    contact = create_sample_contact(organisation_id=sample_organisation.id)
    contact_repository.add(contact)
    contact_repository.commit()
    contact_repository._db_session.refresh(contact)
    assert contact.is_deprecated is False

    contact_repository.set_deprecation_status(sample_organisation.id, contact.id, True)

    updated_contact = contact_repository.get_contact_by_id(
        sample_organisation.id, contact.id
    )
    assert updated_contact.is_deprecated is True


def test_set_deprecation_status_restore(
    contact_repository: ContactRepository, sample_organisation
):
    contact = create_sample_contact(organisation_id=sample_organisation.id)
    contact.is_deprecated = True
    contact_repository.add(contact)
    contact_repository.commit()

    assert contact.is_deprecated is True

    contact_repository.set_deprecation_status(sample_organisation.id, contact.id, False)

    updated_contact = contact_repository.get_contact_by_id(
        sample_organisation.id, contact.id
    )
    assert updated_contact.is_deprecated is False
