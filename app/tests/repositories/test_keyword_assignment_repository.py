import pytest
from sqlalchemy.orm import Session
from models.keyword_assignment import KeywordAssignment
from repositories.keyword_assignment import KeywordAssignmentRepository


@pytest.fixture
def keyword_assignment_repository(db_session: Session) -> KeywordAssignmentRepository:
    return KeywordAssignmentRepository(db_session)


def test_add_and_get_keyword_assignment(
    keyword_assignment_repository, db_session: Session
):
    assignment = KeywordAssignment(keyword_key="internet", organisation_id=1)
    keyword_assignment_repository.add_keyword_organisation_assignment(assignment)
    keyword_assignment_repository.commit()

    result = keyword_assignment_repository.get_keyword_organisation_assignment(
        keyword_key="internet", organisation_id=1
    )
    assert result is not None
    assert result.keyword_key == "internet"
    assert result.organisation_id == 1


def test_get_keyword_organisation_assignments(
    keyword_assignment_repository, db_session: Session
):
    db_session.add_all(
        [
            KeywordAssignment(keyword_key="health", organisation_id=1),
            KeywordAssignment(keyword_key="health", organisation_id=2),
        ]
    )
    db_session.commit()

    results = keyword_assignment_repository.get_keyword_organisation_assignments(
        "health"
    )
    assert len(results) == 2
    org_ids = {r.organisation_id for r in results}
    assert org_ids == {1, 2}
