from fastapi import Depends, HTTPException, status
from typing import Annotated, List
from models.dataset_relation import DatasetRelation
from models.identity_context import IdentityContext
from repositories.dataset_relation import DatasetRelationRepository
from schemas.dataset_relations import (
    AddRelation,
    ResourceRelation,
    dataset_relation_entity_to_resource,
)
from services.database_session_manager import DatabaseSessionManager
from services.activity_logs.dataset_activity_log import DatasetActivityLogService
from services.dataset_permissions_service import DatasetPermissionsService
from validators.dataset_relation_validator import reciprocal_mapping


class DatasetRelationService:
    def __init__(
        self,
        repository: Annotated[
            DatasetRelationRepository, Depends(DatasetRelationRepository)
        ],
        database_session_manager: Annotated[
            DatabaseSessionManager, Depends(DatabaseSessionManager)
        ],
        activity_log_service: Annotated[
            DatasetActivityLogService, Depends(DatasetActivityLogService)
        ],
        dataset_permissions_service: Annotated[
            DatasetPermissionsService, Depends(DatasetPermissionsService)
        ],
    ):
        self._repository = repository
        self._database_session_manager = database_session_manager
        self._activity_log_service = activity_log_service
        self._dataset_permissions_service = dataset_permissions_service

    def get_relations_by_dataset_id(
        self, dataset_id: int, identity: IdentityContext
    ) -> List[ResourceRelation]:
        self._dataset_permissions_service.validate_read_permissions(
            dataset_id, identity
        )
        relations = self._repository.get_relations_by_dataset_id(dataset_id)
        return [dataset_relation_entity_to_resource(rel) for rel in relations]

    def add_relation(
        self,
        source_dataset_id: int,
        add_relation: AddRelation,
        identity: IdentityContext,
    ) -> ResourceRelation:
        try:
            self._dataset_permissions_service.validate_edit_permissions(
                source_dataset_id, identity
            )

            if add_relation.relation_kind == "dataset":
                return self._add_dataset_relation(
                    source_dataset_id, add_relation, identity
                )
            else:
                return self._add_external_relation(
                    source_dataset_id, add_relation, identity
                )
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

    def _add_dataset_relation(
        self,
        source_dataset_id: int,
        add_relation: AddRelation,
        identity: IdentityContext,
    ) -> ResourceRelation:
        target_dataset_id = add_relation.target_dataset
        relation_type = add_relation.relation_type

        self._validate_dataset_relation(
            source_dataset_id, target_dataset_id, relation_type
        )

        relation = DatasetRelation(
            source_dataset=source_dataset_id,
            target_dataset=target_dataset_id,
            relation_type=relation_type,
        )
        self._repository.add(relation)
        self._log_activity(identity.user_id, None, relation)
        reciprocal_relation = self._determine_reciprocal(relation)
        self._repository.add(reciprocal_relation)
        self._log_activity(identity.user_id, None, reciprocal_relation)

        self._database_session_manager.commit()
        self._database_session_manager.refresh(relation)
        return dataset_relation_entity_to_resource(relation)

    def _add_external_relation(
        self,
        source_dataset_id: int,
        add_relation: AddRelation,
        identity: IdentityContext,
    ) -> ResourceRelation:
        existing_relations = self._repository.get_external_relations_by_dataset_id(
            source_dataset_id
        )
        for rel in existing_relations:
            if rel.external_url == add_relation.external_url:
                raise HTTPException(
                    status_code=400,
                    detail="Relation with this external URL already exists",
                )

        relation = DatasetRelation(
            source_dataset=source_dataset_id,
            external_url=add_relation.external_url,
            external_role=add_relation.external_role,
            external_description=add_relation.external_description,
        )
        self._repository.add(relation)
        self._log_activity(identity.user_id, None, relation)

        self._database_session_manager.commit()
        self._database_session_manager.refresh(relation)
        return dataset_relation_entity_to_resource(relation)

    def delete_relation(
        self,
        dataset_id: int,
        relation_id: int,
        identity: IdentityContext,
    ) -> None:
        self._dataset_permissions_service.validate_edit_permissions(
            dataset_id, identity
        )
        relation = self._repository.get_dataset_relation(relation_id)
        if not relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Relation with ID {relation_id} not found",
            )

        self._log_activity(identity.user_id, relation, None)

        if relation.is_dataset_relation:
            reciprocal_relation = self._determine_reciprocal(relation)
            self._log_activity(identity.user_id, reciprocal_relation, None)
            self._repository.delete_reciprocal_relation(
                dataset_id, reciprocal_relation.relation_type
            )

        self._repository.delete(relation_id)
        self._database_session_manager.commit()

    def _determine_reciprocal(self, relation: DatasetRelation) -> DatasetRelation:
        if not relation.is_dataset_relation:
            raise ValueError("Cannot create reciprocal for non-dataset relations")

        reciprocal_relation_type = reciprocal_mapping.get(
            relation.relation_type, relation.relation_type
        )

        return DatasetRelation(
            source_dataset=relation.target_dataset,
            target_dataset=relation.source_dataset,
            relation_type=reciprocal_relation_type,
        )

    def _validate_dataset_relation(
        self, source_dataset_id: int, target_dataset_id: int, relation_type: str
    ) -> None:
        existing_relations = self._repository.get_dataset_relations_by_dataset_id(
            source_dataset_id
        )
        reciprocal_relation_type = reciprocal_mapping.get(relation_type, relation_type)

        for relation in existing_relations:
            if relation.target_dataset == target_dataset_id and (
                relation.relation_type == relation_type
                or relation.relation_type == reciprocal_relation_type
            ):
                raise HTTPException(
                    status_code=400, detail="Duplicate or reciprocal relation exists"
                )

    def _log_activity(
        self,
        user_id: int,
        old_relation: DatasetRelation,
        new_relation: DatasetRelation,
    ) -> None:
        old_value = old_relation.to_dict_for_diff() if old_relation else None
        new_value = new_relation.to_dict_for_diff() if new_relation else None

        relation = old_relation if old_relation else new_relation
        source_dataset = relation.source_dataset

        if relation.is_dataset_relation:
            field = f"relations.{relation.relation_type}.{relation.target_dataset}"
        else:
            field = f"relations.external.{relation.external_url}"

        self._activity_log_service.log_dictionary_item_activities(
            user_id, source_dataset, field, old_value, new_value
        )

    def copy_dataset_relations(
        self, source_dataset_id: int, target_dataset_id: int, identity: IdentityContext
    ) -> None:
        relations = self._repository.get_relations_by_dataset_id(source_dataset_id)

        for rel in relations:
            if rel.is_dataset_relation:
                new_relation = DatasetRelation(
                    source_dataset=target_dataset_id,
                    target_dataset=rel.target_dataset,
                    relation_type=rel.relation_type,
                )
                self._repository.add(new_relation)
                self._log_activity(identity.user_id, None, new_relation)

                reciprocal_relation = self._determine_reciprocal(new_relation)
                self._repository.add(reciprocal_relation)
                self._log_activity(identity.user_id, None, reciprocal_relation)
            else:
                new_relation = DatasetRelation(
                    source_dataset=target_dataset_id,
                    external_url=rel.external_url,
                    external_role=rel.external_role,
                    external_description=rel.external_description,
                )
                self._repository.add(new_relation)
                self._log_activity(identity.user_id, None, new_relation)

        self._database_session_manager.commit()
