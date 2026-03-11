from datetime import UTC, date, datetime
from unittest.mock import Mock, call
from urllib.parse import urlparse
from fastapi import HTTPException, status
from unittest.mock import MagicMock

import pytest
from deepdiff import DeepDiff
from models.dataset import Dataset, DatasetStatus
from models.distribution import Distribution, DistributionAccessUrl
from models.identity_context import IdentityContext
from models.user import User
from repositories.contact import ContactRepository
from repositories.dataset import DatasetRepository
from schemas.dataset import DatasetDto, ResourceDataset
from services.activity_logs.dataset_activity_log import DatasetActivityLogService
from services.database_session_manager import DatabaseSessionManager
from services.dataset import DatasetService
from services.dataset_permissions_service import DatasetPermissionsService
from services.distribution import DistributionService
from services.enun_values import EnumValuesService
from services.data_dictionary import DataDictionaryService
from services.dataset_relation import DatasetRelationService
from services.qualified_attribution import QualifiedAttributionService
from services.config import ConfigService
from test_factory import (
    dataset_dto,
    expected_dataset_resource,
    expected_empty_dataset_resource,
    sample_contact,
    sample_dataset,
    sample_organisation,
)


@pytest.fixture
def organisation_repository(sample_organisation):
    org_mock = Mock()
    org_mock.get_organisation.return_value = sample_organisation
    return org_mock


@pytest.fixture
def contact_repository(sample_contact):
    contact_mock = Mock(spec=ContactRepository)
    contact_mock.get_contact_by_id.return_value = sample_contact
    return contact_mock


@pytest.fixture
def dataset_service(organisation_repository, contact_repository) -> DatasetService:
    config_service_mock = Mock(spec=ConfigService)

    service = DatasetService(
        vocabulary_service=Mock(spec=EnumValuesService),
        distribution_service=Mock(spec=DistributionService),
        dataset_repository=Mock(spec=DatasetRepository),
        dataset_relation_service=Mock(spec=DatasetRelationService),
        activity_log_service=Mock(spec=DatasetActivityLogService),
        database_session_manager=Mock(spec=DatabaseSessionManager),
        organisation_repository=organisation_repository,
        dataset_permissions_service=Mock(spec=DatasetPermissionsService),
        contact_repository=contact_repository,
        data_dictionary_service=Mock(spec=DataDictionaryService),
        qualified_attribution_service=Mock(spec=QualifiedAttributionService),
        config_service=config_service_mock,
    )
    return service


@pytest.fixture
def dataset() -> Dataset:
    ds = Dataset(
        id=1,
        submitted_at=datetime.now(UTC),
        status=DatasetStatus.DRAFT.value,
        user=User(id=1, name="Jia"),
    )
    ds.contacts = set()
    ds.conforms_to_values = []
    return ds


@pytest.fixture
def identity() -> IdentityContext:
    return IdentityContext(user_id=1, permissions=["datasets:status-change:complete"])


def test_persist_dataset_types(
    dataset: Dataset, dataset_dto: DatasetDto, dataset_service: DatasetService
):
    dataset_service._persist_dataset_types(dataset, dataset_dto)

    dataset_service._vocabulary_service.persist_enum_values.assert_called_once()


def test_persist_themes(
    dataset: Dataset, dataset_dto: DatasetDto, dataset_service: DatasetService
):
    dataset_service._persist_themes(dataset, dataset_dto)

    dataset_service._vocabulary_service.persist_enum_values.assert_called_once()


def test_persist_keywords(
    dataset: Dataset, dataset_dto: DatasetDto, dataset_service: DatasetService
):
    dataset_service._persist_keywords(dataset, dataset_dto)

    dataset_service._vocabulary_service.persist_enum_values.assert_called_once()


def test_persist_spatial_coverages(
    dataset: Dataset, dataset_dto: DatasetDto, dataset_service: DatasetService
):
    dataset_service._persist_spatial_coverages(dataset, dataset_dto)

    dataset_service._vocabulary_service.persist_enum_values.assert_called_once()


def test_persist_conventions(
    dataset: Dataset, dataset_dto: DatasetDto, dataset_service: DatasetService
):
    dataset_service._persist_conventions(dataset, dataset_dto)

    dataset_service._vocabulary_service.persist_enum_values.assert_called_once()


