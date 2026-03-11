from fastapi import Depends, HTTPException
from dependencies.database import get_db_session
from sqlalchemy.orm import Session
from models.dataset_relation import DatasetRelation
from typing import List, Annotated


class DatasetRelationRepository:

    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def add(self, relation: DatasetRelation) -> None:
        self._db_session.add(relation)

    def delete(self, relation_id: int) -> None:
        self._db_session.query(DatasetRelation).filter(
            DatasetRelation.id == relation_id
        ).delete()

    def delete_reciprocal_relation(
        self, target_dataset: int, reciprocal_relation_type: str
    ) -> None:
        self._db_session.query(DatasetRelation).filter(
            DatasetRelation.target_dataset == target_dataset,
            DatasetRelation.relation_type == reciprocal_relation_type,
        ).delete()

    def get_dataset_relation(self, id: int) -> DatasetRelation:
        entry = (
            self._db_session.query(DatasetRelation)
            .filter(DatasetRelation.id == id)
            .first()
        )
        if not entry:
            raise HTTPException(
                status_code=404, detail=f"DatasetRelation[{id}] not found"
            )
        return entry

    def get_relations_by_dataset_id(self, dataset_id: int) -> List[DatasetRelation]:
        return (
            self._db_session.query(DatasetRelation)
            .filter(DatasetRelation.source_dataset == dataset_id)
            .all()
        )

    def get_dataset_relations_by_dataset_id(
        self, dataset_id: int
    ) -> List[DatasetRelation]:
        return (
            self._db_session.query(DatasetRelation)
            .filter(
                DatasetRelation.source_dataset == dataset_id,
                DatasetRelation.target_dataset.isnot(None),
            )
            .all()
        )

    def get_external_relations_by_dataset_id(
        self, dataset_id: int
    ) -> List[DatasetRelation]:
        return (
            self._db_session.query(DatasetRelation)
            .filter(
                DatasetRelation.source_dataset == dataset_id,
                DatasetRelation.external_url.isnot(None),
            )
            .all()
        )
