import pytest
from sqlalchemy.orm import Session

# Have to import these models toinitialize the models properly
from models.dataset import User
from models.dataset import Dataset
from models.dataset_comment import DatasetComment
from repositories.dataset_comment import DatasetCommentRepository
from fastapi import HTTPException


@pytest.fixture
def comment_repository(db_session: Session) -> DatasetCommentRepository:
    return DatasetCommentRepository(db_session)


@pytest.fixture
def sample_comment(db_session: Session) -> DatasetComment:
    comment = DatasetComment(
        dataset_id=1, user_id=1, content="This is a sample comment"
    )
    db_session.add(comment)
    db_session.commit()
    return comment


def test_get_dataset_comments(
    comment_repository: DatasetCommentRepository,
    db_session: Session,
    sample_comment: DatasetComment,
):
    comments = comment_repository.get_dataset_comments(dataset_id=1)
    assert len(comments) == 1
    assert comments[0].content == "This is a sample comment"


def test_add_comment(comment_repository: DatasetCommentRepository, db_session: Session):
    new_comment = DatasetComment(
        dataset_id=1, user_id=2, content="Another sample comment"
    )
    comment_repository.add(new_comment)
    db_session.commit()

    added_comment = (
        db_session.query(DatasetComment)
        .filter_by(content="Another sample comment")
        .first()
    )
    assert added_comment is not None
    assert added_comment.content == "Another sample comment"


def test_no_comments_found(comment_repository: DatasetCommentRepository):
    comments = comment_repository.get_dataset_comments(dataset_id=999)
    assert len(comments) == 0


def test_delete_comment(
    comment_repository: DatasetCommentRepository,
    db_session: Session,
    sample_comment: DatasetComment,
):
    comment_repository.delete_comment_by_id(sample_comment.id)
    db_session.commit()

    deleted_comment = (
        db_session.query(DatasetComment).filter_by(id=sample_comment.id).first()
    )
    assert deleted_comment is None
