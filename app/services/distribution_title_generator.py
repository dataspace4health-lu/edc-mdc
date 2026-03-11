from collections.abc import Iterable
from schemas.distribution import DistributionDto


def normalize_distribution_title(title: str | None) -> str | None:
    if title is None:
        return None
    normalized = title.strip()
    return normalized if normalized else None


def generate_unique_distribution_title(
    distribution_dto: DistributionDto, existing_titles: Iterable[str]
) -> str:
    base_title = _build_generated_title_base(distribution_dto)
    existing_normalized_titles = {
        title.strip().lower() for title in existing_titles if title
    }

    if base_title.lower() not in existing_normalized_titles:
        return base_title

    suffix = 2
    while True:
        candidate = f"{base_title} ({suffix})"
        if candidate.lower() not in existing_normalized_titles:
            return candidate
        suffix += 1


def _build_generated_title_base(distribution_dto: DistributionDto) -> str:
    if distribution_dto.file_type:
        raw_file_type = distribution_dto.file_type.strip()
        file_type = raw_file_type.rstrip("/").rsplit("/", 1)[-1]
        file_type = file_type.split("#", 1)[0].split("?", 1)[0].strip()
        if file_type:
            return f"{file_type} Distribution"

    return "Distribution"