def test_persist_areas_of_work(
    dataset: Dataset, dataset_dto: DatasetDto, dataset_service: DatasetService
):
    dataset_service._persist_areas_of_work(dataset, dataset_dto)

    dataset_service._vocabulary_service.persist_enum_values.assert_called_once()


def test_persist_areas_of_competence(
    dataset: Dataset, dataset_dto: DatasetDto, dataset_service: DatasetService
):
    dataset_service._persist_areas_of_competence(dataset, dataset_dto)

    dataset_service._vocabulary_service.persist_enum_values.assert_called_once()


def test_persist_data_protection_types(
    dataset: Dataset, dataset_dto: DatasetDto, dataset_service: DatasetService
):
    dataset_service._persist_data_protection_types(dataset, dataset_dto)

    dataset_service._vocabulary_service.persist_enum_values.assert_called_once()


def test_persist_applicable_legislations(
    dataset: Dataset, dataset_dto: DatasetDto, dataset_service: DatasetService
):
    dataset_service._persist_applicable_legislations(dataset, dataset_dto)

    dataset_service._vocabulary_service.persist_enum_values.assert_called_once()


def test_persist_languages(
    dataset: Dataset, dataset_dto: DatasetDto, dataset_service: DatasetService
):
    dataset_service._persist_languages(dataset, dataset_dto)

    dataset_service._vocabulary_service.persist_enum_values.assert_called_once()


def test_insert_dataset(
    expected_dataset_resource: ResourceDataset,
    dataset_dto: DatasetDto,
    dataset_service: DatasetService,
    identity: IdentityContext,
):

    dataset_service._dataset_repository.exists_by_title_description_publisher = Mock(
        return_value=False
    )

    def mock_merge(dist, dto, user_id):
        dist.title = "distribution_title"
        dist.description = "distribution_description"
        dist.access_urls = [DistributionAccessUrl(url="https://example.com/access_url")]
        dist.created_at = datetime.now(UTC)
        dist.spatial_resolution = 1
        return dist

    dataset_service._distribution_service.merge_distribution_dto_to_entity.side_effect = (
        mock_merge
    )

    Dataset.user = Mock()
    Dataset.user.return_value = User(id=1, name="Jia")

    actual = dataset_service.insert_dataset(dataset_dto, identity)
    dataset_service._dataset_permissions_service.validate_create_permissions.assert_called_once_with(
        publisher_id=dataset_dto.publisher_id,
        identity=identity,
    )

    dataset_service._dataset_permissions_service.validate_create_permissions.assert_called_once_with(
        publisher_id=dataset_dto.publisher_id,
        identity=identity,
    )

    assert not DeepDiff(
        expected_dataset_resource,
        actual,
        ignore_order=True,
        exclude_regex_paths=[
            "root.group_manager_names",
            "root.author_name",
            "root.qualified_attributions",
            "root.retention_period_start",
            "root.retention_period_end",
            "root.contact_ids",
            "root.contact_names",
            "root.contact_emails",
            "root.status_triggers",
            "root.distributions",
            "id",
            "submitted_at",
            "released_at",
            "source_relations",
            "identifier",
        ],
    )

    assert actual.user_id == identity.user_id

    dataset_service._dataset_repository.add.assert_called_once()
    dataset_service._activity_log_service.log_dataset_activities.assert_called_once()
    assert dataset_service._database_session_manager.commit.call_count == 2


def test_update_dataset(
    expected_dataset_resource: ResourceDataset,
    dataset: Dataset,
    dataset_dto: DatasetDto,
    dataset_service: DatasetService,
    identity: IdentityContext,
):
    def mock_merge(dist, dto, user_id):
        dist.title = "distribution_title"
        dist.description = "distribution_description"
        dist.access_urls = [DistributionAccessUrl(url="https://example.com/access_url")]
        dist.created_at = datetime.now(UTC)
        dist.spatial_resolution = 1
        return dist

    dataset_service._distribution_service.merge_distribution_dto_to_entity.side_effect = (
        mock_merge
    )

    dataset_service._dataset_repository.get_dataset.return_value = dataset

    actual = dataset_service.update_dataset(dataset.id, dataset_dto, identity)

    assert not DeepDiff(
        expected_dataset_resource,
        actual,
        ignore_order=True,
        exclude_regex_paths=[
            "root.group_manager_ids",
            "root.group_manager_names",
            "root.qualified_attributions",
            "root.retention_period_start",
            "root.retention_period_end",
            "root.contact_ids",
            "root.contact_names",
            "root.contact_emails",
            "root.status_triggers",
            "root.distributions",
            "submitted_at",
            "released_at",
            "source_relations",
            "identifier",
        ],
    )
    assert actual.identifier == dataset.identifier

    dataset_service._dataset_repository.merge.assert_called_once()
    dataset_service._activity_log_service.log_dataset_activities.assert_called_once()
    assert dataset_service._database_session_manager.commit.call_count == 1


