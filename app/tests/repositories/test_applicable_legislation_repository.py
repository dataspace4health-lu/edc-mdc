import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.dataset import User, ApplicableLegislation
from models.organisation import Organisation
from models.applicable_legislation_assignment import ApplicableLegislationAssignment
from repositories.applicable_legislation import ApplicableLegislationRepository


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    db_session.query(ApplicableLegislationAssignment).delete()
    db_session.query(ApplicableLegislation).delete()
    db_session.query(User).delete()
    db_session.query(Organisation).delete()
    db_session.commit()


@pytest.fixture
def repository(db_session: Session) -> ApplicableLegislationRepository:
    return ApplicableLegislationRepository(db_session)


@pytest.fixture
def setup_test_data(db_session: Session):
    org1 = Organisation(name="Organization 1", is_deprecated=False)
    org2 = Organisation(name="Organization 2", is_deprecated=False)

    user1 = User(name="John Doe", email="john@example.com", external_id="john-123")
    user2 = User(name="system", external_id="system-456")

    db_session.add_all([org1, org2, user1, user2])
    db_session.commit()

    applicable_legislation1 = ApplicableLegislation(
        key="applicable_legislation1",
        eng_label="First ApplicableLegislation",
        description="First description",
        link="https://first.com",
        created_by_id=user1.id,
    )
    applicable_legislation2 = ApplicableLegislation(
        key="applicable_legislation2",
        eng_label="Second ApplicableLegislation",
        description="Second description",
        link="https://second.com",
        created_by_id=None,
    )
    applicable_legislation3 = ApplicableLegislation(
        key="applicable_legislation3",
        eng_label="Third ApplicableLegislation",
        description="Third description",
        link="https://third.com",
        created_by_id=user1.id,
    )
    applicable_legislation4 = ApplicableLegislation(
        key="test_applicable_legislation",
        eng_label="Test Search ApplicableLegislation",
        description="Test description",
        link="https://test.com",
        created_by_id=user1.id,
    )

    db_session.add_all(
        [
            applicable_legislation1,
            applicable_legislation2,
            applicable_legislation3,
            applicable_legislation4,
        ]
    )
    db_session.commit()

    assignment1 = ApplicableLegislationAssignment(
        applicable_legislation_key="applicable_legislation1", organisation_id=org1.id
    )
    assignment3 = ApplicableLegislationAssignment(
        applicable_legislation_key="applicable_legislation3", organisation_id=org2.id
    )
    assignment4 = ApplicableLegislationAssignment(
        applicable_legislation_key="test_applicable_legislation",
        organisation_id=org1.id,
    )

    db_session.add_all([assignment1, assignment3, assignment4])
    db_session.commit()

    return {
        "applicable_legislations": [
            applicable_legislation1,
            applicable_legislation2,
            applicable_legislation3,
            applicable_legislation4,
        ],
        "users": [user1, user2],
        "orgs": [org1, org2],
        "assignments": [assignment1, assignment3, assignment4],
    }


def test_get_all_paginated_basic(
    repository: ApplicableLegislationRepository, setup_test_data
):
    items, total = repository.get_all_paginated(page=1, page_size=2)

    assert total == 4
    assert len(items) == 2
    assert items[0].eng_label == "First ApplicableLegislation"
    assert items[1].eng_label == "Second ApplicableLegislation"


def test_get_all_paginated_with_search(
    repository: ApplicableLegislationRepository, setup_test_data
):
    items, total = repository.get_all_paginated(page=1, page_size=10, query="test")

    assert total == 1
    assert len(items) == 1
    assert "test" in items[0].eng_label.lower()


def test_get_all_paginated_with_organisation_filter(
    repository: ApplicableLegislationRepository, setup_test_data
):
    items, total = repository.get_all_paginated(
        page=1, page_size=10, organisation_filters=["1"]
    )

    assert total == 2
    applicable_legislation_keys = [item.key for item in items]
    assert "applicable_legislation1" in applicable_legislation_keys
    assert "test_applicable_legislation" in applicable_legislation_keys

    items, total = repository.get_all_paginated(
        page=1, page_size=10, organisation_filters=["global"]
    )

    assert total == 1
    assert items[0].key == "applicable_legislation2"
