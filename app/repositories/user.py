from dependencies.database import get_db_session
from fastapi import Depends
from typing import Annotated, List, Tuple, Optional
from sqlalchemy.orm import Session
from models.user import User
from models.user_assignment import UserOrganisationAssignment, RoleAssignment
from sqlalchemy import or_, desc
from sqlalchemy.orm import aliased


class UserRepository:
    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def get_users_with_roles(self, iam_roles: List[str]) -> List[User]:
        role_patterns = [f"%{role}%" for role in iam_roles]

        query = self._db_session.query(User)
        or_conditions = [User.iam_roles.like(pattern) for pattern in role_patterns]
        query = query.filter(or_(*or_conditions))
        query = query.order_by(User.name.asc())

        return query.all()

    def get_users(
        self,
        page: int = 1,
        page_size: int = 10,
        query: Optional[str] = None,
        organisation_ids: Optional[List[int]] = None,
        role_ids: Optional[List[int]] = None,
        only_unassigned: Optional[bool] = False,
        permission_filter: Optional[dict] = None,
        is_deprecated: Optional[bool] = False,
    ) -> Tuple[List[User], int]:
        query_obj = self._db_session.query(User)
        query_obj = query_obj.filter(User.name != "system", User.email.isnot(None))

        if is_deprecated is not None:
            query_obj = query_obj.filter(User.is_deprecated == is_deprecated)

        if permission_filter:
            org_ids = permission_filter.get("organisation_ids")
            include_unassigned = permission_filter.get("include_unassigned", False)

            if org_ids or include_unassigned:
                assign_alias = aliased(UserOrganisationAssignment)
                query_obj = query_obj.outerjoin(assign_alias)

                conditions = []
                if org_ids:
                    conditions.append(assign_alias.organisation_id.in_(org_ids))
                if include_unassigned:
                    conditions.append(assign_alias.user_id.is_(None))

                query_obj = query_obj.filter(or_(*conditions)).distinct()

        if query:
            query = f"%{query}%"
            query_obj = query_obj.filter(
                or_(
                    User.name.ilike(query),
                    User.email.ilike(query),
                )
            )
        if only_unassigned:
            query_obj = query_obj.filter(~User.organisation_assignments.any())

        if organisation_ids:
            query_obj = query_obj.join(User.organisation_assignments).filter(
                UserOrganisationAssignment.organisation_id.in_(organisation_ids)
            )

        if role_ids:
            query_obj = (
                query_obj.join(User.organisation_assignments)
                .join(UserOrganisationAssignment.roles)
                .filter(RoleAssignment.role_id.in_(role_ids))
            )

        total_count = query_obj.count()

        query_obj = query_obj.order_by(desc(User.id))
        users = query_obj.offset((page - 1) * page_size).limit(page_size).all()

        return users, total_count

    def get_user(self, user_id: int) -> Optional[User]:
        return self._db_session.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self._db_session.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self._db_session.query(User).filter(User.id == user_id).first()

    def set_deprecation_status(self, user_id: int, deprecation=False) -> None:
        user = self.get_user(user_id)
        if user:
            user.is_deprecated = deprecation
            self._db_session.commit()
        else:
            raise ValueError("User not found")

    def delete_user(self, user_id: int) -> None:
        user = self.get_user(user_id)
        if user:
            self._db_session.delete(user)
            self._db_session.commit()
        else:
            raise ValueError("User not found")
