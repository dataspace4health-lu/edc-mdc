import pytest
from test_factory import client_with_logged_in_user, sample_dataset
from conftest import db_session
from sqlalchemy.orm import Session
from models.dataset import Dataset
from models.distribution import (
    Distribution,
    DistributionAccessUrl,
    DistributionDownloadUrl,
)


@pytest.fixture
def clean_db(db_session: Session):
    db_session.query(DistributionDownloadUrl).delete()
    db_session.query(Distribution).delete()
    db_session.query(Dataset).delete()
    db_session.commit()
    yield
    db_session.query(DistributionDownloadUrl).delete()
    db_session.query(Distribution).delete()
    db_session.query(Dataset).delete()
    db_session.commit()


@pytest.fixture
def default_distribution():
    return {
        "title": "Test Distribution",
        "description": "Test description",
        "access_urls": ["https://example.com/data.csv"],
        "download_urls": ["https://example.com/download/data.csv"],
        "byte_size": 1024,
        "media_type": "text/csv",
        "rights_statement": "Public Domain",
        "languages": ["ENG"],
    }


def test_create_distribution(
    client_with_logged_in_user, sample_dataset, default_distribution
):
    dataset_id = sample_dataset.id

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/distributions",
        json=default_distribution,
    )

    assert response.status_code == 201, response.text
    distribution = response.json()

    assert distribution["title"] == default_distribution["title"]
    assert distribution["description"] == default_distribution["description"]
    assert distribution["access_urls"] == default_distribution["access_urls"]
    assert distribution["download_urls"] == default_distribution["download_urls"]
    assert distribution["byte_size"] == default_distribution["byte_size"]
    assert distribution["media_type"] == default_distribution["media_type"]
    assert distribution["rights_statement"] == default_distribution["rights_statement"]
    assert "dataset_id" in distribution
    assert distribution["dataset_id"] == dataset_id
    assert "id" in distribution


def test_get_distributions(
    client_with_logged_in_user, sample_dataset, default_distribution, db_session
):
    dataset_id = sample_dataset.id

    # Clean existing distributions from sample_dataset
    db_session.query(DistributionDownloadUrl).delete()
    db_session.query(DistributionAccessUrl).delete()
    db_session.query(Distribution).filter_by(dataset_id=dataset_id).delete()
    db_session.commit()

    create_response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/distributions",
        json=default_distribution,
    )
    assert create_response.status_code == 201
    created_dist = create_response.json()

    response = client_with_logged_in_user.get(
        f"/api/v1/datasets/{dataset_id}/distributions"
    )

    assert response.status_code == 200
    result = response.json()

    distribution = next(
        (d for d in result if d["title"] == default_distribution["title"]), None
    )
    assert (
        distribution is not None
    ), f"Could not find distribution with title '{default_distribution['title']}'"

    assert distribution["title"] == default_distribution["title"]
    assert distribution["description"] == default_distribution["description"]
    assert distribution["access_urls"] == default_distribution["access_urls"]
    assert distribution["download_urls"] == default_distribution["download_urls"]
    assert distribution["byte_size"] == default_distribution["byte_size"]
    assert distribution["media_type"] == default_distribution["media_type"]
    assert distribution["rights_statement"] == default_distribution["rights_statement"]
    assert "dataset_id" in distribution
    assert distribution["dataset_id"] == dataset_id


def test_update_distribution(
    client_with_logged_in_user, sample_dataset, default_distribution
):
    dataset_id = sample_dataset.id

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/distributions",
        json=default_distribution,
    )
    assert response.status_code == 201
    created_distribution = response.json()
    distribution_id = created_distribution["id"]

    updated_data = {
        "title": "Updated Distribution",
        "description": "Updated description",
        "access_urls": ["https://example.com/updated.json"],
        "download_urls": ["https://example.com/download/updated.json"],
        "byte_size": 2048,
        "media_type": "application/json",
        "rights_statement": "CC BY 4.0",
        "languages": ["FRA"],
    }

    response = client_with_logged_in_user.put(
        f"/api/v1/datasets/{dataset_id}/distributions/{distribution_id}",
        json=updated_data,
    )

    assert response.status_code == 200, response.text
    updated_distribution = response.json()

    assert updated_distribution["title"] == updated_data["title"]
    assert updated_distribution["description"] == updated_data["description"]
    assert sorted(updated_distribution["access_urls"]) == sorted(
        updated_data["access_urls"]
    )
    assert updated_distribution["download_urls"] == updated_data["download_urls"]
    assert updated_distribution["byte_size"] == updated_data["byte_size"]
    assert updated_distribution["media_type"] == updated_data["media_type"]
    assert updated_distribution["rights_statement"] == updated_data["rights_statement"]
    assert updated_distribution["dataset_id"] == dataset_id
    assert updated_distribution["id"] == distribution_id


