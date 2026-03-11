from datetime import datetime, timedelta
from typing import List, Optional
from schemas.organisation import ResourceOrganisation, organisation_entity_to_resource
from repositories.organisation import OrganisationRepository
from fastapi import Depends
from sqlalchemy import desc

_organisation_cache_instance = None


class OrganisationCache:
    def __init__(
        self,
        organisation_repository: OrganisationRepository = Depends(
            OrganisationRepository
        ),
    ):
        self.data: Optional[List[ResourceOrganisation]] = None
        self.last_updated: Optional[datetime] = None
        self.expiry_time = timedelta(hours=10)  # Default: 10 hour
        self._repository = organisation_repository

    def get_all(self) -> List[ResourceOrganisation]:
        if self.is_valid():
            return self.data

        return self.refresh()

    def refresh(self) -> List[ResourceOrganisation]:
        try:
            organisations = self._repository.get_organisations()
            result = [organisation_entity_to_resource(org) for org in organisations]
            self.set(result)
            return result
        except Exception as _:
            # Roll back any failed transaction
            try:
                self._repository._db_session.rollback()
            except Exception as _:
                pass  # In case rollback itself fails
            # After rollback, try once more
            organisations = self._repository.get_organisations()
            result = [organisation_entity_to_resource(org) for org in organisations]
            self.set(result)
            return result

    def set(self, data: List[ResourceOrganisation]) -> None:
        self.data = data
        self.last_updated = datetime.now()

    def is_valid(self) -> bool:
        return (
            self.data is not None
            and self.last_updated is not None
            and datetime.now() - self.last_updated < self.expiry_time
        )

    def invalidate(self) -> None:
        self.data = None
        self.last_updated = None


def get_organisation_cache(
    repository: OrganisationRepository = Depends(OrganisationRepository),
) -> OrganisationCache:
    global _organisation_cache_instance

    if _organisation_cache_instance is None:
        _organisation_cache_instance = OrganisationCache(repository)

    return _organisation_cache_instance
