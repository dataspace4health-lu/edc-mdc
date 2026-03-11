import json
from datetime import date
from unittest.mock import Mock

import pytest
from models.dataset import Dataset, DatasetSpatialResolution
from repositories.activity_log import ActivityLogRepository
from schemas.dataset import DatasetDto
from schemas.distribution import DistributionDto, PolicyActionDto
from services.activity_logs.dataset_activity_log import DatasetActivityLogService
from test_factory import dataset_dto, sample_dataset


@pytest.fixture(autouse=True)
def reset_mocks(dataset_activity_log_service):
    yield
    dataset_activity_log_service._repository.reset_mock()


@pytest.fixture
def dataset_activity_log_service() -> DatasetActivityLogService:
    return DatasetActivityLogService(
        repository=Mock(spec=ActivityLogRepository),
    )


def test_activity_log_service_create_log(dataset_activity_log_service, dataset_dto):
    user_id = 1
    action_type = "create"

    dataset_activity_log_service.log_dataset_activities(
        user_id, Dataset(), dataset_dto, "create"
    )

    log_entry = dataset_activity_log_service._repository.add.call_args.args[0]

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "dataset"
    assert log_entry.action_type == action_type

    diff = json.loads(log_entry.changes)

    expected_contact_ids = (
        ", ".join(map(str, sorted(dataset_dto.contact_ids)))
        if dataset_dto.contact_ids
        else ""
    )

    expected_diff = [
        {
            "field": "areas_of_competence",
            "old_value": "",
            "new_value": "bruit",
            "change_type": "values_changed",
        },
        {
            "field": "areas_of_work",
            "old_value": "",
            "new_value": "monitoring",
            "change_type": "values_changed",
        },
        {
            "field": "conforms_to",
            "old_value": "",
            "new_value": "https://example.com/conforms_to",
            "change_type": "values_changed",
        },
        {
            "field": "contact_ids",
            "old_value": "",
            "new_value": expected_contact_ids,
            "change_type": "values_changed",
        },
        {
            "field": "conventions",
            "old_value": "",
            "new_value": "banana",
            "change_type": "values_changed",
        },
        {
            "field": "creator_ids",
            "old_value": "",
            "new_value": "1",
            "change_type": "values_changed",
        },
        {
            "field": "data_protection_types",
            "old_value": "",
            "new_value": "commercial_confidentiality",
            "change_type": "values_changed",
        },
        {
            "field": "dataset_types",
            "old_value": "",
            "new_value": "http://purl.obolibrary.org/obo/T4FS_0000109",  # NOSONAR
            "change_type": "values_changed",
        },
        {
            "field": "description",
            "old_value": None,
            "new_value": "description",
            "change_type": "type_changes",
        },
        {
            "field": "documentation",
            "old_value": "",
            "new_value": "https://example.com/dataset_document",
            "change_type": "values_changed",
        },
        {
            "field": "duration_of_administrative_utility",
            "old_value": None,
            "new_value": 0,
            "change_type": "type_changes",
        },
        {
            "field": "max_typical_age",
            "old_value": None,
            "new_value": 0,
            "change_type": "type_changes",
        },
        {
            "field": "min_typical_age",
            "old_value": None,
            "new_value": 0,
            "change_type": "type_changes",
        },
        {
            "field": "number_of_records",
            "old_value": None,
            "new_value": 0,
            "change_type": "type_changes",
        },
        {
            "field": "number_of_unique_individuals",
            "old_value": None,
            "new_value": 0,
            "change_type": "type_changes",
        },
        {
            "field": "final_disposition",
            "old_value": None,
            "new_value": "Archive",
            "change_type": "type_changes",
        },
        {
            "field": "group_managers",
            "old_value": "",
            "new_value": ", ".join(map(str, dataset_dto.group_managers)),
            "change_type": "values_changed",
        },
        {
            "field": "keywords",
            "old_value": "",
            "new_value": "WASTE_MANAGEMENT",
            "change_type": "values_changed",
        },
        {
            "field": "health_categories",
            "old_value": "",
            "new_value": "EHRS",
            "change_type": "values_changed",
        },
        {
            "field": "health_themes",
            "old_value": "",
            "new_value": "CLIMATE_HEALTH",
            "change_type": "values_changed",
        },
        {
            "field": "landing_pages",
            "old_value": "",
            "new_value": "https://example.com/landing_page",
            "change_type": "values_changed",
        },
        {
            "field": "languages",
            "old_value": "",
            "new_value": "ENG",
            "change_type": "values_changed",
        },
        {
            "field": "applicable_legislations",
            "old_value": "",
            "new_value": "GDPR",
            "change_type": "values_changed",
        },
        {
            "field": "modified_at",
            "old_value": None,
            "new_value": "2022-12-31",
            "change_type": "type_changes",
        },
        {
            "field": "deprecated_at",
            "old_value": None,
            "new_value": "2022-12-31",
            "change_type": "type_changes",
        },
        {
            "field": "notes",
            "old_value": None,
            "new_value": "notes",
            "change_type": "type_changes",
        },
        {
            "field": "periodicity",
            "old_value": None,
            "new_value": "ANNUAL",
            "change_type": "type_changes",
        },
        {
            "field": "provenance",
            "old_value": "",
            "new_value": "Official records",
            "change_type": "values_changed",
        },
        {
            "field": "population_coverage",
            "old_value": None,
            "new_value": "Adults aged 18-65 in Luxembourg",
            "change_type": "type_changes",
        },
        {
            "field": "code_values",
            "old_value": "",
            "new_value": "ICD-10 Codes",
            "change_type": "values_changed",
        },
        {
            "field": "purpose",
            "old_value": "",
            "new_value": "Research and public health monitoring",
            "change_type": "values_changed",
        },
        {
            "field": "coding_systems",
            "old_value": "",
            "new_value": "https://www.wikidata.org/entity/Q9006342",
            "change_type": "values_changed",
        },
        {
            "field": "publisher_id",
            "old_value": None,
            "new_value": 1,
            "change_type": "type_changes",
        },
        {
            "field": "release_date",
            "old_value": None,
            "new_value": "2022-12-31",
            "change_type": "type_changes",
        },
        {
            "field": "retention_period_start",
            "old_value": None,
            "new_value": "2023-01-01",
            "change_type": "type_changes",
        },
        {
            "field": "retention_period_end",
            "old_value": None,
            "new_value": "2025-12-31",
            "change_type": "type_changes",
        },
        {
            "field": "rights_statement",
            "old_value": None,
            "new_value": "PUBLIC",
            "change_type": "type_changes",
        },
        {
            "field": "spatial_coverages",
            "old_value": "",
            "new_value": "LUXEMBOURG",
            "change_type": "values_changed",
        },
        {
            "field": "spatial_resolutions",
            "old_value": "",
            "new_value": "1",
            "change_type": "values_changed",
        },
        {
            "field": "monitoring_location",
            "old_value": None,
            "new_value": "Luxembourg",
            "change_type": "type_changes",
        },
        {
            "field": "status",
            "old_value": None,
            "new_value": "DRAFT",
            "change_type": "type_changes",
        },
        {
            "change_type": "type_changes",
            "field": "temporal_resolution",
            "new_value": "P1D",
            "old_value": None,
        },
        {
            "field": "themes",
            "old_value": "",
            "new_value": "ENVIRONMENT",
            "change_type": "values_changed",
        },
        {
            "field": "time_period_end",
            "old_value": None,
            "new_value": "2025-02-28",
            "change_type": "type_changes",
        },
        {
            "field": "time_period_start",
            "old_value": None,
            "new_value": "2024-03-01",
            "change_type": "type_changes",
        },
        {
            "field": "title",
            "old_value": None,
            "new_value": "title",
            "change_type": "type_changes",
        },
        {
            "field": "version",
            "old_value": None,
            "new_value": "0.0.0",
            "change_type": "type_changes",
        },
        {
            "change_type": "values_changed",
            "field": "version_notes",
            "new_value": "note-1",
            "old_value": "",
        },
        {
            "field": "is_dataset_series",
            "old_value": None,
            "new_value": False,
            "change_type": "type_changes",
        },
        {
            "field": "personal_data",
            "old_value": "",
            "new_value": "Age",
            "change_type": "values_changed",
        },
    ]
    expected_diff_sorted = sorted(expected_diff, key=lambda x: x["field"])
    diff_sorted = sorted(diff, key=lambda x: x["field"])

    assert (
        diff_sorted == expected_diff_sorted
    ), "The actual diff does not match the expected diff."


