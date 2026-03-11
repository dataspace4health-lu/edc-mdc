import json
import pytest
from deepdiff import DeepDiff
from utils.dataset_diff import DatasetDiff
import uuid
from models.dataset import DatasetStatus


def create_empty_dataset_diff_data():
    """Factory function for empty dataset data used in diff tests."""
    return {
        "title": None,
        "description": None,
        "contact_name": None,
        "publisher_name": None,
        "contact_email": None,
        "time_period_start": None,
        "time_period_end": None,
        "dataset_type": None,
        "rights_statement": None,
        "periodicity": None,
        "status": None,
        "version": None,
        "duration_of_administrative_utility": None,
        "max_typical_age": None,
        "min_typical_age": None,
        "number_of_records": None,
        "number_of_unique_individuals": None,
        "final_disposition": None,
        "creator_ids": [],
        "themes": [],
        "keywords": [],
        "spatial_coverages": [],
        "conventions": [],
        "areas_of_work": [],
        "areas_of_competence": [],
        "applicable_legislations": [],
        "distributions": [],
        "group_managers": [],
        "release_date": None,
        "modified_at": None,
        "data_protection_types": [],
        "monitoring_location": None,
        "provenance": [],
        "version_notes": [],
        "population_coverage": None,
        "code_values": [],
        "coding_systems": [],
        "languages": [],
        "landing_pages": [],
        "documentation": [],
        "conforms_to": [],
        "is_dataset_series": None,
    }


def create_sample_dataset_diff_data():
    """Factory function for populated sample dataset data used in diff tests."""
    return {
        "title": "Sample Dataset Title",
        "description": "This is a sample description for the dataset.",
        "contact_name": "John Doe",
        "publisher_name": "John Doe publisher",
        "contact_email": "johndoe@example.com",
        "time_period_start": "2021-12-31",
        "time_period_end": "2022-12-31",
        "dataset_type": "http://publications.europa.eu/resource/authority/dataset-type/TEST_DATA",
        "rights_statement": "http://publications.europa.eu/resource/authority/access-right/PUBLIC",
        "periodicity": "http://publications.europa.eu/resource/authority/frequency/ANNUAL",
        "status": DatasetStatus.DRAFT.value,
        "version": "0.0.1",
        "duration_of_administrative_utility": 3,
        "max_typical_age": 10,
        "min_typical_age": 5,
        "number_of_records": 100,
        "number_of_unique_individuals": 50,
        "final_disposition": "Destroy",
        "creator_ids": [1],
        "contact_ids": [1, 2],
        "release_date": "2022-12-31",
        "modified_at": "2022-12-31",
        "themes": ["http://publications.europa.eu/resource/authority/data-theme/ENVI"],
        "keywords": ["health"],
        "spatial_coverages": [
            "http://publications.europa.eu/resource/authority/country/LUX"
        ],
        "conventions": ["banana"],
        "areas_of_work": ["monitoring"],
        "areas_of_competence": ["bruit"],
        "applicable_legislations": ["GDPR"],
        "group_managers": [1, 2],
        "data_protection_types": ["commercial_confidentiality"],
        "monitoring_location": "Luxembourg",
        "provenance": ["Official records"],
        "version_notes": ["Initial version"],
        "population_coverage": "Adults aged 18-65 in Luxembourg",
        "code_values": ["ICD-10 Codes"],
        "coding_systems": ["https://www.wikidata.org/entity/Q9006342"],
        "languages": ["http://publications.europa.eu/resource/authority/language/FRA"],
        "landing_pages": ["https://example.com/landing_page"],
        "documentation": ["https://example.com/dataset_document"],
        "conforms_to": ["https://example.com/conforms_to"],
        "is_dataset_series": False,
    }


def create_sample_distribution_diff_data(
    title="Sample Distribution Title",
    description="This is a sample description for distribution.s",
    download_urls=None,
    access_urls=None,
    file_type="http://publications.europa.eu/resource/authority/file-type/JAR",
    languages=None,
    modification_date="2023-12-31",
    release_date="2023-12-31",
    distribution_dcat_status="Completed",
):
    """Factory function for distribution data used in diff tests."""
    if languages is None:
        languages = [
            "http://publications.europa.eu/resource/authority/language/FRA",
            "http://publications.europa.eu/resource/authority/language/ENG",
        ]
    if access_urls is None:
        access_urls = ["https://example.com/sample-distributions"]
    if download_urls is None:
        download_urls = ["https://example.com/sample-distributions"]

    return {
        "title": title,
        "description": description,
        "download_urls": download_urls,
        "access_urls": access_urls,
        "file_type": file_type,
        "rights_statement": "http://publications.europa.eu/resource/authority/access-right/PUBLIC",
        "languages": languages,
        "applicable_legislations": ["GDPR"],
        "availability": "Stable",
        "documentation": ["https://example.com/distribution_document"],
        "modification_date": modification_date,
        "release_date": release_date,
        "distribution_dcat_status": distribution_dcat_status,
    }