def test_get_datasets(
    expected_empty_dataset_resource: ResourceDataset,
    dataset: Dataset,
    dataset_service: DatasetService,
):
    identity = IdentityContext(user_id=1, permissions=["datasets:edit:draft"])

    dataset_service._dataset_repository.get_all_datasets_created_by_user.return_value = [
        dataset
    ]
    dataset_service._dataset_repository.get_draft_datasets.return_value = [dataset]

    actual = dataset_service.get_datasets(identity)[0]

    assert not DeepDiff(
        expected_empty_dataset_resource,
        actual,
        ignore_order=True,
        exclude_regex_paths=[
            "submitted_at",
            "release_date",
            "modified_at",
            "deprecated_at",
            "released_at",
            "source_relations",
            "identifier",
            "is_dataset_series",
        ],
    )


def test_get_datasets_after_draft(
    expected_empty_dataset_resource: ResourceDataset,
    dataset: Dataset,
    dataset_service: DatasetService,
):
    identity = IdentityContext(user_id=1, permissions=["datasets:read:all-after-draft"])

    dataset_service._dataset_repository.get_all_datasets_created_by_user.return_value = [
        dataset
    ]
    dataset_service._dataset_repository.get_datasets_after_draft.return_value = [
        dataset
    ]

    actual = dataset_service.get_datasets(identity)[0]

    assert not DeepDiff(
        expected_empty_dataset_resource,
        actual,
        ignore_order=True,
        exclude_regex_paths=[
            "submitted_at",
            "release_date",
            "modified_at",
            "deprecated_at",
            "released_at",
            "source_relations",
            "identifier",
            "is_dataset_series",
        ],
    )


def test_get_datasets_after_completed(
    expected_empty_dataset_resource: ResourceDataset,
    dataset: Dataset,
    dataset_service: DatasetService,
):
    identity = IdentityContext(
        user_id=1, permissions=["datasets:read:all-after-complete"]
    )

    dataset_service._dataset_repository.get_all_datasets_created_by_user.return_value = [
        dataset
    ]
    dataset_service._dataset_repository.get_datasets_after_completed.return_value = [
        dataset
    ]

    actual = dataset_service.get_datasets(identity)[0]

    assert not DeepDiff(
        expected_empty_dataset_resource,
        actual,
        ignore_order=True,
        exclude_regex_paths=[
            "submitted_at",
            "release_date",
            "modified_at",
            "deprecated_at",
            "released_at",
            "source_relations",
            "identifier",
            "is_dataset_series",
        ],
    )


def test_get_draft_datasets_created_by_user(
    expected_empty_dataset_resource: ResourceDataset,
    dataset: Dataset,
    dataset_service: DatasetService,
):
    identity = IdentityContext(user_id=1, permissions=["datasets:edit:draft:my"])

    dataset_service._dataset_repository.get_all_datasets_created_by_user.return_value = [
        dataset
    ]
    dataset_service._dataset_repository.get_draft_datasets_created_by_user.return_value = [
        dataset
    ]

    actual = dataset_service.get_datasets(identity)[0]

    assert not DeepDiff(
        expected_empty_dataset_resource,
        actual,
        ignore_order=True,
        exclude_regex_paths=[
            "submitted_at",
            "release_date",
            "modified_at",
            "deprecated_at",
            "released_at",
            "source_relations",
            "identifier",
            "is_dataset_series",
        ],
    )


