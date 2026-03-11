from datetime import datetime, timezone
from typing import Annotated, List, Tuple

from constants import ACCESS_RIGHT_NON_PUBLIC
from dependencies.database import get_db_session
from fastapi import Depends
from models.dataset import (
    Dataset,
    DatasetGroupManagers,
    DatasetKeyword,
    DatasetApplicableLegislation,
    DatasetStatus,
    DatasetTheme,
    DatasetTypes,
)
from models.data_dictionary import DataDictionaryEntry
from models.authentic_source_assignment import AuthenticSourceAssignment
from models.organisation import Organisation
from models.distribution import Distribution
from sqlalchemy import desc, or_, select, exists, and_
from sqlalchemy.orm import Session


class DatasetRepository:
    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def get_dataset(self, dataset_id: int) -> Dataset:
        dataset = (
            self._db_session.query(Dataset).filter(Dataset.id == dataset_id).first()
        )
        return dataset

    def get_dataset_by_identifier(self, identifier: str) -> Dataset:
        dataset = (
            self._db_session.query(Dataset)
            .filter(Dataset.identifier == identifier)
            .first()
        )
        return dataset

    def get_dataset_by_source(self, source: str, source_dataset_id: int) -> Dataset:
        dataset = (
            self._db_session.query(Dataset)
            .filter(
                Dataset.source == source, Dataset.source_dataset_id == source_dataset_id
            )
            .first()
        )
        return dataset

    def _build_dataset_query(  # NOSONAR
        self,
        status: str = None,
        group_manager_user_id: int = None,
        created_by_user_id: int = None,
        query: str = None,
        dataset_types: list[str] = None,
        rights_statements: list[str] = None,
        keywords: list[str] = None,
        themes: list[str] = None,
        applicable_legislations: list[str] = None,
        periodicities: list[str] = None,
        organisations: list[int] = None,
        organisation_id: int = None,
        authentic_source_pending: bool = None,
        has_unlabeled_authentic_source: bool = None,
    ):
        query_obj = self._db_session.query(Dataset)

        if status:
            query_obj = query_obj.filter(Dataset.status == status)

        if dataset_types and len(dataset_types):
            query_obj = query_obj.filter(
                Dataset.dataset_types.any(DatasetTypes.key.in_(dataset_types))
            )

        if rights_statements and len(rights_statements):
            query_obj = query_obj.filter(
                Dataset.rights_statement.in_(rights_statements)
            )

        if keywords and len(keywords):
            query_obj = query_obj.filter(
                Dataset.keywords.any(DatasetKeyword.key.in_(keywords))
            )

        if themes and len(themes):
            query_obj = query_obj.filter(
                Dataset.themes.any(DatasetTheme.key.in_(themes))
            )

        if applicable_legislations and len(applicable_legislations):
            query_obj = query_obj.filter(
                Dataset.applicable_legislations.any(
                    DatasetApplicableLegislation.key.in_(applicable_legislations)
                )
            )

        if periodicities and len(periodicities):
            query_obj = query_obj.filter(Dataset.periodicity.in_(periodicities))

        if organisation_id:
            # If an organisation ID is provided, filter by that organisation
            query_obj = query_obj.filter(Dataset.publisher_id == organisation_id)

        if organisations:
            query_obj = query_obj.filter(Dataset.publisher_id.in_(organisations))

        if created_by_user_id and group_manager_user_id:
            # If both are provided (usually for group managers), we need to find:
            # - Datasets created by the user OR
            # - Datasets where the user is a group manager
            query_obj = query_obj.outerjoin(DatasetGroupManagers).filter(
                or_(
                    Dataset.user_id == created_by_user_id,
                    DatasetGroupManagers.user_id == group_manager_user_id,
                )
            )
        elif group_manager_user_id:
            query_obj = query_obj.join(DatasetGroupManagers).filter(
                DatasetGroupManagers.user_id == group_manager_user_id
            )
        elif created_by_user_id:
            query_obj = query_obj.filter(Dataset.user_id == created_by_user_id)

        if authentic_source_pending:
            query_obj = query_obj.filter(Dataset.authentic_source_reviewed_at == None)

        if (
            has_unlabeled_authentic_source is not None
            and has_unlabeled_authentic_source
        ):
            query_obj = query_obj.filter(
                exists().where(
                    and_(
                        DataDictionaryEntry.dataset_id == Dataset.id,
                        DataDictionaryEntry.is_authentic_source == True,
                        ~exists().where(
                            and_(
                                AuthenticSourceAssignment.data_dictionary_entry_id
                                == DataDictionaryEntry.id,
                                AuthenticSourceAssignment.is_active == True,
                            )
                        ),
                    )
                )
            )

        if query:
            search_term = f"%{query}%"
            query_obj = query_obj.outerjoin(
                Distribution, Distribution.dataset_id == Dataset.id
            )
            query_obj = query_obj.filter(
                or_(
                    Dataset.title.ilike(search_term),
                    Dataset.description.ilike(search_term),
                    Dataset.notes.ilike(search_term),
                    Dataset.final_disposition.ilike(search_term),
                    Dataset.identifier.ilike(search_term),
                    Dataset.monitoring_location.ilike(search_term),
                    Distribution.title.ilike(search_term),
                    Distribution.description.ilike(search_term),
                )
            )
        query_obj = query_obj.distinct()

        return query_obj

    def get_paginated_datasets(  # NOSONAR
        self,
        status: str,
        group_manager_user_id: int = None,
        created_by_user_id: int = None,
        page: int = 1,
        page_size: int = 10,
        query: str = None,
        dataset_types: list[str] = [],
        rights_statements: list[str] = [],
        keywords: list[str] = [],
        themes: list[str] = [],
        applicable_legislations: list[str] = [],
        periodicities: list[str] = [],
        organisations: list[int] = [],
        organisation_id: int = None,
        authentic_source_pending: bool = None,
        has_unlabeled_authentic_source: bool = None,
    ) -> Tuple[List[Dataset], int]:
        query_obj = self._build_dataset_query(
            status=status,
            created_by_user_id=created_by_user_id,
            group_manager_user_id=group_manager_user_id,
            query=query,
            dataset_types=dataset_types,
            rights_statements=rights_statements,
            keywords=keywords,
            themes=themes,
            applicable_legislations=applicable_legislations,
            periodicities=periodicities,
            organisations=organisations,
            organisation_id=organisation_id,
            authentic_source_pending=authentic_source_pending,
            has_unlabeled_authentic_source=has_unlabeled_authentic_source,
        )
        query_obj = query_obj.order_by(desc(Dataset.id))
        total_count = query_obj.count()
        query_obj = query_obj.offset((page - 1) * page_size).limit(page_size)
        return query_obj.all(), total_count

    def get_released_datasets_paginated(
        self, page: int = 1, page_size: int = 50
    ) -> Tuple[List[Dataset], int]:
        query_obj = (
            self._db_session.query(Dataset)
            .join(Organisation, Dataset.publisher_id == Organisation.id)
            .filter(Dataset.released_at.isnot(None))
            .filter(
                or_(
                    Organisation.accessible_within_ctie == False,
                    Organisation.accessible_within_ctie.is_(None),
                )
            )
            .order_by(Dataset.released_at)
        )
        total_count = query_obj.count()
        query_obj = query_obj.offset((page - 1) * page_size).limit(page_size)
        return query_obj.all(), total_count

    def get_count_for_status(
        self,
        status: str,
        created_by_user_id: int = None,
        group_manager_user_id: int = None,
        organisation_id: int = None,
    ) -> int:
        query_obj = self._build_dataset_query(
            status=status,
            created_by_user_id=created_by_user_id,
            group_manager_user_id=group_manager_user_id,
            organisation_id=organisation_id,
        )
        return query_obj.count()

    def get_count_for_user(self, user_id: int) -> int:
        return (
            self._db_session.query(Dataset).filter(Dataset.user_id == user_id).count()
        )

    def get_draft_datasets(self) -> List[Dataset]:
        return (
            self._db_session.query(Dataset)
            .filter(Dataset.status == DatasetStatus.DRAFT.value)
            .order_by(desc(Dataset.id))
            .all()
        )

    def get_datasets_after_draft(self) -> List[Dataset]:
        return (
            self._db_session.query(Dataset)
            .filter(Dataset.status != DatasetStatus.DRAFT.value)
            .order_by(desc(Dataset.id))
            .all()
        )

    def get_dataset_by_id(self, dataset_id: int) -> Dataset:
        return (
            self._db_session.query(Dataset)
            .filter(Dataset.id == dataset_id)
            .order_by(desc(Dataset.id))
            .first()
        )

    def get_all_versions_of_dataset(self, dataset_id: int) -> List[Dataset]:
        dataset = self.get_dataset_by_id(dataset_id)
        if not dataset:
            return []

        # Collect all dataset IDs in the version chain
        version_ids = {dataset.id}

        # Walk backwards to collect all previous version IDs
        current = dataset
        while current.previous_version_dataset_id:
            version_ids.add(current.previous_version_dataset_id)
            current = self.get_dataset_by_id(current.previous_version_dataset_id)

        # Walk forwards to collect all next version IDs
        current_id = dataset.id
        while True:
            next_version = (
                self._db_session.query(Dataset.id, Dataset.previous_version_dataset_id)
                .filter(Dataset.previous_version_dataset_id == current_id)
                .first()
            )
            if not next_version:
                break
            version_ids.add(next_version.id)
            current_id = next_version.id

        # Now fetch all versions in a single query and sort
        versions = (
            self._db_session.query(Dataset)
            .filter(Dataset.id.in_(version_ids))
            .order_by(Dataset.submitted_at)
            .all()
        )

        return versions

    def get_datasets_after_completed(self) -> List[Dataset]:
        return (
            self._db_session.query(Dataset)
            .filter(
                Dataset.status.notin_(
                    [DatasetStatus.DRAFT.value, DatasetStatus.COMPLETED.value]
                )
            )
            .order_by(desc(Dataset.id))
            .all()
        )

    def get_draft_datasets_created_by_user(self, user_id: int) -> List[Dataset]:
        return (
            self._db_session.query(Dataset)
            .filter(Dataset.user_id == user_id)
            .filter(Dataset.status == DatasetStatus.DRAFT.value)
            .order_by(desc(Dataset.id))
            .all()
        )

    def get_all_datasets_created_by_user(self, user_id: int) -> List[Dataset]:
        return (
            self._db_session.query(Dataset)
            .filter(Dataset.user_id == user_id)
            .order_by(desc(Dataset.id))
            .all()
        )

    def get_datasets_by_group(self, user_id: int) -> List[Dataset]:
        return (
            self._db_session.query(Dataset)
            .join(DatasetGroupManagers)
            .filter(DatasetGroupManagers.user_id == user_id)
            .order_by(desc(Dataset.id))
            .all()
        )

    def get_dataset_status_publisher_id_and_user_id(
        self, dataset_id: int
    ) -> Tuple[str, int]:
        status_publisher_id_and_user_id = self._db_session.execute(
            select(Dataset.status, Dataset.publisher_id, Dataset.user_id).where(
                Dataset.id == dataset_id
            )
        ).first()
        if not status_publisher_id_and_user_id:
            return [None, None, None]  # NOSONAR
        return status_publisher_id_and_user_id

    def is_dataset_imported(self, dataset_id: int) -> bool:
        imported_dataset = self._db_session.execute(
            select(Dataset.id).where(
                Dataset.id == dataset_id, Dataset.source.isnot(None)
            )
        ).first()
        return imported_dataset is not None

    def get_dataset_group_manager_user_ids(self, dataset_id):
        return [
            user_id
            for (user_id,) in self._db_session.query(DatasetGroupManagers.user_id)
            .filter(DatasetGroupManagers.dataset_id == dataset_id)
            .all()
        ]

    def get_public_datasets(
        self, only_non_public_access: bool = False
    ) -> List[Dataset]:
        query = self._db_session.query(Dataset).filter(
            Dataset.status == DatasetStatus.PUBLISHED.value
        )

        if only_non_public_access:
            query = query.filter(Dataset.rights_statement == ACCESS_RIGHT_NON_PUBLIC)

        return query.order_by(desc(Dataset.id)).all()

    def add(self, dataset: Dataset) -> None:
        self._db_session.add(dataset)

    def merge(self, dataset: Dataset) -> None:
        self._db_session.merge(dataset)

    def get_datasets_by_theme(self, key: str) -> List[Dataset]:
        return self._db_session.query(Dataset).filter(Dataset.themes.any(key=key)).all()

    def get_datasets_by_keyword(self, key: str) -> List[Dataset]:
        return (
            self._db_session.query(Dataset).filter(Dataset.keywords.any(key=key)).all()
        )

    def get_datasets_by_applicable_legislation(self, key: str) -> List[Dataset]:
        return (
            self._db_session.query(Dataset)
            .filter(Dataset.applicable_legislations.any(key=key))
            .all()
        )

    def delete_dataset(self, dataset_id: int) -> None:
        dataset = (
            self._db_session.query(Dataset).filter(Dataset.id == dataset_id).first()
        )
        self._db_session.delete(dataset)

    def complete_authentic_source_review(
        self,
        dataset_id: int,
    ) -> Dataset:
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} not found")

        dataset.authentic_source_reviewed_at = datetime.now(timezone.utc)

        return dataset

    def exists_by_title_description_publisher(
        self, title: str, description: str, publisher_id: int
    ) -> bool:
        normalized_title = title.strip().lower()
        normalized_description = description.strip().lower()

        return (
            self._db_session.query(Dataset)
            .filter(
                Dataset.title.ilike(normalized_title),
                Dataset.description.ilike(normalized_description),
                Dataset.publisher_id == publisher_id,
            )
            .first()
            is not None
        )

    def has_published_newer_version(self, dataset_id: int) -> bool:
        return (
            self._db_session.query(Dataset)
            .filter(
                Dataset.previous_version_dataset_id == dataset_id,
                Dataset.status == DatasetStatus.PUBLISHED.value,
            )
            .first()
            is not None
        )
