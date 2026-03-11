from sqlalchemy.orm import Session
from fastapi import Depends
from dependencies.database import get_db_session
from models.user_assignment import RoleAssignment, Role
from typing import List, Annotated


class RoleRepository:
    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def commit(self) -> None:
        self._db_session.commit()

    def refresh(self, assignment: RoleAssignment) -> None:
        self._db_session.refresh(assignment)

    def get_all_roles(self) -> List[Role]:
        return self._db_session.query(Role).all()

    def get_by_id(self, role_id: int) -> Role:
        role = self._db_session.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError(f"Role with id {role_id} not found")
        return role