def test_overlapping_permissions(
    expected_empty_dataset_resource: ResourceDataset,
    dataset: Dataset,
    dataset_service: DatasetService,
):
    identity = IdentityContext(
        user_id=1,
        permissions=["datasets:read:all-after-complete", "datasets:edit:draft:my"],
    )

    dataset_service._dataset_repository.get_all_datasets_created_by_user.return_value = [
        dataset
    ]
    dataset_service._dataset_repository.get_datasets_after_completed.return_value = [
        dataset
    ]
    dataset_service._dataset_repository.get_draft_datasets_created_by_user.return_value = [
        dataset
    ]

    actual = dataset_service.get_datasets(identity)

    assert len(actual) == 1
    assert not DeepDiff(
        expected_empty_dataset_resource,
        actual[0],
        ignore_order=True,
        exclude_regex_paths=[
            "submitted_at",
            "release_date",
            "modified_at",
            "deprecated_at",
            "released_at",
            "source_relations",
            "identifier",
            "is_dataset_series",
        ],
    )


def test_clone_dataset_success(
    dataset_service, sample_dataset, identity, dataset_dto, expected_dataset_resource
):
    dataset_service._dataset_repository.get_dataset.return_value = sample_dataset
    dataset_service._dataset_permissions_service.validate_read_permissions.return_value = (
        None
    )
    dataset_service.insert_dataset = Mock(return_value=expected_dataset_resource)
    dataset_service.get_dataset = Mock(return_value=expected_dataset_resource)

    result = dataset_service.clone_dataset(sample_dataset.id, identity)

    assert result == expected_dataset_resource
    # get_dataset is called twice: once in clone_dataset, once in _copy_distributions
    assert dataset_service._dataset_repository.get_dataset.call_count == 2
    dataset_service._dataset_permissions_service.validate_read_permissions.assert_called_once_with(
        sample_dataset.id, identity
    )
    dataset_service.insert_dataset.assert_called_once()
    dataset_service.get_dataset.assert_called_once_with(
        expected_dataset_resource.id, identity
    )


def test_delete_dataset_success(dataset_service, identity, sample_dataset):
    dataset_service._dataset_permissions_service.validate_delete_permissions.return_value = (
        None
    )

    dataset_service.delete_dataset(sample_dataset.id, identity)

    dataset_service._dataset_permissions_service.validate_delete_permissions.assert_called_once_with(
        sample_dataset.id, identity
    )
    dataset_service._dataset_repository.delete_dataset.assert_called_once_with(
        sample_dataset.id
    )
    dataset_service._database_session_manager.commit.assert_called_once()


def test_get_paginated_datasets_with_published_status(dataset_service, sample_dataset):
    identity = IdentityContext(user_id=1, permissions=["datasets:read:all-after-draft"])

    dataset_service._dataset_permissions_service.get_dataset_list_access_params.return_value = (
        None,  # created_by_user_id = None (can see all)
        None,  # group_manager_user_id = None (can see all)
        None,
    )

    dataset_service._dataset_repository.get_paginated_datasets.return_value = (
        [sample_dataset],
        1,
    )

    result = dataset_service.get_paginated_datasets(
        identity=identity,
        status="PUBLISHED",
        page=1,
        page_size=10,
        query=None,
        dataset_types=[],
        rights_statements=[],
        keywords=[],
        themes=[],
        applicable_legislations=[],
        periodicities=[],
        organisations=[],
        authentic_source_pending=None,
        has_unlabeled_authentic_source=None,
    )

    assert result.meta.total_items == 1
    assert result.meta.page == 1
    assert result.meta.page_size == 10
    assert result.meta.total_pages == 1
    assert len(result.items) == 1
    assert result.items[0].id == sample_dataset.id
    assert result.items[0].title == sample_dataset.title

    dataset_service._dataset_permissions_service.get_dataset_list_access_params.assert_called_once_with(
        identity, "PUBLISHED"
    )
    dataset_service._dataset_repository.get_paginated_datasets.assert_called_once_with(
        status="PUBLISHED",
        created_by_user_id=None,
        group_manager_user_id=None,
        page=1,
        page_size=10,
        query=None,
        dataset_types=[],
        rights_statements=[],
        keywords=[],
        themes=[],
        applicable_legislations=[],
        periodicities=[],
        organisations=[],
        organisation_id=None,
        authentic_source_pending=None,
        has_unlabeled_authentic_source=None,
    )


