from sqlalchemy.orm import Session
from models.activity_log import ActivityLog
from repositories.activity_log import ActivityLogRepository
import pytest
from unittest.mock import Mock


@pytest.fixture
def activity_log_repository() -> ActivityLogRepository:
    return ActivityLogRepository(Mock(spec=Session))


def test_get_activity_logs_from_dataset(activity_log_repository: ActivityLogRepository):
    dataset_id = 1
    page = 1
    page_size = 10

    activity_logs = [
        ActivityLog(
            id=1,
            user_id=1,
            entity_id=1,
            entity_type="dataset",
            action_type="ActivityLog 1",
        )
    ]
    activity_log_repository._db_session.query().filter().filter().order_by().offset(
        (page - 1) * page_size
    ).limit(page_size).all.return_value = activity_logs

    actual = activity_log_repository.get_activity_logs_from_dataset(
        dataset_id,
        page,
        page_size,
    )

    assert isinstance(actual, list)
    assert len(actual) == 1
    assert actual[0].action_type == "ActivityLog 1"


def test_get_activity_logs_from_organisation(
    activity_log_repository: ActivityLogRepository,
):
    organisation_id = 1
    page = 1
    page_size = 10

    activity_logs = [
        ActivityLog(
            id=2,
            user_id=2,
            entity_id=1,
            entity_type="organisation",
            action_type="ActivityLog for Organisation",
        )
    ]
    activity_log_repository._db_session.query().filter().filter().order_by().offset(
        (page - 1) * page_size
    ).limit(page_size).all.return_value = activity_logs

    actual = activity_log_repository.get_activity_logs_from_organisation(
        organisation_id,
        page,
        page_size,
    )

    assert len(actual) == 1
    assert actual[0].action_type == "ActivityLog for Organisation"


def test_get_activity_logs_for_applicable_legislation(
    activity_log_repository: ActivityLogRepository,
):
    entity_type = "applicable_legislation"
    page = 1
    page_size = 10

    activity_logs = [
        ActivityLog(
            id=3,
            user_id=3,
            entity_id="GDPR",
            entity_type="applicable_legislation",
            action_type="Created applicable legislation",
        )
    ]
    activity_log_repository._db_session.query().filter().order_by().offset(
        (page - 1) * page_size
    ).limit(page_size).all.return_value = activity_logs

    actual = activity_log_repository.get_all_activity_logs_for_entity(
        entity_type,
        page,
        page_size,
    )

    assert len(actual) == 1
    assert actual[0].entity_type == "applicable_legislation"
    assert actual[0].entity_id == "GDPR"


def test_get_all_activity_logs_for_keywords(
    activity_log_repository: ActivityLogRepository,
):
    entity_type = "keyword"
    page = 1
    page_size = 10

    activity_logs = [
        ActivityLog(
            id=4,
            user_id=4,
            entity_id="keyword1",
            entity_type="keyword",
            action_type="Updated keyword label",
        )
    ]
    activity_log_repository._db_session.query().filter().order_by().offset(
        (page - 1) * page_size
    ).limit(page_size).all.return_value = activity_logs

    actual = activity_log_repository.get_all_activity_logs_for_entity(
        entity_type,
        page,
        page_size,
    )

    assert len(actual) == 1
    assert actual[0].entity_type == "keyword"
    assert actual[0].entity_id == "keyword1"


def test_get_all_activity_logs_from_organisations(
    activity_log_repository: ActivityLogRepository,
):
    organisation_ids = [7, 8]
    page = 2
    page_size = 3

    activity_logs = [
        ActivityLog(
            id=10,
            user_id=5,
            entity_id="7",
            entity_type="organisation",
            action_type="OrgLog for 7",
        ),
        ActivityLog(
            id=11,
            user_id=6,
            entity_id="8",
            entity_type="organisation",
            action_type="OrgLog for 8",
        ),
    ]

    session_query = activity_log_repository._db_session.query.return_value
    session_query.filter.return_value = session_query
    session_query.filter.return_value = session_query
    session_query.order_by.return_value = session_query
    session_query.offset.return_value = session_query
    session_query.limit.return_value = session_query
    session_query.all.return_value = activity_logs

    actual = activity_log_repository.get_all_activity_logs_from_organisations(
        organisation_ids,
        page,
        page_size,
    )

    assert isinstance(actual, list)
    assert len(actual) == 2
    assert actual[0].action_type == "OrgLog for 7"
    assert actual[1].action_type == "OrgLog for 8"
