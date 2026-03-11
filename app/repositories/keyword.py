from fastapi import Depends
from sqlalchemy.orm import Session
from dependencies.database import get_db_session
from models.dataset import Keyword
from models.keyword_assignment import KeywordAssignment
from typing import Annotated, List, Tuple, Optional
from sqlalchemy import asc, or_


class KeywordRepository:
    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def get_all(self, user_org_ids: Optional[List[int]] = None) -> List[Keyword]:
        q = self._db_session.query(Keyword)
        if user_org_ids is not None:
            q = (
                q.outerjoin(KeywordAssignment)
                .filter(
                    or_(
                        KeywordAssignment.organisation_id.is_(None),
                        KeywordAssignment.organisation_id.in_(user_org_ids),
                    )
                )
                .distinct()
            )
        return q.order_by(asc(Keyword.key)).all()

    def get_all_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        query: Optional[str] = None,
        user_org_ids: Optional[List[int]] = None,
        organisation_filters: Optional[List[str]] = None,
    ) -> Tuple[List[Keyword], int]:
        query_obj = self._db_session.query(Keyword)

        if user_org_ids is not None:
            query_obj = (
                query_obj.outerjoin(KeywordAssignment)
                .filter(
                    or_(
                        KeywordAssignment.organisation_id.is_(None),
                        KeywordAssignment.organisation_id.in_(user_org_ids),
                    )
                )
                .distinct()
            )

        # Apply search query
        if query:
            search_pattern = f"%{query}%"
            query_obj = query_obj.filter(
                or_(
                    Keyword.eng_label.ilike(search_pattern),
                    Keyword.key.ilike(search_pattern),
                )
            )

        # Apply organisation filters
        if organisation_filters:
            # Join if not already joined
            if user_org_ids is None:
                query_obj = query_obj.outerjoin(KeywordAssignment)

            org_conditions = []
            for org_filter in organisation_filters:
                if org_filter == "global":
                    org_conditions.append(KeywordAssignment.organisation_id.is_(None))
                else:
                    try:
                        org_id = int(org_filter)
                        org_conditions.append(
                            KeywordAssignment.organisation_id == org_id
                        )
                    except ValueError:
                        continue

            if org_conditions:
                query_obj = query_obj.filter(or_(*org_conditions))

        # Get total count
        total_count = query_obj.count()

        # Apply pagination and ordering
        keywords = (
            query_obj.order_by(asc(Keyword.eng_label))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return keywords, total_count

    def get(self, key: str) -> Keyword:
        return self._db_session.query(Keyword).filter(Keyword.key == key).first()

    def get_by_eng_label(self, eng_label: str) -> Optional[Keyword]:
        return self._db_session.query(Keyword).filter_by(eng_label=eng_label).first()

    def get_by_key_or_label(self, value: str) -> Optional[Keyword]:
        return (
            self._db_session.query(Keyword)
            .filter(or_(Keyword.key == value, Keyword.eng_label == value))
            .first()
        )

    def get_count_for_user(self, user_id: int) -> int:
        return (
            self._db_session.query(Keyword)
            .filter(Keyword.created_by_id == user_id)
            .count()
        )

    def add(self, keyword: Keyword) -> None:
        self._db_session.add(keyword)

    def update(self, key: str, eng_label: str) -> Keyword:
        keyword = self.get(key)
        if keyword:
            keyword.eng_label = eng_label
            self._db_session.add(keyword)
        return keyword

    def commit(self) -> None:
        self._db_session.commit()

    def refresh(self, keyword: Keyword) -> None:
        self._db_session.refresh(keyword)

    def delete(self, keyword: Keyword) -> None:
        self._db_session.delete(keyword)
        self._db_session.commit()