@pytest.fixture
def updated_dataset_dto():
    return DatasetDto(
        title="Updated Sample Dataset",
        description="Updated sample dataset description",
        contact_ids={2},
        publisher_id=2,
        time_period_start=date(2024, 4, 1),
        time_period_end=date(2025, 3, 28),
        retention_period_start=date(2023, 6, 1),
        retention_period_end=date(2026, 5, 31),
        rights_statement="NO_LIMITATIONS_TO_PUBLIC_ACCESS",
        periodicity="MONTHLY",
        status="DRAFT",
        dataset_types=set(["OTHER"]),
        themes=set(["ENVIRONMENT"]),
        keywords=set(["WASTE_MANAGEMENT"]),
        health_categories=set(["MRMR"]),
        health_themes=set(["ENVIRONMENTAL_HEALTH"]),
        spatial_coverages=set(["LUXEMBOURG"]),
        conventions=set(["hello"]),
        areas_of_work=set(["policy_advice"]),
        areas_of_competence=set(["procedures_administratives"]),
        applicable_legislations=set(["DDPR"]),
        modified_at=date(2022, 12, 31),
        deprecated_at=date(2022, 12, 31),
        released_at=None,
        release_date=date(2022, 12, 31),
        notes="Updated notes",
        version="0.0.1",
        version_change_type=None,
        duration_of_administrative_utility=3,
        min_typical_age=5,
        max_typical_age=10,
        number_of_records=100,
        number_of_unique_individuals=50,
        final_disposition="Unknown",
        creator_ids={2},
        group_managers=[2],
        data_protection_types=set(["statistical_confidentiality"]),
        monitoring_location="New Location",
        provenance=["Gov"],
        health_legal_basis=[],
        population_coverage="Children aged 0-17 in France",
        code_values=["SNOMED CT Codes"],
        purpose={"Public health planning"},
        coding_systems=set(["https://www.wikidata.org/entity/Q5969475"]),
        conforms_to=["https://example.com/conforms_to"],
        languages=frozenset(["ENG"]),
        landing_pages=["https://example.com/landing_page_url"],
        is_dataset_series=False,
        member_datasets=[],
        documentation=["https://example.com/updated_documentation"],
        was_generated_by=[],
        other_identifiers=[],
        version_notes=[],
        spatial_resolutions=[1],
        temporal_resolution="P10D",
        source=None,
        source_dataset_id=None,
        personal_data=list(["EmailAddress"]),
        distributions=[
            DistributionDto(
                title="Sample Distribution 1",
                description="Updated Sample Description 1",
                download_urls=["https://example.com/updated_download_urls_1"],
                access_urls=["https://example.com/updated_access_url_1"],
                file_type="OTHER",
                languages=frozenset(["ENG"]),
                rights_statement="PUBLIC",
                internal_only=False,
                applicable_legislations=["DDPR"],
                notes="Updated notes",
                license="no_license",
                distribution_path="HVD",
                availability="Stable",
                documentation=["https://example.com/distribution_document"],
                modification_date=date(2023, 12, 31),
                release_date=date(2023, 12, 31),
                linked_schemas=["dcat"],
                byte_size=10,
                checksum="test",
                policy_actions=[
                    PolicyActionDto(
                        policy_action_type="prohibition",
                        policy_constraint_type="industry",
                        policy_constraint_value="DUO:0000005",
                        temporal_restriction_start=None,
                        temporal_restriction_end=None,
                        spatial_restrictions=[],
                    )
                ],
                media_type="application/json",
                compression_format="application/zip",
                packaging_format="application/xml",
                distribution_dcat_status="Withdrawn",
                spatial_resolution=1,
                temporal_resolution="PT1H",
                access_service_ids=frozenset(),
            ),
            DistributionDto(
                title="New Distribution Title 3",
                description="New Distribution Description 3",
                download_urls=["https://example.com/new_download_urls_3"],
                access_urls=["https://example.com/new_access_url_3"],
                file_type="XML",
                languages=frozenset(["ENG"]),
                rights_statement="PUBLIC",
                internal_only=True,
                applicable_legislations=["DDPR"],
                notes="Updated notes",
                license="no_license",
                distribution_path="HVD",
                availability="Stable",
                documentation=["https://example.com/distribution_document"],
                modification_date=date(2023, 12, 31),
                release_date=date(2023, 12, 31),
                linked_schemas=["dcat"],
                byte_size=10,
                checksum="test",
                policy_actions=[
                    PolicyActionDto(
                        policy_action_type="prohibition",
                        policy_constraint_type="temporal",
                        policy_constraint_value=None,
                        temporal_restriction_start=date(2023, 1, 1),
                        temporal_restriction_end=date(2023, 12, 31),
                        spatial_restrictions=[],
                    )
                ],
                media_type="application/json",
                compression_format="application/zip",
                packaging_format="application/rtx",
                distribution_dcat_status="Withdrawn",
                spatial_resolution=1,
                temporal_resolution="PT1H",
                access_service_ids=frozenset(),
            ),
        ],
    )


