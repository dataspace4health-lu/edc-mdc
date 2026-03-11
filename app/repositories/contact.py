from fastapi import Depends
from sqlalchemy.orm import Session
from dependencies.database import get_db_session
from models.organisation import Contact
from models.dataset import DatasetContact
from typing import List, Annotated, Optional
from sqlalchemy import desc, or_, func


class ContactRepository:
    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def get_contact_by_id(self, organisation_id: int, contact_id: int) -> Contact:
        return (
            self._db_session.query(Contact)
            .filter(
                Contact.id == contact_id, Contact.organisation_id == organisation_id
            )
            .first()
        )

    def is_contact_assigned_to_dataset(self, contact_id: int) -> bool:
        return (
            self._db_session.query(DatasetContact)
            .filter(DatasetContact.contact_id == contact_id)
            .first()
            is not None
        )

    def add(self, contact: Contact) -> None:
        self._db_session.add(contact)

    def update(self, contact: Contact) -> None:
        self._db_session.merge(contact)

    def exists_by_name_or_email(
        self, organisation_id: int, name: str, email: str
    ) -> bool:
        return (
            self._db_session.query(Contact)
            .filter(
                Contact.organisation_id == organisation_id,
                or_(Contact.name == name, Contact.email == email),
            )
            .first()
            is not None
        )

    def get_contact_by_email(
        self, organisation_id: int, email: str
    ) -> Optional[Contact]:
        if not email:
            return None

        return (
            self._db_session.query(Contact)
            .filter(
                Contact.organisation_id == organisation_id,
                func.lower(Contact.email) == func.lower(email),
            )
            .first()
        )

    def set_deprecation_status(
        self, organisation_id: int, contact_id: int, deprecation: bool = False
    ) -> None:
        contact = self.get_contact_by_id(organisation_id, contact_id)
        if contact:
            contact.is_deprecated = deprecation
            self._db_session.commit()
        else:
            raise ValueError("Contact not found")

    def delete(self, contact: Contact) -> None:
        self._db_session.delete(contact)

    def commit(self) -> None:
        self._db_session.commit()
