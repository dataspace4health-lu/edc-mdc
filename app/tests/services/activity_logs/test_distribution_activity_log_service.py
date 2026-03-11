import json
from unittest.mock import Mock
import pytest
from repositories.activity_log import ActivityLogRepository
from services.activity_logs.distribution_activity_log import (
    DistributionActivityLogService,
)


@pytest.fixture
def service() -> DistributionActivityLogService:
    return DistributionActivityLogService(
        repository=Mock(spec=ActivityLogRepository),
    )


def test_log_distribution_created_with_title(service):
    user_id = 1
    dataset_id = 100
    distribution_id = 200
    distribution_title = "CSV Distribution"

    service.log_distribution_created(
        user_id=user_id,
        dataset_id=dataset_id,
        distribution_id=distribution_id,
        distribution_title=distribution_title,
    )

    log_entry = service._repository.add.call_args.args[0]

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "dataset"
    assert log_entry.entity_id == str(dataset_id)
    assert log_entry.action_type == "update"

    expected_changes = [
        {
            "field": "distribution",
            "old_value": None,
            "new_value": {
                "dataset_id": dataset_id,
                "distribution_id": distribution_id,
                "distribution_title": distribution_title,
            },
            "change_type": "created",
        }
    ]

    actual_changes = json.loads(log_entry.changes)
    assert (
        actual_changes == expected_changes
    ), f"Expected {expected_changes} but got {actual_changes}"

    service._repository.add.assert_called_once_with(log_entry)
    service._repository.commit.assert_called_once()


def test_log_distribution_created_without_title(service):
    user_id = 1
    dataset_id = 100
    distribution_id = 200

    service.log_distribution_created(
        user_id=user_id,
        dataset_id=dataset_id,
        distribution_id=distribution_id,
        distribution_title=None,
    )

    log_entry = service._repository.add.call_args.args[0]

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "dataset"
    assert log_entry.entity_id == str(dataset_id)
    assert log_entry.action_type == "update"

    expected_changes = [
        {
            "field": "distribution",
            "old_value": None,
            "new_value": {
                "dataset_id": dataset_id,
                "distribution_id": distribution_id,
                "distribution_title": None,
            },
            "change_type": "created",
        }
    ]

    actual_changes = json.loads(log_entry.changes)
    assert (
        actual_changes == expected_changes
    ), f"Expected {expected_changes} but got {actual_changes}"

    service._repository.add.assert_called_once_with(log_entry)
    service._repository.commit.assert_called_once()


def test_log_distribution_updated_with_title_change(service):
    user_id = 1
    dataset_id = 100
    distribution_id = 200
    old_title = "Old CSV Distribution"
    new_title = "New CSV Distribution"

    old_distribution = {
        "title": old_title,
        "download_urls": ["http://old.example.com"],
        "languages": ["ENG"],
    }
    new_distribution = {
        "title": new_title,
        "download_urls": ["http://new.example.com"],
        "languages": ["ENG", "FRA"],
    }

    service.log_distribution_updated(
        user_id=user_id,
        dataset_id=dataset_id,
        old_distribution=old_distribution,
        new_distribution=new_distribution,
        distribution_title=new_title,
    )

    log_entry = service._repository.add.call_args.args[0]

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "dataset"
    assert log_entry.entity_id == str(dataset_id)
    assert log_entry.action_type == "update"

    expected_changes = [
        {
            "field": f"distributions.{new_title}.title",
            "old_value": old_title,
            "new_value": new_title,
            "change_type": "values_changed",
        },
        {
            "field": f"distributions.{new_title}.download_urls",
            "old_value": "http://old.example.com",
            "new_value": "http://new.example.com",
            "change_type": "values_changed",
        },
        {
            "field": f"distributions.{new_title}.languages",
            "old_value": "ENG",
            "new_value": "ENG, FRA",
            "change_type": "values_changed",
        },
    ]

    actual_changes = sorted(json.loads(log_entry.changes), key=lambda x: x["field"])
    expected_changes = sorted(expected_changes, key=lambda x: x["field"])
    assert (
        actual_changes == expected_changes
    ), f"Expected {expected_changes} but got {actual_changes}"

    service._repository.add.assert_called_once_with(log_entry)
    service._repository.commit.assert_called_once()


