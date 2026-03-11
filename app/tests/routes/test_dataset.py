from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from conftest import db_session
from fastapi.testclient import TestClient
from main import app
from dependencies.database import Base
from models.dataset import (
    Dataset,
    DatasetSpatialResolution,
    DatasetStatus,
)
from models.dataset_comment import DatasetComment
from models.dataset_relation import DatasetRelation
from models.distribution import Distribution
from repositories.dataset_comment import DatasetCommentRepository
from schemas.dataset import DatasetDto, DistributionDto
from services.config import ConfigService
from sqlalchemy.orm import Session
from test_factory import (
    client_with_logged_in_user,
    dataset_dto,
    sample_dataset,
    sample_dataset_with_relation,
)


@pytest.fixture(autouse=True)
def clean_db(db_session):
    yield
    tables_to_skip = {
        "keyword",
        "dataset_type",
        "periodicity",
        "theme",
        "language",
        "spatial_coverage",
        "applicable_legislation",
        "file_type",
        "license",
    }

    for table in reversed(Base.metadata.sorted_tables):
        if table.name not in tables_to_skip:
            db_session.execute(table.delete())

    db_session.commit()


@pytest.fixture
def dataset_comment_repository(db_session: Session) -> DatasetCommentRepository:
    return DatasetCommentRepository(db_session)


@pytest.fixture
def client():
    config_service = ConfigService(config_file_path="./config.json")
    config_service.get_roles = MagicMock(return_value=[])
    app.state.config_service = config_service
    return TestClient(app)


def test_retrieve_dataset(client_with_logged_in_user, sample_dataset):
    response = client_with_logged_in_user.get(f"/api/v1/datasets/{sample_dataset.id}")
    assert response.status_code == 200
    dataset = response.json()
    assert dataset["id"] == sample_dataset.id
    assert dataset["title"] == sample_dataset.title
    assert dataset["identifier"] == sample_dataset.identifier


def test_create_dataset(client_with_logged_in_user, dataset_dto):
    response = client_with_logged_in_user.post(
        "/api/v1/datasets", json=dataset_dto.model_dump(mode="json")
    )
    assert response.status_code == 200
    created_dataset = response.json()
    assert created_dataset["title"] == dataset_dto.title
    assert created_dataset["description"] == dataset_dto.description
    assert "identifier" in created_dataset
    assert created_dataset["identifier"] is not None
    assert len(created_dataset["identifier"]) == 36


