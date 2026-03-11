from schemas.distribution import DistributionDto
from services.distribution_title_generator import (
    generate_unique_distribution_title,
    normalize_distribution_title,
)


def _build_distribution_dto(**overrides) -> DistributionDto:
    base_payload = {
        "title": None,
        "access_urls": ["https://example.com/data"],
        "download_urls": [],
        "rights_statement": "Public Domain",
        "languages": frozenset({"ENG"}),
        "file_type": None,
        "media_type": None,
    }
    base_payload.update(overrides)
    return DistributionDto(**base_payload)


def test_normalize_distribution_title():
    assert normalize_distribution_title("  CSV Export  ") == "CSV Export"
    assert normalize_distribution_title("   ") is None
    assert normalize_distribution_title(None) is None


def test_generate_unique_distribution_title_uses_file_type_base():
    dto = _build_distribution_dto(file_type="CSV")

    result = generate_unique_distribution_title(
        dto,
        existing_titles=["CSV Distribution", "CSV Distribution (2)"],
    )

    assert result == "CSV Distribution (3)"


def test_generate_unique_distribution_title_uses_last_uri_segment_for_file_type():
    dto = _build_distribution_dto(
        file_type="http://publications.europa.eu/resource/authority/file-type/CSV"
    )

    result = generate_unique_distribution_title(dto, existing_titles=[])

    assert result == "CSV Distribution"


def test_generate_unique_distribution_title_falls_back_to_distribution_when_no_file_type():
    dto = _build_distribution_dto(media_type="application/json")

    result = generate_unique_distribution_title(dto, existing_titles=[])

    assert result == "Distribution"


def test_generate_unique_distribution_title_adds_suffix_for_distribution_fallback():
    dto = _build_distribution_dto(
        access_urls=["https://www.data.example.gov/resource"],
        media_type="text/csv",
    )

    result = generate_unique_distribution_title(
        dto,
        existing_titles=["Distribution", "distribution (2)"],
    )

    assert result == "Distribution (3)"
