import pytest
from unittest.mock import Mock
from models.dataset_relation import DatasetRelation
from models.identity_context import IdentityContext
from services.dataset_relation import DatasetRelationService
from schemas.dataset_relations import (
    AddRelation,
    dataset_relation_entity_to_resource,
)
from deepdiff import DeepDiff
from typing import Dict
import copy


@pytest.fixture
def dataset_relation_service() -> DatasetRelationService:
    mock_repo = Mock()
    mock_repo.get_relations_by_dataset_id.return_value = []
    mock_repo.get_dataset_relations_by_dataset_id.return_value = []
    mock_repo.get_external_relations_by_dataset_id.return_value = []

    mock_permissions = Mock()
    mock_permissions.validate_read_permissions.return_value = None
    mock_permissions.validate_edit_permissions.return_value = None

    return DatasetRelationService(
        repository=mock_repo,
        database_session_manager=Mock(),
        activity_log_service=Mock(),
        dataset_permissions_service=mock_permissions,
    )


@pytest.fixture
def expected_dataset_relation() -> DatasetRelation:
    return DatasetRelation(
        id=1,
        source_dataset=1,
        target_dataset=2,
        relation_type="dct:hasVersion",
    )


@pytest.fixture
def dataset_relation() -> DatasetRelation:
    return DatasetRelation(
        id=1,
        source_dataset=1,
        target_dataset=2,
        relation_type="dct:hasVersion",
    )


@pytest.fixture
def external_relation() -> DatasetRelation:
    return DatasetRelation(
        id=3,
        source_dataset=1,
        external_url="https://example.com/resource",
        external_role="describedby",
        external_description="Documentation for the dataset",
    )


reciprocal_mapping_fixture = [
    {"key": "dct:hasVersion", "value": "dct:isVersionOf"},
    {"key": "dct:isVersionOf", "value": "dct:hasVersion"},
    {"key": "dct:source", "value": "dct:relation"},
    {"key": "dct:relation", "value": "dct:relation"},
    {"key": "dct:hasPart", "value": "dct:isPartOf"},
    {"key": "dct:isPartOf", "value": "dct:hasPart"},
    {"key": "dct:conformsTo", "value": "dct:relation"},
    {"key": "dct:hasFormat", "value": "dct:isFormatOf"},
    {"key": "dct:isFormatOf", "value": "dct:hasFormat"},
    {"key": "dct:isReferencedBy", "value": "dct:references"},
    {"key": "dct:references", "value": "dct:isReferencedBy"},
    {"key": "dct:isReplacedBy", "value": "dct:replaces"},
    {"key": "dct:replaces", "value": "dct:isReplacedBy"},
    {"key": "dct:isRequiredBy", "value": "dct:requires"},
    {"key": "dct:requires", "value": "dct:isRequiredBy"},
]


def test_get_dataset_relations_by_dataset_id(
    expected_dataset_relation: DatasetRelation,
    dataset_relation_service: DatasetRelationService,
):
    dataset_id = 1
    dataset_relations = [expected_dataset_relation]
    dataset_relation_service._repository.get_relations_by_dataset_id.return_value = (
        dataset_relations
    )

    expected_resources = [
        dataset_relation_entity_to_resource(dr) for dr in dataset_relations
    ]

    actual = dataset_relation_service.get_relations_by_dataset_id(dataset_id, None)

    assert not DeepDiff(expected_resources, actual, ignore_order=True)
    dataset_relation_service._repository.get_relations_by_dataset_id.assert_called_once_with(
        dataset_id
    )


@pytest.mark.parametrize("reciprocal_mapping", reciprocal_mapping_fixture)
def test_add_dataset_relation(
    dataset_relation: DatasetRelation,
    dataset_relation_service: DatasetRelationService,
    reciprocal_mapping: Dict[str, str],
):
    relation_type = reciprocal_mapping["key"]
    reciprocal_relation_type = reciprocal_mapping["value"]
    dataset_relation_service._repository.add = Mock()
    dataset_relation_service._repository.get_dataset_relations_by_dataset_id.return_value = (
        []
    )

    input_data = AddRelation(
        relation_kind="dataset",
        target_dataset=dataset_relation.target_dataset,
        relation_type=relation_type,
    )

    identity = IdentityContext(user_id=1, permissions=[])

    dataset_relation_service.add_relation(
        dataset_relation.source_dataset, input_data, identity
    )

    relations = dataset_relation_service._repository.add.call_args_list
    assert len(relations) == 2

    actual = [
        {
            "source_dataset": relation.args[0].source_dataset,
            "target_dataset": relation.args[0].target_dataset,
            "relation_type": relation.args[0].relation_type,
        }
        for relation in relations
    ]
    expected = [
        {
            "source_dataset": dataset_relation.source_dataset,
            "target_dataset": dataset_relation.target_dataset,
            "relation_type": relation_type,
        },
        {
            "source_dataset": dataset_relation.target_dataset,
            "target_dataset": dataset_relation.source_dataset,
            "relation_type": reciprocal_relation_type,
        },
    ]

    assert not DeepDiff(expected, actual, ignore_order=True)

    calls = (
        dataset_relation_service._activity_log_service.log_dictionary_item_activities.call_args_list
    )
    assert len(calls) == 2


