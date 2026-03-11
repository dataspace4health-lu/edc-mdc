import pytest
import json

from sqlalchemy.orm import Session
from datetime import datetime, timezone

# Have to import these models toinitialize the models properly
from models.dataset import User
from models.dataset import Dataset
from models.dataset_comment import DatasetComment
from services.user import UserService
from test_factory import db_session
from repositories.user import UserRepository
from repositories.user_assignment import UserAssignmentRepository
from repositories.activity_log import ActivityLogRepository
from repositories.dataset import DatasetRepository
from repositories.applicable_legislation import ApplicableLegislationRepository
from repositories.keyword import KeywordRepository
from services.config import ConfigService
from unittest.mock import Mock
from services.user_assignment_permissions import UserAssignmentPermissionsService
from services.activity_logs.user_assignment_activity_log import (
    UserAssignmentActivityLogService,
)
from models.identity_context import IdentityContext
from fastapi import HTTPException
from models.activity_log import ActivityLog


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    yield
    db_session.query(User).delete()
    db_session.commit()


@pytest.fixture
def test_user_data():
    """Common test user data used across multiple tests."""
    return {"email": "test@example.com", "name": "Test User", "external_id": "12345"}


@pytest.fixture
def test_delete_user_data():
    """Common test user data for delete operations."""
    return {
        "email": "todelete@example.com",
        "name": "ToDelete",
        "external_id": "ext-delete-1",
    }


@pytest.fixture(scope="function")
def config_service():
    return ConfigService("./config.json")


@pytest.fixture(scope="function")
def user_repository(db_session):
    return UserRepository(db_session=db_session)


@pytest.fixture(scope="function")
def dataset_repository(db_session):
    return DatasetRepository(db_session=db_session)


@pytest.fixture(scope="function")
def applicable_legislation_repository(db_session):
    return ApplicableLegislationRepository(db_session=db_session)


@pytest.fixture(scope="function")
def keyword_repository(db_session):
    return KeywordRepository(db_session=db_session)


@pytest.fixture(scope="function")
def user_assignment_permissions_service():
    mock = Mock(spec=UserAssignmentPermissionsService)
    mock.get_user_permission_filters.return_value = None
    return mock


@pytest.fixture(scope="function")
def user_assignment_repository(db_session):
    return UserAssignmentRepository(db_session=db_session)


@pytest.fixture(scope="function")
def activity_log_repository(db_session):
    return ActivityLogRepository(db_session=db_session)


@pytest.fixture(scope="function")
def user_assignment_activity_log_service(activity_log_repository):
    return UserAssignmentActivityLogService(repository=activity_log_repository)


@pytest.fixture(scope="function")
def user_service(
    db_session,
    user_repository,
    user_assignment_repository,
    config_service,
    user_assignment_permissions_service,
    dataset_repository,
    applicable_legislation_repository,
    keyword_repository,
    activity_log_repository,
    user_assignment_activity_log_service,
):
    return UserService(
        db_session=db_session,
        user_repository=user_repository,
        user_assignment_repository=user_assignment_repository,
        config_service=config_service,
        user_assignment_permissions_service=user_assignment_permissions_service,
        dataset_repository=dataset_repository,
        applicable_legislation_repository=applicable_legislation_repository,
        keyword_repository=keyword_repository,
        activity_log_repository=activity_log_repository,
        user_assignment_activity_log_service=user_assignment_activity_log_service,
    )


def test_user_service_create_or_find(db_session, user_service, test_user_data):
    created_user = user_service.create_or_find(
        email=test_user_data["email"],
        name=test_user_data["name"],
        external_id=test_user_data["external_id"],
        iam_roles=["DATA_MANAGER"],
    )

    assert created_user is not None
    assert created_user.email == test_user_data["email"]
    assert created_user.name == test_user_data["name"]
    assert created_user.external_id == test_user_data["external_id"]

    found_user = user_service.create_or_find(
        email=test_user_data["email"],
        name=test_user_data["name"],
        external_id=test_user_data["external_id"],
        iam_roles=["CONTRIBUTOR", "DATA_MANAGER"],
    )

    assert found_user.id == created_user.id
    assert found_user.email == test_user_data["email"]
    assert found_user.name == test_user_data["name"]
    assert found_user.external_id == test_user_data["external_id"]
    assert found_user.iam_roles == "CONTRIBUTOR,DATA_MANAGER"


def test_find_dataset_validator_users(db_session, user_service):
    user1 = User(
        name="Alice", iam_roles="DATA_MANAGER,GROUP_MANAGER", external_id="123"
    )
    user2 = User(name="Bob", iam_roles="CONTRIBUTER", external_id="456")
    db_session.add_all([user1, user2])
    db_session.commit()

    users = user_service.find_dataset_validator_users()

    assert len(users) == 1
    assert users[0].name == "Alice"


def test_delete_unassigned_user_success(
    db_session: Session,
    user_service: UserService,
    test_delete_user_data,
):
    created = user_service.create_or_find(
        email=test_delete_user_data["email"],
        name=test_delete_user_data["name"],
        external_id=test_delete_user_data["external_id"],
        iam_roles=[],
    )

    assert created.id is not None

    identity = IdentityContext(user_id=999, permissions=["roles:manage"])

    user_service.delete_unassigned_user(user_id=created.id, identity=identity)

    assert user_service.find_by_id(created.id) is None