def test_delete_distribution(
    client_with_logged_in_user, sample_dataset, default_distribution, db_session
):
    dataset_id = sample_dataset.id

    # Clean existing distributions from sample_dataset
    db_session.query(Distribution).filter_by(dataset_id=dataset_id).delete()
    db_session.commit()

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/distributions",
        json=default_distribution,
    )
    assert response.status_code == 201
    distribution = response.json()
    distribution_id = distribution["id"]

    response = client_with_logged_in_user.delete(
        f"/api/v1/datasets/{dataset_id}/distributions/{distribution_id}"
    )
    assert response.status_code == 204

    response = client_with_logged_in_user.get(
        f"/api/v1/datasets/{dataset_id}/distributions"
    )
    result = response.json()
    assert len(result) == 0


def test_create_distribution_invalid_dataset(
    client_with_logged_in_user, default_distribution
):
    invalid_dataset_id = 99999

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{invalid_dataset_id}/distributions",
        json=default_distribution,
    )

    assert response.status_code == 404, response.text


def test_update_distribution_not_found(
    client_with_logged_in_user, sample_dataset, default_distribution
):
    dataset_id = sample_dataset.id
    invalid_distribution_id = 99999

    response = client_with_logged_in_user.put(
        f"/api/v1/datasets/{dataset_id}/distributions/{invalid_distribution_id}",
        json=default_distribution,
    )

    assert response.status_code == 404, response.text


def test_delete_distribution_not_found(client_with_logged_in_user, sample_dataset):
    dataset_id = sample_dataset.id
    invalid_distribution_id = 99999

    response = client_with_logged_in_user.delete(
        f"/api/v1/datasets/{dataset_id}/distributions/{invalid_distribution_id}"
    )

    assert response.status_code == 404, response.text


def test_create_multiple_distributions(
    client_with_logged_in_user, sample_dataset, default_distribution, db_session
):
    dataset_id = sample_dataset.id

    # Clean existing distributions from sample_dataset
    db_session.query(Distribution).filter_by(dataset_id=dataset_id).delete()
    db_session.commit()

    distribution1 = default_distribution.copy()
    distribution1["title"] = "Distribution 1"
    response1 = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/distributions",
        json=distribution1,
    )
    assert response1.status_code == 201

    distribution2 = default_distribution.copy()
    distribution2["title"] = "Distribution 2"
    response2 = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/distributions",
        json=distribution2,
    )
    assert response2.status_code == 201

    response = client_with_logged_in_user.get(
        f"/api/v1/datasets/{dataset_id}/distributions"
    )
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 2


def test_create_distribution_rejects_duplicate_title_for_same_dataset(
    client_with_logged_in_user, sample_dataset, default_distribution
):
    dataset_id = sample_dataset.id

    first_response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/distributions",
        json=default_distribution,
    )
    assert first_response.status_code == 201

    second_response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/distributions",
        json={**default_distribution, "title": f"  {default_distribution['title']}  "},
    )
    assert second_response.status_code == 409
    assert (
        second_response.json()["detail"]
        == "A distribution with this title already exists."
    )


def test_update_distribution_rejects_duplicate_title_for_same_dataset(
    client_with_logged_in_user, sample_dataset, default_distribution
):
    dataset_id = sample_dataset.id

    first_response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/distributions",
        json={**default_distribution, "title": "Distribution A"},
    )
    assert first_response.status_code == 201
    first_id = first_response.json()["id"]

    second_response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/distributions",
        json={**default_distribution, "title": "Distribution B"},
    )
    assert second_response.status_code == 201
    second_id = second_response.json()["id"]

    update_response = client_with_logged_in_user.put(
        f"/api/v1/datasets/{dataset_id}/distributions/{second_id}",
        json={**default_distribution, "title": "distribution a"},
    )
    assert update_response.status_code == 409
    assert (
        update_response.json()["detail"]
        == "A distribution with this title already exists."
    )

    # Control check: updating with the same title as itself should still be allowed.
    self_update_response = client_with_logged_in_user.put(
        f"/api/v1/datasets/{dataset_id}/distributions/{first_id}",
        json={**default_distribution, "title": "Distribution A"},
    )
    assert self_update_response.status_code == 200


def test_create_distribution_generates_unique_titles_when_missing(
    client_with_logged_in_user, sample_dataset, default_distribution
):
    dataset_id = sample_dataset.id
    payload = {k: v for k, v in default_distribution.items() if k != "title"}

    first_response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/distributions",
        json=payload,
    )
    assert first_response.status_code == 201
    assert first_response.json()["title"] == "Distribution"

    second_response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{dataset_id}/distributions",
        json=payload,
    )
    assert second_response.status_code == 201
    assert second_response.json()["title"] == "Distribution (2)"
