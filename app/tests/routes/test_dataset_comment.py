import pytest
from fastapi.testclient import TestClient
from services.dataset_comment import DatasetCommentService
from test_factory import client_with_logged_in_user, sample_dataset
from test_factory import sample_contributor, sample_comment
from conftest import db_session
from models.dataset_comment import DatasetComment
from models.dataset import User
from sqlalchemy.orm import Session


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    yield
    db_session.query(User).delete()
    db_session.query(DatasetComment).delete()
    db_session.commit()


def test_get_dataset_comments(
    client_with_logged_in_user,
    db_session,
    sample_dataset,
    sample_contributor,
    sample_comment,
):
    db_session.add(sample_contributor)
    db_session.commit()
    sample_comment.user_id = sample_contributor.id
    sample_comment.dataset_id = sample_dataset.id
    db_session.add(sample_comment)
    db_session.commit()

    dataset_id = sample_dataset.id
    response = client_with_logged_in_user.get(f"/api/v1/datasets/{dataset_id}/comments")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    comments = response.json()
    assert comments[0]["content"] == "Great data!"
    assert comments[0]["author"] == "contributor"
    assert comments[0]["dataset_id"] == dataset_id
