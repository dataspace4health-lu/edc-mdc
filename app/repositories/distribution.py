from datetime import date
from fastapi import HTTPException, Depends
from dependencies.database import get_db_session
from sqlalchemy.orm import Session
from models.distribution import Distribution
from models.distribution import DistributionPolicyAction
from typing import List, Annotated
from sqlalchemy import desc


class DistributionRepository:
    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def get_distributions_from_dataset(self, dataset_id: int) -> List[Distribution]:
        return (
            self._db_session.query(Distribution)
            .filter(Distribution.dataset_id == dataset_id)
            .order_by(desc(Distribution.id))
            .all()
        )

    def get_distribution(self, distribution_id: int) -> Distribution:
        distribution = (
            self._db_session.query(Distribution)
            .filter(Distribution.id == distribution_id)
            .first()
        )
        if not distribution:
            raise HTTPException(
                status_code=404, detail=f"Distribution[{distribution_id}] not found"
            )
        return distribution

    def get_distribution_by_applicable_legislation(
        self, applicable_legislation_key: str
    ) -> Distribution:
        return (
            self._db_session.query(Distribution)
            .filter(
                Distribution.applicable_legislations.any(key=applicable_legislation_key)
            )
            .all()
        )

    def get_distributions_by_applicable_legislation(
        self, applicable_legislation_key: str
    ):
        """Alias for backward compatibility"""
        return self.get_distribution_by_applicable_legislation(
            applicable_legislation_key
        )

    def get_policy_action(
        self, policy_action_id: int
    ) -> DistributionPolicyAction | None:
        return (
            self._db_session.query(DistributionPolicyAction)
            .filter(DistributionPolicyAction.id == policy_action_id)
            .first()
        )

    def add(self, distribution: Distribution) -> None:
        self._db_session.add(distribution)

    def merge(self, distribution: Distribution) -> None:
        self._db_session.merge(distribution)

    def delete(self, distribution_id: int) -> None:
        distribution = self.get_distribution(distribution_id)
        self._db_session.delete(distribution)

    def refresh(self, distribution: Distribution) -> None:
        self._db_session.refresh(distribution)

    def commit(self) -> None:
        self._db_session.commit()