def test_edit_dataset(client_with_logged_in_user, sample_dataset, dataset_dto):
    updated_title = "Updated Test Dataset"

    updated_dataset_dto = DatasetDto(
        status=dataset_dto.status,
        title=updated_title,
        description=dataset_dto.description,
        contact_ids=dataset_dto.contact_ids,
        publisher_id=dataset_dto.publisher_id,
        time_period_start=dataset_dto.time_period_start,
        time_period_end=dataset_dto.time_period_end,
        retention_period_start=dataset_dto.retention_period_start,
        retention_period_end=dataset_dto.retention_period_end,
        rights_statement=dataset_dto.rights_statement,
        periodicity=dataset_dto.periodicity,
        creator_ids=dataset_dto.creator_ids,
        dataset_types=dataset_dto.dataset_types,
        themes=dataset_dto.themes,
        keywords=dataset_dto.keywords,
        health_categories=dataset_dto.health_categories,
        health_themes=dataset_dto.health_themes,
        spatial_coverages=dataset_dto.spatial_coverages,
        conventions=dataset_dto.conventions,
        areas_of_work=dataset_dto.areas_of_work,
        areas_of_competence=dataset_dto.areas_of_competence,
        applicable_legislations=dataset_dto.applicable_legislations,
        notes=dataset_dto.notes,
        duration_of_administrative_utility=dataset_dto.duration_of_administrative_utility,
        max_typical_age=dataset_dto.max_typical_age,
        min_typical_age=dataset_dto.min_typical_age,
        number_of_records=dataset_dto.number_of_records,
        number_of_unique_individuals=dataset_dto.number_of_unique_individuals,
        final_disposition=dataset_dto.final_disposition,
        version=dataset_dto.version,
        version_change_type=dataset_dto.version_change_type,
        release_date=dataset_dto.release_date,
        modified_at=dataset_dto.modified_at,
        deprecated_at=dataset_dto.deprecated_at,
        released_at=dataset_dto.released_at,
        was_generated_by=[],
        other_identifiers=[],
        version_notes=dataset_dto.version_notes,
        spatial_resolutions=[1],
        temporal_resolution="P10D",
        personal_data=dataset_dto.personal_data,
        distributions=[
            DistributionDto(
                title=dist.title,
                description=dist.description,
                download_urls=dist.download_urls,
                access_urls=dist.access_urls,
                file_type=dist.file_type,
                rights_statement=dist.rights_statement,
                internal_only=dist.internal_only,
                applicable_legislations=dist.applicable_legislations,
                languages=dist.languages,
                notes=dist.notes,
                license=dist.license,
                distribution_path=dist.distribution_path,
                availability=dist.availability,
                documentation=dist.documentation,
                linked_schemas=["DCAT-AP"],
                modification_date=dist.modification_date,
                release_date=dist.release_date,
                byte_size=dist.byte_size,
                checksum=dist.checksum,
                policy_actions=getattr(dist, "policy_actions", ()),
                media_type=dist.media_type,
                compression_format=dist.compression_format,
                packaging_format=dist.packaging_format,
                distribution_dcat_status=dist.distribution_dcat_status,
                spatial_resolution=dist.spatial_resolution,
                temporal_resolution=dist.temporal_resolution,
                access_service_ids=frozenset(),
            )
            for dist in dataset_dto.distributions
        ],
        group_managers=dataset_dto.group_managers,
        data_protection_types=dataset_dto.data_protection_types,
        monitoring_location=dataset_dto.monitoring_location,
        provenance=dataset_dto.provenance,
        health_legal_basis=dataset_dto.health_legal_basis,
        population_coverage=dataset_dto.population_coverage,
        code_values=dataset_dto.code_values,
        purpose=dataset_dto.purpose,
        coding_systems=dataset_dto.coding_systems,
        languages=dataset_dto.languages,
        landing_pages=dataset_dto.landing_pages,
        documentation=dataset_dto.documentation,
        conforms_to=dataset_dto.conforms_to,
        is_dataset_series=dataset_dto.is_dataset_series,
        member_datasets=dataset_dto.member_datasets,
        source=dataset_dto.source,
        source_dataset_id=dataset_dto.source_dataset_id,
    )

    response = client_with_logged_in_user.put(
        f"/api/v1/datasets/{sample_dataset.id}",
        json=updated_dataset_dto.model_dump(mode="json"),
    )
    assert response.status_code == 200
    updated_dataset = response.json()
    assert updated_dataset["id"] == sample_dataset.id
    assert updated_dataset["title"] == updated_title


def test_retrieve_nonexistent_dataset(client_with_logged_in_user):
    non_existent_id = 9999
    response = client_with_logged_in_user.get(f"/api/v1/datasets/{non_existent_id}")
    assert response.status_code == 404


def test_edit_nonexistent_dataset(client_with_logged_in_user, dataset_dto):
    non_existent_id = 9999
    response = client_with_logged_in_user.put(
        f"/api/v1/datasets/{non_existent_id}",
        json=dataset_dto.model_dump(mode="json"),
    )
    assert response.status_code == 404


def test_retrieve_dataset_with_relations(
    client_with_logged_in_user, sample_dataset_with_relation
):
    response = client_with_logged_in_user.get(
        f"/api/v1/datasets/{sample_dataset_with_relation.id}"
    )
    assert response.status_code == 200
    dataset = response.json()
    assert dataset["id"] == sample_dataset_with_relation.id
    assert dataset["title"] == sample_dataset_with_relation.title
    assert dataset["identifier"] == sample_dataset_with_relation.identifier

    assert "source_relations" in dataset
    assert len(dataset["source_relations"]) > 0

    relation = dataset["source_relations"][0]
    assert relation["title"] == "Related Dataset"
    assert relation["internal_only"] == True
    assert relation["relation_type"] == "dct:isPartOf"


