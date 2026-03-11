from dataclasses import dataclass, field
from datetime import date
from typing import FrozenSet, Optional, Union, Annotated, Tuple
from urllib.parse import unquote

from pydantic import (
    AnyUrl,
    BaseModel,
    Field,
    model_validator,
    field_validator,
    ConfigDict,
)

from models.distribution import Distribution
from schemas.data_service import ResourceDataService, data_service_entity_to_resource
from schemas.form_field import EnumValue
from validators.temporal_resolution_validator import validate_temporal_resolution


class PolicyActionDto(BaseModel):
    model_config = ConfigDict(frozen=True)

    policy_action_type: Annotated[
        str,
        Field(max_length=100, description="Policy action type (max 100 characters)"),
    ]
    policy_constraint_type: Optional[
        Annotated[
            str,
            Field(
                max_length=100,
                description="Policy constraint type (max 100 characters)",
            ),
        ]
    ] = None
    policy_constraint_value: Optional[
        Annotated[
            str,
            Field(
                max_length=200,
                description="Policy constraint value (max 200 characters)",
            ),
        ]
    ] = None
    temporal_restriction_start: Optional[date] = None
    temporal_restriction_end: Optional[date] = None
    spatial_restrictions: frozenset[str] = Field(default_factory=frozenset)


@dataclass(frozen=True)
class ResourcePolicyAction:
    policy_action_type: str
    policy_constraint_type: Optional[str]
    policy_constraint_value: Optional[str]
    temporal_restriction_start: Optional[str] = None
    temporal_restriction_end: Optional[str] = None
    spatial_restrictions: FrozenSet[EnumValue] = field(default_factory=frozenset)


