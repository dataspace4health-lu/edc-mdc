from fastapi import Depends
from dependencies.database import get_db_session
from sqlalchemy.orm import Session
from models.activity_log import ActivityLog
from typing import List, Annotated, Tuple
from sqlalchemy import desc


class ActivityLogRepository:
    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def get_activity_logs_from_dataset(
        self, dataset_id: int, page: int, page_size: int
    ) -> List[ActivityLog]:
        return (
            self._db_session.query(ActivityLog)
            .filter(ActivityLog.entity_id == str(dataset_id))
            .filter(ActivityLog.entity_type == "dataset")
            .order_by(desc(ActivityLog.id))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

    def get_activity_logs_from_organisation(
        self, organisation_id: int, page: int, page_size: int
    ) -> List[ActivityLog]:
        return (
            self._db_session.query(ActivityLog)
            .filter(ActivityLog.entity_id == str(organisation_id))
            .filter(ActivityLog.entity_type == "organisation")
            .order_by(desc(ActivityLog.id))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

    def get_all_activity_logs_from_organisations(
        self, organisation_ids: List[int], page: int, page_size: int
    ) -> List[ActivityLog]:
        return (
            self._db_session.query(ActivityLog)
            .filter(ActivityLog.entity_type == "organisation")
            .filter(ActivityLog.entity_id.in_(map(str, organisation_ids)))
            .order_by(desc(ActivityLog.id))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

    def get_all_activity_logs_for_entity(
        self, entity_type: str, page: int, page_size: int
    ) -> List[ActivityLog]:
        return (
            self._db_session.query(ActivityLog)
            .filter(ActivityLog.entity_type == entity_type)
            .order_by(desc(ActivityLog.id))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

    def get_activity_log_count_from_user(self, user_id: int) -> int:
        return (
            self._db_session.query(ActivityLog)
            .filter(ActivityLog.user_id == user_id)
            .count()
        )

    def add(self, activity_log: ActivityLog) -> None:
        self._db_session.add(activity_log)

    def merge(self, activity_log: ActivityLog) -> None:
        self._db_session.merge(activity_log)

    def refresh(self, activity_log: ActivityLog) -> None:
        self._db_session.refresh(activity_log)

    def commit(self) -> None:
        self._db_session.commit()