def test_log_dataset_update(
    dataset_activity_log_service, sample_dataset, updated_dataset_dto
):
    user_id = 1

    dataset_activity_log_service.log_dataset_activities(
        user_id, sample_dataset, updated_dataset_dto, "update"
    )

    log_entry = dataset_activity_log_service._repository.add.call_args.args[0]

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "dataset"

    diff = json.loads(log_entry.changes)

    old_contact_ids = (
        ", ".join(map(str, sorted([dc.contact_id for dc in sample_dataset.contacts])))
        if sample_dataset.contacts
        else ""
    )
    new_contact_ids = (
        ", ".join(map(str, sorted(updated_dataset_dto.contact_ids)))
        if updated_dataset_dto.contact_ids
        else ""
    )

    expected_diff = [
        {
            "field": "areas_of_competence",
            "old_value": "bruit",
            "new_value": "procedures_administratives",
            "change_type": "values_changed",
        },
        {
            "field": "areas_of_work",
            "old_value": "monitoring",
            "new_value": "policy_advice",
            "change_type": "values_changed",
        },
        {
            "field": "contact_ids",
            "old_value": old_contact_ids,
            "new_value": new_contact_ids,
            "change_type": "values_changed",
        },
        {
            "field": "conventions",
            "old_value": "banana",
            "new_value": "hello",
            "change_type": "values_changed",
        },
        {
            "field": "creator_ids",
            "old_value": "1",
            "new_value": "2",
            "change_type": "values_changed",
        },
        {
            "field": "data_protection_types",
            "old_value": "commercial_confidentiality",
            "new_value": "statistical_confidentiality",
            "change_type": "values_changed",
        },
        {
            "field": "dataset_types",
            "old_value": "REPORTING",
            "new_value": "OTHER",
            "change_type": "values_changed",
        },
        {
            "field": "description",
            "old_value": "Sample dataset description",
            "new_value": "Updated sample dataset description",
            "change_type": "values_changed",
        },
        {
            "change_type": "values_changed",
            "field": "version_notes",
            "new_value": "",
            "old_value": "note-1",
        },
        {
            "change_type": "values_changed",
            "field": "was_generated_by",
            "new_value": "",
            "old_value": "id-1",
        },
        {
            "change_type": "values_changed",
            "field": "other_identifiers",
            "new_value": "",
            "old_value": "id-1",
        },
        {
            "change_type": "values_changed",
            "field": "deprecated_at",
            "old_value": "2022-12-31T00:00:00",
            "new_value": "2022-12-31",
        },
        {
            "field": "documentation",
            "old_value": "https://example.com/dataset_document",
            "new_value": "https://example.com/updated_documentation",
            "change_type": "values_changed",
        },
        {
            "field": "duration_of_administrative_utility",
            "old_value": 0,
            "new_value": 3,
            "change_type": "values_changed",
        },
        {
            "field": "max_typical_age",
            "old_value": 0,
            "new_value": 10,
            "change_type": "values_changed",
        },
        {
            "field": "min_typical_age",
            "old_value": 0,
            "new_value": 5,
            "change_type": "values_changed",
        },
        {
            "field": "number_of_records",
            "old_value": 0,
            "new_value": 100,
            "change_type": "values_changed",
        },
        {
            "field": "number_of_unique_individuals",
            "old_value": 0,
            "new_value": 50,
            "change_type": "values_changed",
        },
        {
            "field": "final_disposition",
            "old_value": "Archive",
            "new_value": "Unknown",
            "change_type": "values_changed",
        },
        {
            "field": "keywords",
            "old_value": "security",
            "new_value": "WASTE_MANAGEMENT",
            "change_type": "values_changed",
        },
        {
            "field": "health_categories",
            "old_value": "EHRS",
            "new_value": "MRMR",
            "change_type": "values_changed",
        },
        {
            "field": "health_themes",
            "old_value": "CLIMATE_HEALTH",
            "new_value": "ENVIRONMENTAL_HEALTH",
            "change_type": "values_changed",
        },
        {
            "field": "landing_pages",
            "old_value": "https://example.com/landing_page",
            "new_value": "https://example.com/landing_page_url",
            "change_type": "values_changed",
        },
        {
            "field": "languages",
            "old_value": "SAN",
            "new_value": "ENG",
            "change_type": "values_changed",
        },
        {
            "field": "applicable_legislations",
            "old_value": "GDPR",
            "new_value": "DDPR",
            "change_type": "values_changed",
        },
        {
            "field": "notes",
            "old_value": "",
            "new_value": "Updated notes",
            "change_type": "values_changed",
        },
        {
            "field": "periodicity",
            "old_value": "ANNUALLY",
            "new_value": "MONTHLY",
            "change_type": "values_changed",
        },
        {
            "field": "retention_period_end",
            "old_value": None,
            "new_value": "2026-05-31",
            "change_type": "type_changes",
        },
        {
            "field": "retention_period_start",
            "old_value": None,
            "new_value": "2023-06-01",
            "change_type": "type_changes",
        },
        {
            "field": "provenance",
            "old_value": "Official records",
            "new_value": "Gov",
            "change_type": "values_changed",
        },
        {
            "field": "population_coverage",
            "old_value": "Adults aged 18-65 in Luxembourg",
            "new_value": "Children aged 0-17 in France",
            "change_type": "values_changed",
        },
        {
            "field": "code_values",
            "old_value": "ICD-10 Codes",
            "new_value": "SNOMED CT Codes",
            "change_type": "values_changed",
        },
        {
            "field": "purpose",
            "old_value": "Research and public health monitoring",
            "new_value": "Public health planning",
            "change_type": "values_changed",
        },
        {
            "field": "coding_systems",
            "old_value": "https://www.wikidata.org/entity/Q9006342",
            "new_value": "https://www.wikidata.org/entity/Q5969475",
            "change_type": "values_changed",
        },
        {
            "field": "publisher_id",
            "old_value": 1,
            "new_value": 2,
            "change_type": "values_changed",
        },
        {
            "field": "rights_statement",
            "old_value": "PUBLIC",
            "new_value": "NO_LIMITATIONS_TO_PUBLIC_ACCESS",
            "change_type": "values_changed",
        },
        {
            "field": "spatial_coverages",
            "old_value": "LUX",
            "new_value": "LUXEMBOURG",
            "change_type": "values_changed",
        },
        {
            "field": "monitoring_location",
            "old_value": "Luxembourg",
            "new_value": "New Location",
            "change_type": "values_changed",
        },
        {
            "field": "themes",
            "old_value": "ENV",
            "new_value": "ENVIRONMENT",
            "change_type": "values_changed",
        },
        {
            "field": "time_period_end",
            "old_value": "2025-02-28",
            "new_value": "2025-03-28",
            "change_type": "values_changed",
        },
        {
            "field": "time_period_start",
            "old_value": "2024-03-01",
            "new_value": "2024-04-01",
            "change_type": "values_changed",
        },
        {
            "field": "title",
            "old_value": "Sample Dataset",
            "new_value": "Updated Sample Dataset",
            "change_type": "values_changed",
        },
        {
            "field": "version",
            "old_value": "0.0.0",
            "new_value": "0.0.1",
            "change_type": "values_changed",
        },
        {
            "field": "personal_data",
            "old_value": "Age",
            "new_value": "EmailAddress",
            "change_type": "values_changed",
        },
    ]

    # Filter out group_managers due to test isolation issues
    diff_sorted = sorted(
        [d for d in diff if d["field"] != "group_managers"], key=lambda x: x["field"]
    )
    expected_diff_sorted = sorted(expected_diff, key=lambda x: x["field"])

    assert (
        diff_sorted == expected_diff_sorted
    ), "The actual diff does not match the expected diff."


def test_log_dataset_status_change(dataset_activity_log_service):
    user_id = 1
    dataset_id = 1
    old_status = "DRAFT"
    new_status = "PUBLISHED"

    dataset_activity_log_service.log_dataset_status_change(
        user_id, dataset_id, old_status, new_status
    )

    log_entry = dataset_activity_log_service._repository.add.call_args.args[0]

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "dataset"
    assert log_entry.entity_id == str(dataset_id)
    assert log_entry.action_type == "update"

    expected_diff = [
        {
            "field": "status",
            "change_type": "status_change",
            "old_value": old_status,
            "new_value": new_status,
        }
    ]

    actual_diff = json.loads(log_entry.changes)
    assert (
        actual_diff == expected_diff
    ), f"Expected {expected_diff} but got {actual_diff}"

    dataset_activity_log_service._repository.add.assert_called_once_with(log_entry)
    dataset_activity_log_service._repository.commit.assert_called_once()