@pytest.mark.parametrize("reciprocal_mapping", reciprocal_mapping_fixture)
def test_delete_dataset_relation(
    dataset_relation: DatasetRelation,
    dataset_relation_service: DatasetRelationService,
    reciprocal_mapping: Dict[str, str],
):
    relation_type = reciprocal_mapping["key"]
    reciprocal_relation_type = reciprocal_mapping["value"]

    new_relation = copy.deepcopy(dataset_relation)
    new_relation.relation_type = relation_type

    identity = IdentityContext(user_id=1, permissions=[])
    dataset_relation_service._repository.get_dataset_relation.return_value = (
        new_relation
    )

    dataset_relation_service.delete_relation(
        new_relation.source_dataset, new_relation.id, identity
    )

    dataset_relation_service._repository.delete_reciprocal_relation.assert_called_once_with(
        new_relation.source_dataset, reciprocal_relation_type
    )
    dataset_relation_service._repository.delete.assert_called_once_with(new_relation.id)

    calls = (
        dataset_relation_service._activity_log_service.log_dictionary_item_activities.call_args_list
    )
    assert len(calls) == 2


def test_add_external_relation(dataset_relation_service: DatasetRelationService):
    dataset_relation_service._repository.add = Mock()
    dataset_relation_service._repository.get_external_relations_by_dataset_id.return_value = (
        []
    )

    input_data = AddRelation(
        relation_kind="external",
        external_url="https://example.com/resource",
        external_role="describedby",
        external_description="Documentation for the dataset",
    )

    identity = IdentityContext(user_id=1, permissions=[])
    source_dataset_id = 1

    dataset_relation_service.add_relation(source_dataset_id, input_data, identity)

    relations = dataset_relation_service._repository.add.call_args_list
    assert len(relations) == 1

    actual_relation = relations[0].args[0]
    assert actual_relation.source_dataset == source_dataset_id
    assert actual_relation.external_url == "https://example.com/resource"
    assert actual_relation.external_role == "describedby"
    assert actual_relation.external_description == "Documentation for the dataset"
    assert actual_relation.target_dataset is None
    assert actual_relation.relation_type is None

    calls = (
        dataset_relation_service._activity_log_service.log_dictionary_item_activities.call_args_list
    )
    assert len(calls) == 1


def test_delete_external_relation(
    external_relation: DatasetRelation,
    dataset_relation_service: DatasetRelationService,
):
    identity = IdentityContext(user_id=1, permissions=[])
    dataset_relation_service._repository.get_dataset_relation.return_value = (
        external_relation
    )

    dataset_relation_service.delete_relation(
        external_relation.source_dataset, external_relation.id, identity
    )

    dataset_relation_service._repository.delete_reciprocal_relation.assert_not_called()
    dataset_relation_service._repository.delete.assert_called_once_with(
        external_relation.id
    )

    calls = (
        dataset_relation_service._activity_log_service.log_dictionary_item_activities.call_args_list
    )
    assert len(calls) == 1


def test_get_external_relations(
    external_relation: DatasetRelation,
    dataset_relation_service: DatasetRelationService,
):
    dataset_id = 1
    dataset_relations = [external_relation]
    dataset_relation_service._repository.get_relations_by_dataset_id.return_value = (
        dataset_relations
    )

    expected_resources = [
        dataset_relation_entity_to_resource(dr) for dr in dataset_relations
    ]

    actual = dataset_relation_service.get_relations_by_dataset_id(dataset_id, None)

    assert not DeepDiff(expected_resources, actual, ignore_order=True)
    assert actual[0].relation_kind == "external"
    assert actual[0].external_url == "https://example.com/resource"
    assert actual[0].external_role == "describedby"
