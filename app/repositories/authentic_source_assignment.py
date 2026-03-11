from fastapi import Depends
from sqlalchemy.orm import Session
from dependencies.database import get_db_session
from models.authentic_source_assignment import AuthenticSourceAssignment
from typing import List, Annotated, Optional
from sqlalchemy import asc, desc
from typing import Dict, Optional


class AuthenticSourceAssignmentRepository:
    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def get_current_assignment(
        self, entry_id: int
    ) -> Optional[AuthenticSourceAssignment]:
        return (
            self._db_session.query(AuthenticSourceAssignment)
            .filter(
                AuthenticSourceAssignment.data_dictionary_entry_id == entry_id,
                AuthenticSourceAssignment.is_active == True,
            )
            .first()
        )

    def get_current_assignment_for_label(
        self, label_id: int
    ) -> Optional[AuthenticSourceAssignment]:
        return (
            self._db_session.query(AuthenticSourceAssignment)
            .filter(
                AuthenticSourceAssignment.authentic_source_label_id == label_id,
                AuthenticSourceAssignment.is_active == True,
            )
            .first()
        )

    def get_previous_assignments_for_label(
        self, label_id: int
    ) -> List[AuthenticSourceAssignment]:
        q = self._db_session.query(AuthenticSourceAssignment).filter(
            AuthenticSourceAssignment.authentic_source_label_id == label_id,
            AuthenticSourceAssignment.is_active == False,
        )
        return q.all()

    def process_label_assignment(
        self, label_id: int, new_entry_id: Optional[int], assigned_by: int
    ) -> Dict[str, int]:
        result = {"created": 0, "deactivated": 0}

        current_assignment = (
            self._db_session.query(AuthenticSourceAssignment)
            .filter(
                AuthenticSourceAssignment.authentic_source_label_id == label_id,
                AuthenticSourceAssignment.is_active == True,
            )
            .first()
        )

        current_entry_id = (
            current_assignment.data_dictionary_entry_id if current_assignment else None
        )

        # If no new entry (unassigning the label)
        if new_entry_id is None:
            if current_assignment:
                current_assignment.is_active = False
                self._db_session.add(current_assignment)
                result["deactivated"] += 1
            return result

        # If same entry, no change needed
        if current_entry_id == new_entry_id:
            return result

        # Deactivate current assignment if exists
        if current_assignment:
            current_assignment.is_active = False
            self._db_session.add(current_assignment)
            result["deactivated"] += 1

        # Deactivate any existing assignment for the new entry (from other labels)
        existing_assignment = self.get_current_assignment(new_entry_id)
        if existing_assignment:
            existing_assignment.is_active = False
            self._db_session.add(existing_assignment)

        # Create new assignment
        new_assignment = AuthenticSourceAssignment(
            data_dictionary_entry_id=new_entry_id,
            authentic_source_label_id=label_id,
            assigned_by=assigned_by,
            is_active=True,
        )
        self._db_session.add(new_assignment)
        result["created"] += 1

        return result

    def commit(self) -> None:
        self._db_session.commit()

    def refresh(self, assignment: AuthenticSourceAssignment) -> None:
        self._db_session.refresh(assignment)
