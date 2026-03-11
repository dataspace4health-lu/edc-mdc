from itertools import chain
from typing import Any, List, Dict

from repositories import applicable_legislation
from dependencies.database import get_db_session
from fastapi import Depends, APIRouter
from models.dataset import (
    DatasetType,
    HealthCategory,
    HealthTheme,
    Keyword,
    Periodicity,
    Theme,
    SpatialCoverage,
    ApplicableLegislation,
)
from models.distribution import FileType, Language, License
from models.contact import Contact
from models.user import User
from models.data_service import DataService
from models.keyword_assignment import KeywordAssignment
from models.applicable_legislation_assignment import ApplicableLegislationAssignment
from models.organisation import Organisation
from schemas.form_field import Field, Form
from services.config import ConfigService, get_config_service
from sqlalchemy.orm import Session
from models.identity_context import IdentityContext
from schemas.data_service import DataServiceEndpointDto
from routes.auth import validate_and_retrieve_identity_context
from services.user import UserService
from services.organisation_cache import OrganisationCache, get_organisation_cache

router = APIRouter()


@router.get("/api/v1/form-fields", response_model=Form, tags=["front-end"])
def retrieve_form_fields(
    db_session: Session = Depends(get_db_session),
    config_service: ConfigService = Depends(get_config_service),
    organisation_cache: OrganisationCache = Depends(get_organisation_cache),
    user_service: UserService = Depends(UserService),
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:edit:draft:my",
                "datasets:edit:draft:organisation",
                "datasets:edit:draft:group",
                "datasets:edit:draft",
                "datasets:read:all-after-draft:organisation",
            ]
        )
    ),
) -> Form:
    values = [
        query_values(db_session, "dataset", "dataset_types", DatasetType),
        query_values(db_session, "dataset", "periodicities", Periodicity),
        query_values(db_session, "dataset", "themes", Theme),
        query_values(db_session, "dataset", "languages", Language),
        sorted(
            query_keywords(db_session, "dataset"),
            key=lambda field: field.value,
        ),
        query_values(db_session, "dataset", "health_categories", HealthCategory),
        query_values(db_session, "dataset", "health_themes", HealthTheme),
        query_values(db_session, "dataset", "spatial_coverages", SpatialCoverage),
        query_values(db_session, "distribution", "licenses", License),
        query_values(db_session, "distribution", "file_types", FileType),
        query_values(db_session, "distribution", "languages", Language),
        query_values(
            db_session, "distribution", "spatial_restrictions", SpatialCoverage
        ),
        query_organisations(organisation_cache),
        query_data_services(db_session),
        query_conventions(config_service),
        query_applicable_legislations_for_datasets(db_session),
        query_applicable_legislations_for_distributions(db_session),
        query_areas_of_work(config_service),
        query_areas_of_competence(config_service),
        query_contacts(db_session),
        query_distribution_path(config_service),
        query_group_managers(user_service),
    ]

    return build_form(list(chain.from_iterable(values)))


def query_values(
    db_session: Session, group_name: str, field_name: str, clazz: Any
) -> List[Field]:
    all_values = db_session.query(clazz).all()
    fields = list(
        map(
            lambda value: Field(
                group_name=group_name,
                field_name=field_name,
                value=value.key,
                label=value.eng_label,
                parent_value=getattr(value, "parent_key", None),
                organisation_ids=[],
            ),
            all_values,
        )
    )
    return fields


def query_organisations(organisation_cache: OrganisationCache) -> List[Field]:
    all_organisations = organisation_cache.get_all()
    sorted_organisations_by_name = sorted(
        all_organisations, key=lambda org: org.name.lower()
    )
    return list(
        map(
            lambda org: Field(
                group_name="organisation",
                field_name="organisations",
                value=str(org.id),
                label=org.name,
                parent_value=None,
                is_deprecated=org.is_deprecated,
                accessible_within_ctie=org.accessible_within_ctie,
            ),
            sorted_organisations_by_name,
        )
    )