def test_compute_diff_for_new_dataset():
    original_data = create_empty_dataset_diff_data()

    updated_data = create_sample_dataset_diff_data()
    updated_data["distributions"] = [create_sample_distribution_diff_data()]

    diff_json = DatasetDiff.compute(original_data, updated_data)
    diffs = json.loads(diff_json)

    expected_changes = {
        "title": "Sample Dataset Title",
        "description": "This is a sample description for the dataset.",
        "contact_name": "John Doe",
        "publisher_name": "John Doe publisher",
        "contact_email": "johndoe@example.com",
        "time_period_start": "2021-12-31",
        "time_period_end": "2022-12-31",
        "dataset_type": "http://publications.europa.eu/resource/authority/dataset-type/TEST_DATA",
        "rights_statement": "http://publications.europa.eu/resource/authority/access-right/PUBLIC",
        "periodicity": "http://publications.europa.eu/resource/authority/frequency/ANNUAL",
        "status": DatasetStatus.DRAFT.value,
        "version": "0.0.1",
        "duration_of_administrative_utility": 3,
        "max_typical_age": 10,
        "min_typical_age": 5,
        "number_of_records": 100,
        "number_of_unique_individuals": 50,
        "final_disposition": "Destroy",
        "creator_ids": [1],
        "release_date": "2022-12-31",
        "modified_at": "2022-12-31",
        "data_protection_types": "commercial_confidentiality",
        "monitoring_location": "Luxembourg",
        "areas_of_competence": "bruit",
        "provenance": "Official records",
        "version_notes": "Initial version",
        "population_coverage": "Adults aged 18-65 in Luxembourg",
        "code_values": ["ICD-10 Codes"],
        "coding_systems": ["https://www.wikidata.org/entity/Q9006342"],
        "landing_pages": ["https://example.com/landing_page"],
        "documentation": ["https://example.com/dataset_document"],
        "is_dataset_series": False,
    }

    for diff in diffs:
        if diff["change_type"] == "type_changes":
            field_name = diff["field"]
            assert (
                diff["old_value"] is None
            ), f"Old value for {field_name} should be None"
            assert (
                diff["new_value"] == expected_changes[field_name]
            ), f"New value for {field_name} does not match expected"
        elif diff["change_type"] == "dictionary_item_added":
            assert diff["field"] in [
                "contact_ids",
            ], f"Field name mismatch for dictionary item added: {diff['field']}"
        elif diff["change_type"] == "values_changed":
            if diff["field"] == "themes":
                assert (
                    diff["new_value"]
                    == "http://publications.europa.eu/resource/authority/data-theme/ENVI"
                ), "Themes value changed mismatch"
            elif diff["field"] == "keywords":
                assert diff["new_value"] == "health", "Keywords value changed mismatch"
            elif diff["field"] == "spatial_coverages":
                assert (
                    diff["new_value"]
                    == "http://publications.europa.eu/resource/authority/country/LUX"
                ), "Spatial coverages value changed mismatch"
            elif diff["field"] == "applicable_legislations":
                assert (
                    diff["new_value"] == "GDPR"
                ), "applicable_legislations value changed mismatch"
            elif diff["field"] == "conventions":
                assert (
                    diff["new_value"] == "banana"
                ), "conventions value changed mismatch"
            elif diff["field"] == "areas_of_work":
                assert (
                    diff["new_value"] == "monitoring"
                ), "areas_of_work value changed mismatch"
            elif diff["field"] == "areas_of_competence":
                assert (
                    diff["new_value"] == "bruit"
                ), "areas_of_competence value changed mismatch"
            elif diff["field"] == "group_managers":
                assert (
                    diff["new_value"] == "1, 2"
                ), "group_managers value changed mismatch"
            elif diff["field"] == "contact_ids":
                assert diff["new_value"] == "1, 2", "contact_ids value changed mismatch"
            elif diff["field"] == "data_protection_types":
                assert (
                    diff["new_value"] == "commercial_confidentiality"
                ), "data_protection_types value changed mismatch"
            elif diff["field"] == "languages":
                assert (
                    diff["new_value"]
                    == "http://publications.europa.eu/resource/authority/language/FRA"
                ), "languages value changed mismatch"
            elif diff["field"] == "coding_systems":
                assert (
                    diff["new_value"] == "https://www.wikidata.org/entity/Q9006342"
                ), "coding_systems value changed mismatch"
    assert (
        len(diffs) == len(expected_changes) + 10
    ), "The number of diffs does not match expected"


