import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.dataset import User, Keyword
from models.organisation import Organisation
from models.keyword_assignment import KeywordAssignment
from repositories.keyword import KeywordRepository


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    db_session.query(KeywordAssignment).delete()
    db_session.query(Keyword).delete()
    db_session.query(User).delete()
    db_session.query(Organisation).delete()
    db_session.commit()


@pytest.fixture
def keyword_repository(db_session: Session) -> KeywordRepository:
    return KeywordRepository(db_session)


@pytest.fixture
def setup_test_data(db_session: Session):
    org1 = Organisation(name="Organization 1", is_deprecated=False)
    org2 = Organisation(name="Organization 2", is_deprecated=False)

    user1 = User(name="John Doe", email="john@example.com", external_id="john-123")
    user2 = User(name="system", external_id="system-456")

    db_session.add_all([org1, org2, user1, user2])
    db_session.commit()

    keyword1 = Keyword(
        key="keyword1",
        eng_label="First Keyword",
        created_by_id=user1.id,
    )
    keyword2 = Keyword(
        key="keyword2",
        eng_label="Second Keyword",
        created_by_id=None,
    )
    keyword3 = Keyword(
        key="keyword3",
        eng_label="Third Keyword",
        created_by_id=user1.id,
    )
    keyword4 = Keyword(
        key="test_keyword",
        eng_label="Test Search Keyword",
        created_by_id=user1.id,
    )

    db_session.add_all([keyword1, keyword2, keyword3, keyword4])
    db_session.commit()

    assignment1 = KeywordAssignment(keyword_key="keyword1", organisation_id=org1.id)
    assignment3 = KeywordAssignment(keyword_key="keyword3", organisation_id=org2.id)
    assignment4 = KeywordAssignment(keyword_key="test_keyword", organisation_id=org1.id)

    db_session.add_all([assignment1, assignment3, assignment4])
    db_session.commit()

    return {
        "keywords": [keyword1, keyword2, keyword3, keyword4],
        "users": [user1, user2],
        "orgs": [org1, org2],
        "assignments": [assignment1, assignment3, assignment4],
    }


def test_get_all_paginated_basic(
    keyword_repository: KeywordRepository, setup_test_data
):
    keywords, total = keyword_repository.get_all_paginated(page=1, page_size=2)

    assert total == 4
    assert len(keywords) == 2
    assert keywords[0].eng_label == "First Keyword"
    assert keywords[1].eng_label == "Second Keyword"


def test_get_all_paginated_with_search(
    keyword_repository: KeywordRepository, setup_test_data
):
    keywords, total = keyword_repository.get_all_paginated(
        page=1, page_size=10, query="test"
    )

    assert total == 1
    assert len(keywords) == 1
    assert "test" in keywords[0].eng_label.lower()


def test_get_all_paginated_with_organisation_filter(
    keyword_repository: KeywordRepository, setup_test_data
):

    keywords, total = keyword_repository.get_all_paginated(
        page=1, page_size=10, organisation_filters=["1"]
    )

    assert total == 2
    keyword_keys = [k.key for k in keywords]
    assert "keyword1" in keyword_keys
    assert "test_keyword" in keyword_keys

    keywords, total = keyword_repository.get_all_paginated(
        page=1, page_size=10, organisation_filters=["global"]
    )

    assert total == 1
    assert keywords[0].key == "keyword2"
