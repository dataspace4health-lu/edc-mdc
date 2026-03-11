from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from dependencies.database import get_db_session
from models.organisation import Organisation, Contact
from typing import List, Annotated
from sqlalchemy import desc, or_


class OrganisationRepository:
    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def get_organisations(self) -> List[Organisation]:
        return (
            self._db_session.query(Organisation).order_by(desc(Organisation.id)).all()
        )

    def get_organisation(self, organisation_id: int) -> Organisation:
        organisation = (
            self._db_session.query(Organisation)
            .filter(Organisation.id == organisation_id)
            .first()
        )
        if not organisation:
            raise HTTPException(
                status_code=404, detail=f"Organisation[{organisation_id}] not found"
            )
        return organisation

    def add(self, organisation: Organisation) -> None:
        self._db_session.add(organisation)

    def update(self, organisation: Organisation) -> None:
        self._db_session.merge(organisation)

    def set_deprecation_status(
        self, organisation_id: int, deprecation: bool = False
    ) -> None:
        organisation = self.get_organisation(organisation_id)
        if organisation:
            organisation.is_deprecated = deprecation
            self._db_session.merge(organisation)

    def add_contacts(self, contacts: List[Contact]) -> None:
        self._db_session.add_all(contacts)

    def exists_by_name(self, name: str) -> bool:
        return (
            self._db_session.query(Organisation)
            .filter(or_(Organisation.name == name))
            .first()
            is not None
        )

    def find_by_name(self, name: str) -> Organisation | None:
        return (
            self._db_session.query(Organisation)
            .filter(Organisation.name == name)
            .first()
        )

    def commit(self) -> None:
        self._db_session.commit()

    def refresh(self, organisation: Organisation) -> None:
        self._db_session.refresh(organisation)