def test_get_paginated_datasets_with_published_status_and_public_rights_statement_and_periodicity(
    dataset_service, sample_dataset
):
    identity = IdentityContext(user_id=1, permissions=["datasets:read:all-after-draft"])

    dataset_service._dataset_permissions_service.get_dataset_list_access_params.return_value = (
        None,  # created_by_user_id = None (can see all)
        None,  # group_manager_user_id = None (can see all)
        None,
    )

    dataset_service._dataset_repository.get_paginated_datasets.return_value = (
        [sample_dataset],
        1,
    )

    result = dataset_service.get_paginated_datasets(
        identity=identity,
        status="PUBLISHED",
        page=1,
        page_size=10,
        query=None,
        dataset_types=[],
        rights_statements=["PUBLIC"],
        keywords=[],
        themes=[],
        applicable_legislations=[],
        periodicities=["weekly"],
        organisations=[],
        authentic_source_pending=None,
        has_unlabeled_authentic_source=None,
    )

    assert result.meta.total_items == 1
    assert result.meta.page == 1
    assert result.meta.page_size == 10
    assert result.meta.total_pages == 1
    assert len(result.items) == 1
    assert result.items[0].id == sample_dataset.id
    assert result.items[0].title == sample_dataset.title

    dataset_service._dataset_permissions_service.get_dataset_list_access_params.assert_called_once_with(
        identity, "PUBLISHED"
    )
    dataset_service._dataset_repository.get_paginated_datasets.assert_called_once_with(
        status="PUBLISHED",
        created_by_user_id=None,
        group_manager_user_id=None,
        page=1,
        page_size=10,
        query=None,
        dataset_types=[],
        rights_statements=["PUBLIC"],
        keywords=[],
        themes=[],
        applicable_legislations=[],
        periodicities=["weekly"],
        organisations=[],
        organisation_id=None,
        authentic_source_pending=None,
        has_unlabeled_authentic_source=None,
    )


def test_get_paginated_datasets_with_published_status_and_dataset_type_and_keywords(
    dataset_service, sample_dataset
):
    identity = IdentityContext(user_id=1, permissions=["datasets:read:all-after-draft"])

    dataset_service._dataset_permissions_service.get_dataset_list_access_params.return_value = (
        None,  # created_by_user_id = None (can see all)
        None,  # group_manager_user_id = None (can see all)
        None,
    )

    dataset_service._dataset_repository.get_paginated_datasets.return_value = (
        [sample_dataset],
        1,
    )

    result = dataset_service.get_paginated_datasets(
        identity=identity,
        status="PUBLISHED",
        page=1,
        page_size=10,
        query=None,
        dataset_types=["REPORTING"],
        rights_statements=[],
        keywords=[
            "connectivity",
            "connection speed",
        ],
        themes=[],
        applicable_legislations=[],
        periodicities=[],
        organisations=[],
        authentic_source_pending=None,
        has_unlabeled_authentic_source=None,
    )

    assert result.meta.total_items == 1
    assert result.meta.page == 1
    assert result.meta.page_size == 10
    assert result.meta.total_pages == 1
    assert len(result.items) == 1
    assert result.items[0].id == sample_dataset.id
    assert result.items[0].title == sample_dataset.title

    dataset_service._dataset_permissions_service.get_dataset_list_access_params.assert_called_once_with(
        identity, "PUBLISHED"
    )
    dataset_service._dataset_repository.get_paginated_datasets.assert_called_once_with(
        status="PUBLISHED",
        created_by_user_id=None,
        group_manager_user_id=None,
        page=1,
        page_size=10,
        query=None,
        dataset_types=["REPORTING"],
        rights_statements=[],
        keywords=["connectivity", "connection speed"],
        themes=[],
        applicable_legislations=[],
        periodicities=[],
        organisations=[],
        organisation_id=None,
        authentic_source_pending=None,
        has_unlabeled_authentic_source=None,
    )


def test_get_paginated_datasets_with_restricted_permission(
    dataset_service, sample_dataset
):
    identity = IdentityContext(user_id=1, permissions=[])

    dataset_service._dataset_permissions_service.get_dataset_list_access_params.return_value = (
        1,  # created_by_user_id = 1 (can only see own)
        None,  # group_manager_user_id = None NOSONAR
        None,
    )

    # Mock the repository's response
    dataset_service._dataset_repository.get_paginated_datasets.return_value = (
        [sample_dataset],
        1,
    )

    # Call the method
    result = dataset_service.get_paginated_datasets(
        identity=identity,
        status="PUBLISHED",
        page=1,
        page_size=10,
        query=None,
        dataset_types=[],
        rights_statements=[],
        keywords=[],
        themes=[],
        applicable_legislations=[],
        periodicities=[],
        organisations=[],
        authentic_source_pending=None,
        has_unlabeled_authentic_source=None,
    )

    # Assert the results
    assert result.meta.total_items == 1
    assert result.meta.page == 1
    assert len(result.items) == 1

    # Verify correct calls were made
    dataset_service._dataset_permissions_service.get_dataset_list_access_params.assert_called_once_with(
        identity, "PUBLISHED"
    )
    dataset_service._dataset_repository.get_paginated_datasets.assert_called_once_with(
        status="PUBLISHED",
        created_by_user_id=1,
        group_manager_user_id=None,
        page=1,
        page_size=10,
        query=None,
        dataset_types=[],
        rights_statements=[],
        keywords=[],
        themes=[],
        applicable_legislations=[],
        periodicities=[],
        organisations=[],
        organisation_id=None,
        authentic_source_pending=None,
        has_unlabeled_authentic_source=None,
    )


