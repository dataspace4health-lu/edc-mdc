from dataclasses import dataclass
from datetime import UTC, date
from typing import Any, FrozenSet, List, Optional, Union, Annotated, Tuple

from models.dataset import Dataset, DatasetStatus, DatasetVersionChangeType
from models.dataset_relation import DatasetRelation
from pydantic import BaseModel, Field, model_validator, field_validator, AnyUrl
from validators.temporal_resolution_validator import validate_temporal_resolution
from schemas.distribution import (
    DistributionDto,
    ResourceDistribution,
    distribution_entity_to_resource,
    generate_distribution_dto_from_distribution,
)
from schemas.qualified_attribution import (
    ResourceQualifiedAttribution,
    qualified_attribution_entity_to_resource,
)
from schemas.form_field import EnumValue, HierarchicalEnumValue


@dataclass(frozen=True)
class SeriesMembershipInfo(BaseModel):
    dataset_id: int
    position: int
    is_first: bool
    is_last: bool


@dataclass(frozen=True)
class DatasetDto(BaseModel):
    status: str = DatasetStatus.DRAFT.value
    title: Annotated[
        str,
        Field(
            min_length=1, max_length=500, description="Dataset title (1-500 characters)"
        ),
    ]
    description: Annotated[
        str,
        Field(
            min_length=1,
            max_length=5000,
            description="Dataset description (1-5000 characters)",
        ),
    ]
    contact_ids: Optional[set[int]] = None
    publisher_id: int
    time_period_start: Union[date, None] = None
    time_period_end: Union[date, None] = None
    retention_period_start: Union[date, None] = None
    retention_period_end: Union[date, None] = None
    release_date: Optional[date] = None
    modified_at: Optional[date] = None
    deprecated_at: Optional[date] = None
    released_at: Optional[date] = None
    rights_statement: Annotated[
        str,
        Field(
            min_length=1,
            max_length=500,
            description="Rights statement (1-500 characters)",
        ),
    ]
    periodicity: Optional[
        Annotated[
            str,
            Field(max_length=100, description="Periodicity (max 100 characters)"),
        ]
    ] = None
    version: Optional[
        Annotated[
            str,
            Field(max_length=50, description="Version (max 50 characters)"),
        ]
    ] = None
    version_change_type: Optional[
        Annotated[
            str,
            Field(
                max_length=30,
                description="Version change type (METADATA_ONLY or UNDERLYING_DATA)",
            ),
        ]
    ] = None
    duration_of_administrative_utility: Union[int, None] = None
    max_typical_age: Union[int, None] = None
    min_typical_age: Union[int, None] = None
    number_of_records: Union[int, None] = None
    number_of_unique_individuals: Union[int, None] = None
    final_disposition: Optional[
        Annotated[
            str,
            Field(max_length=200, description="Final disposition (max 200 characters)"),
        ]
    ] = None
    notes: Optional[
        Annotated[
            str,
            Field(max_length=2000, description="Notes (max 2000 characters)"),
        ]
    ] = None
    themes: set[str] = Field(min_items=1)
    keywords: set[str] = Field(min_items=0)
    health_categories: set[str] = Field(min_items=0)
    health_themes: set[str] = Field(min_items=0)
    applicable_legislations: set[str] = Field(min_length=0)
    spatial_coverages: set[str] = Field(min_items=0)
    conventions: set[str] = Field(min_items=0)
    areas_of_work: set[str] = Field(min_items=0)
    areas_of_competence: set[str] = Field(min_items=0)
    dataset_types: set[str] = Field(min_items=1)
    distributions: Optional[list[DistributionDto]] = None
    creator_ids: set[int] = Field(min_items=0)
    group_managers: Optional[set[int]] = None
    data_protection_types: set[str] = Field(min_items=0)
    monitoring_location: Optional[
        Annotated[
            str,
            Field(
                max_length=100, description="Monitoring location (max 100 characters)"
            ),
        ]
    ] = None
    provenance: list[
        Annotated[
            str,
            Field(
                max_length=1000,
                description="Provenance entry (max 1000 characters)",
            ),
        ]
    ] = Field(default_factory=list)
    health_legal_basis: Optional[
        list[
            Annotated[
                str,
                Field(
                    max_length=1000,
                    description="Health legal basis entry (max 1000 characters)",
                ),
            ]
        ]
    ] = Field(default=[])
    languages: frozenset[str] = Field()
    landing_pages: list[AnyUrl] = Field(default_factory=list, min_items=0)
    documentation: list[str] = Field(default_factory=list, min_items=0)
    purpose: set[str] = Field(min_items=0, default=set())
    conforms_to: list[AnyUrl] = Field(default_factory=list)
    is_dataset_series: bool = False
    member_datasets: Optional[List[int]] = None
    was_generated_by: Optional[frozenset[str]] = Field(min_length=0)
    other_identifiers: Optional[frozenset[str]] = Field(min_length=0)
    version_notes: list[
        Annotated[
            str,
            Field(
                max_length=1000,
                description="Version note entry (max 1000 characters)",
            ),
        ]
    ] = Field(default_factory=list)
    spatial_resolutions: list[int] = Field(
        default_factory=list, description="Spatial resolution values in meters"
    )
    temporal_resolution: Optional[
        Annotated[
            str,
            Field(
                max_length=100, description="Temporal resolution (max 100 characters)"
            ),
        ]
    ] = None
    population_coverage: Optional[
        Annotated[
            str,
            Field(
                max_length=2000,
                description="Population coverage (max 2000 characters)",
            ),
        ]
    ] = None
    source: Optional[str] = None
    source_dataset_id: Optional[int] = None
    coding_systems: list[str] = Field(default_factory=list, min_length=0)
    code_values: list[str] = Field(default_factory=list, min_length=0)
    personal_data: list[str] = Field(default_factory=list, min_length=0)

    @model_validator(mode="after")
    def validate_distribution_titles(cls, values):
        titles = [distribution.title for distribution in (values.distributions or [])]
        if len(titles) != len(set(titles)):
            raise ValueError("Distribution titles must be unique.")
        return values

    @field_validator("spatial_resolutions", mode="before")
    @classmethod
    def validate_spatial_resolutions_field(cls, value) -> list[int]:
        if value is None:
            return []

        if isinstance(value, (list, set, tuple, frozenset)):
            raw_values = list(value)
        else:
            raw_values = [value]

        validated_values: list[int] = []
        seen: set[int] = set()
        for raw in raw_values:
            resolution = int(raw)
            if resolution < 0:
                raise ValueError("All spatial resolution values must be non-negative")
            if resolution in seen:
                continue
            seen.add(resolution)
            validated_values.append(resolution)

        return validated_values

    @field_validator("temporal_resolution")
    @classmethod
    def validate_temporal_resolution_field(cls, value: Optional[str]) -> Optional[str]:
        return validate_temporal_resolution(value)

    @field_validator("version_change_type")
    @classmethod
    def validate_version_change_type_field(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        allowed = {
            DatasetVersionChangeType.METADATA_ONLY.value,
            DatasetVersionChangeType.UNDERLYING_DATA.value,
        }
        if value not in allowed:
            raise ValueError(
                "version_change_type must be METADATA_ONLY or UNDERLYING_DATA."
            )
        return value


@dataclass(frozen=True)
class DatasetVersionCreateDto(BaseModel):
    version_change_type: str = DatasetVersionChangeType.METADATA_ONLY.value

    @field_validator("version_change_type")
    @classmethod
    def validate_version_change_type(cls, value: str) -> str:
        allowed = {
            DatasetVersionChangeType.METADATA_ONLY.value,
            DatasetVersionChangeType.UNDERLYING_DATA.value,
        }
        if value not in allowed:
            raise ValueError(
                "version_change_type must be METADATA_ONLY or UNDERLYING_DATA."
            )
        return value


@dataclass(frozen=True)
class DatasetStatusUpdateDto(BaseModel):
    comment: Optional[
        Annotated[
            str,
            Field(
                max_length=5000,
                description="Status update comment (max 5000 characters)",
            ),
        ]
    ] = None


@dataclass(frozen=True)
class ResourceSourceRelation:
    id: int
    relation_kind: str

    title: Optional[str] = None
    status: Optional[str] = None
    internal_only: Optional[bool] = None
    dataset_id: Optional[int] = None
    relation_type: Optional[str] = None
    previous_version_dataset_id: Optional[int] = None

    external_url: Optional[str] = None
    external_role: Optional[str] = None
    external_description: Optional[str] = None


@dataclass
class ResourceDataset:
    id: int
    status: str
    status_triggers: list[str]
    title: str
    description: str
    contact_ids: list[int]
    contact_names: list[str]
    contact_emails: list[str]
    user_id: int
    publisher_name: str
    publisher_id: int
    identifier: str
    submitted_at: str
    time_period_start: Union[str, None]
    dataset_types: FrozenSet[EnumValue]
    themes: FrozenSet[EnumValue]
    keywords: FrozenSet[HierarchicalEnumValue]
    health_categories: FrozenSet[EnumValue]
    health_themes: FrozenSet[EnumValue]
    spatial_coverages: FrozenSet[EnumValue]
    conventions: list[str]
    areas_of_work: list[str]
    areas_of_competence: list[str]
    applicable_legislations: list[str]
    languages: FrozenSet[EnumValue]
    distributions: List[ResourceDistribution]
    group_manager_ids: list[int]
    group_manager_names: list[str]
    data_protection_types: list[str]
    creator_names: list[str]
    creator_ids: list[int]
    release_date: Union[str, None]
    released_at: Union[str, None]
    modified_at: Union[str, None]
    deprecated_at: Union[str, None]
    time_period_end: Union[str, None]
    retention_period_start: Union[str, None]
    retention_period_end: Union[str, None]
    rights_statement: str
    periodicity: Union[EnumValue, None]
    version: Union[str, None]
    version_change_type: Union[str, None]
    notes: Union[str, None]
    conforms_to: Optional[List[str]]
    duration_of_administrative_utility: Union[int, None]
    max_typical_age: Union[int, None]
    min_typical_age: Union[int, None]
    number_of_records: Union[int, None]
    number_of_unique_individuals: Union[int, None]
    is_any_dictionary_authentic_source: Union[bool, None]
    final_disposition: Optional[str]
    author_name: str
    qualified_attributions: Optional[List[ResourceQualifiedAttribution]] = None
    source_relations: Optional[List[ResourceSourceRelation]] = None
    total_dictionaries: int = 0
    total_relations: int = 0
    comments_count: int = 0
    author_name: str = ""
    monitoring_location: Optional[str] = None
    source: Optional[str] = None
    source_dataset_id: Optional[int] = None
    provenance: list[str] = Field(default_factory=list)
    health_legal_basis: list[str] = Field(default_factory=list)
    landing_pages: list[str] = Field(default_factory=list)
    documentation: list[str] = Field(default_factory=list)
    purpose: list[str] = Field(default_factory=list)
    is_dataset_series: bool = False
    member_datasets: Optional[List[SeriesMembershipInfo]] = None
    series_memberships: Optional[List[SeriesMembershipInfo]] = None
    first_dataset_id: Optional[int] = None
    last_dataset_id: Optional[int] = None
    spatial_resolutions: List[int] = Field(
        default_factory=list,
        description="Spatial resolution values in meters",
    )
    temporal_resolution: Optional[str] = None
    authentic_source_reviewed_at: Union[str, None] = None
    previous_version_dataset_id: Optional[int] = None
    latest_version_dataset_id: Optional[int] = None
    has_versions: bool = False
    was_generated_by: Optional[List[str]] = None
    other_identifiers: Optional[List[str]] = None
    version_notes: list[str] = Field(default_factory=list)
    population_coverage: Union[str, None] = None
    code_values: list[str] = Field(default_factory=list)
    coding_systems: list[str] = Field(default_factory=list)
    personal_data: list[str] = Field(default_factory=list)


def dataset_entity_to_resource(
    dataset: Dataset,
    status_triggers: list[str],
    latest_version_dataset_id: Optional[int] = None,
) -> ResourceDataset:
    is_any_dictionary_authentic_source = (
        any(entry.is_authentic_source for entry in dataset.data_dictionaries)
        if hasattr(dataset, "data_dictionaries") and dataset.data_dictionaries
        else False
    )
    resource = ResourceDataset(
        comments_count=len(dataset.dataset_comments),
        author_name=dataset.user.name if dataset.user else "",
        id=dataset.id,
        title=dataset.title,
        status=dataset.status,
        status_triggers=status_triggers,
        description=dataset.description,
        contact_ids=(
            [dc.contact_id for dc in dataset.contacts if dc and dc.contact]
            if dataset.contacts
            else []
        ),
        contact_names=(
            [dc.contact.name for dc in dataset.contacts if dc and dc.contact]
            if dataset.contacts
            else []
        ),
        contact_emails=(
            [dc.contact.email for dc in dataset.contacts if dc and dc.contact]
            if dataset.contacts
            else []
        ),
        user_id=dataset.user_id,
        publisher_name=dataset.publisher.name if dataset.publisher else None,
        publisher_id=dataset.publisher_id,
        submitted_at=dataset.submitted_at.isoformat(),
        authentic_source_reviewed_at=(
            dataset.authentic_source_reviewed_at.isoformat()
            if dataset.authentic_source_reviewed_at
            else None
        ),
        release_date=dataset.release_date.isoformat() if dataset.release_date else None,
        modified_at=(dataset.modified_at.isoformat() if dataset.modified_at else None),
        released_at=(dataset.released_at.isoformat() if dataset.released_at else None),
        deprecated_at=(
            dataset.deprecated_at.isoformat() if dataset.deprecated_at else None
        ),
        time_period_start=(
            dataset.time_period_start.isoformat() if dataset.time_period_start else None
        ),
        time_period_end=(
            dataset.time_period_end.isoformat() if dataset.time_period_end else None
        ),
        retention_period_start=(
            dataset.retention_period_start.isoformat()
            if dataset.retention_period_start
            else None
        ),
        retention_period_end=(
            dataset.retention_period_end.isoformat()
            if dataset.retention_period_end
            else None
        ),
        rights_statement=dataset.rights_statement,
        periodicity=(
            EnumValue(
                dataset.periodicity_value.key, dataset.periodicity_value.eng_label
            )
            if dataset.periodicity_value
            else None
        ),
        version=dataset.version,
        version_change_type=dataset.version_change_type,
        themes=frozenset(
            [
                EnumValue(it.value.key, it.value.eng_label)
                for it in dataset.themes
                if it.value
            ]
        ),
        spatial_resolutions=(
            [sr.value for sr in dataset.spatial_resolutions]
            if dataset.spatial_resolutions
            else []
        ),
        qualified_attributions=[
            qualified_attribution_entity_to_resource(qa)
            for qa in getattr(dataset, "qualified_attributions", [])
        ],
        dataset_types=frozenset(
            [
                EnumValue(dt.value.key, dt.value.eng_label)
                for dt in dataset.dataset_types
                if dt.value
            ]
        ),
        keywords=frozenset(
            [
                HierarchicalEnumValue(
                    it.value.key, it.value.eng_label, it.value.parent_key
                )
                for it in dataset.keywords
                if it.value
            ]
        ),
        health_categories=frozenset(
            [
                EnumValue(it.value.key, it.value.eng_label)
                for it in dataset.health_categories
                if it.value
            ]
        ),
        health_themes=frozenset(
            [
                EnumValue(it.value.key, it.value.eng_label)
                for it in dataset.health_themes
                if it.value
            ]
        ),
        spatial_coverages=frozenset(
            [
                EnumValue(it.value.key, it.value.eng_label)
                for it in dataset.spatial_coverages
                if it.value
            ]
        ),
        conventions=[it.key for it in dataset.conventions],
        areas_of_work=[it.key for it in dataset.areas_of_work],
        areas_of_competence=[it.key for it in dataset.areas_of_competence],
        applicable_legislations=[it.key for it in dataset.applicable_legislations],
        notes=dataset.notes,
        duration_of_administrative_utility=dataset.duration_of_administrative_utility,
        max_typical_age=dataset.max_typical_age,
        min_typical_age=dataset.min_typical_age,
        number_of_records=dataset.number_of_records,
        number_of_unique_individuals=dataset.number_of_unique_individuals,
        is_any_dictionary_authentic_source=is_any_dictionary_authentic_source,
        total_dictionaries=len(dataset.data_dictionaries),
        total_relations=len(dataset.source_relations) + len(dataset.target_relations),
        previous_version_dataset_id=dataset.previous_version_dataset_id,
        latest_version_dataset_id=latest_version_dataset_id,
        final_disposition=dataset.final_disposition,
        languages=frozenset(
            [
                EnumValue(it.value.key, it.value.eng_label)
                for it in dataset.languages
                if it.value
            ]
        ),
        distributions=(
            [
                distribution_entity_to_resource(it)
                for it in sorted(
                    dataset.distributions,
                    key=lambda distribution: distribution.id or 0,
                    reverse=True,
                )
            ]
            if dataset.distributions
            else []
        ),
        source_relations=[
            source_dataset_relation_entity_to_resource(it)
            for it in dataset.source_relations
        ],
        group_manager_ids=(
            [gm.user_id for gm in dataset.group_managers if gm and gm.user]
            if dataset.group_managers
            else []
        ),
        group_manager_names=(
            [gm.user.name for gm in dataset.group_managers if gm and gm.user]
            if dataset.group_managers
            else []
        ),
        was_generated_by=(
            [oi.key for oi in dataset.was_generated_by]
            if dataset.was_generated_by
            else []
        ),
        other_identifiers=(
            [oi.key for oi in dataset.other_identifiers]
            if dataset.other_identifiers
            else []
        ),
        version_notes=(
            [vn.value for vn in dataset.version_notes] if dataset.version_notes else []
        ),
        creator_ids=(
            [creator.organisation_id for creator in dataset.creators]
            if dataset.creators
            else []
        ),
        creator_names=(
            [
                creator.organisation.name
                for creator in dataset.creators
                if creator.organisation
            ]
            if dataset.creators
            else []
        ),
        identifier=dataset.identifier,
        source=dataset.source,
        source_dataset_id=dataset.source_dataset_id,
        data_protection_types=[it.key for it in dataset.data_protection_types],
        monitoring_location=dataset.monitoring_location,
        provenance=(
            [p.value for p in dataset.provenance_entries]
            if dataset.provenance_entries
            else []
        ),
        health_legal_basis=(
            [hlb.value for hlb in dataset.health_legal_basis_entries]
            if dataset.health_legal_basis_entries
            else []
        ),
        landing_pages=(
            [landing_page.url for landing_page in dataset.landing_pages]
            if dataset.landing_pages
            else []
        ),
        conforms_to=(
            [ct.key for ct in dataset.conforms_to_values]
            if dataset.conforms_to_values
            else []
        ),
        documentation=(
            [doc.value for doc in dataset.documentation_entries]
            if dataset.documentation_entries
            else []
        ),
        purpose=(
            [purpose.value for purpose in dataset.purpose_entries]
            if dataset.purpose_entries
            else []
        ),
        is_dataset_series=dataset.is_dataset_series,
        temporal_resolution=dataset.temporal_resolution,
        has_versions=len(dataset.versions) > 0,
        population_coverage=dataset.population_coverage,
        code_values=(
            [cv.value for cv in dataset.code_values] if dataset.code_values else []
        ),
        coding_systems=(
            [cs.value for cs in dataset.coding_systems]
            if dataset.coding_systems
            else []
        ),
        personal_data=(
            [pd.key for pd in dataset.personal_data] if dataset.personal_data else []
        ),
    )

    if dataset.is_dataset_series and hasattr(dataset, "member_datasets"):
        # Sort member datasets by position
        sorted_members = sorted(
            dataset.member_datasets,
            key=lambda m: m.position if hasattr(m, "position") else 0,
        )

        # Create membership info for each member dataset
        resource.member_datasets = [
            SeriesMembershipInfo(
                dataset_id=membership.dataset_id,
                position=membership.position,
                is_first=membership.is_first,
                is_last=membership.is_last,
            )
            for membership in sorted_members
        ]

        # Add first and last dataset IDs for easier reference
        if sorted_members:
            first_member = next((m for m in sorted_members if m.is_first), None)
            if first_member:
                resource.first_dataset_id = first_member.dataset_id

            last_member = next((m for m in sorted_members if m.is_last), None)
            if last_member:
                resource.last_dataset_id = last_member.dataset_id

    # Add series membership info for this dataset (if it belongs to series)
    if hasattr(dataset, "series_memberships") and dataset.series_memberships:
        resource.series_memberships = [
            SeriesMembershipInfo(
                dataset_id=membership.series_id,  # Using series_id here since it's from the perspective of the dataset
                position=membership.position,
                is_first=membership.is_first,
                is_last=membership.is_last,
            )
            for membership in dataset.series_memberships
        ]
    return resource


def source_dataset_relation_entity_to_resource(
    relation: DatasetRelation,
) -> ResourceSourceRelation:
    if relation.is_dataset_relation:
        return ResourceSourceRelation(
            id=relation.id,
            relation_kind="dataset",
            title=relation.target.title,
            dataset_id=relation.target.id,
            internal_only=relation.target.status == DatasetStatus.INTERNAL_ONLY.value,
            relation_type=relation.relation_type,
            status=relation.target.status,
            previous_version_dataset_id=relation.target.previous_version_dataset_id,
        )
    else:
        return ResourceSourceRelation(
            id=relation.id,
            relation_kind="external",
            external_url=relation.external_url,
            external_role=relation.external_role,
            external_description=relation.external_description,
        )


def generate_dataset_dto_from_dataset(
    dataset: Dataset, clone: bool = True
) -> DatasetDto:
    return DatasetDto(
        title=("Clone - " + dataset.title) if clone else dataset.title,
        description=dataset.description,
        contact_ids=(
            {contact.contact_id for contact in dataset.contacts}
            if dataset.contacts
            else None
        ),
        publisher_id=dataset.publisher_id,
        creator_ids=[creator.organisation_id for creator in dataset.creators],
        time_period_start=dataset.time_period_start,
        time_period_end=dataset.time_period_end,
        retention_period_start=dataset.retention_period_start,
        retention_period_end=dataset.retention_period_end,
        rights_statement=dataset.rights_statement,
        periodicity=dataset.periodicity,
        notes=dataset.notes,
        duration_of_administrative_utility=dataset.duration_of_administrative_utility,
        max_typical_age=dataset.max_typical_age,
        min_typical_age=dataset.min_typical_age,
        number_of_records=dataset.number_of_records,
        number_of_unique_individuals=dataset.number_of_unique_individuals,
        final_disposition=dataset.final_disposition,
        version=dataset.version,
        version_change_type=None,
        monitoring_location=dataset.monitoring_location,
        dataset_types=[type.key for type in dataset.dataset_types],
        themes=[theme.key for theme in dataset.themes],
        keywords=[keyword.key for keyword in dataset.keywords],
        health_categories=[hc.key for hc in dataset.health_categories],
        health_themes=[ht.key for ht in dataset.health_themes],
        spatial_coverages=[coverage.key for coverage in dataset.spatial_coverages],
        conventions=[convention.key for convention in dataset.conventions],
        areas_of_work=[aow.key for aow in dataset.areas_of_work],
        areas_of_competence=[aoc.key for aoc in dataset.areas_of_competence],
        applicable_legislations=[
            basis.key for basis in dataset.applicable_legislations
        ],
        data_protection_types=[dpt.key for dpt in dataset.data_protection_types],
        group_managers=[gm.user_id for gm in dataset.group_managers],
        status=DatasetStatus.DRAFT.value,
        release_date=dataset.release_date,
        modified_at=dataset.modified_at,
        deprecated_at=dataset.deprecated_at,
        released_at=None,  # New version starts as DRAFT, released_at set when published
        provenance=(
            [p.value for p in dataset.provenance_entries]
            if dataset.provenance_entries
            else []
        ),
        health_legal_basis=(
            [hlb.value for hlb in dataset.health_legal_basis_entries]
            if dataset.health_legal_basis_entries
            else []
        ),
        languages=[language.key for language in dataset.languages],
        distributions=[
            generate_distribution_dto_from_distribution(distribution)
            for distribution in dataset.distributions
        ],
        landing_pages=[landing_page.url for landing_page in dataset.landing_pages],
        is_dataset_series=dataset.is_dataset_series,
        member_datasets=(
            [membership.dataset_id for membership in dataset.member_datasets]
            if dataset.member_datasets
            else None
        ),
        documentation=[doc.value for doc in dataset.documentation_entries],
        purpose={purpose.value for purpose in dataset.purpose_entries},
        conforms_to=[ct.key for ct in dataset.conforms_to_values],
        was_generated_by=[oi.key for oi in dataset.was_generated_by],
        other_identifiers=[oi.key for oi in dataset.other_identifiers],
        version_notes=(
            [vn.value for vn in dataset.version_notes] if dataset.version_notes else []
        ),
        spatial_resolutions=(
            [sr.value for sr in dataset.spatial_resolutions]
            if dataset.spatial_resolutions
            else []
        ),
        temporal_resolution=dataset.temporal_resolution,
        population_coverage=dataset.population_coverage,
        source=None,  # Don't clone source tracking
        source_dataset_id=None,  # Don't clone source tracking
        code_values=(
            [cv.value for cv in dataset.code_values] if dataset.code_values else []
        ),
        coding_systems=(
            [cs.value for cs in dataset.coding_systems]
            if dataset.coding_systems
            else []
        ),
        personal_data=[pd.key for pd in dataset.personal_data],
    )


class PaginationMeta(BaseModel):
    total_items: int
    page: int
    page_size: int
    total_pages: int


class PaginatedDatasetResponse(BaseModel):
    items: List[ResourceDataset]
    meta: PaginationMeta


class DatasetCountsResponse(BaseModel):
    draft: int
    published: int
    completed: int
    validated: int
    approved: int
    internal_only: int
    deprecated: int
    total: int


class DatasetListRequest(BaseModel):
    status: str
    page: int = 1
    page_size: int = 10
    query: Optional[str] = None
    dataset_types: list[str] = []
    rights_statements: list[str] = []
    keywords: list[str] = []
    themes: list[str] = []
    applicable_legislations: list[str] = []
    periodicities: list[str] = []
    organisations: list[int] = []
    authentic_source_pending: Optional[bool] = None
    has_unlabeled_authentic_source: Optional[bool] = None
