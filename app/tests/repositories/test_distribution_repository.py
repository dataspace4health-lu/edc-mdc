from datetime import date
from models.distribution import (
    DistributionPolicyAction,
    DistributionApplicableLegislation,
)
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.dataset import Distribution
from repositories.distribution import DistributionRepository
import pytest
from unittest.mock import Mock


@pytest.fixture
def distribution_repository() -> DistributionRepository:
    return DistributionRepository(Mock(spec=Session))


def test_get_distributions_from_dataset(
    distribution_repository: DistributionRepository,
):
    dataset_id = 1
    distributions = [Distribution(id=1, dataset_id=1, title="Distribution 1")]
    distribution_repository._db_session.query().filter().order_by().all.return_value = (
        distributions
    )

    actual = distribution_repository.get_distributions_from_dataset(dataset_id)

    assert len(actual) == 1
    assert actual[0].title == "Distribution 1"


def test_get_distribution_exists(distribution_repository: DistributionRepository):
    distribution_id = 1
    distribution_repository._db_session.query().filter().first.return_value = (
        Distribution(id=1, dataset_id=1, title="Distribution 1")
    )

    result = distribution_repository.get_distribution(distribution_id)

    assert result.id == distribution_id
    assert result.title == "Distribution 1"


def test_get_distribution_not_found(distribution_repository: DistributionRepository):
    distribution_id = 1
    distribution_repository._db_session.query().filter().first.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        distribution_repository.get_distribution(distribution_id)
    assert excinfo.value.status_code == 404


def test_get_distribution_with_policy_actions(
    distribution_repository: DistributionRepository,
):
    policy_action_1 = DistributionPolicyAction(
        id=1,
        distribution_id=1,
        policy_action_type="permission",
        policy_constraint_type="purpose",
        policy_constraint_value="DUO:0000006",
    )

    policy_action_2 = DistributionPolicyAction(
        id=2,
        distribution_id=1,
        policy_action_type="prohibition",
        policy_constraint_type="temporal",
        temporal_restriction_start=date(2024, 1, 1),
        temporal_restriction_end=date(2024, 12, 31),
    )

    distribution = Distribution(
        id=1, dataset_id=1, title="Distribution with Policy Actions"
    )
    distribution.policy_actions = {policy_action_1, policy_action_2}

    distribution_repository._db_session.query().filter().first.return_value = (
        distribution
    )

    result = distribution_repository.get_distribution(1)

    assert len(result.policy_actions) == 2
    policy_action_types = {
        action.policy_action_type for action in result.policy_actions
    }
    assert "permission" in policy_action_types
    assert "prohibition" in policy_action_types


def test_delete_distribution_with_applicable_legislation(
    distribution_repository: DistributionRepository,
):
    distribution = Distribution(
        id=1, dataset_id=1, title="Distribution with Applicable Legislation"
    )
    applicable_legislation = DistributionApplicableLegislation(
        key="GDPR", distribution_id=1
    )
    distribution.applicable_legislation = {applicable_legislation}

    distribution_repository._db_session.query().filter().first.return_value = (
        distribution
    )

    distribution_repository.delete(1)

    distribution_repository._db_session.delete.assert_called_once_with(distribution)
