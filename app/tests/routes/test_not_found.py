from test_factory import (
    client_with_logged_in_user,
    default_dataset_json,
    sample_dataset,
)
from datetime import date
import uuid


def test_not_found_get_dataset_in_datasets_route(client_with_logged_in_user):
    response = client_with_logged_in_user.get("/api/v1/datasets/9999")
    actual = response.json()["detail"]

    assert response.status_code == 404
    assert actual == "Dataset[9999] not found"


def test_not_found_put_dataset_in_datasets_route(
    client_with_logged_in_user, default_dataset_json
):
    response = client_with_logged_in_user.put(
        "/api/v1/datasets/9999", json=default_dataset_json
    )
    actual = response.json()["detail"]

    assert response.status_code == 404
