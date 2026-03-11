import copy

import pytest
from deepdiff import DeepDiff
from test_factory import (
    client_with_logged_in_user,
    default_dataset_json,
    sample_dataset,
)
import uuid


def test_update_dataset(client_with_logged_in_user, default_dataset_json):
    create_response = client_with_logged_in_user.post(
        "/api/v1/datasets",
        json=default_dataset_json,
    )

    updated_dataset = copy.deepcopy(default_dataset_json)

    create_response_json = create_response.json()

    actual_dataset_id = create_response_json["id"]

    updated_dataset["description"] = "new_dummy_description"
    updated_dataset["themes"] = [
        "http://publications.europa.eu/resource/authority/data-theme/HEAL"
    ]
    updated_dataset["spatial_coverages"] = [
        "http://publications.europa.eu/resource/authority/country/FRA"
    ]
    updated_dataset["applicable_legislations"] = ["GDPR"]
    updated_dataset["data_protection_types"] = [
        "statistical_confidentiality",
    ]
    updated_dataset["distributions"] = [
        {
            "languages": [
                "http://publications.europa.eu/resource/authority/language/ENG",
            ],
            "title": "Test Distribution Title",
            "description": "dummy_update",
            "download_urls": ["https://example.com/"],
            "access_urls": ["https://example.com/"],
            "file_type": "http://publications.europa.eu/resource/authority/file-type/PDF",
            "rights_statement": "http://publications.europa.eu/resource/authority/access-right/PUBLIC",
            "internal_only": True,
            "notes": None,
            "license": "no_license",
            "applicable_legislations": ["GDPR"],
            "modification_date": None,
            "release_date": None,
            "linked_schemas": [],
            "distribution_dcat_status": "Completed",
            "access_service_ids": [],
        },
        {
            "languages": [
                "http://publications.europa.eu/resource/authority/language/ENG"
            ],
            "title": "Test Distribution Title 3",
            "description": "Test Distribution Description 3",
            "download_urls": ["https://example.com/"],
            "access_urls": ["https://example.com/"],
            "file_type": "http://publications.europa.eu/resource/authority/file-type/PDF",
            "rights_statement": "http://publications.europa.eu/resource/authority/access-right/PUBLIC",
            "internal_only": False,
            "notes": None,
            "license": "no_license",
            "applicable_legislations": ["GDPR"],
            "modification_date": None,
            "release_date": None,
            "linked_schemas": [],
            "distribution_dcat_status": "Completed",
            "access_service_ids": [],
        },
    ]

    update_response = client_with_logged_in_user.put(
        f"/api/v1/datasets/{actual_dataset_id}",
        json=updated_dataset,
    )

    actual = update_response.json()

    assert update_response.status_code == 200

    assert actual["title"] == updated_dataset["title"]
    assert actual["description"] == updated_dataset["description"]