# def test_retrieve_dataset_with_qualified_relations(
#     client_with_logged_in_user, db_session, sample_dataset
# ):
#     db_session.query(DatasetQualifiedRelationEntry).filter_by(
#         source_dataset=sample_dataset.id
#     ).delete()

#     qualified_relation = DatasetQualifiedRelationEntry(
#         source_dataset=sample_dataset.id,
#         qualified_relation_url="https://example.com/qualified-relation",
#         qualified_relation_role="hasPart",
#         qualified_relation_description="This dataset is a qualified part of another dataset.",
#     )
#     db_session.add(qualified_relation)
#     db_session.commit()

#     response = client_with_logged_in_user.get(
#         f"/api/v1/datasets/{sample_dataset.id}/qualified-relations"
#     )
#     assert response.status_code == 200

#     relations = response.json()
#     assert isinstance(relations, list)
#     assert len(relations) == 1

#     relation = next(
#         (
#             r
#             for r in relations
#             if r["qualified_relation_url"] == "https://example.com/qualified-relation"
#         ),
#         None,
#     )
#     assert relation is not None, "Expected qualified relation not found in response"
#     assert relation["source_dataset"] == sample_dataset.id
#     assert relation["qualified_relation_role"] == "hasPart"
#     assert relation["qualified_relation_description"] == (
#         "This dataset is a qualified part of another dataset."
#     )


def test_update_dataset_status(
    client,
    db_session,
    client_with_logged_in_user,
    sample_dataset,
    dataset_comment_repository,
):
    new_status = "complete"

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{sample_dataset.id}/status/{new_status}",
        json={"comment": "Test comment", "action_type": "add_comment"},
    )

    dataset = response.json()
    assert response.status_code == 200
    assert dataset["status"] == DatasetStatus.COMPLETED.value

    comments = dataset_comment_repository.get_dataset_comments(sample_dataset.id)
    assert len(comments) == 1
    assert comments[0].content == "Test comment"


def test_update_dataset_status_without_comment(
    client, db_session, client_with_logged_in_user, sample_dataset
):
    new_status = "complete"

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{sample_dataset.id}/status/{new_status}", json={}
    )

    assert response.status_code == 200


