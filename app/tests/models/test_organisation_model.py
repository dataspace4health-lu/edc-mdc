import pytest
from sqlalchemy.orm import Session
from models.organisation import Organisation
from test_factory import sample_organisation


def test_create_and_get_organisation(
    db_session: Session, sample_organisation: Organisation
):
    db_organisation = (
        db_session.query(Organisation)
        .filter(Organisation.id == sample_organisation.id)
        .one()
    )

    assert db_organisation.id == sample_organisation.id, "Organisation ID mismatch"
    assert (
        db_organisation.name == sample_organisation.name
    ), "Organisation name mismatch"
    assert (
        db_organisation.type == sample_organisation.type
    ), "Organisation type mismatch"
    assert len(db_organisation.contacts) == len(
        sample_organisation.contacts
    ), "Organisation contacts count mismatch"
    assert (
        db_organisation.contacts[0].name == sample_organisation.contacts[0].name
    ), "First contact name mismatch"
    assert (
        db_organisation.contacts[0].email == sample_organisation.contacts[0].email
    ), "First contact email mismatch"
    assert (
        db_organisation.contacts[0].role == sample_organisation.contacts[0].role
    ), "First contact role mismatch"
    assert (
        db_organisation.contacts[1].name == sample_organisation.contacts[1].name
    ), "Second contact name mismatch"
    assert (
        db_organisation.contacts[1].email == sample_organisation.contacts[1].email
    ), "Second contact email mismatch"
    assert (
        db_organisation.contacts[1].role == sample_organisation.contacts[1].role
    ), "Second contact role mismatch"