class DistributionDto(BaseModel):
    model_config = ConfigDict(frozen=True)

    title: Optional[
        Annotated[
            str,
            Field(
                min_length=1,
                max_length=500,
                description="Distribution title (1-500 characters)",
            ),
        ]
    ] = None
    description: Optional[
        Annotated[
            str,
            Field(
                min_length=8,
                max_length=2000,
                description="Distribution description (8-2000 characters)",
            ),
        ]
    ] = None
    download_urls: list[AnyUrl] = Field(default_factory=list)
    access_urls: list[AnyUrl] = Field(min_length=1)
    file_type: Union[str, None] = None
    rights_statement: Annotated[
        str,
        Field(
            min_length=1,
            max_length=500,
            description="Rights statement (1-500 characters)",
        ),
    ]
    internal_only: bool = False
    is_analytics: bool = False
    applicable_legislations: frozenset[str] = Field(default_factory=frozenset)
    languages: frozenset[str] = Field()
    notes: Optional[
        Annotated[
            str, Field(max_length=2000, description="Notes (max 2000 characters)")
        ]
    ] = None
    license: Optional[
        Annotated[
            str,
            Field(
                min_length=1, max_length=100, description="License (1-100 characters)"
            ),
        ]
    ] = None
    distribution_path: Optional[
        Annotated[
            str,
            Field(max_length=500, description="Distribution path (max 500 characters)"),
        ]
    ] = None
    policy_actions: Tuple[PolicyActionDto, ...] = Field(default_factory=tuple)
    availability: Optional[
        Annotated[
            str, Field(max_length=100, description="Availability (max 100 characters)")
        ]
    ] = None
    documentation: list[Annotated[str, Field(max_length=2000)]] = Field(
        default_factory=list
    )
    modification_date: Optional[date] = None
    release_date: Optional[date] = None
    linked_schemas: list[str] = Field(default_factory=list)
    byte_size: Optional[int] = None
    checksum: Optional[
        Annotated[
            str, Field(max_length=128, description="Checksum (max 128 characters)")
        ]
    ] = None
    media_type: Optional[
        Annotated[
            str, Field(max_length=100, description="Media type (max 100 characters)")
        ]
    ] = None
    compression_format: Optional[
        Annotated[
            str,
            Field(
                max_length=100, description="Compression format (max 100 characters)"
            ),
        ]
    ] = None
    packaging_format: Optional[
        Annotated[
            str,
            Field(max_length=100, description="Packaging format (max 100 characters)"),
        ]
    ] = None
    distribution_dcat_status: Optional[
        Annotated[
            str, Field(max_length=100, description="DCAT status (max 100 characters)")
        ]
    ] = None
    spatial_resolution: Optional[int] = None
    temporal_resolution: Optional[
        Annotated[
            str,
            Field(
                max_length=100, description="Temporal resolution (max 100 characters)"
            ),
        ]
    ] = None
    access_service_ids: frozenset[int] = Field(default_factory=frozenset)

    @model_validator(mode="after")
    def validate_temporal_restriction_date_fields(cls, values):
        for action in getattr(values, "policy_actions", ()):
            constraint_type = getattr(action, "policy_constraint_type", None)
            start = getattr(action, "temporal_restriction_start", None)
            end = getattr(action, "temporal_restriction_end", None)
            if constraint_type == "temporal" and not (start or end):
                raise ValueError(
                    "At least one of 'temporal_restriction_start' or 'temporal_restriction_end' must be provided when Policy Constraint Type is 'temporal'."
                )
        return values

    @model_validator(mode="after")
    def validate_spatial_restrictions(cls, values):
        for action in getattr(values, "policy_actions", ()):
            constraint_type = getattr(action, "policy_constraint_type", None)
            srs = getattr(action, "spatial_restrictions", frozenset())
            if constraint_type == "spatial" and len(srs) == 0:
                raise ValueError(
                    "At least one spatial restriction must be provided when Policy Constraint Type is 'spatial'."
                )
        return values

    @field_validator("spatial_resolution")
    @classmethod
    def validate_spatial_resolution(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and value < 0:
            raise ValueError("Spatial resolution must be a non-negative integer")
        return value

    @field_validator("temporal_resolution")
    @classmethod
    def validate_temporal_resolution_field(cls, value: Optional[str]) -> Optional[str]:
        return validate_temporal_resolution(value)

    @field_validator("documentation", mode="before")
    @classmethod
    def validate_documentation(cls, value):
        if value is None:
            return []
        if isinstance(value, (list, tuple)):
            # Strip whitespace and filter out empty strings
            return [str(v).strip() for v in value if v and str(v).strip()]
        return []


@dataclass(frozen=True)
class ResourceDistribution:
    id: int
    title: str
    description: Union[str, None]
    dataset_id: int
    distribution_dcat_status: Union[str, None]
    download_urls: Tuple[str, ...]
    access_urls: Tuple[str, ...]
    file_type: Union[EnumValue, None]
    rights_statement: str
    languages: FrozenSet[EnumValue]
    internal_only: Union[bool, None]
    is_analytics: Union[bool, None]
    applicable_legislations: FrozenSet[str]
    notes: Union[str, None]
    license: Union[EnumValue, None]
    distribution_path: Union[str, None]
    availability: Union[str, None]
    linked_schemas: Tuple[str, ...]
    access_services: FrozenSet[ResourceDataService]
    modification_date: Union[str, None] = None
    release_date: Union[str, None] = None
    documentation: Tuple[str, ...] = field(default_factory=tuple)
    byte_size: Optional[int] = None
    checksum: Optional[str] = None
    policy_actions: Tuple[ResourcePolicyAction, ...] = field(default_factory=tuple)
    media_type: Optional[str] = None
    compression_format: Optional[str] = None
    packaging_format: Optional[str] = None
    spatial_resolution: Optional[int] = None
    temporal_resolution: Optional[str] = None

    def __post_init__(self):
        object.__setattr__(self, "policy_actions", tuple(self.policy_actions))


def distribution_entity_to_resource(distribution: Distribution) -> ResourceDistribution:
    entity_top_srs = [
        EnumValue(sr.value.key, sr.value.eng_label)
        for sr in getattr(distribution, "spatial_restrictions", set())
        if getattr(sr, "value", None)
    ]
    from_actions_srs = [
        EnumValue(sr.value.key, sr.value.eng_label)
        for action in getattr(distribution, "policy_actions", [])
        for sr in getattr(action, "spatial_restrictions", set())
        if getattr(sr, "value", None)
    ]
    spatial_restrictions_union: FrozenSet[EnumValue] = frozenset(
        entity_top_srs or from_actions_srs
    )

    return ResourceDistribution(
        id=distribution.id,
        title=distribution.title,
        description=distribution.description,
        dataset_id=distribution.dataset_id,
        download_urls=(
            tuple(
                unquote(download_urls.url)
                for download_urls in distribution.download_urls
            )
            if distribution.download_urls
            else ()
        ),
        access_urls=(
            tuple(unquote(access_url.url) for access_url in distribution.access_urls)
            if distribution.access_urls
            else ()
        ),
        file_type=(
            EnumValue(
                distribution.file_type_value.key, distribution.file_type_value.eng_label
            )
            if getattr(distribution, "file_type_value", None)
            else None
        ),
        rights_statement=distribution.rights_statement,
        internal_only=distribution.internal_only,
        is_analytics=distribution.is_analytics,
        applicable_legislations=frozenset(
            [
                it.applicable_legislation.key
                for it in distribution.applicable_legislations
                if it.applicable_legislation
            ]
        ),
        languages=frozenset(
            [
                EnumValue(it.value.key, it.value.eng_label)
                for it in distribution.languages
                if it.value
            ]
        ),
        notes=distribution.notes,
        license=(
            EnumValue(
                distribution.license_value.key, distribution.license_value.eng_label
            )
            if getattr(distribution, "license_value", None)
            else None
        ),
        distribution_path=distribution.distribution_path,
        availability=distribution.availability,
        documentation=(
            tuple(doc.value for doc in distribution.documentation_entries)
            if distribution.documentation_entries
            else ()
        ),
        modification_date=(
            distribution.modification_date.isoformat()
            if distribution.modification_date
            else None
        ),
        release_date=(
            distribution.release_date.isoformat() if distribution.release_date else None
        ),
        access_services=frozenset(
            [
                data_service_entity_to_resource(ds.data_service)
                for ds in distribution.access_services
            ]
        ),
        linked_schemas=tuple(it.key for it in distribution.linked_schemas),
        byte_size=distribution.byte_size,
        checksum=distribution.checksum,
        policy_actions=tuple(
            ResourcePolicyAction(
                policy_action_type=action.policy_action_type,
                policy_constraint_type=action.policy_constraint_type,
                policy_constraint_value=action.policy_constraint_value,
                temporal_restriction_start=(
                    action.temporal_restriction_start.isoformat()
                    if action.temporal_restriction_start
                    else None
                ),
                temporal_restriction_end=(
                    action.temporal_restriction_end.isoformat()
                    if action.temporal_restriction_end
                    else None
                ),
                spatial_restrictions=frozenset(
                    [
                        EnumValue(sr.value.key, sr.value.eng_label)
                        for sr in getattr(action, "spatial_restrictions", set())
                        if getattr(sr, "value", None)
                    ]
                ),
            )
            for action in getattr(distribution, "policy_actions", [])
        ),
        media_type=distribution.media_type,
        compression_format=distribution.compression_format,
        packaging_format=distribution.packaging_format,
        distribution_dcat_status=distribution.distribution_dcat_status,
        spatial_resolution=distribution.spatial_resolution,
        temporal_resolution=distribution.temporal_resolution,
    )


def generate_distribution_dto_from_distribution(
    distribution: Distribution,
) -> DistributionDto:
    return DistributionDto(
        title=distribution.title,
        description=distribution.description,
        download_urls=(
            [download_urls.url for download_urls in distribution.download_urls]
            if distribution.download_urls
            else []
        ),
        access_urls=(
            [access_url.url for access_url in distribution.access_urls]
            if distribution.access_urls
            else []
        ),
        file_type=distribution.file_type,
        rights_statement=distribution.rights_statement,
        internal_only=distribution.internal_only,
        is_analytics=(
            distribution.is_analytics
            if distribution.is_analytics is not None
            else False
        ),
        applicable_legislations=[
            basis.key for basis in distribution.applicable_legislations
        ],
        languages=[lang.key for lang in distribution.languages],
        notes=distribution.notes,
        license=distribution.license,
        distribution_path=distribution.distribution_path,
        availability=distribution.availability,
        documentation=(
            [doc.value for doc in distribution.documentation_entries]
            if distribution.documentation_entries
            else []
        ),
        modification_date=distribution.modification_date,
        release_date=distribution.release_date,
        linked_schemas=[schema.key for schema in distribution.linked_schemas],
        byte_size=distribution.byte_size,
        checksum=distribution.checksum,
        policy_actions=tuple(
            PolicyActionDto(
                policy_action_type=action.policy_action_type,
                policy_constraint_type=action.policy_constraint_type,
                policy_constraint_value=action.policy_constraint_value,
                temporal_restriction_start=action.temporal_restriction_start,
                temporal_restriction_end=action.temporal_restriction_end,
                spatial_restrictions=frozenset(
                    [sr.key for sr in getattr(action, "spatial_restrictions", set())]
                ),
            )
            for action in getattr(distribution, "policy_actions", [])
        ),
        media_type=distribution.media_type,
        compression_format=distribution.compression_format,
        packaging_format=distribution.packaging_format,
        distribution_dcat_status=distribution.distribution_dcat_status,
        spatial_resolution=distribution.spatial_resolution,
        temporal_resolution=distribution.temporal_resolution,
        access_service_ids=frozenset(
            [ds.data_service_id for ds in distribution.access_services]
        ),
    )
