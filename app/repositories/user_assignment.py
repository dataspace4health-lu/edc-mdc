from sqlalchemy.orm import Session
from fastapi import Depends
from dependencies.database import get_db_session
from models.user_assignment import UserOrganisationAssignment, RoleAssignment, Role
from typing import List, Optional, Annotated


class UserAssignmentRepository:
    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def get_user_organisation_assignment(
        self, organisation_id: int, user_id: int
    ) -> Optional[UserOrganisationAssignment]:
        return (
            self._db_session.query(UserOrganisationAssignment)
            .filter(
                UserOrganisationAssignment.organisation_id == organisation_id,
                UserOrganisationAssignment.user_id == user_id,
            )
            .first()
        )

    def get_user_organisation_assignments(
        self, user_id: int
    ) -> List[UserOrganisationAssignment]:
        return (
            self._db_session.query(UserOrganisationAssignment)
            .filter(UserOrganisationAssignment.user_id == user_id)
            .all()
        )

    def get_organisation_user_assignments(
        self, organisation_id: int
    ) -> List[UserOrganisationAssignment]:
        return (
            self._db_session.query(UserOrganisationAssignment)
            .filter(UserOrganisationAssignment.organisation_id == organisation_id)
            .all()
        )

    def get_user_organisation_assignments_by_roles(
        self, organisation_id: int, roles: List[str]
    ) -> List[UserOrganisationAssignment]:

        if not roles:
            return []

        return (
            self._db_session.query(UserOrganisationAssignment)
            .join(UserOrganisationAssignment.roles)
            .join(RoleAssignment.role)
            .filter(
                UserOrganisationAssignment.organisation_id == organisation_id,
                Role.name.in_(roles),
            )
            .distinct()
            .all()
        )

    def add_user_organisation_assignment(
        self, assignment: UserOrganisationAssignment
    ) -> None:
        self._db_session.add(assignment)

    def delete_user_organisation_assignment(
        self, assignment: UserOrganisationAssignment
    ) -> None:
        self._db_session.delete(assignment)

    def commit(self) -> None:
        self._db_session.commit()

    def refresh(self, assignment: UserOrganisationAssignment) -> None:
        self._db_session.refresh(assignment)