def test_log_distribution_updated_without_title_change(service):
    user_id = 1
    dataset_id = 100
    distribution_id = 200
    title = "CSV Distribution"

    old_distribution = {
        "title": title,
        "download_urls": ["http://old.example.com"],
    }
    new_distribution = {
        "title": title,
        "download_urls": ["http://new.example.com"],
    }

    service.log_distribution_updated(
        user_id=user_id,
        dataset_id=dataset_id,
        old_distribution=old_distribution,
        new_distribution=new_distribution,
        distribution_title=title,
    )

    log_entry = service._repository.add.call_args.args[0]

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "dataset"
    assert log_entry.entity_id == str(dataset_id)
    assert log_entry.action_type == "update"

    expected_changes = [
        {
            "field": f"distributions.{title}.download_urls",
            "old_value": "http://old.example.com",
            "new_value": "http://new.example.com",
            "change_type": "values_changed",
        }
    ]

    actual_changes = json.loads(log_entry.changes)
    assert (
        actual_changes == expected_changes
    ), f"Expected {expected_changes} but got {actual_changes}"


def test_log_distribution_updated_with_all_fields_changed(service):
    user_id = 1
    dataset_id = 100
    title = "All Fields Distribution"

    old_distribution = {
        "title": title,
        "description": "Old description",
        "download_urls": ["http://old.example.com"],
        "access_urls": ["http://old.access.example.com"],
        "file_type": "CSV",
        "rights_statement": "PUBLIC",
        "languages": ["ENG"],
        "internal_only": False,
        "is_analytics": False,
        "applicable_legislations": ["GDPR"],
        "notes": "old notes",
        "license": "no_license",
        "distribution_path": "INSIPRE",
        "availability": "Stable",
        "documentation": "http://old.docs.example.com",
        "modification_date": "2024-01-01",
        "release_date": "2024-01-02",
        "linked_schemas": ["dcat"],
        "media_type": "application/json",
        "compression_format": "application/zip",
        "packaging_format": "text/csv",
        "distribution_dcat_status": "Completed",
        "spatial_resolution": 1,
        "temporal_resolution": "PT1H",
        "access_service_ids": [1],
        "policy_actions": [
            {
                "policy_action_type": "permission",
                "policy_constraint_type": "temporal",
                "policy_constraint_value": None,
                "temporal_restriction_start": "2023-01-01",
                "temporal_restriction_end": "2023-12-31",
                "spatial_restrictions": ["LUX"],
            }
        ],
    }

    new_distribution = {
        "title": title,
        "description": "New description",
        "download_urls": ["http://new.example.com"],
        "access_urls": ["http://new.access.example.com"],
        "file_type": "JSON",
        "rights_statement": "NO_LIMITATIONS_TO_PUBLIC_ACCESS",
        "languages": ["ENG", "FRA"],
        "internal_only": True,
        "is_analytics": True,
        "applicable_legislations": ["GDPR", "DDPR"],
        "notes": "new notes",
        "license": "cc_by",
        "distribution_path": "HVD",
        "availability": "Deprecated",
        "documentation": "http://new.docs.example.com",
        "modification_date": "2024-02-01",
        "release_date": "2024-02-02",
        "linked_schemas": ["dcat", "dcat-ap"],
        "media_type": "application/xml",
        "compression_format": "text/turtle",
        "packaging_format": "application/zip",
        "distribution_dcat_status": "Withdrawn",
        "spatial_resolution": 2,
        "temporal_resolution": "P1D",
        "access_service_ids": [2],
        "policy_actions": [
            {
                "policy_action_type": "prohibition",
                "policy_constraint_type": "spatial",
                "policy_constraint_value": "DUO:0000006",
                "temporal_restriction_start": None,
                "temporal_restriction_end": None,
                "spatial_restrictions": ["LUX", "FRA"],
            }
        ],
    }

    service.log_distribution_updated(
        user_id=user_id,
        dataset_id=dataset_id,
        old_distribution=old_distribution,
        new_distribution=new_distribution,
        distribution_title=title,
    )

    log_entry = service._repository.add.call_args.args[0]
    actual_changes = sorted(json.loads(log_entry.changes), key=lambda x: x["field"])

    expected_changes = sorted(
        [
            {
                "field": f"distributions.{title}.description",
                "old_value": "Old description",
                "new_value": "New description",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.download_urls",
                "old_value": "http://old.example.com",
                "new_value": "http://new.example.com",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.access_urls",
                "old_value": "http://old.access.example.com",
                "new_value": "http://new.access.example.com",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.file_type",
                "old_value": "CSV",
                "new_value": "JSON",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.rights_statement",
                "old_value": "PUBLIC",
                "new_value": "NO_LIMITATIONS_TO_PUBLIC_ACCESS",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.languages",
                "old_value": "ENG",
                "new_value": "ENG, FRA",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.internal_only",
                "old_value": False,
                "new_value": True,
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.is_analytics",
                "old_value": False,
                "new_value": True,
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.applicable_legislations",
                "old_value": "GDPR",
                "new_value": "DDPR, GDPR",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.notes",
                "old_value": "old notes",
                "new_value": "new notes",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.license",
                "old_value": "no_license",
                "new_value": "cc_by",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.distribution_path",
                "old_value": "INSIPRE",
                "new_value": "HVD",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.availability",
                "old_value": "Stable",
                "new_value": "Deprecated",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.documentation",
                "old_value": "http://old.docs.example.com",
                "new_value": "http://new.docs.example.com",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.modification_date",
                "old_value": "2024-01-01",
                "new_value": "2024-02-01",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.release_date",
                "old_value": "2024-01-02",
                "new_value": "2024-02-02",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.linked_schemas",
                "old_value": "dcat",
                "new_value": "dcat, dcat-ap",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.media_type",
                "old_value": "application/json",
                "new_value": "application/xml",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.compression_format",
                "old_value": "application/zip",
                "new_value": "text/turtle",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.packaging_format",
                "old_value": "text/csv",
                "new_value": "application/zip",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.distribution_dcat_status",
                "old_value": "Completed",
                "new_value": "Withdrawn",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.spatial_resolution",
                "old_value": 1,
                "new_value": 2,
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.temporal_resolution",
                "old_value": "PT1H",
                "new_value": "P1D",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.access_service_ids",
                "old_value": "1",
                "new_value": "2",
                "change_type": "values_changed",
            },
            {
                "field": f"distributions.{title}.policy_actions[0]",
                "old_value": {
                    "policy_action_type": "permission",
                    "policy_constraint_type": "temporal",
                    "policy_constraint_value": None,
                    "temporal_restriction_start": "2023-01-01",
                    "temporal_restriction_end": "2023-12-31",
                    "spatial_restrictions": "LUX",
                },
                "new_value": {
                    "policy_action_type": "prohibition",
                    "policy_constraint_type": "spatial",
                    "policy_constraint_value": "DUO:0000006",
                    "temporal_restriction_start": None,
                    "temporal_restriction_end": None,
                    "spatial_restrictions": "FRA, LUX",
                },
                "change_type": "values_changed",
            },
        ],
        key=lambda x: x["field"],
    )

    assert actual_changes == expected_changes

    service._repository.add.assert_called_once_with(log_entry)
    service._repository.commit.assert_called_once()