def test_compute_diff_for_update_dataset():
    original_data = create_sample_dataset_diff_data()
    original_data["conforms_to"] = []
    original_data["distributions"] = [
        create_sample_distribution_diff_data(
            languages=["http://publications.europa.eu/resource/authority/language/FRA"]
        )
    ]
    # Add linked_schemas to distribution
    original_data["distributions"][0]["linked_schemas"] = []

    updated_data = {
        "title": "Updated Dataset Title",
        "description": "Updated sample description for the dataset.",
        "contact_name": "Jane Doe",
        "publisher_name": "Jane Doe Publisher",
        "contact_email": "janedoe@example.com",
        "time_period_start": "2022-01-01",
        "time_period_end": "2023-01-01",
        "dataset_type": "http://publications.europa.eu/resource/authority/dataset-type/UPDATED_TEST_DATA",
        "rights_statement": "http://publications.europa.eu/resource/authority/access-right/RESTRICTED",
        "periodicity": "http://publications.europa.eu/resource/authority/frequency/MONTHLY",
        "status": "PUBLISHED",
        "version": "0.0.2",
        "duration_of_administrative_utility": 4,
        "max_typical_age": 12,
        "min_typical_age": 6,
        "number_of_records": 150,
        "number_of_unique_individuals": 75,
        "final_disposition": "Unknown",
        "creator_ids": [2],
        "contact_ids": [4, 3],
        "release_date": "2022-12-31",
        "modified_at": "2022-12-31",
        "themes": ["http://publications.europa.eu/resource/authority/data-theme/AGRI"],
        "keywords": ["health", "wellness"],
        "group_managers": [3, 4],
        "spatial_coverages": [
            "http://publications.europa.eu/resource/authority/country/FRA"
        ],
        "conventions": ["hello"],
        "areas_of_work": ["policy_advice"],
        "areas_of_competence": ["procedures_administratives"],
        "applicable_legislations": ["GDPR", "CCPA"],
        "data_protection_types": ["statistical_confidentiality"],
        "monitoring_location": "New Location",
        "provenance": ["Gov"],
        "version_notes": ["Updated version notes"],
        "population_coverage": "Children aged 0-17 in France",
        "code_values": ["SNOMED CT Codes"],
        "coding_systems": ["https://www.wikidata.org/entity/Q5969475"],
        "languages": ["http://publications.europa.eu/resource/authority/language/ENG"],
        "landing_pages": ["https://example.com/updated_landing_page"],
        "documentation": ["https://example.com/updated_dataset_document"],
        "conforms_to": [],
        "is_dataset_series": False,
        "distributions": [
            {
                "title": "Sample Distribution Title",
                "description": "Updated description for distribution.",
                "download_urls": ["https://example.com/updated-distributions"],
                "access_urls": ["https://example.com/updated-distributions"],
                "file_type": "http://publications.europa.eu/resource/authority/file-type/ZIP",
                "rights_statement": "http://publications.europa.eu/resource/authority/access-right/RESTRICTED",
                "languages": [
                    "http://publications.europa.eu/resource/authority/language/ENG"
                ],
                "applicable_legislations": ["CCPA"],
                "availability": "Stable",
                "documentation": ["https://example.com/updated_distribution_document"],
                "modification_date": "2024-12-31",
                "release_date": "2024-12-31",
                "linked_schemas": [],
                "distribution_dcat_status": "Withdrawn",
            }
        ],
    }

    diff_json = DatasetDiff.compute(original_data, updated_data)
    diffs = json.loads(diff_json)

    expected_diffs = {
        "title": ("values_changed", "Sample Dataset Title", "Updated Dataset Title"),
        "description": (
            "values_changed",
            "This is a sample description for the dataset.",
            "Updated sample description for the dataset.",
        ),
        "contact_name": ("values_changed", "John Doe", "Jane Doe"),
        "publisher_name": (
            "values_changed",
            "John Doe publisher",
            "Jane Doe Publisher",
        ),
        "contact_email": (
            "values_changed",
            "johndoe@example.com",
            "janedoe@example.com",
        ),
        "time_period_start": ("values_changed", "2021-12-31", "2022-01-01"),
        "time_period_end": ("values_changed", "2022-12-31", "2023-01-01"),
        "dataset_type": (
            "values_changed",
            "http://publications.europa.eu/resource/authority/dataset-type/TEST_DATA",
            "http://publications.europa.eu/resource/authority/dataset-type/UPDATED_TEST_DATA",
        ),
        "rights_statement": (
            "values_changed",
            "http://publications.europa.eu/resource/authority/access-right/PUBLIC",
            "http://publications.europa.eu/resource/authority/access-right/RESTRICTED",
        ),
        "periodicity": (
            "values_changed",
            "http://publications.europa.eu/resource/authority/frequency/ANNUAL",
            "http://publications.europa.eu/resource/authority/frequency/MONTHLY",
        ),
        "status": (
            "values_changed",
            "DRAFT",
            "PUBLISHED",
        ),
        "version": (
            "values_changed",
            "0.0.1",
            "0.0.2",
        ),
        "duration_of_administrative_utility": ("values_changed", 3, 4),
        "max_typical_age": ("values_changed", 10, 12),
        "min_typical_age": ("values_changed", 5, 6),
        "number_of_records": ("values_changed", 100, 150),
        "number_of_unique_individuals": ("values_changed", 50, 75),
        "final_disposition": ("values_changed", "Destroy", "Unknown"),
        "creator_ids": (
            "values_changed",
            "1",
            "2",
        ),
        "themes": (
            "values_changed",
            "http://publications.europa.eu/resource/authority/data-theme/ENVI",
            "http://publications.europa.eu/resource/authority/data-theme/AGRI",
        ),
        "keywords": ("values_changed", "health", "health, wellness"),
        "group_managers": ("values_changed", "1, 2", "3, 4"),
        "contact_ids": ("values_changed", "1, 2", "3, 4"),
        "spatial_coverages": (
            "values_changed",
            "http://publications.europa.eu/resource/authority/country/LUX",
            "http://publications.europa.eu/resource/authority/country/FRA",
        ),
        "conventions": (
            "values_changed",
            "banana",
            "hello",
        ),
        "areas_of_work": ("values_changed", "monitoring", "policy_advice"),
        "areas_of_competence": (
            "values_changed",
            "bruit",
            "procedures_administratives",
        ),
        "applicable_legislations": ("values_changed", "GDPR", "CCPA, GDPR"),
        "data_protection_types": (
            "values_changed",
            "commercial_confidentiality",
            "statistical_confidentiality",
        ),
        "monitoring_location": ("values_changed", "Luxembourg", "New Location"),
        "provenance": ("values_changed", "Official records", "Gov"),
        "version_notes": ("values_changed", "Initial version", "Updated version notes"),
        "population_coverage": (
            "values_changed",
            "Adults aged 18-65 in Luxembourg",
            "Children aged 0-17 in France",
        ),
        "code_values": (
            "values_changed",
            "ICD-10 Codes",
            "SNOMED CT Codes",
        ),
        "coding_systems": (
            "values_changed",
            "https://www.wikidata.org/entity/Q9006342",
            "https://www.wikidata.org/entity/Q5969475",
        ),
        "languages": (
            "values_changed",
            "http://publications.europa.eu/resource/authority/language/FRA",
            "http://publications.europa.eu/resource/authority/language/ENG",
        ),
        "landing_pages": (
            "values_changed",
            "https://example.com/landing_page",
            "https://example.com/updated_landing_page",
        ),
        "documentation": (
            "values_changed",
            "https://example.com/dataset_document",
            "https://example.com/updated_dataset_document",
        ),
    }

    for diff in diffs:
        field = diff["field"]
        expected_type, expected_old_value, expected_new_value = expected_diffs[field]

        assert diff["change_type"] == expected_type, f"Change type mismatch for {field}"
        assert (
            diff["old_value"] == expected_old_value
        ), f"Old value mismatch for {field}"
        assert (
            diff["new_value"] == expected_new_value
        ), f"New value mismatch for {field}"

    assert len(diffs) == len(
        expected_diffs
    ), "The number of diffs does not match expected"