def test_get_paginated_datasets_with_organisations_filter(
    dataset_service, sample_dataset
):
    identity = IdentityContext(user_id=1, permissions=["datasets:read:all-after-draft"])

    dataset_service._dataset_permissions_service.get_dataset_list_access_params.return_value = (
        None,  # created_by_user_id = None (can see all)
        None,  # group_manager_user_id = None (can see all)
        None,
    )

    dataset_service._dataset_repository.get_paginated_datasets.return_value = (
        [sample_dataset],
        1,
    )

    result = dataset_service.get_paginated_datasets(
        identity=identity,
        status="PUBLISHED",
        page=1,
        page_size=10,
        query=None,
        dataset_types=["REPORTING"],
        rights_statements=[],
        keywords=[
            "connectivity",
            "connection speed",
        ],
        themes=[],
        applicable_legislations=[],
        periodicities=[],
        organisations=[1],
        authentic_source_pending=None,
        has_unlabeled_authentic_source=None,
    )

    assert result.meta.total_items == 1
    assert result.meta.page == 1
    assert result.meta.page_size == 10
    assert result.meta.total_pages == 1
    assert len(result.items) == 1
    assert result.items[0].id == sample_dataset.id
    assert result.items[0].title == sample_dataset.title

    dataset_service._dataset_repository.get_paginated_datasets.assert_called_once_with(
        status="PUBLISHED",
        created_by_user_id=None,
        group_manager_user_id=None,
        page=1,
        page_size=10,
        query=None,
        dataset_types=["REPORTING"],
        rights_statements=[],
        keywords=["connectivity", "connection speed"],
        themes=[],
        applicable_legislations=[],
        periodicities=[],
        organisations=[1],
        organisation_id=None,
        authentic_source_pending=None,
        has_unlabeled_authentic_source=None,
    )


