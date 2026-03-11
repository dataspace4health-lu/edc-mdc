from typing import Annotated, List, Optional
from fastapi import Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session
from dependencies.database import get_db_session
from models.dataset_comment import DatasetComment


class DatasetCommentRepository:
    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def get_dataset_comments(self, dataset_id: int) -> List[DatasetComment]:
        return (
            self._db_session.query(DatasetComment)
            .filter(DatasetComment.dataset_id == dataset_id)
            .order_by(desc(DatasetComment.timestamp))
            .all()
        )

    def delete_comment_by_id(self, comment_id: int) -> None:
        comment = self._db_session.get(DatasetComment, comment_id)
        if not comment:
            return
        self._db_session.delete(comment)

    def add(self, comment: DatasetComment) -> None:
        self._db_session.add(comment)

    def commit(self) -> None:
        self._db_session.commit()
