from fastapi import Depends
from sqlalchemy.orm import Session
from dependencies.database import get_db_session
from models.dataset import Theme
from typing import List, Annotated
from sqlalchemy import asc
from schemas.form_field import FormFieldDto


class ThemeRepository:
    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def get_all(self) -> List[Theme]:
        return self._db_session.query(Theme).order_by(asc(Theme.key)).all()

    def get(self, key: str) -> Theme:
        return self._db_session.query(Theme).filter(Theme.key == key).first()

    def add(self, theme: Theme) -> None:
        self._db_session.add(theme)

    def update(self, key: str, eng_label: str) -> Theme:
        theme = self.get(key)
        if theme:
            theme.eng_label = eng_label
            self._db_session.add(theme)
        return theme

    def commit(self) -> None:
        self._db_session.commit()

    def refresh(self, theme: Theme) -> None:
        self._db_session.refresh(theme)

    def delete(self, theme: Theme) -> None:
        self._db_session.delete(theme)
        self._db_session.commit()
