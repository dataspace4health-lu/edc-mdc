from sqlalchemy.orm import Session
from fastapi import Depends
from dependencies.database import get_db_session
from models.applicable_legislation_assignment import ApplicableLegislationAssignment
from typing import List, Optional, Annotated


class ApplicableLegislationAssignmentRepository:
    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def get_applicable_legislation_organisation_assignment(
        self, applicable_legislation_key: str, organisation_id: int
    ) -> Optional[ApplicableLegislationAssignment]:
        return (
            self._db_session.query(ApplicableLegislationAssignment)
            .filter(
                ApplicableLegislationAssignment.applicable_legislation_key
                == applicable_legislation_key,
                ApplicableLegislationAssignment.organisation_id == organisation_id,
            )
            .first()
        )

    def get_applicable_legislation_organisation_assignments(
        self, applicable_legislation_key: str
    ) -> List[ApplicableLegislationAssignment]:
        return (
            self._db_session.query(ApplicableLegislationAssignment)
            .filter(
                ApplicableLegislationAssignment.applicable_legislation_key
                == applicable_legislation_key
            )
            .all()
        )

    def add_applicable_legislation_organisation_assignment(
        self, assignment: ApplicableLegislationAssignment
    ) -> None:
        self._db_session.add(assignment)

    def commit(self) -> None:
        self._db_session.commit()

    def refresh(self, assignment: ApplicableLegislationAssignment) -> None:
        self._db_session.refresh(assignment)