def test_log_distribution_updated_with_policy_action_added(service):
    user_id = 1
    dataset_id = 100
    title = "Policy Action Added"

    old_distribution = {
        "title": title,
        "policy_actions": [],
    }
    new_distribution = {
        "title": title,
        "policy_actions": [
            {
                "policy_action_type": "permission",
                "policy_constraint_type": "temporal",
                "policy_constraint_value": None,
                "temporal_restriction_start": "2023-01-01",
                "temporal_restriction_end": "2023-12-31",
                "spatial_restrictions": ["LUX"],
            }
        ],
    }

    service.log_distribution_updated(
        user_id=user_id,
        dataset_id=dataset_id,
        old_distribution=old_distribution,
        new_distribution=new_distribution,
        distribution_title=title,
    )

    log_entry = service._repository.add.call_args.args[0]
    actual_changes = json.loads(log_entry.changes)

    expected_changes = [
        {
            "field": f"distributions.{title}.policy_actions[0]",
            "old_value": None,
            "new_value": {
                "policy_action_type": "permission",
                "policy_constraint_type": "temporal",
                "policy_constraint_value": None,
                "temporal_restriction_start": "2023-01-01",
                "temporal_restriction_end": "2023-12-31",
                "spatial_restrictions": "LUX",
            },
            "change_type": "iterable_item_added",
        }
    ]

    assert actual_changes == expected_changes