def test_compute_diff_for_new_distribution():
    dist1 = create_sample_distribution_diff_data(
        title="Title 1",
        description="Description 1",
        download_urls=["https://example.com/1"],
        access_urls=["https://example.com/1"],
        file_type="http://publications.europa.eu/resource/authority/file-type/JAR",
        modification_date=None,
        release_date=None,
    )
    dist1["rights_statement"] = (
        "http://publications.europa.eu/resource/authority/access-right/RESTRICTED"
    )
    del dist1["modification_date"]
    del dist1["release_date"]

    original_data = {
        "title": "Dataset Title",
        "distributions": [dist1],
    }

    dist2 = create_sample_distribution_diff_data(
        title="Title 2",
        description="Description 2",
        download_urls=["https://example.com/2"],
        access_urls=["https://example.com/2"],
        file_type="http://publications.europa.eu/resource/authority/file-type/CSV",
        languages=["http://publications.europa.eu/resource/authority/language/FRA"],
        modification_date="2024-12-31",
        release_date="2024-12-31",
        distribution_dcat_status="Withdrawn",
    )
    dist2["rights_statement"] = (
        "http://publications.europa.eu/resource/authority/access-right/RESTRICTED"
    )

    dist1_updated = dist1.copy()
    dist1_updated["modification_date"] = "2024-12-31"
    dist1_updated["release_date"] = "2024-12-31"
    dist1_updated["distribution_dcat_status"] = "Withdrawn"

    updated_data = {
        "title": "Dataset Title",
        "distributions": [dist2, dist1_updated],
    }

    diff_json = DatasetDiff.compute(original_data, updated_data)
    diffs = json.loads(diff_json)

    assert diffs == []