def test_update_status_invalid_transition(
    db_session, client_with_logged_in_user, sample_dataset
):
    new_status = "publish"

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{sample_dataset.id}/status/{new_status}",
        json={"comment": "Test comment"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Transition not allowed."


def test_clone_dataset(client_with_logged_in_user, sample_dataset):
    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{sample_dataset.id}/clone"
    )
    assert response.status_code == 200
    cloned_dataset = response.json()

    assert (
        cloned_dataset["title"] == "Clone - " + sample_dataset.title
    ), f"Cloned dataset title mismatch: expected 'Clone - {sample_dataset.title}', got '{cloned_dataset['title']}'"
    assert (
        cloned_dataset["description"] == sample_dataset.description
    ), "Cloned dataset description does not match the original"
    assert (
        cloned_dataset["identifier"] != sample_dataset.identifier
    ), "Cloned dataset should have a new unique identifier"
    assert (
        cloned_dataset["status"] == DatasetStatus.DRAFT.value
    ), "Cloned dataset status should be set to draft"

    assert (
        cloned_dataset["time_period_start"]
        == sample_dataset.time_period_start.isoformat()
    ), "Mismatch in time_period_start"
    assert cloned_dataset["time_period_end"] == (
        sample_dataset.time_period_end.isoformat()
        if sample_dataset.time_period_end
        else None
    ), "Mismatch in time_period_end"

    assert len(cloned_dataset.get("distributions", [])) == 2

    cloned_theme_keys = {theme["value"] for theme in cloned_dataset["themes"]}
    sample_theme_keys = {theme.value.key for theme in sample_dataset.themes}
    assert (
        cloned_theme_keys == sample_theme_keys
    ), "Themes not cloned properly: expected keys {sample_theme_keys}, but got {cloned_theme_keys}"

    cloned_qualified_attribution_keys = {
        qa if isinstance(qa, int) else qa["value"]
        for qa in cloned_dataset["qualified_attributions"]
    }
    sample_qualified_attribution_keys = {
        qualified_attribution.organisation_id
        for qualified_attribution in sample_dataset.qualified_attributions
    }
    assert (
        cloned_qualified_attribution_keys == sample_qualified_attribution_keys
    ), "Qualified attributions not cloned properly: expected keys {sample_qualified_attribution_keys}, but got {cloned_qualified_attribution_keys}"

    cloned_keyword_keys = {keyword["value"] for keyword in cloned_dataset["keywords"]}
    sample_keyword_keys = {keyword.value.key for keyword in sample_dataset.keywords}
    assert cloned_keyword_keys == sample_keyword_keys, "Keywords not cloned properly"

    cloned_coverage_keys = {
        coverage["value"] for coverage in cloned_dataset["spatial_coverages"]
    }
    sample_coverage_keys = {
        coverage.value.key for coverage in sample_dataset.spatial_coverages
    }
    assert (
        cloned_coverage_keys == sample_coverage_keys
    ), "Spatial coverages not cloned properly"

    cloned_convention_values = set(cloned_dataset["conventions"])
    sample_convention_values = {
        convention.key for convention in sample_dataset.conventions
    }
    assert (
        cloned_convention_values == sample_convention_values
    ), "Conventions not cloned properly"

    cloned_area_of_work_values = set(cloned_dataset["areas_of_work"])
    sample_area_of_work_values = {
        area_of_work.key for area_of_work in sample_dataset.areas_of_work
    }
    assert (
        cloned_area_of_work_values == sample_area_of_work_values
    ), "Area of work not cloned properly"

    cloned_area_of_competence_values = set(cloned_dataset["areas_of_competence"])
    sample_area_of_competence_values = {
        area_of_competence.key
        for area_of_competence in sample_dataset.areas_of_competence
    }
    assert (
        cloned_area_of_competence_values == sample_area_of_competence_values
    ), "Area of competence not cloned properly"
    cloned_dpt_keys = set(cloned_dataset["data_protection_types"])
    sample_dpt_keys = {dpt.key for dpt in sample_dataset.data_protection_types}
    assert (
        cloned_dpt_keys == sample_dpt_keys
    ), "Data protection types not cloned properly"

    cloned_types_keys = {dtype["value"] for dtype in cloned_dataset["dataset_types"]}
    sample_types_keys = {dtype.value.key for dtype in sample_dataset.dataset_types}
    assert cloned_types_keys == sample_types_keys, "Dataset types not cloned properly"

    cloned_bases_keys = set(cloned_dataset["applicable_legislations"])
    sample_bases_keys = {base.key for base in sample_dataset.applicable_legislations}
    assert (
        cloned_bases_keys == sample_bases_keys
    ), "Applicable Legislations are not cloned properly"

    cloned_manager_ids = set(cloned_dataset.get("group_manager_ids", []))
    sample_manager_ids = (
        {gm.user.id for gm in sample_dataset.group_managers}
        if sample_dataset.group_managers
        else set()
    )
    assert (
        cloned_manager_ids == sample_manager_ids
    ), "Group managers not cloned properly: expected {sample_manager_ids}, got {cloned_manager_ids}"

    cloned_personal_data = list(cloned_dataset["personal_data"])
    sample_personal_data = [pd.key for pd in sample_dataset.personal_data]
    assert (
        cloned_personal_data == sample_personal_data
    ), "Personal data not cloned properly"

    assert (
        cloned_dataset["submitted_at"] != sample_dataset.submitted_at
    ), "Cloned dataset should have a new submitted_at timestamp"
    assert (
        cloned_dataset["modified_at"] != sample_dataset.modified_at
    ), "Cloned dataset should have a new modified_at timestamp"
    assert (
        cloned_dataset["deprecated_at"] != sample_dataset.deprecated_at
    ), "Cloned dataset should have a new deprecated_at timestamp"
    assert (
        cloned_dataset["release_date"] != sample_dataset.release_date
    ), "Cloned dataset should have a new release_date timestamp"


