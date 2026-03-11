import pytest
from pydantic import ValidationError

from schemas.dataset import DatasetDto


def _base_dataset_payload() -> dict:
    return {
        "status": "DRAFT",
        "title": "Test dataset",
        "description": "Dataset description",
        "contact_ids": None,
        "publisher_id": 1,
        "time_period_start": None,
        "time_period_end": None,
        "retention_period_start": None,
        "retention_period_end": None,
        "release_date": None,
        "modified_at": None,
        "deprecated_at": None,
        "released_at": None,
        "rights_statement": "https://example.org/rights/public",
        "periodicity": None,
        "version": None,
        "version_change_type": None,
        "duration_of_administrative_utility": None,
        "max_typical_age": None,
        "min_typical_age": None,
        "number_of_records": None,
        "number_of_unique_individuals": None,
        "final_disposition": None,
        "notes": None,
        "themes": ["https://example.org/theme/ENV"],
        "keywords": [],
        "health_categories": [],
        "health_themes": [],
        "applicable_legislations": [],
        "spatial_coverages": [],
        "conventions": [],
        "areas_of_work": [],
        "areas_of_competence": [],
        "dataset_types": ["https://example.org/type/REPORT"],
        "distributions": None,
        "creator_ids": [],
        "group_managers": None,
        "data_protection_types": [],
        "monitoring_location": None,
        "provenance": [],
        "health_legal_basis": [],
        "languages": ["http://publications.europa.eu/resource/authority/language/ENG"],
        "landing_pages": [],
        "documentation": [],
        "purpose": [],
        "conforms_to": [],
        "is_dataset_series": False,
        "member_datasets": None,
        "was_generated_by": [],
        "other_identifiers": [],
        "version_notes": [],
        "spatial_resolutions": [],
        "temporal_resolution": None,
        "population_coverage": None,
        "source": None,
        "source_dataset_id": None,
        "code_values": [],
        "coding_systems": [],
    }


def test_dataset_schema_accepts_valid_landing_pages_and_conforms_to_urls():
    payload = _base_dataset_payload()
    payload["landing_pages"] = [
        "https://example.org/landing/a",
        "https://example.org/landing/b",
    ]
    payload["conforms_to"] = [
        "https://example.org/spec/1",
        "https://example.org/spec/2",
    ]

    dto = DatasetDto.model_validate(payload)

    assert [str(url) for url in dto.landing_pages] == [
        "https://example.org/landing/a",
        "https://example.org/landing/b",
    ]
    assert [str(url) for url in dto.conforms_to] == [
        "https://example.org/spec/1",
        "https://example.org/spec/2",
    ]


def test_dataset_schema_accepts_full_payload_all_fields():
    payload = _base_dataset_payload()
    payload.update(
        {
            "status": "APPROVED",
            "contact_ids": [11, 22],
            "time_period_start": "2023-01-01",
            "time_period_end": "2023-12-31",
            "retention_period_start": "2022-01-01",
            "retention_period_end": "2024-01-01",
            "release_date": "2024-01-15",
            "modified_at": "2024-01-20",
            "deprecated_at": None,
            "released_at": "2024-01-21",
            "periodicity": "http://publications.europa.eu/resource/authority/frequency/ANNUAL",
            "version": "1.2.3",
            "version_change_type": "METADATA_ONLY",
            "duration_of_administrative_utility": 365,
            "max_typical_age": 99,
            "min_typical_age": 1,
            "number_of_records": 1000,
            "number_of_unique_individuals": 450,
            "final_disposition": "Archived after retention",
            "notes": "Detailed notes",
            "keywords": ["ENV", "AIR"],
            "health_categories": ["HC-1"],
            "health_themes": ["HT-1"],
            "applicable_legislations": ["https://example.org/legal/1"],
            "spatial_coverages": ["https://example.org/geo/LU"],
            "conventions": ["conv-1"],
            "areas_of_work": ["aow-1"],
            "areas_of_competence": ["aoc-1"],
            "dataset_types": ["https://example.org/type/REPORT"],
            "distributions": [
                {
                    "title": "Main export",
                    "description": "Distribution description",
                    "download_urls": ["https://example.org/download.csv"],
                    "access_urls": ["https://example.org/access.csv"],
                    "rights_statement": "https://example.org/rights/public",
                    "languages": [
                        "http://publications.europa.eu/resource/authority/language/ENG"
                    ],
                    "applicable_legislations": ["https://example.org/legal/1"],
                    "documentation": ("https://example.org/dist-doc",),
                    "linked_schemas": ["https://example.org/schema/v1"],
                }
            ],
            "group_managers": [33, 44],
            "data_protection_types": ["PersonalData"],
            "monitoring_location": "National",
            "provenance": ["Source system A"],
            "health_legal_basis": ["Legal basis text"],
            "languages": [
                "http://publications.europa.eu/resource/authority/language/ENG"
            ],
            "landing_pages": ["https://example.org/landing/a"],
            "documentation": ["https://example.org/doc/1", "doc-literal"],
            "purpose": ["Research"],
            "conforms_to": ["https://example.org/spec/1"],
            "is_dataset_series": True,
            "member_datasets": [101, 102],
            "was_generated_by": ["Generator Job"],
            "other_identifiers": ["ALT-123"],
            "version_notes": ["First publication"],
            "spatial_resolutions": [10, 20],
            "temporal_resolution": "P1D",
            "population_coverage": "Adults in Luxembourg",
            "source": "lnds-mdc",
            "source_dataset_id": 999,
            "code_values": ["ICD-10"],
            "coding_systems": ["https://www.wikidata.org/entity/Q9006342"],
        }
    )

    dto = DatasetDto.model_validate(payload)

    assert dto.status == "APPROVED"
    assert dto.contact_ids == {11, 22}
    assert dto.member_datasets == [101, 102]
    assert [str(url) for url in dto.landing_pages] == ["https://example.org/landing/a"]
    assert [str(url) for url in dto.conforms_to] == ["https://example.org/spec/1"]
    assert dto.distributions is not None
    assert len(dto.distributions) == 1


def test_dataset_schema_rejects_invalid_landing_page_url():
    payload = _base_dataset_payload()
    payload["landing_pages"] = ["not-a-url"]

    with pytest.raises(ValidationError):
        DatasetDto.model_validate(payload)


def test_dataset_schema_rejects_invalid_conforms_to_url():
    payload = _base_dataset_payload()
    payload["conforms_to"] = ["still-not-a-url"]

    with pytest.raises(ValidationError):
        DatasetDto.model_validate(payload)