def test_compute_diff_for_remove_distribution():
    dist1 = create_sample_distribution_diff_data(
        title="Title 1",
        description="Description 1",
        download_urls=["https://example.com/1"],
        access_urls=["https://example.com/1"],
        file_type="http://publications.europa.eu/resource/authority/file-type/JAR",
        modification_date=None,
        release_date=None,
    )
    dist1["rights_statement"] = (
        "http://publications.europa.eu/resource/authority/access-right/RESTRICTED"
    )
    dist1["languages"] = [
        "http://publications.europa.eu/resource/authority/language/FRA",
        "http://publications.europa.eu/resource/authority/language/ENG",
    ]

    dist2 = create_sample_distribution_diff_data(
        title="Title 2",
        description="Description 2",
        download_urls=["https://example.com/2"],
        access_urls=["https://example.com/2"],
        file_type="http://publications.europa.eu/resource/authority/file-type/CSV",
        languages=["http://publications.europa.eu/resource/authority/language/FRA"],
        modification_date=None,
        release_date=None,
    )
    dist2["rights_statement"] = (
        "http://publications.europa.eu/resource/authority/access-right/RESTRICTED"
    )

    original_data = {
        "title": "Dataset Title",
        "distributions": [dist2, dist1],
    }

    dist1_updated = dist1.copy()
    dist1_updated["documentation"] = [
        "https://example.com/updated_distribution_document"
    ]
    dist1_updated["distribution_dcat_status"] = "Withdrawn"

    updated_data = {
        "title": "Dataset Title",
        "distributions": [dist1_updated],
    }

    diff_json = DatasetDiff.compute(original_data, updated_data)
    diffs = json.loads(diff_json)

    assert diffs == []


def test_compute_diff_for_update_distribution():
    dist_original = create_sample_distribution_diff_data(
        title="Title",
        description="Description",
        download_urls=["https://example.com/1"],
        access_urls=["https://example.com/1"],
        file_type="http://publications.europa.eu/resource/authority/file-type/JAR",
        languages=["http://publications.europa.eu/resource/authority/language/FRA"],
        modification_date=None,
        release_date=None,
    )
    dist_original["rights_statement"] = (
        "http://publications.europa.eu/resource/authority/access-right/RESTRICTED"
    )

    original_data = {
        "title": "Dataset Title",
        "distributions": [dist_original],
    }

    dist_updated = create_sample_distribution_diff_data(
        title="Title",
        description="Updated Description",
        download_urls=["https://example.com/2"],
        access_urls=["https://example.com/2"],
        file_type="http://publications.europa.eu/resource/authority/file-type/CSV",
        modification_date="2024-12-31",
        release_date="2024-12-31",
        distribution_dcat_status="Withdrawn",
    )
    dist_updated["rights_statement"] = (
        "http://publications.europa.eu/resource/authority/access-right/RESTRICTED"
    )
    dist_updated["documentation"] = [
        "https://example.com/updated_distribution_document"
    ]

    updated_data = {
        "title": "Dataset Title",
        "distributions": [dist_updated],
    }

    diff_json = DatasetDiff.compute(original_data, updated_data)
    diffs = json.loads(diff_json)

    assert diffs == []
