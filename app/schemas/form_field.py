from collections import defaultdict
from dataclasses import dataclass, field
from typing import Union, Optional, Annotated, List
from pydantic import BaseModel, Field
from schemas.data_service import DataServiceEndpointDto


@dataclass(frozen=True)
class CreateFormFieldDto(BaseModel):
    eng_label: Annotated[
        str,
        Field(
            min_length=1, max_length=500, description="English label (1-500 characters)"
        ),
    ]
    organisation_ids: Optional[list[int]] = field(default_factory=list)


@dataclass(frozen=True)
class CreateApplicableLegislationFormFieldDto(CreateFormFieldDto):
    description: Annotated[
        str,
        Field(max_length=1000, description="Description (max 1000 characters)"),
    ]
    link: Annotated[
        str,
        Field(max_length=500, description="Link (max 500 characters)"),
    ]


@dataclass(frozen=True)
class FormFieldDto(BaseModel):
    key: Annotated[
        str,
        Field(min_length=1, max_length=100, description="Field key (1-100 characters)"),
    ]
    eng_label: Annotated[
        str,
        Field(
            min_length=1, max_length=500, description="English label (1-500 characters)"
        ),
    ]
    organisation_ids: Optional[list[int]] = field(default_factory=list)


@dataclass(frozen=True)
class ApplicableLegislationFormFieldDto(FormFieldDto):
    key: Annotated[
        str,
        Field(min_length=1, max_length=100, description="Field key (1-100 characters)"),
    ]
    description: Annotated[
        str,
        Field(max_length=1000, description="Description (max 1000 characters)"),
    ]
    link: Annotated[
        str,
        Field(max_length=500, description="Link (max 500 characters)"),
    ]


@dataclass(frozen=True)
class ResourceFormField(BaseModel):
    key: str
    eng_label: str
    organisation_ids: Optional[list[int]] = field(default_factory=list)
    created_by_id: Optional[int] = None
    created_by_name: Optional[str] = None


@dataclass(frozen=True)
class ApplicableLegislationFormField(ResourceFormField):
    description: str
    link: str


@dataclass(frozen=True)
class EnumValue:
    value: str
    eng_label: str


@dataclass(frozen=True)
class ApplicableLegislationEnumValue(EnumValue):
    organisation_ids: list[int] = field(default_factory=list)
    description: Union[str, None] = None
    link: Union[str, None] = None


@dataclass(frozen=True)
class HierarchicalEnumValue(EnumValue):
    parent_value: Union[str, None]


@dataclass(frozen=True)
class KeywordEnumValue(HierarchicalEnumValue):
    organisation_ids: list[int] = field(default_factory=list)


@dataclass(frozen=True)
class ContactEnumValue(HierarchicalEnumValue):
    is_deprecated: Optional[bool] = None


@dataclass(frozen=True)
class OrganisationEnumValue(EnumValue):
    is_deprecated: Optional[bool] = None
    accessible_within_ctie: Optional[bool] = None


@dataclass(frozen=True)
class DistributionForm:
    file_types: list[EnumValue]
    languages: list[EnumValue]
    licenses: list[EnumValue]
    distribution_path: list[EnumValue]
    applicable_legislations: list[ApplicableLegislationEnumValue]
    spatial_restrictions: list[EnumValue]


@dataclass(frozen=True)
class DatasetForm:
    dataset_types: list[EnumValue]
    periodicities: list[EnumValue]
    themes: list[EnumValue]
    keywords: list[KeywordEnumValue]
    health_categories: list[EnumValue]
    health_themes: list[EnumValue]
    spatial_coverages: list[EnumValue]
    applicable_legislations: list[ApplicableLegislationEnumValue]
    conventions: list[EnumValue]
    areas_of_work: list[EnumValue]
    areas_of_competence: list[EnumValue]
    group_managers: list[EnumValue]
    languages: list[EnumValue]


@dataclass(frozen=True)
class OrganisationForm:
    organisations: list[OrganisationEnumValue]


