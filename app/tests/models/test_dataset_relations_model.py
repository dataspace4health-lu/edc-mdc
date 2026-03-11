from sqlalchemy.orm import Session
from models.dataset_relation import DatasetRelation
from models.dataset import Dataset
from repositories.dataset_relation import DatasetRelationRepository
from test_factory import sample_dataset


def test_create_and_get_dataset_relation_entry(
    db_session: Session, sample_dataset: Dataset
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

    db_dataset_relation_entry = (
        db_session.query(DatasetRelation)
        .filter_by(source_dataset=sample_dataset.id)
        .first()
    )

    assert db_dataset_relation_entry is not None
    assert db_dataset_relation_entry.source_dataset == sample_dataset.id
