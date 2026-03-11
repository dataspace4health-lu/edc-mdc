from typing import Annotated
from fastapi import Depends
from dependencies.database import get_db_session
from sqlalchemy.orm import Session
from models.dataset import Dataset
from models.dataset_relation import DatasetRelation
from models.data_dictionary import DataDictionaryEntry


class DatabaseSessionManager:
    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def refresh(self, dataset: Dataset) -> None:
        self._db_session.refresh(dataset)

    def refresh(self, relation: DatasetRelation) -> None:
        self._db_session.refresh(relation)

    def refresh(self, entry: DataDictionaryEntry) -> None:
        self._db_session.refresh(entry)

    def commit(self) -> None:
        self._db_session.commit()

    def rollback(self) -> None:
        self._db_session.rollback()
