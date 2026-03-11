from fastapi import Depends, HTTPException
from dependencies.database import get_db_session
from sqlalchemy.orm import Session, joinedload
from models.qualified_attribution import DatasetQualifiedAttribution
from typing import List, Annotated, Optional


class QualifiedAttributionRepository:

    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def get_qualified_attribution(
        self, attribution_id: int
    ) -> DatasetQualifiedAttribution:
        attribution = (
            self._db_session.query(DatasetQualifiedAttribution)
            .filter(DatasetQualifiedAttribution.id == attribution_id)
            .first()
        )
        if not attribution:
            raise HTTPException(
                status_code=404,
                detail=f"QualifiedAttribution[{attribution_id}] not found",
            )
        return attribution

    def get_attributions_by_dataset_id(
        self, dataset_id: int
    ) -> List[DatasetQualifiedAttribution]:
        return (
            self._db_session.query(DatasetQualifiedAttribution)
            .filter(DatasetQualifiedAttribution.dataset_id == dataset_id)
            .all()
        )

    def exists(self, dataset_id: int, organisation_id: int, role: str) -> bool:
        return (
            self._db_session.query(DatasetQualifiedAttribution)
            .filter(
                DatasetQualifiedAttribution.dataset_id == dataset_id,
                DatasetQualifiedAttribution.organisation_id == organisation_id,
                DatasetQualifiedAttribution.role == role,
            )
            .first()
            is not None
        )

    def add(self, attribution: DatasetQualifiedAttribution) -> None:
        self._db_session.add(attribution)

    def update(
        self,
        attribution: DatasetQualifiedAttribution,
        organisation_id: Optional[int] = None,
        role: Optional[str] = None,
    ) -> DatasetQualifiedAttribution:
        if organisation_id is not None:
            attribution.organisation_id = organisation_id
        if role is not None:
            attribution.role = role

        self._db_session.add(attribution)
        return attribution

    def delete(self, attribution_id: int) -> None:
        self._db_session.query(DatasetQualifiedAttribution).filter(
            DatasetQualifiedAttribution.id == attribution_id
        ).delete()

    def commit(self) -> None:
        self._db_session.commit()

    def refresh(self, attribution: DatasetQualifiedAttribution) -> None:
        self._db_session.refresh(attribution)
