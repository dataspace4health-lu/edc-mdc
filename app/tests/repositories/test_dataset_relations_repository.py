import pytest
from sqlalchemy.orm import Session
from models.dataset_relation import DatasetRelation
from models.dataset import Dataset
from repositories.dataset_relation import DatasetRelationRepository
from fastapi import HTTPException
from test_factory import sample_dataset


@pytest.fixture
def dataset_relations_repository(db_session: Session) -> DatasetRelationRepository:
    return DatasetRelationRepository(db_session)


def test_get_dataset_relations_by_dataset_id(
    dataset_relations_repository: DatasetRelationRepository,
    db_session: Session,
    sample_dataset: Dataset,
):
    # Create another sample dataset
    sample_dataset2 = sample_dataset
    db_session.add(sample_dataset2)
    db_session.flush()

    dataset_relation_entry = DatasetRelation(
        source_dataset=sample_dataset.id,
        target_dataset=sample_dataset2.id,
        relation_type="dct:hasVersion",
    )
    db_session.add(dataset_relation_entry)
    db_session.commit()

    relations = dataset_relations_repository.get_dataset_relations_by_dataset_id(
        sample_dataset.id
    )

    assert len(relations) == 1
    assert relations[0].target_dataset == sample_dataset2.id


def test_get_dataset_relation_exists(
    dataset_relations_repository: DatasetRelationRepository,
    db_session: Session,
    sample_dataset: Dataset,
):
    # Create another sample dataset
    sample_dataset2 = sample_dataset
    db_session.add(sample_dataset2)
    db_session.flush()

    dataset_relation_entry = DatasetRelation(
        source_dataset=sample_dataset.id,
        target_dataset=sample_dataset2.id,
        relation_type="dct:hasVersion",
    )
    db_session.add(dataset_relation_entry)
    db_session.commit()

    relation = dataset_relations_repository.get_dataset_relation(
        dataset_relation_entry.id
    )

    assert relation.target_dataset == sample_dataset2.id
    assert relation.source_dataset == sample_dataset.id
    assert relation.relation_type == dataset_relation_entry.relation_type


def test_get_dataset_relation_not_found(
    dataset_relations_repository: DatasetRelationRepository,
):
    relation_id = -1

    with pytest.raises(HTTPException) as excinfo:
        dataset_relations_repository.get_dataset_relation(relation_id)
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == f"DatasetRelation[{relation_id}] not found"


def test_add_dataset_relation_entry(
    dataset_relations_repository: DatasetRelationRepository,
    db_session: Session,
    sample_dataset: Dataset,
):
    # Create another sample dataset
    sample_dataset2 = sample_dataset
    db_session.add(sample_dataset2)
    db_session.flush()

    dataset_relation_entry = DatasetRelation(
        source_dataset=sample_dataset.id,
        target_dataset=sample_dataset2.id,
        relation_type="dct:hasVersion",
    )
    dataset_relations_repository.add(dataset_relation_entry)
    db_session.flush()

    db_relation = (
        db_session.query(DatasetRelation)
        .filter_by(source_dataset=sample_dataset.id)
        .first()
    )
    assert db_relation is not None
    assert db_relation.target_dataset == sample_dataset2.id


def test_delete_dataset_relation(
    dataset_relations_repository: DatasetRelationRepository,
    db_session: Session,
    sample_dataset: Dataset,
):
    # Create another sample dataset
    sample_dataset2 = sample_dataset
    db_session.add(sample_dataset2)
    db_session.flush()

    new_entry = DatasetRelation(
        source_dataset=sample_dataset.id,
        target_dataset=sample_dataset2.id,
        relation_type="dct:hasVersion",
    )
    dataset_relations_repository.add(new_entry)
    db_session.flush()
    db_session.refresh(new_entry)

    # Delete the original relation
    dataset_relations_repository.delete(new_entry.id)
    db_session.flush()

    # Verify original relation is deleted
    original_relation = (
        db_session.query(DatasetRelation)
        .filter_by(source_dataset=sample_dataset.id, target_dataset=sample_dataset2.id)
        .first()
    )
    assert original_relation is None
