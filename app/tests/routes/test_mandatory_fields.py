import copy

import pytest
from deepdiff import DeepDiff
from test_factory import (
    client_with_logged_in_user,
    default_dataset_json,
    default_expected_json,
    sample_dataset,
)
import uuid


def test_create_dataset(
    client_with_logged_in_user, default_dataset_json, default_expected_json
):
    dataset = copy.deepcopy(default_dataset_json)
    dataset["author_name"] = "system"

    response = client_with_logged_in_user.post("/api/v1/datasets", json=dataset)
    assert response.status_code == 200

    actual = response.json()
    expected_json = copy.deepcopy(default_expected_json)

    expected_json["author_name"] = actual.get("author_name", "system")
    expected_json["contact_names"] = actual["contact_names"]
    expected_json["contact_emails"] = actual["contact_emails"]
    expected_json["health_categories"] = actual.get("health_categories", [])
    expected_json["health_themes"] = actual.get("health_themes", [])
    # Retention period fields will be None when created through API if not explicitly set
    expected_json["retention_period_start"] = actual.get("retention_period_start")
    expected_json["retention_period_end"] = actual.get("retention_period_end")

    # Distributions are no longer created via dataset creation endpoint, so don't compare them
    expected_json["distributions"] = []

    assert not DeepDiff(
        expected_json,
        actual,
        ignore_order=True,
        exclude_regex_paths=[
            "id",
            "submitted_at",
            "released_at",
            "dataset_id",
            "status_triggers",
            "source_relations",
            "total_relations",
            "group_manager_names",
            "qualified_attributions",
            "qualified_attributions_names",
            "access_services",
            "has_version",
            "code_values",
        ],
    )


def test_time_period_end_is_not_mandatory(
    client_with_logged_in_user, default_dataset_json
):
    dataset = copy.deepcopy(default_dataset_json)
    del dataset["time_period_end"]
    response = client_with_logged_in_user.post(
        "/api/v1/datasets",
        json=dataset,
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "mandatory_field",
    [
        "title",
        "description",
        "publisher_id",
        "rights_statement",
    ],
)
def test_mandatory_field_in_datasets(
    client_with_logged_in_user, default_dataset_json, mandatory_field
):
    dataset = copy.deepcopy(default_dataset_json)
    del dataset[mandatory_field]
    response = client_with_logged_in_user.post(
        "/api/v1/datasets",
        json=dataset,
    )

    assert response.status_code == 422

    validation_array = response.json()["detail"]
    validation = validation_array[0]

    assert len(validation_array) == 1
    assert validation["type"] == "missing"
    assert mandatory_field in validation["loc"]


@pytest.mark.parametrize(
    "collection",
    [
        "dataset_types",
        "themes",
    ],
)
def test_not_empty_collection(
    client_with_logged_in_user, default_dataset_json, collection
):
    dataset = copy.deepcopy(default_dataset_json)
    dataset[collection] = []

    response = client_with_logged_in_user.post(
        "/api/v1/datasets",
        json=dataset,
    )

    assert response.status_code == 422

    validation_array = response.json()["detail"]
    validation = validation_array[0]

    assert len(validation_array) == 1
    assert validation["type"] == "too_short"
    assert collection in validation["loc"]


@pytest.mark.parametrize(
    "mandatory_field",
    ["languages"],
)
def test_mandatory_field_in_distributions(
    client_with_logged_in_user, default_dataset_json, mandatory_field
):
    dataset = copy.deepcopy(default_dataset_json)
    distribution = dataset["distributions"][0]
    del distribution[mandatory_field]

    response = client_with_logged_in_user.post(
        "/api/v1/datasets",
        json=dataset,
    )

    assert response.status_code == 422

    validation_array = response.json()["detail"]
    validation = validation_array[0]

    assert len(validation_array) == 1
    assert validation["type"] == "missing"
    assert mandatory_field in validation["loc"]


def test_download_urls_in_distributions_is_valid(
    client_with_logged_in_user, default_dataset_json
):
    dataset = copy.deepcopy(default_dataset_json)
    distribution = dataset["distributions"][0]
    distribution["download_urls"] = ["blablabla"]

    response = client_with_logged_in_user.post(
        "/api/v1/datasets",
        json=dataset,
    )

    assert response.status_code == 422

    validation_array = response.json()["detail"]
    validation = validation_array[0]

    assert len(validation_array) == 1
    assert validation["type"] == "url_parsing"
    assert "download_urls" in validation["loc"]


def test_access_urls_in_distributions_is_valid(
    client_with_logged_in_user, default_dataset_json
):
    dataset = copy.deepcopy(default_dataset_json)
    distribution = dataset["distributions"][0]
    distribution["access_urls"] = ["blablabla"]

    response = client_with_logged_in_user.post(
        "/api/v1/datasets",
        json=dataset,
    )

    assert response.status_code == 422

    validation_array = response.json()["detail"]
    validation = validation_array[0]

    assert len(validation_array) == 1
    assert validation["type"] == "url_parsing"
    assert "access_urls" in validation["loc"]


def test_download_urls_is_not_mandatory(
    client_with_logged_in_user, default_dataset_json
):
    dataset = copy.deepcopy(default_dataset_json)
    distribution = dataset["distributions"][0]
    del distribution["download_urls"]

    del dataset["time_period_end"]
    response = client_with_logged_in_user.post(
        "/api/v1/datasets",
        json=dataset,
    )

    assert response.status_code == 200


def test_access_urls_is_mandatory(client_with_logged_in_user, default_dataset_json):
    dataset = copy.deepcopy(default_dataset_json)
    distribution = dataset["distributions"][0]
    del distribution["access_urls"]

    response = client_with_logged_in_user.post(
        "/api/v1/datasets",
        json=dataset,
    )

    assert response.status_code == 422

    validation_array = response.json()["detail"]
    validation = validation_array[0]

    assert len(validation_array) == 1
    assert validation["type"] == "missing"
    assert "access_urls" in validation["loc"]


def test_notes_is_not_mandatory(client_with_logged_in_user, default_dataset_json):
    dataset = copy.deepcopy(default_dataset_json)
    del dataset["notes"]
    response = client_with_logged_in_user.post(
        "/api/v1/datasets",
        json=dataset,
    )

    assert response.status_code == 200


def test_description_is_not_mandatory_in_distributions(
    client_with_logged_in_user, default_dataset_json
):
    dataset = copy.deepcopy(default_dataset_json)
    distribution = dataset["distributions"][0]
    del distribution["description"]

    response = client_with_logged_in_user.post(
        "/api/v1/datasets",
        json=dataset,
    )

    assert response.status_code == 200
