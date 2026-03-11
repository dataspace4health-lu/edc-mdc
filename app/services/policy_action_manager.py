from typing import Annotated, List
from fastapi import Depends

from models.distribution import (
    Distribution,
    DistributionPolicyAction,
    DistributionSpatialRestrictions,
)
from schemas.distribution import PolicyActionDto
from repositories.distribution import DistributionRepository


class PolicyActionManager:
    def __init__(
        self,
        distribution_repository: Annotated[
            DistributionRepository, Depends(DistributionRepository)
        ],
    ):
        self._repository = distribution_repository

    def update_policy_actions(
        self,
        distribution: Distribution,
        new_actions: List[PolicyActionDto],
        user_id: int,
    ) -> None:
        distribution.policy_actions.clear()
        for action_dto in new_actions:
            policy_action = self._create_policy_action_from_dto(
                distribution.id, action_dto
            )
            distribution.policy_actions.add(policy_action)

    def _create_policy_action_from_dto(
        self, distribution_id: int, action_dto: PolicyActionDto
    ) -> DistributionPolicyAction:
        policy_action = DistributionPolicyAction(
            distribution_id=distribution_id,
            policy_action_type=action_dto.policy_action_type,
            policy_constraint_type=action_dto.policy_constraint_type,
            policy_constraint_value=action_dto.policy_constraint_value,
            temporal_restriction_start=action_dto.temporal_restriction_start,
            temporal_restriction_end=action_dto.temporal_restriction_end,
        )

        if action_dto.spatial_restrictions:
            for spatial_key in action_dto.spatial_restrictions:
                spatial_restriction = DistributionSpatialRestrictions(
                    key=spatial_key, policy_action=policy_action
                )
                policy_action.spatial_restrictions.add(spatial_restriction)

        return policy_action
