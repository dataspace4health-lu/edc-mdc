import pytest
from datetime import date, datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from services.dataset_comment import DatasetCommentService
from repositories.dataset_comment import DatasetCommentRepository
from test_factory import sample_dataset
from models.identity_context import IdentityContext

# Have to import these models toinitialize the models properly
from models.dataset import User
from models.dataset import Dataset
from models.dataset_comment import DatasetComment
from schemas.dataset_comment import DatasetCommentDto, ResourceDatasetComment
from services.activity_logs.comment_activity_log import CommentActivityLogService
from services.dataset_permissions_service import DatasetPermissionsService
from unittest.mock import Mock


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    yield
    db_session.query(DatasetComment).delete()
    db_session.commit()


@pytest.fixture
def dataset_comment_repository(db_session: Session) -> DatasetCommentRepository:
    return DatasetCommentRepository(db_session)


@pytest.fixture
def dataset_comment_service(
    db_session: Session, dataset_comment_repository: DatasetCommentRepository
) -> DatasetCommentService:
    mock_activity_log_service = Mock(spec=CommentActivityLogService)
    mock_permissions_service = Mock(spec=DatasetPermissionsService)
    return DatasetCommentService(
        comment_repository=dataset_comment_repository,
        activity_log_service=mock_activity_log_service,
        dataset_permissions_service=mock_permissions_service,
    )


@pytest.fixture
def dataset_comment_dto() -> DatasetCommentDto:
    return DatasetCommentDto(
        content="This is a test comment",
        user_id=1,
        dataset_id=1,
        action_type="add_comment",
    )


@pytest.fixture
def sample_dataset_comment() -> DatasetComment:
    return DatasetComment(
        id=1,
        content="This is a test comment",
        user_id=1,
        dataset_id=1,
        timestamp=datetime.now(),
    )


@pytest.fixture
def sample_identity() -> IdentityContext:
    return IdentityContext(
        user_id=1,
        permissions=["datasets:read:published"],
        current_organisation_id=1,
    )


def test_add_dataset_comment(
    dataset_comment_service: DatasetCommentService,
    dataset_comment_dto: DatasetCommentDto,
):
    new_comment = dataset_comment_service.add_dataset_comment(dataset_comment_dto)
    assert new_comment.content == dataset_comment_dto.content
    assert new_comment.dataset_id == dataset_comment_dto.dataset_id


def test_get_comments_by_dataset(
    db_session: Session,
    dataset_comment_service: DatasetCommentService,
    sample_dataset_comment: DatasetComment,
    sample_identity: IdentityContext,
):
    db_session.add(sample_dataset_comment)
    db_session.commit()

    dataset_comment_service._dataset_permissions_service.validate_read_permissions.return_value = (
        None
    )

    comments = dataset_comment_service.get_comments_by_dataset(
        dataset_id=1, identity=sample_identity
    )
    assert len(comments) == 1
    assert comments[0].id == sample_dataset_comment.id
    assert comments[0].content == "This is a test comment"


def test_get_comments_by_dataset_validates_read_permissions(
    dataset_comment_service: DatasetCommentService,
    sample_identity: IdentityContext,
):
    dataset_comment_service._dataset_permissions_service.validate_read_permissions = (
        Mock()
    )

    dataset_comment_service.get_comments_by_dataset(
        dataset_id=42, identity=sample_identity
    )

    dataset_comment_service._dataset_permissions_service.validate_read_permissions.assert_called_once_with(
        42, sample_identity
    )


def test_delete_comment(
    dataset_comment_service, sample_dataset_comment, sample_dataset, db_session
):

    db_session.add(sample_dataset)
    db_session.add(sample_dataset_comment)
    db_session.commit()

    dataset_comment_service.delete_comment(sample_dataset_comment.id)

    comment = db_session.get(DatasetComment, sample_dataset_comment.id)
    assert comment is None
