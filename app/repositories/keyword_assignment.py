from sqlalchemy.orm import Session
from fastapi import Depends
from dependencies.database import get_db_session
from models.keyword_assignment import KeywordAssignment
from typing import List, Optional, Annotated


class KeywordAssignmentRepository:
    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def get_keyword_organisation_assignment(
        self, keyword_key: str, organisation_id: int
    ) -> Optional[KeywordAssignment]:
        return (
            self._db_session.query(KeywordAssignment)
            .filter(
                KeywordAssignment.keyword_key == keyword_key,
                KeywordAssignment.organisation_id == organisation_id,
            )
            .first()
        )

    def get_keyword_organisation_assignments(
        self, keyword_key: str
    ) -> List[KeywordAssignment]:
        return (
            self._db_session.query(KeywordAssignment)
            .filter(KeywordAssignment.keyword_key == keyword_key)
            .all()
        )

    def add_keyword_organisation_assignment(
        self, assignment: KeywordAssignment
    ) -> None:
        self._db_session.add(assignment)

    def commit(self) -> None:
        self._db_session.commit()

    def refresh(self, assignment: KeywordAssignment) -> None:
        self._db_session.refresh(assignment)
