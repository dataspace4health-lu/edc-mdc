import pytest
from sqlalchemy.orm import Session
from models.applicable_legislation_assignment import ApplicableLegislationAssignment
from repositories.applicable_legislation_assignment import (
    ApplicableLegislationAssignmentRepository,
)


@pytest.fixture
def applicable_legislation_assignment_repository(
    db_session: Session,
) -> ApplicableLegislationAssignmentRepository:
    return ApplicableLegislationAssignmentRepository(db_session)


def test_add_and_get_applicable_legislation_assignment(
    applicable_legislation_assignment_repository, db_session: Session
):
    assignment = ApplicableLegislationAssignment(
        applicable_legislation_key="GDPR1", organisation_id=1
    )
    applicable_legislation_assignment_repository.add_applicable_legislation_organisation_assignment(
        assignment
    )
    applicable_legislation_assignment_repository.commit()

    result = applicable_legislation_assignment_repository.get_applicable_legislation_organisation_assignment(
        applicable_legislation_key="GDPR1", organisation_id=1
    )
    assert result is not None
    assert result.applicable_legislation_key == "GDPR1"
    assert result.organisation_id == 1


def test_get_applicable_legislation_organisation_assignments(
    applicable_legislation_assignment_repository, db_session: Session
):
    db_session.add_all(
        [
            ApplicableLegislationAssignment(
                applicable_legislation_key="GDPR2", organisation_id=1
            ),
            ApplicableLegislationAssignment(
                applicable_legislation_key="GDPR2", organisation_id=2
            ),
        ]
    )
    db_session.commit()

    results = applicable_legislation_assignment_repository.get_applicable_legislation_organisation_assignments(
        "GDPR2"
    )
    assert len(results) == 2
    org_ids = {r.organisation_id for r in results}
    assert org_ids == {1, 2}
