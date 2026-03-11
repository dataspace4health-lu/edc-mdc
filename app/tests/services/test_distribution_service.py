from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from models.dataset import Dataset
from models.distribution import Distribution
from repositories.dataset import DatasetRepository
from repositories.distribution import DistributionRepository
from schemas.distribution import DistributionDto, ResourceDistribution, PolicyActionDto
from services.distribution import DistributionService
from services.enun_values import EnumValuesService
from services.policy_action_manager import PolicyActionManager
from services.dataset_permissions_service import DatasetPermissionsService
from services.activity_logs.distribution_activity_log import (
    DistributionActivityLogService,
)
from test_factory import (
    expected_resource_distribution,
    sample_distribution,
    sample_distribution_dto,
)


@pytest.fixture
def distribution_service() -> DistributionService:
    distribution_repository = Mock(spec=DistributionRepository)
    distribution_repository.get_distributions_from_dataset.return_value = []

    return DistributionService(
        vocabulary_service=Mock(spec=EnumValuesService),
        dataset_repository=Mock(spec=DatasetRepository),
        distribution_repository=distribution_repository,
        policy_action_manager=Mock(spec=PolicyActionManager),
        dataset_permissions_service=Mock(spec=DatasetPermissionsService),
        distribution_activity_log_service=Mock(spec=DistributionActivityLogService),
    )


def test_persist_languages(
    sample_distribution: Distribution,
    sample_distribution_dto: DistributionDto,
    distribution_service: DistributionService,
):
    distribution_service._persist_languages(
        sample_distribution, sample_distribution_dto
    )

    distribution_service._vocabulary_service.persist_enum_values.assert_called_once()


def test_persist_application_legislations(
    sample_distribution: Distribution,
    sample_distribution_dto: DistributionDto,
    distribution_service: DistributionService,
):
    distribution_service._persist_applicable_legislations(
        sample_distribution, sample_distribution_dto
    )

    distribution_service._vocabulary_service.persist_enum_values.assert_called_once()


def test_persist_policy_actions(
    sample_distribution: Distribution,
    sample_distribution_dto: DistributionDto,
    distribution_service: DistributionService,
    user_id=1,
):
    distribution_service._persist_policy_actions(
        sample_distribution, sample_distribution_dto, user_id
    )

    distribution_service._policy_action_manager.update_policy_actions.assert_called_once_with(
        sample_distribution, sample_distribution_dto.policy_actions, user_id
    )


def test_persist_multiple_policy_actions(
    sample_distribution: Distribution,
    distribution_service: DistributionService,
    user_id=1,
):
    distribution_dto_multi = DistributionDto(
        title="test",
        description="test description with multiple policy actions",
        download_urls=["http://example.com"],  # NOSONAR
        access_urls=["http://example.com"],  # NOSONAR
        file_type="CSV",
        rights_statement="PUBLIC",
        internal_only=False,
        applicable_legislations=[],
        languages=frozenset(),
        notes="",
        license="no_license",
        policy_actions=[
            PolicyActionDto(
                policy_action_type="permission",
                policy_constraint_type="purpose",
                policy_constraint_value="DUO:0000006",
            ),
            PolicyActionDto(
                policy_action_type="prohibition",
                policy_constraint_type="temporal",
                temporal_restriction_start=datetime(2024, 1, 1).date(),
                temporal_restriction_end=datetime(2024, 12, 31).date(),
            ),
            PolicyActionDto(
                policy_action_type="permission",
                policy_constraint_type="spatial",
                spatial_restrictions=["LUX", "FRA"],
            ),
        ],
        linked_schemas=[],
        media_type="application/json",
        compression_format=None,
        packaging_format=None,
        distribution_dcat_status=None,
        access_service_ids=frozenset(),
    )

    distribution_service._persist_policy_actions(
        sample_distribution, distribution_dto_multi, user_id
    )

    distribution_service._policy_action_manager.update_policy_actions.assert_called_once_with(
        sample_distribution, distribution_dto_multi.policy_actions, user_id
    )


def test_add_distribution(
    sample_distribution_dto: DistributionDto,
    distribution_service: DistributionService,
):
    from unittest.mock import patch

    dataset_id = 1
    user_id = 123
    mock_identity = Mock()
    mock_identity.user_id = user_id

    # Mock the repository and service methods
    mock_distribution = Mock(spec=Distribution)
    mock_distribution.id = 456
    mock_distribution.title = sample_distribution_dto.title
    mock_distribution.dataset_id = dataset_id

    distribution_service.merge_distribution_dto_to_entity = Mock(
        return_value=mock_distribution
    )
    distribution_service._distribution_repository.refresh = Mock()

    # Mock the entity to resource conversion
    mock_result = Mock()
    with patch(
        "services.distribution.distribution_entity_to_resource",
        return_value=mock_result,
    ):
        result = distribution_service.add_distribution(
            dataset_id=dataset_id,
            distribution_dto=sample_distribution_dto,
            identity=mock_identity,
        )

    # Verify permissions were checked
    distribution_service._dataset_permissions_service.validate_edit_permissions.assert_called_once_with(
        dataset_id, mock_identity
    )

    # Verify merge was called with a new Distribution instance
    distribution_service.merge_distribution_dto_to_entity.assert_called_once()
    call_args = distribution_service.merge_distribution_dto_to_entity.call_args
    assert (
        call_args[0][0].dataset_id == dataset_id
    )  # Check first arg is Distribution with correct dataset_id
    assert call_args[0][1] == sample_distribution_dto  # Check second arg is the DTO
    assert call_args[0][2] == user_id  # Check third arg is user_id

    # Verify activity log was created
    distribution_service._distribution_activity_log_service.log_distribution_created.assert_called_once_with(
        user_id=user_id,
        dataset_id=dataset_id,
        distribution_id=456,
        distribution_title=sample_distribution_dto.title,
    )
