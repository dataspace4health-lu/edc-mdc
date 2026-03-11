from fastapi import Depends
from sqlalchemy.orm import Session
from dependencies.database import get_db_session
from models.authentic_source_label import AuthenticSourceLabel
from typing import List, Annotated, Optional
from sqlalchemy import asc, desc


class AuthenticSourceLabelRepository:
    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def get_all(self, include_deprecated: bool = False) -> List[AuthenticSourceLabel]:
        q = self._db_session.query(AuthenticSourceLabel)
        if not include_deprecated:
            q = q.filter(AuthenticSourceLabel.is_deprecated == False)
        return q.all()

    def get_by_name(self, name: str) -> Optional[AuthenticSourceLabel]:
        return (
            self._db_session.query(AuthenticSourceLabel)
            .filter(AuthenticSourceLabel.name == name)
            .first()
        )

    def get_by_id(self, label_id: int) -> Optional[AuthenticSourceLabel]:
        return (
            self._db_session.query(AuthenticSourceLabel)
            .filter(AuthenticSourceLabel.id == label_id)
            .first()
        )

    def add(self, label: AuthenticSourceLabel) -> None:
        self._db_session.add(label)

    def delete(self, label: AuthenticSourceLabel) -> None:
        self._db_session.delete(label)

    def set_deprecation_status(self, label_id: int, deprecation: bool = False) -> None:
        label = self.get_by_id(label_id)
        if label:
            label.is_deprecated = deprecation
            self._db_session.commit()
        else:
            raise ValueError("Authentic Source Label not found")

    def commit(self) -> None:
        self._db_session.commit()

    def refresh(self, label: AuthenticSourceLabel) -> None:
        self._db_session.refresh(label)