def test_get_dataset_counts(dataset_service):
    # Create a mock identity context
    identity = IdentityContext(user_id=1, permissions=["datasets:read:all-after-draft"])

    # Save the original methods for later restoration
    original_get_params = (
        dataset_service._dataset_permissions_service.get_dataset_list_access_params
    )
    original_get_count = dataset_service._dataset_repository.get_count_for_status

    # Mock the permissions service method
    dataset_service._dataset_permissions_service.get_dataset_list_access_params = Mock()
    dataset_service._dataset_permissions_service.get_dataset_list_access_params.side_effect = [
        (None, None, None),  # DRAFT
        (None, None, None),  # COMPLETED
        (None, None, None),  # VALIDATED
        (None, None, None),  # APPROVED
        (None, None, None),  # PUBLISHED
        (None, None, None),  # INTERNAL_ONLY
        (None, None, None),  # DEPRECATED
    ]

    # Mock the repository method
    dataset_service._dataset_repository.get_count_for_status = Mock()
    dataset_service._dataset_repository.get_count_for_status.return_value = 1

    try:
        # Call the method under test
        result = dataset_service.get_dataset_counts(identity)

        # Verify results
        assert result.draft == 1
        assert result.completed == 1
        assert result.validated == 1
        assert result.approved == 1
        assert result.published == 1
        assert result.internal_only == 1
        assert result.deprecated == 1
        assert result.total == 7

        # Verify the permissions service was called for each status
        expected_permissions_calls = [
            call(identity, DatasetStatus.DRAFT.value),
            call(identity, DatasetStatus.COMPLETED.value),
            call(identity, DatasetStatus.VALIDATED.value),
            call(identity, DatasetStatus.APPROVED.value),
            call(identity, DatasetStatus.PUBLISHED.value),
            call(identity, DatasetStatus.INTERNAL_ONLY.value),
            call(identity, DatasetStatus.DEPRECATED.value),
        ]
        assert (
            dataset_service._dataset_permissions_service.get_dataset_list_access_params.call_args_list
            == expected_permissions_calls
        )

        # Verify the repository method was called for each status with the correct parameters
        expected_repo_calls = [
            call(
                status="DRAFT",
                created_by_user_id=None,
                group_manager_user_id=None,
                organisation_id=None,
            ),
            call(
                status="COMPLETED",
                created_by_user_id=None,
                group_manager_user_id=None,
                organisation_id=None,
            ),
            call(
                status="VALIDATED",
                created_by_user_id=None,
                group_manager_user_id=None,
                organisation_id=None,
            ),
            call(
                status="APPROVED",
                created_by_user_id=None,
                group_manager_user_id=None,
                organisation_id=None,
            ),
            call(
                status="PUBLISHED",
                created_by_user_id=None,
                group_manager_user_id=None,
                organisation_id=None,
            ),
            call(
                status="INTERNAL_ONLY",
                created_by_user_id=None,
                group_manager_user_id=None,
                organisation_id=None,
            ),
            call(
                status="DEPRECATED",
                created_by_user_id=None,
                group_manager_user_id=None,
                organisation_id=None,
            ),
        ]
        assert (
            dataset_service._dataset_repository.get_count_for_status.call_args_list
            == expected_repo_calls
        )

    finally:
        # Restore the original methods to avoid affecting other tests
        dataset_service._dataset_permissions_service.get_dataset_list_access_params = (
            original_get_params
        )
        dataset_service._dataset_repository.get_count_for_status = original_get_count


def test_create_dataset_version_not_found_raises(dataset_service, identity):
    dataset_service._dataset_permissions_service.validate_read_permissions = Mock()
    dataset_service._dataset_repository.get_dataset = Mock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        dataset_service.create_dataset_version(999, identity)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Dataset with ID 999 not found." in exc_info.value.detail

    dataset_service._dataset_permissions_service.validate_read_permissions.assert_called_once_with(
        999, identity
    )


def test_create_dataset_version_success():
    vocabulary_service = MagicMock()
    distribution_service = MagicMock()
    activity_log_service = MagicMock()
    organisation_repository = MagicMock()
    contact_repository = MagicMock()
    dataset_repository = MagicMock()
    dataset_permissions_service = MagicMock()
    database_session_manager = MagicMock()
    data_dictionary_service = MagicMock()
    dataset_relation_service = MagicMock()
    qualified_attribution_service = MagicMock()
    config_service = MagicMock()

    service = DatasetService(
        vocabulary_service=vocabulary_service,
        distribution_service=distribution_service,
        activity_log_service=activity_log_service,
        organisation_repository=organisation_repository,
        contact_repository=contact_repository,
        dataset_repository=dataset_repository,
        dataset_permissions_service=dataset_permissions_service,
        database_session_manager=database_session_manager,
        data_dictionary_service=data_dictionary_service,
        dataset_relation_service=dataset_relation_service,
        qualified_attribution_service=qualified_attribution_service,
        config_service=config_service,
    )

    original_dataset = MagicMock()
    original_dataset.id = 1
    original_dataset.status = "published"

    new_dataset_entity = MagicMock()
    new_dataset_entity.id = 2
    new_dataset_entity.status = "draft"
    new_dataset_entity.previous_version_dataset_id = original_dataset.id

    dataset_repository.get_dataset.side_effect = [
        original_dataset,
        new_dataset_entity,
        original_dataset,
    ]

    dataset_permissions_service.validate_read_permissions.return_value = None

    new_version_dataset_resource = MagicMock()
    new_version_dataset_resource.id = 2
    service.insert_dataset = MagicMock(return_value=new_version_dataset_resource)

    dataset_repository.merge = MagicMock()
    database_session_manager.commit = MagicMock()
    database_session_manager.refresh = MagicMock()

    dict_entry = MagicMock()
    dict_entry.field_name = "field1"
    dict_entry.description = "desc1"
    dict_entry.data_type = "string"
    dict_entry.personally_identifiable_variable = True
    dict_entry.required = True
    dict_entry.max_allowed_value = None
    dict_entry.min_allowed_value = None
    dict_entry.variable_unit = None
    dict_entry.allowed_values = None
    dict_entry.allowed_values_description = None
    dict_entry.table_name = "table1"
    dict_entry.is_authentic_source = False
    dict_entry.privacy_risk_type = None

    result = service.create_dataset_version(
        1,
        IdentityContext(
            user_id=123,
            groups=[],
            permissions=["datasets:status-change:publish"],
        ),
    )

    assert result is not None
    dataset_permissions_service.validate_read_permissions.assert_called_once()
    dataset_repository.get_dataset.assert_any_call(1)
    dataset_repository.get_dataset.assert_any_call(2)
    service.insert_dataset.assert_called_once()
    dataset_repository.merge.assert_called_once()
    database_session_manager.commit.assert_called_once()
    database_session_manager.refresh.assert_called_once_with(new_dataset_entity)

    merged_dataset = dataset_repository.merge.call_args[0][0]
    assert merged_dataset.previous_version_dataset_id == original_dataset.id

    data_dictionary_service.copy_data_dictionaries.assert_called_once_with(
        source_dataset_id=1,
        target_dataset_id=new_dataset_entity.id,
        identity=IdentityContext(
            user_id=123,
            groups=[],
            permissions=["datasets:status-change:publish"],
        ),
        preserve_authentic_source=True,
    )

    dataset_relation_service.copy_dataset_relations.assert_called_once_with(
        source_dataset_id=original_dataset.id,
        target_dataset_id=new_dataset_entity.id,
        identity=IdentityContext(
            user_id=123,
            groups=[],
            permissions=["datasets:status-change:publish"],
        ),
    )