def query_data_services(db_session: Session) -> List[Field]:
    all_data_services = db_session.query(DataService).all()
    sorted_data_services_by_name = sorted(
        all_data_services, key=lambda org: org.title.lower()
    )
    return list(
        map(
            lambda ds: Field(
                group_name="data_service",
                field_name="data_services",
                value=str(ds.id),
                label=ds.title,
                parent_value=None,
                endpoints=[
                    DataServiceEndpointDto(
                        endpoint_url=endpoint.endpoint_url,
                        endpoint_description=endpoint.endpoint_description,
                    )
                    for endpoint in ds.endpoints
                ],
            ),
            sorted_data_services_by_name,
        )
    )


def query_keywords(db_session: Session, group_name: str) -> List[Field]:
    all_keywords = db_session.query(Keyword).all()
    return [
        Field(
            group_name=group_name,
            field_name="keywords",
            value=keyword.key,
            label=keyword.eng_label,
            parent_value=keyword.parent_key,
            organisation_ids=[org.id for org in keyword.organisations],
        )
        for keyword in all_keywords
    ]


def query_applicable_legislations_for_datasets(db_session: Session) -> List[Field]:
    return _query_applicable_legislations(db_session, "dataset")


def query_applicable_legislations_for_distributions(db_session: Session) -> List[Field]:
    return _query_applicable_legislations(db_session, "distribution")


def _query_applicable_legislations(db_session: Session, group_name: str) -> List[Field]:
    all_applicable_legislations = db_session.query(ApplicableLegislation).all()
    return [
        Field(
            group_name=group_name,
            field_name="applicable_legislations",
            value=str(applicable_legislation.key),
            label=applicable_legislation.eng_label,
            parent_value=None,
            description=applicable_legislation.description,
            link=applicable_legislation.link,
            organisation_ids=[org.id for org in applicable_legislation.organisations],
        )
        for applicable_legislation in all_applicable_legislations
    ]


def query_contacts(db_session: Session) -> List[Field]:
    all_contacts = db_session.query(Contact).all()

    return [
        Field(
            group_name="contact",
            field_name="contacts",
            value=str(contact.id),
            label=f"{contact.name} ({contact.email})",
            parent_value=str(contact.organisation_id),
            is_deprecated=contact.is_deprecated,
        )
        for contact in all_contacts
    ]


def build_form(fields: List[Field]) -> Form:
    return Form.from_(fields)


def query_conventions(config_service: ConfigService) -> List[Field]:
    conventions = config_service.get_conventions()
    return [
        Field(
            group_name="dataset",
            field_name="conventions",
            value=convention["key"],
            label=convention["eng_label"],
            parent_value=None,
        )
        for convention in conventions
    ]


def query_areas_of_work(config_service: ConfigService) -> List[Field]:
    areas_of_work = config_service.get_areas_of_work()
    return [
        Field(
            group_name="dataset",
            field_name="areas_of_work",
            value=area_of_work["key"],
            label=area_of_work["eng_label"],
            parent_value=None,
        )
        for area_of_work in areas_of_work
    ]


def query_areas_of_competence(config_service: ConfigService) -> List[Field]:
    areas_of_competence = config_service.get_areas_of_competence()
    return [
        Field(
            group_name="dataset",
            field_name="areas_of_competence",
            value=area_of_competence["key"],
            label=area_of_competence["eng_label"],
            parent_value=None,
        )
        for area_of_competence in areas_of_competence
    ]


def query_distribution_path(config_service: ConfigService) -> List[Field]:
    distribution_path = config_service.get_distribution_path()
    return [
        Field(
            group_name="distribution",
            field_name="distribution_path",
            value=path["key"],
            label=path["eng_label"],
            parent_value=None,
        )
        for path in distribution_path
    ]


def query_group_managers(user_service: UserService) -> List[Field]:
    group_managers = user_service.find_dataset_validator_users()
    return [
        Field(
            group_name="dataset",
            field_name="group_managers",
            value=str(user.id),
            label=user.name,
            parent_value=None,
        )
        for user in group_managers
    ]
