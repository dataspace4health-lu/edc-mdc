import pytest
from fastapi import HTTPException
from models.qualified_attribution import DatasetQualifiedAttribution
from models.dataset import Dataset, DatasetStatus
from models.organisation import Organisation
from repositories.qualified_attribution import QualifiedAttributionRepository
from sqlalchemy.orm import Session
from test_factory import sample_dataset, sample_organisation
import uuid
from datetime import datetime


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    yield
    db_session.query(DatasetQualifiedAttribution).delete()
    db_session.query(Dataset).delete()
    db_session.query(Organisation).delete()
    db_session.commit()


@pytest.fixture
def qa_repository(db_session: Session) -> QualifiedAttributionRepository:
    return QualifiedAttributionRepository(db_session)


@pytest.fixture
def sample_qa(
    db_session: Session, sample_dataset: Dataset, sample_organisation: Organisation
) -> DatasetQualifiedAttribution:
    qa = DatasetQualifiedAttribution(
        dataset_id=sample_dataset.id,
        organisation_id=sample_organisation.id,
        role="author",
    )
    db_session.add(qa)
    db_session.commit()
    db_session.refresh(qa)
    return qa


def test_get_qualified_attribution_exists(
    qa_repository: QualifiedAttributionRepository,
    db_session: Session,
    sample_qa: DatasetQualifiedAttribution,
):
    result = qa_repository.get_qualified_attribution(sample_qa.id)

    assert result is not None
    assert result.id == sample_qa.id
    assert result.dataset_id == sample_qa.dataset_id
    assert result.organisation_id == sample_qa.organisation_id
    assert result.role == sample_qa.role


def test_get_qualified_attribution_not_found(
    qa_repository: QualifiedAttributionRepository,
):
    non_existent_id = 99999

    with pytest.raises(HTTPException) as exc_info:
        qa_repository.get_qualified_attribution(non_existent_id)

    assert exc_info.value.status_code == 404
    assert f"QualifiedAttribution[{non_existent_id}] not found" in str(
        exc_info.value.detail
    )


def test_get_attributions_by_dataset_id_exists(
    qa_repository: QualifiedAttributionRepository,
    db_session: Session,
    sample_dataset: Dataset,
    sample_organisation: Organisation,
):
    qa1 = DatasetQualifiedAttribution(
        dataset_id=sample_dataset.id,
        organisation_id=sample_organisation.id,
        role="author",
    )
    qa2 = DatasetQualifiedAttribution(
        dataset_id=sample_dataset.id,
        organisation_id=sample_organisation.id,
        role="contributor",
    )

    db_session.add_all([qa1, qa2])
    db_session.commit()

    result = qa_repository.get_attributions_by_dataset_id(sample_dataset.id)

    assert len(result) == 2
    assert all(qa.dataset_id == sample_dataset.id for qa in result)
    roles = {qa.role for qa in result}
    assert "author" in roles
    assert "contributor" in roles


def test_get_attributions_by_dataset_id_empty(
    qa_repository: QualifiedAttributionRepository, sample_dataset: Dataset
):
    result = qa_repository.get_attributions_by_dataset_id(sample_dataset.id)

    assert len(result) == 0
    assert result == []


def test_get_attributions_by_dataset_id_non_existent_dataset(
    qa_repository: QualifiedAttributionRepository,
):
    result = qa_repository.get_attributions_by_dataset_id(99999)
    assert len(result) == 0


def test_exists_returns_true(
    qa_repository: QualifiedAttributionRepository,
    db_session: Session,
    sample_dataset: Dataset,
    sample_organisation: Organisation,
):
    qa = DatasetQualifiedAttribution(
        dataset_id=sample_dataset.id,
        organisation_id=sample_organisation.id,
        role="author",
    )
    db_session.add(qa)
    db_session.commit()

    result = qa_repository.exists(sample_dataset.id, sample_organisation.id, "author")
    assert result is True


def test_exists_returns_false(
    qa_repository: QualifiedAttributionRepository,
    sample_dataset: Dataset,
    sample_organisation: Organisation,
):
    result = qa_repository.exists(sample_dataset.id, sample_organisation.id, "author")
    assert result is False


def test_exists_different_role(
    qa_repository: QualifiedAttributionRepository,
    db_session: Session,
    sample_dataset: Dataset,
    sample_organisation: Organisation,
):
    qa = DatasetQualifiedAttribution(
        dataset_id=sample_dataset.id,
        organisation_id=sample_organisation.id,
        role="author",
    )
    db_session.add(qa)
    db_session.commit()

    result = qa_repository.exists(
        sample_dataset.id, sample_organisation.id, "contributor"
    )
    assert result is False


def test_add_qualified_attribution(
    qa_repository: QualifiedAttributionRepository,
    db_session: Session,
    sample_dataset: Dataset,
    sample_organisation: Organisation,
):
    qa = DatasetQualifiedAttribution(
        dataset_id=sample_dataset.id,
        organisation_id=sample_organisation.id,
        role="publisher",
    )

    qa_repository.add(qa)
    db_session.commit()

    result = (
        db_session.query(DatasetQualifiedAttribution)
        .filter(
            DatasetQualifiedAttribution.dataset_id == sample_dataset.id,
            DatasetQualifiedAttribution.organisation_id == sample_organisation.id,
            DatasetQualifiedAttribution.role == "publisher",
        )
        .first()
    )

    assert result is not None
    assert result.role == "publisher"