def test_log_distribution_updated_with_second_policy_action_added(service):
    user_id = 1
    dataset_id = 100
    title = "Policy Action Added Second"

    old_distribution = {
        "title": title,
        "policy_actions": [
            {
                "policy_action_type": "permission",
                "policy_constraint_type": "temporal",
                "policy_constraint_value": None,
                "temporal_restriction_start": "2023-01-01",
                "temporal_restriction_end": "2023-12-31",
                "spatial_restrictions": ["LUX"],
            }
        ],
    }
    new_distribution = {
        "title": title,
        "policy_actions": [
            {
                "policy_action_type": "permission",
                "policy_constraint_type": "temporal",
                "policy_constraint_value": None,
                "temporal_restriction_start": "2023-01-01",
                "temporal_restriction_end": "2023-12-31",
                "spatial_restrictions": ["LUX"],
            },
            {
                "policy_action_type": "prohibition",
                "policy_constraint_type": "spatial",
                "policy_constraint_value": "DUO:0000006",
                "temporal_restriction_start": None,
                "temporal_restriction_end": None,
                "spatial_restrictions": ["LUX", "FRA"],
            },
        ],
    }

    service.log_distribution_updated(
        user_id=user_id,
        dataset_id=dataset_id,
        old_distribution=old_distribution,
        new_distribution=new_distribution,
        distribution_title=title,
    )

    log_entry = service._repository.add.call_args.args[0]
    actual_changes = json.loads(log_entry.changes)

    assert len(actual_changes) == 1
    assert actual_changes[0]["change_type"] == "iterable_item_added"
    assert actual_changes[0]["field"].startswith(
        f"distributions.{title}.policy_actions["
    )
    assert actual_changes[0]["old_value"] is None
    assert actual_changes[0]["new_value"] == {
        "policy_action_type": "prohibition",
        "policy_constraint_type": "spatial",
        "policy_constraint_value": "DUO:0000006",
        "temporal_restriction_start": None,
        "temporal_restriction_end": None,
        "spatial_restrictions": "FRA, LUX",
    }


def test_log_distribution_deleted_with_title(service):
    user_id = 1
    dataset_id = 100
    distribution_id = 200
    distribution_title = "CSV Distribution"

    service.log_distribution_deleted(
        user_id=user_id,
        dataset_id=dataset_id,
        distribution_id=distribution_id,
        distribution_title=distribution_title,
    )

    log_entry = service._repository.add.call_args.args[0]

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "dataset"
    assert log_entry.entity_id == str(dataset_id)
    assert log_entry.action_type == "update"

    expected_changes = [
        {
            "field": "distribution",
            "old_value": {
                "dataset_id": dataset_id,
                "distribution_id": distribution_id,
                "distribution_title": distribution_title,
            },
            "new_value": None,
            "change_type": "deleted",
        }
    ]

    actual_changes = json.loads(log_entry.changes)
    assert (
        actual_changes == expected_changes
    ), f"Expected {expected_changes} but got {actual_changes}"

    service._repository.add.assert_called_once_with(log_entry)
    service._repository.commit.assert_called_once()


def test_log_distribution_deleted_without_title(service):
    user_id = 1
    dataset_id = 100
    distribution_id = 200

    service.log_distribution_deleted(
        user_id=user_id,
        dataset_id=dataset_id,
        distribution_id=distribution_id,
        distribution_title=None,
    )

    log_entry = service._repository.add.call_args.args[0]

    assert log_entry is not None
    assert log_entry.user_id == user_id
    assert log_entry.entity_type == "dataset"
    assert log_entry.entity_id == str(dataset_id)
    assert log_entry.action_type == "update"

    expected_changes = [
        {
            "field": "distribution",
            "old_value": {
                "dataset_id": dataset_id,
                "distribution_id": distribution_id,
                "distribution_title": None,
            },
            "new_value": None,
            "change_type": "deleted",
        }
    ]

    actual_changes = json.loads(log_entry.changes)
    assert (
        actual_changes == expected_changes
    ), f"Expected {expected_changes} but got {actual_changes}"

    service._repository.add.assert_called_once_with(log_entry)
    service._repository.commit.assert_called_once()