def test_delete_unassigned_user_no_permission(
    db_session: Session, user_service: UserService, test_delete_user_data
):
    created = user_service.create_or_find(
        email=test_delete_user_data["email"],
        name=test_delete_user_data["name"],
        external_id=test_delete_user_data["external_id"],
        iam_roles=[],
    )
    assert created.id is not None

    identity = IdentityContext(user_id=999, permissions=["DATA_MANAGER"])

    with pytest.raises(HTTPException) as excinfo:
        user_service.delete_unassigned_user(user_id=created.id, identity=identity)

    assert excinfo.value.status_code == 403
    assert "You do not have permission to delete users" in excinfo.value.detail


def test_delete_unassigned_user_with_activity_logs_succeeds(
    db_session: Session,
    user_service: UserService,
    test_delete_user_data,
):
    created = user_service.create_or_find(
        email=test_delete_user_data["email"],
        name=test_delete_user_data["name"],
        external_id=test_delete_user_data["external_id"],
        iam_roles=[],
    )
    assert created.id is not None

    db_session.add(
        ActivityLog(
            user_id=created.id,
            action_type="create",
            entity_type="dataset",
            entity_id="1",
            changes="{}",
        )
    )
    db_session.commit()

    identity = IdentityContext(user_id=999, permissions=["roles:manage"])

    user_service.delete_unassigned_user(user_id=created.id, identity=identity)

    assert user_service.find_by_id(created.id) is None
    assert db_session.query(ActivityLog).count() == 1


def test_user_service_create_or_find_by_email(db_session, user_service):
    email = "user@example.com"
    name = "Test User"
    old_external_id = "old-iam-sub-12345"
    new_external_id = "new-iam-sub-67890"

    # Create user with old IAM external_id
    created_user = user_service.create_or_find(
        email=email, name=name, external_id=old_external_id, iam_roles=["DATA_MANAGER"]
    )

    assert created_user.external_id == old_external_id
    original_user_id = created_user.id

    # Simulate login from new IAM with same email but different external_id
    found_user = user_service.create_or_find(
        email=email,
        name=name,
        external_id=new_external_id,
        iam_roles=["DATA_MANAGER"],
    )

    # Should find the same user (not create new one)
    assert found_user.id == original_user_id
    assert found_user.email == email.lower()
    # External ID should be updated to new IAM's sub
    assert found_user.external_id == new_external_id

    # Verify only one user exists in database
    all_users = db_session.query(User).filter_by(email=email.lower()).all()
    assert len(all_users) == 1


def test_user_service_finds_existing_uppercase_email_in_db(db_session, user_service):
    # Simulate existing user in DB with uppercase email (before normalization was added)
    existing_user = User(
        email="USER@EXAMPLE.COM",
        name="Existing User",
        external_id="old-ext-123",
        iam_roles="DATA_MANAGER",
    )
    db_session.add(existing_user)
    db_session.commit()
    original_user_id = existing_user.id

    # New IAM sends lowercase email with different external_id
    found_user = user_service.create_or_find(
        email="user@example.com",
        name="Existing User",
        external_id="new-ext-456",
        iam_roles=["CONTRIBUTOR"],
    )

    # Should find the existing user (case-insensitive match)
    assert found_user.id == original_user_id
    assert found_user.external_id == "new-ext-456"

    # Verify only one user exists
    all_users = (
        db_session.query(User).filter(User.email.ilike("user@example.com")).all()
    )
    assert len(all_users) == 1


def test_create_or_find_sets_last_login_at(db_session, user_service, test_user_data):
    # Create user
    created_user = user_service.create_or_find(
        email=test_user_data["email"],
        name=test_user_data["name"],
        external_id=test_user_data["external_id"],
        iam_roles=["DATA_MANAGER"],
    )

    # Verify last_login_at is set
    assert created_user.last_login_at is not None
    assert isinstance(created_user.last_login_at, datetime)

    # Verify it's a recent timestamp (within last 2 hours to account for timezone differences in test env)
    if created_user.last_login_at.tzinfo is not None:
        now = datetime.now(timezone.utc)
    else:
        now = datetime.now()

    time_diff = abs((now - created_user.last_login_at).total_seconds())
    assert time_diff < 7200  # Within 2 hours


def test_create_or_find_updates_last_login_at(db_session, user_service, test_user_data):
    # Create user
    created_user = user_service.create_or_find(
        email=test_user_data["email"],
        name=test_user_data["name"],
        external_id=test_user_data["external_id"],
        iam_roles=["DATA_MANAGER"],
    )

    first_login = created_user.last_login_at
    assert first_login is not None

    # Manually set to an older time to verify update
    import time

    time.sleep(0.1)  # Small delay to ensure different timestamp

    # Login again (find existing user)
    found_user = user_service.create_or_find(
        email=test_user_data["email"],
        name=test_user_data["name"],
        external_id=test_user_data["external_id"],
        iam_roles=["DATA_MANAGER"],
    )

    # Verify last_login_at is updated
    assert found_user.last_login_at is not None
    assert found_user.last_login_at > first_login