@dataclass(frozen=True)
class DataServiceEnumValue(EnumValue):
    endpoints: list[DataServiceEndpointDto]


@dataclass(frozen=True)
class DataServiceForm:
    data_services: list[DataServiceEnumValue]


@dataclass(frozen=True)
class ContactForm:
    contacts: list[ContactEnumValue]


@dataclass(frozen=True)
class Field:
    group_name: str
    field_name: str
    value: str
    label: str
    parent_value: Union[str, None]
    description: Optional[str] = None
    link: Optional[str] = None
    organisation_ids: list[int] = field(default_factory=list)
    endpoints: Optional[frozenset[DataServiceEndpointDto]] = None
    is_deprecated: Optional[bool] = None
    accessible_within_ctie: Optional[bool] = None

    def to_enum_value(self) -> EnumValue:
        if self.field_name == "keywords":
            return KeywordEnumValue(
                self.value,
                self.label,
                self.parent_value,
                self.organisation_ids,
            )
        if self.group_name == "contact":
            return ContactEnumValue(
                self.value, self.label, self.parent_value, self.is_deprecated
            )
        if self.field_name == "applicable_legislations":
            return ApplicableLegislationEnumValue(
                self.value,
                self.label,
                self.organisation_ids,
                self.description,
                self.link,
            )
        if self.field_name == "data_services":
            return DataServiceEnumValue(self.value, self.label, self.endpoints)

        if self.field_name == "organisations":
            return OrganisationEnumValue(
                self.value, self.label, self.is_deprecated, self.accessible_within_ctie
            )

        return EnumValue(self.value, self.label)


@dataclass(frozen=True)
class Form:
    dataset: DatasetForm
    distribution: DistributionForm
    organisation: OrganisationForm
    data_service: DataServiceForm
    contact: ContactForm

    @staticmethod
    def from_(fields: list[Field]) -> "Form":
        dataset_fields = defaultdict(
            lambda: [],
            {
                "keywords": [],
                "spatial_coverages": [],
                "conventions": [],
                "areas_of_work": [],
                "areas_of_competence": [],
                "applicable_legislations": [],
                "themes": [],
                "periodicities": [],
                "dataset_types": [],
                "group_managers": [],
                "health_categories": [],
                "health_themes": [],
                "languages": [],
            },
        )
        distribution_fields = defaultdict(
            lambda: [],
            {
                "distribution_path": [],
                "applicable_legislations": [],
                "spatial_restrictions": [],
                "file_types": [],
                "languages": [],
                "licenses": [],
            },
        )
        organisation_fields = defaultdict(lambda: [], {"organisations": []})
        data_service_fields = defaultdict(lambda: [], {"data_services": []})
        contact_fields = defaultdict(lambda: [], {"contacts": []})

        for field in fields:
            if field.group_name == "dataset":
                dataset_fields[field.field_name].append(field.to_enum_value())
            elif field.group_name == "distribution":
                distribution_fields[field.field_name].append(field.to_enum_value())
            elif field.group_name == "organisation":
                organisation_fields[field.field_name].append(field.to_enum_value())
            elif field.group_name == "data_service":
                data_service_fields[field.field_name].append(field.to_enum_value())
            elif field.group_name == "contact":
                contact_fields[field.field_name].append(field.to_enum_value())

        return Form(
            DatasetForm(**dataset_fields),
            DistributionForm(**distribution_fields),
            OrganisationForm(**organisation_fields),
            DataServiceForm(**data_service_fields),
            ContactForm(**contact_fields),
        )


class PaginationMeta(BaseModel):
    total_items: int
    page: int
    page_size: int
    total_pages: int


class PaginatedFormFieldResponse(BaseModel):
    items: Union[
        List[ResourceFormField],
        List[ApplicableLegislationFormField],
    ]
    meta: PaginationMeta


class FormFieldListRequest(BaseModel):
    page: int = 1
    page_size: int = 10
    query: Optional[str] = None
    organisation_filters: Optional[List[str]] = None