def test_delete_dataset(client_with_logged_in_user, sample_dataset):
    response = client_with_logged_in_user.delete(
        f"/api/v1/datasets/{sample_dataset.id}"
    )
    assert response.status_code == 204


def test_paginated_datasets_with_published_status_and_public_rights_statement(
    client_with_logged_in_user, sample_dataset, db_session
):
    sample_dataset.status = DatasetStatus.PUBLISHED.value
    sample_dataset.rights_statement = "NON_PUBLIC"
    sample_dataset.health_categories = set()
    db_session.commit()

    response = client_with_logged_in_user.post(
        "/api/v1/paginated_datasets",
        json={
            "status": "PUBLISHED",
            "page": 1,
            "page_size": 10,
            "rights_statements": ["NON_PUBLIC"],
        },
    )

    assert response.status_code == 200
    result = response.json()

    assert "items" in result
    assert "meta" in result
    assert "total_items" in result["meta"]
    assert "page" in result["meta"]
    assert "page_size" in result["meta"]
    assert "total_pages" in result["meta"]

    dataset_ids = [item["id"] for item in result["items"]]
    assert sample_dataset.id in dataset_ids


def test_dataset_counts(
    client_with_logged_in_user,
    db_session,
    sample_dataset,
):
    sample_dataset.health_categories = set()
    db_session.commit()

    response = client_with_logged_in_user.get("/api/v1/datasets/counts")
    assert response.status_code == 200
    counts = response.json()
    # assert counts["draft"] == 1
    assert counts["published"] == 0
    assert counts["completed"] == 0
    assert counts["validated"] == 0
    assert counts["approved"] == 0
    assert counts["internal_only"] == 0
    assert counts["total"] == 1


def test_create_dataset_version(
    client_with_logged_in_user, db_session, sample_dataset, monkeypatch
):
    sample_dataset.status = DatasetStatus.PUBLISHED.value
    db_session.commit()

    # Patch to prevent duplicate conflict during version creation
    monkeypatch.setattr(
        "services.dataset.DatasetRepository.exists_by_title_description_publisher",
        lambda self, title, desc, pub_id: False,
    )

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{sample_dataset.id}/version"
    )

    assert response.status_code == 200

    new_version = response.json()

    assert new_version["id"] != sample_dataset.id
    assert (
        new_version["identifier"] == sample_dataset.identifier
    )  # Versions share the same identifier
    assert new_version["status"] == DatasetStatus.DRAFT.value


def test_create_dataset_version_fails_if_not_published(
    client_with_logged_in_user, db_session, sample_dataset
):
    sample_dataset.status = DatasetStatus.DRAFT.value
    db_session.commit()

    response = client_with_logged_in_user.post(
        f"/api/v1/datasets/{sample_dataset.id}/version"
    )

    assert response.status_code == 403 or response.status_code == 400
    assert "detail" in response.json()


def test_get_dataset_versions_chain_with_versions(
    client_with_logged_in_user, db_session, sample_dataset, monkeypatch
):
    sample_dataset.status = DatasetStatus.PUBLISHED.value
    db_session.commit()

    # Patch to prevent duplicate conflict during version creation
    monkeypatch.setattr(
        "services.dataset.DatasetRepository.exists_by_title_description_publisher",
        lambda self, title, desc, pub_id: False,
    )

    response1 = client_with_logged_in_user.post(
        f"/api/v1/datasets/{sample_dataset.id}/version"
    )
    assert response1.status_code == 200
    version1 = response1.json()

    dataset1 = db_session.query(Dataset).get(version1["id"])
    dataset1.status = DatasetStatus.PUBLISHED.value
    db_session.commit()

    response2 = client_with_logged_in_user.post(
        f"/api/v1/datasets/{version1['id']}/version"
    )
    assert response2.status_code == 200
    version2 = response2.json()

    response_chain = client_with_logged_in_user.get(
        f"/api/v1/datasets/{version2['id']}/versions-chain"
    )
    assert response_chain.status_code == 200
    data = response_chain.json()

    print("Versions chain:", [d["id"] for d in data])
    assert len(data) == 3

    assert data[0]["id"] == sample_dataset.id
