from fastapi import Depends
from sqlalchemy.orm import Session
from dependencies.database import get_db_session
from models.applicable_legislation import ApplicableLegislation
from models.applicable_legislation_assignment import ApplicableLegislationAssignment
from typing import List, Annotated, Optional, Tuple
from sqlalchemy import asc, or_


class ApplicableLegislationRepository:
    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def get_all(
        self, user_org_ids: Optional[List[int]] = None
    ) -> List[ApplicableLegislation]:
        q = self._db_session.query(ApplicableLegislation)
        if user_org_ids is not None:
            q = (
                q.outerjoin(ApplicableLegislationAssignment)
                .filter(
                    or_(
                        ApplicableLegislationAssignment.organisation_id.is_(None),
                        ApplicableLegislationAssignment.organisation_id.in_(
                            user_org_ids
                        ),
                    )
                )
                .distinct()
            )
        return q.order_by(asc(ApplicableLegislation.key)).all()

    def get_all_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        query: Optional[str] = None,
        user_org_ids: Optional[List[int]] = None,
        organisation_filters: Optional[List[str]] = None,
    ) -> Tuple[List[ApplicableLegislation], int]:
        query_obj = self._db_session.query(ApplicableLegislation)

        if user_org_ids is not None:
            query_obj = (
                query_obj.outerjoin(ApplicableLegislationAssignment)
                .filter(
                    or_(
                        ApplicableLegislationAssignment.organisation_id.is_(None),
                        ApplicableLegislationAssignment.organisation_id.in_(
                            user_org_ids
                        ),
                    )
                )
                .distinct()
            )

        # Apply search query
        if query:
            search_pattern = f"%{query}%"
            query_obj = query_obj.filter(
                or_(
                    ApplicableLegislation.eng_label.ilike(search_pattern),
                    ApplicableLegislation.key.ilike(search_pattern),
                )
            )

        # Apply organisation filters
        if organisation_filters:
            if user_org_ids is None:
                query_obj = query_obj.outerjoin(ApplicableLegislationAssignment)

            org_conditions = []
            for org_filter in organisation_filters:
                if org_filter == "global":
                    org_conditions.append(
                        ApplicableLegislationAssignment.organisation_id.is_(None)
                    )
                else:
                    try:
                        org_id = int(org_filter)
                        org_conditions.append(
                            ApplicableLegislationAssignment.organisation_id == org_id
                        )
                    except ValueError:
                        continue

            if org_conditions:
                query_obj = query_obj.filter(or_(*org_conditions))

        # Get total count
        total_count = query_obj.count()

        # Apply pagination and ordering
        applicable_legislations = (
            query_obj.order_by(asc(ApplicableLegislation.eng_label))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return applicable_legislations, total_count

    def get(self, key: str) -> ApplicableLegislation:
        return (
            self._db_session.query(ApplicableLegislation)
            .filter(ApplicableLegislation.key == key)
            .first()
        )

    def get_by_key_or_link(self, key: str, link: str) -> ApplicableLegislation:
        if not link:
            return self.get(key)
        else:
            return (
                self._db_session.query(ApplicableLegislation)
                .filter(
                    or_(
                        ApplicableLegislation.key == key,
                        ApplicableLegislation.link == link,
                    )
                )
                .first()
            )

    def add(self, applicable_legislation: ApplicableLegislation) -> None:
        self._db_session.add(applicable_legislation)

    def get_count_for_user(self, user_id: int) -> int:
        return (
            self._db_session.query(ApplicableLegislation)
            .filter(ApplicableLegislation.created_by_id == user_id)
            .count()
        )

    def update(
        self,
        key: str,
        eng_label: str,
        description: str,
        link: str,
    ) -> ApplicableLegislation:
        applicable_legislation = self.get(key)
        if applicable_legislation:
            applicable_legislation.eng_label = eng_label
            applicable_legislation.description = description
            applicable_legislation.link = link
            self._db_session.add(applicable_legislation)
        return applicable_legislation

    def commit(self) -> None:
        self._db_session.commit()

    def refresh(self, applicable_legislation: ApplicableLegislation) -> None:
        self._db_session.refresh(applicable_legislation)

    def delete(self, applicable_legislation: ApplicableLegislation) -> None:
        self._db_session.delete(applicable_legislation)
        self._db_session.commit()
