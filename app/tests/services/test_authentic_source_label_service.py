import pytest
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from services.authentic_source_label import AuthenticSourceLabelService
from services.activity_logs.authentic_source_label_activity_log import (
    AuthenticSourceLabelActivityLogService,
)

from repositories.authentic_source_label import AuthenticSourceLabelRepository
from repositories.authentic_source_assignment import AuthenticSourceAssignmentRepository
from repositories.activity_log import ActivityLogRepository
from models.authentic_source_label import AuthenticSourceLabel
from models.identity_context import IdentityContext
from schemas.authentic_source_label import (
    AuthenticSourceLabelDto,
    ResourceAuthenticSourceLabel,
)
from unittest.mock import Mock
from factories.authentic_source_label import create_sample_authentic_source_label


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    yield
    db_session.query(AuthenticSourceLabel).delete()
    db_session.commit()


@pytest.fixture
def authentic_source_label_repository(
    db_session: Session,
) -> AuthenticSourceLabelRepository:
    return AuthenticSourceLabelRepository(db_session)


@pytest.fixture
def authentic_source_assignment_repository(
    db_session: Session,
) -> AuthenticSourceAssignmentRepository:
    return AuthenticSourceAssignmentRepository(db_session=db_session)


@pytest.fixture
def authentic_source_label_activity_log_service(
    db_session: Session,
    authentic_source_label_repository: AuthenticSourceLabelRepository,
) -> AuthenticSourceLabelActivityLogService:
    return AuthenticSourceLabelActivityLogService(
        repository=authentic_source_label_repository,
    )


@pytest.fixture
def authentic_source_label_service(
    db_session: Session,
    authentic_source_label_repository: AuthenticSourceLabelRepository,
    authentic_source_label_activity_log_service: AuthenticSourceLabelActivityLogService,
    authentic_source_assignment_repository: AuthenticSourceAssignmentRepository,
) -> AuthenticSourceLabelService:
    return AuthenticSourceLabelService(
        label_repo=authentic_source_label_repository,
        assignment_repo=authentic_source_assignment_repository,
        activity_log_service=authentic_source_label_activity_log_service,
    )


@pytest.fixture
def identity_context() -> IdentityContext:
    mock_identity = Mock(spec=IdentityContext)
    mock_identity.user_id = 1
    return mock_identity


@pytest.fixture
def authentic_source_label_dto() -> AuthenticSourceLabelDto:
    return AuthenticSourceLabelDto(
        name="Government Records",
        description="Official government databases and records",
    )


@pytest.fixture
def sample_authentic_source_label() -> AuthenticSourceLabel:
    return create_sample_authentic_source_label()


@pytest.fixture
def existing_label_in_db(
    db_session: Session, sample_authentic_source_label: AuthenticSourceLabel
) -> AuthenticSourceLabel:
    db_session.add(sample_authentic_source_label)
    db_session.commit()
    db_session.refresh(sample_authentic_source_label)
    return sample_authentic_source_label


def test_create_label_success(
    authentic_source_label_service: AuthenticSourceLabelService,
    authentic_source_label_dto: AuthenticSourceLabelDto,
    identity_context: IdentityContext,
):
    new_label = authentic_source_label_service.create_label(
        authentic_source_label_dto, identity_context
    )

    assert new_label.name == authentic_source_label_dto.name
    assert new_label.description == authentic_source_label_dto.description
    assert new_label.created_by == identity_context.user_id
    assert new_label.id is not None
    assert new_label.created_at is not None


def test_create_label_duplicate_name_conflict(
    authentic_source_label_service: AuthenticSourceLabelService,
    authentic_source_label_dto: AuthenticSourceLabelDto,
    identity_context: IdentityContext,
    existing_label_in_db: AuthenticSourceLabel,
):
    duplicate_dto = AuthenticSourceLabelDto(
        name=existing_label_in_db.name, description="Different description"
    )

    with pytest.raises(HTTPException) as exc_info:
        authentic_source_label_service.create_label(duplicate_dto, identity_context)

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail
    assert existing_label_in_db.name in exc_info.value.detail


def test_get_all_labels_single_label(
    authentic_source_label_service: AuthenticSourceLabelService,
    existing_label_in_db: AuthenticSourceLabel,
):
    labels = authentic_source_label_service.get_all_labels()

    assert labels[0].id == existing_label_in_db.id
    assert labels[0].name == existing_label_in_db.name
    assert labels[0].description == existing_label_in_db.description


def test_update_label_success(
    authentic_source_label_service: AuthenticSourceLabelService,
    identity_context: IdentityContext,
    existing_label_in_db: AuthenticSourceLabel,
):
    updated_dto = AuthenticSourceLabelDto(
        name="Updated Government Records",
        description="Updated official government databases and records",
    )

    updated_label = authentic_source_label_service.update_label(
        label_id=existing_label_in_db.id,
        label_dto=updated_dto,
        identity=identity_context,
    )

    assert updated_label.id == existing_label_in_db.id
    assert updated_label.name == updated_dto.name
    assert updated_label.description == updated_dto.description
    assert updated_label.created_by == identity_context.user_id


def test_delete_label_success(
    authentic_source_label_service: AuthenticSourceLabelService,
    identity_context: IdentityContext,
    existing_label_in_db: AuthenticSourceLabel,
):
    label_id = existing_label_in_db.id

    authentic_source_label_service.delete_label(
        label_id=label_id,
        identity=identity_context,
    )

    remaining_labels = authentic_source_label_service.get_all_labels()
    assert len(remaining_labels) == 0


def test_deprecate_label_success(
    authentic_source_label_service: AuthenticSourceLabelService,
    identity_context: IdentityContext,
    existing_label_in_db: AuthenticSourceLabel,
    db_session: Session,
):
    assert not existing_label_in_db.is_deprecated
    result = authentic_source_label_service.update_deprecation_status(
        label_id=existing_label_in_db.id, identity=identity_context
    )
    db_session.refresh(existing_label_in_db)

    assert result.id == existing_label_in_db.id
    assert result.is_deprecated is True
    assert existing_label_in_db.is_deprecated is True


def test_update_deprecation_status_deprecate(
    authentic_source_label_service: AuthenticSourceLabelService,
    identity_context: IdentityContext,
    existing_label_in_db: AuthenticSourceLabel,
    db_session: Session,
):
    assert not existing_label_in_db.is_deprecated

    result = authentic_source_label_service.update_deprecation_status(
        label_id=existing_label_in_db.id, identity=identity_context
    )
    db_session.refresh(existing_label_in_db)

    assert result.id == existing_label_in_db.id
    assert result.is_deprecated is True
    assert existing_label_in_db.is_deprecated is True


def test_update_deprecation_status_restore(
    authentic_source_label_service: AuthenticSourceLabelService,
    identity_context: IdentityContext,
    existing_label_in_db: AuthenticSourceLabel,
    db_session: Session,
):
    existing_label_in_db.is_deprecated = True
    db_session.commit()

    result = authentic_source_label_service.update_deprecation_status(
        label_id=existing_label_in_db.id, identity=identity_context
    )
    db_session.refresh(existing_label_in_db)

    assert result.id == existing_label_in_db.id
    assert result.is_deprecated is False
    assert existing_label_in_db.is_deprecated is False