def test_get_dataset_versions_chain_returns_correct_order(dataset_service, identity):
    dataset_A = MagicMock()
    dataset_A.id = 1
    dataset_A.previous_version_dataset_id = None

    dataset_B = MagicMock()
    dataset_B.id = 2
    dataset_B.previous_version_dataset_id = 1

    dataset_C = MagicMock()
    dataset_C.id = 3
    dataset_C.previous_version_dataset_id = 2

    dataset_service._dataset_repository.get_dataset.side_effect = lambda id: {
        1: dataset_A,
        2: dataset_B,
        3: dataset_C,
    }.get(id)
    dataset_service._dataset_permissions_service.validate_read_permissions = Mock()

    chain = dataset_service.get_dataset_versions_chain(3, identity)

    assert chain == [dataset_A, dataset_B, dataset_C]


def test_get_dataset_versions_chain_with_no_parents_returns_empty_list(
    dataset_service, identity
):
    dataset = MagicMock()
    dataset.id = 10
    dataset.previous_version_dataset_id = None

    dataset_service._dataset_repository.get_dataset.return_value = dataset
    dataset_service._dataset_permissions_service.validate_read_permissions = Mock()

    chain = dataset_service.get_dataset_versions_chain(10, identity)

    assert chain == [dataset]


def test_get_dataset_versions_chain_stops_on_missing_parent(dataset_service, identity):
    dataset_B = MagicMock()
    dataset_B.id = 2
    dataset_B.previous_version_dataset_id = 1
    dataset_service._dataset_repository.get_dataset.side_effect = lambda id: {
        2: dataset_B,
    }.get(id)
    dataset_service._dataset_permissions_service.validate_read_permissions = Mock()

    chain = dataset_service.get_dataset_versions_chain(2, identity)

    assert chain == [dataset_B]


def test_get_dataset_versions_chain_validates_read_permissions(
    dataset_service, identity
):
    dataset_service._dataset_permissions_service.validate_read_permissions = Mock()
    dataset_service._dataset_repository.get_dataset = Mock(return_value=None)

    dataset_service.get_dataset_versions_chain(999, identity)

    dataset_service._dataset_permissions_service.validate_read_permissions.assert_called_once_with(
        999, identity
    )


def test_create_dataset_raises_conflict_if_duplicate(
    dataset_service: DatasetService,
    dataset_dto: DatasetDto,
    identity: IdentityContext,
):
    dataset_service._dataset_repository.exists_by_title_description_publisher = (
        lambda title, desc, pub_id: True
    )

    with pytest.raises(HTTPException) as exc_info:
        dataset_service.insert_dataset(dataset_dto, identity)

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert (
        "same title, description, and publisher already exists"
        in exc_info.value.detail.lower()
    )
