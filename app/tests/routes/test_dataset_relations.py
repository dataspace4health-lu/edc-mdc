import pytest
from test_factory import client_with_logged_in_user
from conftest import db_session
from test_factory import sample_dataset
from models.dataset import Dataset


@pytest.fixture
def default_dataset_relation():
    return {"relation_kind": "dataset", "relation_type": "dct:hasVersion"}


@pytest.fixture
def default_external_relation():
    return {
        "relation_kind": "external",
        "external_url": "https://example.com/documentation",
        "external_role": "describedby",
        "external_description": "Official documentation",
    }


def test_create_dataset_relation(
    client_with_logged_in_user,
    sample_dataset,
    db_session,
    default_dataset_relation,
):
    # Create another sample dataset
    sample_dataset2 = sample_dataset
    db_session.add(sample_dataset2)
    db_session.flush()

    source_dataset_id = sample_dataset.id
    target_dataset_id = sample_dataset2.id

    data = {
        "relation_kind": "dataset",
        "target_dataset": target_dataset_id,
        "relation_type": default_dataset_relation["relation_type"],
    }

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{source_dataset_id}/relations",
        json=data,
    )

    assert response.status_code == 201
    dataset_relation = response.json()

    assert (
        dataset_relation["relation_type"] == default_dataset_relation["relation_type"]
    )
    assert dataset_relation["source_dataset"] == source_dataset_id
    assert dataset_relation["target_dataset"] == target_dataset_id

    duplicate_response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{source_dataset_id}/relations",
        json=data,
    )
    assert duplicate_response.status_code == 400
    assert (
        "Duplicate or reciprocal relation exists" in duplicate_response.json()["detail"]
    )

    reciprocal_data = {
        "relation_kind": "dataset",
        "target_dataset": source_dataset_id,
        "relation_type": "dct:isVersionOf",
    }
    reciprocal_response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{target_dataset_id}/relations",
        json=reciprocal_data,
    )
    assert reciprocal_response.status_code == 400
    assert (
        "Duplicate or reciprocal relation exists"
        in reciprocal_response.json()["detail"]
    )


def test_create_external_relation(
    client_with_logged_in_user,
    sample_dataset,
    default_external_relation,
):
    source_dataset_id = sample_dataset.id

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{source_dataset_id}/relations",
        json=default_external_relation,
    )

    assert response.status_code == 201
    external_relation = response.json()

    assert external_relation["relation_kind"] == "external"
    assert (
        external_relation["external_url"] == default_external_relation["external_url"]
    )
    assert (
        external_relation["external_role"] == default_external_relation["external_role"]
    )
    assert (
        external_relation["external_description"]
        == default_external_relation["external_description"]
    )

    duplicate_response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{source_dataset_id}/relations",
        json=default_external_relation,
    )
    assert duplicate_response.status_code == 400
    assert (
        "Relation with this external URL already exists"
        in duplicate_response.json()["detail"]
    )


def test_get_dataset_relations(
    client_with_logged_in_user,
    sample_dataset,
    default_dataset_relation,
):
    source_dataset_id = sample_dataset.id
    target_dataset_id = sample_dataset.id  # Using the same dataset for simplicity

    data = {
        "relation_kind": "dataset",
        "target_dataset": target_dataset_id,
        "relation_type": default_dataset_relation["relation_type"],
    }

    # Create a relation
    create_response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{source_dataset_id}/relations",
        json=data,
    )
    assert create_response.status_code == 201

    # Get the relations
    get_response = client_with_logged_in_user.get(
        f"/api/v1/datasets/{source_dataset_id}/relations"
    )
    assert get_response.status_code == 200
    result = get_response.json()

    # Check if the created relation exists in the result
    assert any(
        r["source_dataset"] == source_dataset_id
        and r["target_dataset"] == target_dataset_id
        and r["relation_type"] == default_dataset_relation["relation_type"]
        for r in result
    )

    # Check for the reciprocal relation
    reciprocal_relation_type = "dct:isVersionOf"
    assert any(
        r["source_dataset"] == target_dataset_id
        and r["target_dataset"] == source_dataset_id
        and r["relation_type"] == reciprocal_relation_type
        for r in result
    )


def test_delete_dataset_relation(
    client_with_logged_in_user,
    sample_dataset,
    db_session,
    default_dataset_relation,
):
    # Create another sample dataset
    sample_dataset2 = sample_dataset
    db_session.add(sample_dataset2)
    db_session.flush()

    source_dataset_id = sample_dataset.id
    target_dataset_id = sample_dataset2.id

    data = {
        "relation_kind": "dataset",
        "target_dataset": target_dataset_id,
        "relation_type": default_dataset_relation["relation_type"],
    }

    create_response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{source_dataset_id}/relations",
        json=data,
    )
    assert create_response.status_code == 201

    # Get the relations
    get_response = client_with_logged_in_user.get(
        f"/api/v1/datasets/{source_dataset_id}/relations"
    )
    assert get_response.status_code == 200
    result = get_response.json()

    assert len(result) > 0, "No relations found after creation"

    relation_id = result[0]["id"]

    # Delete
    delete_response = client_with_logged_in_user.delete(
        f"/api/v1/datasets/{source_dataset_id}/relations/{relation_id}"
    )

    assert delete_response.status_code == 204

    get_after_delete = client_with_logged_in_user.get(
        f"/api/v1/datasets/{source_dataset_id}/relations"
    )
    result_after = get_after_delete.json()

    assert len(result_after) == 0


def test_delete_external_relation(
    client_with_logged_in_user,
    sample_dataset,
    default_external_relation,
):
    source_dataset_id = sample_dataset.id

    create_response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{source_dataset_id}/relations",
        json=default_external_relation,
    )
    assert create_response.status_code == 201
    relation_id = create_response.json()["id"]

    delete_response = client_with_logged_in_user.delete(
        f"/api/v1/datasets/{source_dataset_id}/relations/{relation_id}"
    )
    assert delete_response.status_code == 204

    get_response = client_with_logged_in_user.get(
        f"/api/v1/datasets/{source_dataset_id}/relations"
    )
    result = get_response.json()

    assert not any(r["id"] == relation_id for r in result)