def test_update_qualified_attribution_organisation(
    qa_repository: QualifiedAttributionRepository,
    db_session: Session,
    sample_qa: DatasetQualifiedAttribution,
):
    new_org = Organisation(
        name="New Organisation",
        email="new@example.com",
        type="Company",
        is_deprecated=False,
    )
    db_session.add(new_org)
    db_session.commit()
    db_session.refresh(new_org)

    original_role = sample_qa.role
    qa_repository.update(sample_qa, organisation_id=new_org.id)
    db_session.commit()
    db_session.refresh(sample_qa)

    assert sample_qa.organisation_id == new_org.id
    assert sample_qa.role == original_role


def test_update_qualified_attribution_role(
    qa_repository: QualifiedAttributionRepository,
    db_session: Session,
    sample_qa: DatasetQualifiedAttribution,
):
    original_org_id = sample_qa.organisation_id

    qa_repository.update(sample_qa, role="contributor")
    db_session.commit()
    db_session.refresh(sample_qa)

    assert sample_qa.role == "contributor"
    assert sample_qa.organisation_id == original_org_id


def test_update_qualified_attribution_both(
    qa_repository: QualifiedAttributionRepository,
    db_session: Session,
    sample_qa: DatasetQualifiedAttribution,
):
    new_org = Organisation(
        name="Another Organisation",
        email="another@example.com",
        type="Company",
        is_deprecated=False,
    )
    db_session.add(new_org)
    db_session.commit()
    db_session.refresh(new_org)

    qa_repository.update(sample_qa, organisation_id=new_org.id, role="publisher")
    db_session.commit()
    db_session.refresh(sample_qa)

    assert sample_qa.organisation_id == new_org.id
    assert sample_qa.role == "publisher"


def test_update_qualified_attribution_no_changes(
    qa_repository: QualifiedAttributionRepository,
    db_session: Session,
    sample_qa: DatasetQualifiedAttribution,
):
    original_org_id = sample_qa.organisation_id
    original_role = sample_qa.role

    qa_repository.update(sample_qa)
    db_session.commit()
    db_session.refresh(sample_qa)

    assert sample_qa.organisation_id == original_org_id
    assert sample_qa.role == original_role


def test_delete_qualified_attribution(
    qa_repository: QualifiedAttributionRepository,
    db_session: Session,
    sample_qa: DatasetQualifiedAttribution,
):
    qa_id = sample_qa.id

    qa_repository.delete(qa_id)
    db_session.commit()

    result = (
        db_session.query(DatasetQualifiedAttribution)
        .filter(DatasetQualifiedAttribution.id == qa_id)
        .first()
    )

    assert result is None


def test_delete_non_existent_qualified_attribution(
    qa_repository: QualifiedAttributionRepository, db_session: Session
):
    qa_repository.delete(99999)
    db_session.commit()


def test_multiple_datasets_same_organisation(
    qa_repository: QualifiedAttributionRepository,
    db_session: Session,
    sample_organisation: Organisation,
):
    dataset1 = Dataset(
        title="Dataset 1",
        description="Test dataset 1",
        identifier=str(uuid.uuid4()),
        status=DatasetStatus.DRAFT.value,
        user_id=1,
        publisher_id=sample_organisation.id,
        submitted_at=datetime.now(),
        time_period_start=datetime.now(),
        rights_statement="PUBLIC",
        periodicity="ANNUALLY",
    )
    dataset2 = Dataset(
        title="Dataset 2",
        description="Test dataset 2",
        identifier=str(uuid.uuid4()),
        status=DatasetStatus.DRAFT.value,
        user_id=1,
        publisher_id=sample_organisation.id,
        submitted_at=datetime.now(),
        time_period_start=datetime.now(),
        rights_statement="PUBLIC",
        periodicity="ANNUALLY",
    )
    db_session.add_all([dataset1, dataset2])
    db_session.commit()

    qa1 = DatasetQualifiedAttribution(
        dataset_id=dataset1.id, organisation_id=sample_organisation.id, role="author"
    )
    qa2 = DatasetQualifiedAttribution(
        dataset_id=dataset2.id, organisation_id=sample_organisation.id, role="author"
    )
    db_session.add_all([qa1, qa2])
    db_session.commit()

    result1 = qa_repository.get_attributions_by_dataset_id(dataset1.id)
    result2 = qa_repository.get_attributions_by_dataset_id(dataset2.id)

    assert len(result1) == 1
    assert len(result2) == 1
    assert result1[0].organisation_id == sample_organisation.id
    assert result2[0].organisation_id == sample_organisation.id


def test_multiple_roles_same_dataset_organisation(
    qa_repository: QualifiedAttributionRepository,
    db_session: Session,
    sample_dataset: Dataset,
    sample_organisation: Organisation,
):
    qa1 = DatasetQualifiedAttribution(
        dataset_id=sample_dataset.id,
        organisation_id=sample_organisation.id,
        role="author",
    )
    qa2 = DatasetQualifiedAttribution(
        dataset_id=sample_dataset.id,
        organisation_id=sample_organisation.id,
        role="contributor",
    )

    db_session.add_all([qa1, qa2])
    db_session.commit()

    result = qa_repository.get_attributions_by_dataset_id(sample_dataset.id)

    assert len(result) == 2
    roles = {qa.role for qa in result}
    assert "author" in roles
    assert "contributor" in roles
