import uuid
from datetime import datetime, timezone

import pytest
from models.dataset import (
    Dataset,
    DatasetCreator,
    DatasetGroupManagers,
    DatasetKeyword,
    DatasetApplicableLegislation,
    DatasetTheme,
    DatasetTypes,
    DatasetStatus,
)
from models.data_dictionary import DataDictionaryEntry
from models.authentic_source_assignment import AuthenticSourceAssignment
from models.authentic_source_label import AuthenticSourceLabel
from models.distribution import Distribution
from repositories.dataset import DatasetRepository
from sqlalchemy.orm import Session
from test_factory import sample_dataset
from factories.data_dictionary_entry import create_sample_data_dictionary_entry
from factories.authentic_source_label import create_sample_authentic_source_label


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    yield
    db_session.query(AuthenticSourceAssignment).delete()
    db_session.query(AuthenticSourceLabel).delete()
    db_session.query(DataDictionaryEntry).delete()
    db_session.query(DatasetGroupManagers).delete()
    db_session.query(DatasetApplicableLegislation).delete()
    db_session.query(Dataset).delete()
    db_session.commit()


@pytest.fixture
def dataset_repository(db_session: Session) -> DatasetRepository:
    return DatasetRepository(db_session)


def create_label_assignment(db_session, entry_id, label_id, is_active=True):
    assignment = AuthenticSourceAssignment(
        data_dictionary_entry_id=entry_id,
        authentic_source_label_id=label_id,
        assigned_by=1,
        assigned_at=datetime.now(timezone.utc),
        is_active=is_active,
    )
    db_session.add(assignment)
    db_session.flush()
    return assignment


def test_get_dataset_exists(
    dataset_repository: DatasetRepository, db_session: Session, sample_dataset: Dataset
):
    db_session.add(sample_dataset)
    db_session.commit()

    actual = dataset_repository.get_dataset(sample_dataset.id)

    assert actual.id == sample_dataset.id
    assert actual.title == sample_dataset.title


def test_get_datasets_by_group(
    dataset_repository: DatasetRepository, db_session: Session, sample_dataset: Dataset
):
    db_session.add(sample_dataset)
    db_session.commit()

    group_managers_list = list(sample_dataset.group_managers)
    group_manager_user_id = group_managers_list[0].user.id

    actual = dataset_repository.get_datasets_by_group(group_manager_user_id)

    assert len(actual) == 1
    assert actual[0].id == sample_dataset.id
    assert actual[0].title == sample_dataset.title


def test_get_dataset_group_manager_user_ids(
    dataset_repository: DatasetRepository, db_session: Session, sample_dataset: Dataset
):
    db_session.add(sample_dataset)
    db_session.commit()

    actual = dataset_repository.get_dataset_group_manager_user_ids(sample_dataset.id)

    group_managers_list = list(sample_dataset.group_managers)
    group_manager_user_id = group_managers_list[0].user.id

    assert len(actual) == 1
    assert actual[0] == group_manager_user_id


def test_not_found_get_datasets_by_group(
    dataset_repository: DatasetRepository, db_session: Session, sample_dataset: Dataset
):
    db_session.add(sample_dataset)
    db_session.commit()

    actual = dataset_repository.get_datasets_by_group(999)

    assert len(actual) == 0


def test_get_draft_datasets(
    dataset_repository: DatasetRepository, db_session: Session, sample_dataset: Dataset
):
    db_session.add(sample_dataset)
    db_session.commit()

    actual = dataset_repository.get_draft_datasets()

    assert len(actual) == 1
    assert actual[0].id == sample_dataset.id


def test_get_dataset_by_id_exists(
    dataset_repository: DatasetRepository, db_session: Session, sample_dataset: Dataset
):
    db_session.add(sample_dataset)
    db_session.commit()

    actual = dataset_repository.get_dataset_by_id(sample_dataset.id)

    assert actual is not None
    assert actual.id == sample_dataset.id
    assert actual.title == sample_dataset.title
    assert actual.description == sample_dataset.description


def test_get_dataset_by_id_not_found(dataset_repository: DatasetRepository):
    non_existent_id = 99999
    actual = dataset_repository.get_dataset_by_id(non_existent_id)

    assert actual is None


def test_get_dataset_by_id_with_multiple_datasets(
    dataset_repository: DatasetRepository, db_session: Session, sample_dataset: Dataset
):
    second_dataset = Dataset(
        title="Second Test Dataset",
        description="Description for second test dataset",
        identifier=str(uuid.uuid4()),
        status=DatasetStatus.DRAFT.value,
        user_id=1,
    )

    db_session.add(sample_dataset)
    db_session.add(second_dataset)
    db_session.commit()
    actual_first = dataset_repository.get_dataset_by_id(sample_dataset.id)
    actual_second = dataset_repository.get_dataset_by_id(second_dataset.id)

    assert actual_first.id == sample_dataset.id
    assert actual_first.title == sample_dataset.title

    assert actual_second.id == second_dataset.id
    assert actual_second.title == second_dataset.title


def test_delete_dataset(
    dataset_repository: DatasetRepository, db_session: Session, sample_dataset: Dataset
):
    db_session.add(sample_dataset)
    db_session.commit()

    dataset_repository.delete_dataset(sample_dataset.id)

    db_session.commit()

    actual = db_session.query(Dataset).filter(Dataset.id == sample_dataset.id).first()

    assert actual is None


def create_test_dataset(
    db_session,
    title=None,
    status="DRAFT",
    rights_statement="PUBLIC",
    dataset_type_keys=[],
    keyword_keys=[],
    theme_keys=[],
    applicable_legislation_keys=[],
    periodicity="daily",
    user_id=1,
):
    new_dataset = Dataset(
        title=title or "Test Dataset",
        description="Test dataset description",
        publisher_id=1,
        submitted_at=datetime.now(),
        time_period_start=datetime.now(),
        time_period_end=datetime.now(),
        rights_statement=rights_statement,
        identifier=str(uuid.uuid1()),
        user_id=user_id,
        status=status,
        periodicity=periodicity,
    )

    db_session.add(new_dataset)
    db_session.flush()

    # Add creator using junction table
    dataset_creator = DatasetCreator(dataset_id=new_dataset.id, organisation_id=1)
    new_dataset.creators.add(dataset_creator)

    for key in dataset_type_keys:
        dataset_type_relation = DatasetTypes(key=key, dataset_id=new_dataset.id)
        new_dataset.dataset_types.add(dataset_type_relation)

    for key in keyword_keys:
        dataset_keyword_relation = DatasetKeyword(key=key, dataset_id=new_dataset.id)
        new_dataset.keywords.add(dataset_keyword_relation)

    for key in theme_keys:
        dataset_theme_relation = DatasetTheme(key=key, dataset_id=new_dataset.id)
        new_dataset.themes.add(dataset_theme_relation)

    for key in applicable_legislation_keys:
        dataset_applicable_legislation_relation = DatasetApplicableLegislation(
            key=key, dataset_id=new_dataset.id
        )
        new_dataset.applicable_legislations.add(dataset_applicable_legislation_relation)

    db_session.commit()
    db_session.refresh(new_dataset)
    return new_dataset


def test_get_paginated_datasets_status_filter(
    dataset_repository: DatasetRepository, db_session: Session
):
    create_test_dataset(db_session, status="DRAFT", title="Dataset 1")
    create_test_dataset(db_session, status="COMPLETED", title="Dataset 2")
    create_test_dataset(db_session, status="DRAFT", title="Dataset 3")

    datasets, count = dataset_repository.get_paginated_datasets(status="DRAFT")

    assert count == 2
    assert len(datasets) == 2
    assert all(d.status == "DRAFT" for d in datasets)
    assert {d.title for d in datasets} == {"Dataset 1", "Dataset 3"}


def test_get_paginated_datasets_dataset_type_filter(
    dataset_repository: DatasetRepository, db_session: Session
):
    create_test_dataset(
        db_session,
        status="DRAFT",
        title="Dataset 1",
        dataset_type_keys=["code-list", "glossary"],
    )
    create_test_dataset(
        db_session,
        status="DRAFT",
        title="Dataset 2",
        dataset_type_keys=["glossary"],
    )
    create_test_dataset(
        db_session,
        status="COMPLETED",
        title="Dataset 3",
        dataset_type_keys=["code-list"],
    )
    create_test_dataset(
        db_session, status="DRAFT", title="Dataset 4", dataset_type_keys=[]
    )
    create_test_dataset(
        db_session, status="DRAFT", title="Dataset 5", dataset_type_keys=["glossary"]
    )

    datasets, count = dataset_repository.get_paginated_datasets(
        status="DRAFT", dataset_types=["code-list", "glossary"]
    )

    assert count == 3
    assert len(datasets) == 3
    assert all(d.status == "DRAFT" for d in datasets)
    assert {d.title for d in datasets} == {"Dataset 1", "Dataset 2", "Dataset 5"}


def test_get_paginated_datasets_rights_statement_filter(
    dataset_repository: DatasetRepository, db_session: Session
):
    create_test_dataset(
        db_session, status="DRAFT", title="Dataset 1", rights_statement="NON-PUBLIC"
    )
    create_test_dataset(
        db_session, status="COMPLETED", title="Dataset 2", rights_statement="PUBLIC"
    )
    create_test_dataset(
        db_session, status="COMPLETED", title="Dataset 3", rights_statement="NON-PUBLIC"
    )

    datasets, count = dataset_repository.get_paginated_datasets(
        status="DRAFT", rights_statements=["NON-PUBLIC"]
    )

    assert count == 1
    assert len(datasets) == 1
    assert all(d.rights_statement == "NON-PUBLIC" for d in datasets)
    assert {d.title for d in datasets} == {"Dataset 1"}


def test_get_paginated_datasets_keyword_filter(
    dataset_repository: DatasetRepository, db_session: Session
):
    create_test_dataset(
        db_session, status="DRAFT", title="Dataset 1", keyword_keys=["health"]
    )
    create_test_dataset(
        db_session,
        status="COMPLETED",
        title="Dataset 2",
        keyword_keys=["connection speed"],
    )
    create_test_dataset(
        db_session, status="COMPLETED", title="Dataset 3", keyword_keys=[]
    )

    create_test_dataset(
        db_session,
        status="DRAFT",
        title="Dataset 4",
        keyword_keys=["health", "employment"],
    )

    datasets, count = dataset_repository.get_paginated_datasets(
        status="DRAFT", keywords=["health"]
    )

    assert count == 2
    assert len(datasets) == 2
    print([d.keywords for d in datasets])
    assert all("health" in [keyword.key for keyword in d.keywords] for d in datasets)
    assert {d.title for d in datasets} == {"Dataset 1", "Dataset 4"}


def test_get_paginated_datasets_theme_filter(
    dataset_repository: DatasetRepository, db_session: Session
):
    create_test_dataset(
        db_session, status="DRAFT", title="Dataset 1", theme_keys=["energy"]
    )
    create_test_dataset(
        db_session,
        status="COMPLETED",
        title="Dataset 2",
        theme_keys=["transport", "energy"],
    )
    create_test_dataset(
        db_session, status="COMPLETED", title="Dataset 3", theme_keys=["energy"]
    )

    create_test_dataset(
        db_session, status="COMPLETED", title="Dataset 4", theme_keys=[]
    )

    datasets, count = dataset_repository.get_paginated_datasets(
        status="COMPLETED", themes=["energy"]
    )

    assert count == 2
    assert len(datasets) == 2
    assert all("energy" in [theme.key for theme in d.themes] for d in datasets)
    assert {d.title for d in datasets} == {"Dataset 2", "Dataset 3"}


def test_get_paginated_datasets_applicable_legislation_filter(
    dataset_repository: DatasetRepository, db_session: Session
):
    create_test_dataset(
        db_session,
        status="DRAFT",
        title="Dataset 1",
        applicable_legislation_keys=["public_interest"],
    )
    create_test_dataset(
        db_session,
        status="COMPLETED",
        title="Dataset 2",
        applicable_legislation_keys=[],
    )
    create_test_dataset(
        db_session,
        status="COMPLETED",
        title="Dataset 3",
        applicable_legislation_keys=["legal_obligation"],
    )

    datasets, count = dataset_repository.get_paginated_datasets(
        status="DRAFT", applicable_legislations=["public_interest"]
    )

    assert count == 1
    assert len(datasets) == 1
    assert all(
        "public_interest" in [base.key for base in d.applicable_legislations]
        for d in datasets
    )
    assert {d.title for d in datasets} == {"Dataset 1"}


def test_get_paginated_datasets_periodicity_filter(
    dataset_repository: DatasetRepository, db_session: Session
):
    create_test_dataset(
        db_session,
        status="DRAFT",
        title="Dataset 1",
        periodicity="daily",
    )
    create_test_dataset(
        db_session,
        status="COMPLETED",
        title="Dataset 2",
        periodicity="weekly",
    )
    create_test_dataset(
        db_session, status="COMPLETED", title="Dataset 3", periodicity="quarterly"
    )

    datasets, count = dataset_repository.get_paginated_datasets(
        status="COMPLETED", periodicities=["weekly", "quarterly"]
    )

    assert count == 2
    assert len(datasets) == 2
    assert all(d.periodicity in ["weekly", "quarterly"] for d in datasets)
    assert {d.title for d in datasets} == {"Dataset 2", "Dataset 3"}


def test_get_paginated_datasets_created_by_user(dataset_repository, db_session):
    user_id_1 = 10001
    user_id_2 = 10002

    create_test_dataset(
        db_session, status="DRAFT", title="User Test 1", user_id=user_id_1
    )
    create_test_dataset(
        db_session, status="DRAFT", title="User Test 2", user_id=user_id_2
    )
    create_test_dataset(
        db_session, status="DRAFT", title="User Test 3", user_id=user_id_1
    )

    datasets, count = dataset_repository.get_paginated_datasets(
        status="DRAFT", created_by_user_id=user_id_1
    )

    assert count >= 2
    user1_datasets = [d for d in datasets if d.title in ["User Test 1", "User Test 3"]]
    assert len(user1_datasets) == 2
    assert all(d.user_id == user_id_1 for d in user1_datasets)


def test_get_paginated_datasets_group_manager(dataset_repository, db_session):
    dataset1 = create_test_dataset(db_session, status="DRAFT", title="GM Test 1")
    dataset2 = create_test_dataset(db_session, status="DRAFT", title="GM Test 2")
    dataset3 = create_test_dataset(db_session, status="DRAFT", title="GM Test 3")

    gm_id_1 = 20001
    gm_id_2 = 20002

    group_manager1 = DatasetGroupManagers(dataset_id=dataset1.id, user_id=gm_id_1)
    group_manager2 = DatasetGroupManagers(dataset_id=dataset3.id, user_id=gm_id_1)
    group_manager3 = DatasetGroupManagers(dataset_id=dataset2.id, user_id=gm_id_2)

    db_session.add_all([group_manager1, group_manager2, group_manager3])
    db_session.commit()

    datasets, count = dataset_repository.get_paginated_datasets(
        status="DRAFT", group_manager_user_id=gm_id_1
    )

    assert count >= 2
    gm1_datasets = [d for d in datasets if d.title in ["GM Test 1", "GM Test 3"]]
    assert len(gm1_datasets) == 2


def test_get_paginated_datasets_created_by_and_group_manager(
    dataset_repository, db_session
):
    user_id_1 = 30001
    user_id_2 = 30002
    user_id_3 = 30003

    dataset1 = create_test_dataset(
        db_session, status="DRAFT", title="Combined Test 1", user_id=user_id_1
    )
    dataset2 = create_test_dataset(
        db_session, status="DRAFT", title="Combined Test 2", user_id=user_id_2
    )
    dataset3 = create_test_dataset(
        db_session, status="DRAFT", title="Combined Test 3", user_id=user_id_3
    )
    dataset4 = create_test_dataset(
        db_session, status="DRAFT", title="Combined Test 4", user_id=user_id_3
    )

    group_managers = [
        DatasetGroupManagers(dataset_id=dataset1.id, user_id=user_id_2),
        DatasetGroupManagers(dataset_id=dataset2.id, user_id=user_id_3),
        DatasetGroupManagers(dataset_id=dataset3.id, user_id=user_id_1),
        DatasetGroupManagers(dataset_id=dataset4.id, user_id=user_id_3),
    ]

    db_session.add_all(group_managers)
    db_session.commit()

    datasets, count = dataset_repository.get_paginated_datasets(
        status="DRAFT", created_by_user_id=user_id_1, group_manager_user_id=user_id_1
    )

    # Should return datasets 1 and 3
    assert count >= 2
    matching_datasets = [
        d for d in datasets if d.title in ["Combined Test 1", "Combined Test 3"]
    ]
    assert len(matching_datasets) == 2


def test_get_paginated_datasets_with_query_title(dataset_repository, db_session):
    # Create datasets with distinct titles
    create_test_dataset(db_session, title="Apple Dataset", status="DRAFT")
    create_test_dataset(db_session, title="Banana Dataset", status="DRAFT")
    create_test_dataset(db_session, title="Another Apple Data", status="DRAFT")
    create_test_dataset(db_session, title="Orange Data Collection", status="DRAFT")

    # Search for "Apple" in title
    datasets, count = dataset_repository.get_paginated_datasets(
        status="DRAFT", query="Apple"
    )

    assert count == 2
    assert len(datasets) == 2
    titles = {d.title for d in datasets}
    assert "Apple Dataset" in titles
    assert "Another Apple Data" in titles
    assert "Banana Dataset" not in titles
    assert "Orange Data Collection" not in titles


def test_get_paginated_datasets_with_query_description(dataset_repository, db_session):
    # Create datasets with different descriptions
    dataset1 = create_test_dataset(db_session, title="Dataset 1", status="DRAFT")
    dataset1.description = "Contains important financial data"

    dataset2 = create_test_dataset(db_session, title="Dataset 2", status="DRAFT")
    dataset2.description = "Contains customer records"

    dataset3 = create_test_dataset(db_session, title="Dataset 3", status="DRAFT")
    dataset3.description = "More financial information"

    db_session.commit()

    # Search for "financial" in description
    datasets, count = dataset_repository.get_paginated_datasets(
        status="DRAFT", query="financial"
    )

    assert count == 2
    assert len(datasets) == 2
    titles = {d.title for d in datasets}
    assert "Dataset 1" in titles
    assert "Dataset 3" in titles
    assert "Dataset 2" not in titles


def test_get_paginated_datasets_with_query_notes(dataset_repository, db_session):
    # Create datasets with notes
    dataset1 = create_test_dataset(db_session, title="Dataset 1", status="DRAFT")
    dataset1.notes = "Reviewed by department A"

    dataset2 = create_test_dataset(db_session, title="Dataset 2", status="DRAFT")
    dataset2.notes = "Pending review"

    dataset3 = create_test_dataset(db_session, title="Dataset 3", status="DRAFT")
    dataset3.notes = "Reviewed by committee"

    db_session.commit()

    # Search for "review" in notes
    datasets, count = dataset_repository.get_paginated_datasets(
        status="DRAFT", query="review"
    )

    assert count == 3
    assert len(datasets) == 3


def test_get_paginated_datasets_with_query_multiple_fields(
    dataset_repository, db_session
):
    # Create datasets with searchable content in different fields
    dataset1 = create_test_dataset(db_session, title="Research Data", status="DRAFT")
    dataset1.description = "Standard research"

    dataset2 = create_test_dataset(db_session, title="Standard Dataset", status="DRAFT")
    dataset2.description = "From research department"

    dataset3 = create_test_dataset(db_session, title="Customer Data", status="DRAFT")
    dataset3.notes = "Used for research purposes"

    dataset4 = create_test_dataset(db_session, title="Employee Data", status="DRAFT")
    dataset4.monitoring_location = "HR department"

    db_session.commit()

    # Search for "research" across multiple fields
    datasets, count = dataset_repository.get_paginated_datasets(
        status="DRAFT", query="research"
    )

    assert count == 3
    assert len(datasets) == 3
    titles = {d.title for d in datasets}
    assert "Research Data" in titles
    assert "Standard Dataset" in titles
    assert "Customer Data" in titles
    assert "Employee Data" not in titles


def test_get_paginated_datasets_with_query_case_insensitive(
    dataset_repository, db_session
):
    # Create datasets to test case insensitivity
    create_test_dataset(db_session, title="UPPERCASE TITLE", status="DRAFT")
    create_test_dataset(db_session, title="lowercase title", status="DRAFT")
    create_test_dataset(db_session, title="Mixed Case Title", status="DRAFT")

    db_session.commit()

    # Search with lowercase
    datasets, count = dataset_repository.get_paginated_datasets(
        status="DRAFT", query="title"
    )

    assert count == 3
    assert len(datasets) == 3

    # Search with uppercase
    datasets, count = dataset_repository.get_paginated_datasets(
        status="DRAFT", query="TITLE"
    )

    assert count == 3
    assert len(datasets) == 3


def test_get_paginated_datasets_with_query_distribution_title(
    dataset_repository, db_session
):
    """Test that query searches in distribution titles and descriptions (OR logic with dataset fields)"""

    # Dataset 1: Match in dataset title
    dataset1 = create_test_dataset(db_session, title="Climate Dataset", status="DRAFT")

    # Dataset 2: Match in distribution title only
    dataset2 = create_test_dataset(db_session, title="Health Dataset", status="DRAFT")
    distribution2 = Distribution(
        dataset_id=dataset2.id,
        title="Climate Data Export",
        description="Export data in CSV format",
    )
    db_session.add(distribution2)

    # Dataset 3: Match in distribution description only
    dataset3 = create_test_dataset(db_session, title="Economic Data", status="DRAFT")
    distribution3 = Distribution(
        dataset_id=dataset3.id,
        title="GDP Export",
        description="Climate-related economic indicators",
    )
    db_session.add(distribution3)

    # Dataset 4: No match anywhere
    dataset4 = create_test_dataset(db_session, title="Population Data", status="DRAFT")
    distribution4 = Distribution(
        dataset_id=dataset4.id,
        title="Demographics Export",
        description="Population statistics",
    )
    db_session.add(distribution4)

    db_session.commit()

    # Search for "Climate"
    datasets, count = dataset_repository.get_paginated_datasets(
        status="DRAFT", query="Climate"
    )

    # Should find dataset1 (dataset title), dataset2 (distribution title), and dataset3 (distribution description)
    assert count == 3
    assert len(datasets) == 3
    titles = {d.title for d in datasets}
    assert "Climate Dataset" in titles
    assert "Health Dataset" in titles
    assert "Economic Data" in titles
    assert "Population Data" not in titles


def test_get_paginated_datasets_authentic_source_pending_filter(
    dataset_repository: DatasetRepository, db_session: Session
):
    dataset1 = create_test_dataset(
        db_session, status="PUBLISHED", title="Reviewed Dataset"
    )
    dataset2 = create_test_dataset(
        db_session, status="PUBLISHED", title="Not Reviewed Dataset"
    )
    dataset3 = create_test_dataset(
        db_session, status="PUBLISHED", title="Another Reviewed Dataset"
    )

    dataset1.authentic_source_reviewed_at = datetime.now(timezone.utc)
    dataset3.authentic_source_reviewed_at = datetime.now(timezone.utc)
    db_session.commit()

    datasets, count = dataset_repository.get_paginated_datasets(
        status="PUBLISHED", authentic_source_pending=True
    )

    assert count == 1
    assert len(datasets) == 1
    reviewed_titles = {d.title for d in datasets}
    assert "Not Reviewed Dataset" in reviewed_titles


def test_get_paginated_datasets_unlabeled_authentic_source_filter(
    dataset_repository: DatasetRepository, db_session: Session
):
    dataset1 = create_test_dataset(
        db_session, status="PUBLISHED", title="Has Unlabeled Authentic"
    )
    dataset2 = create_test_dataset(
        db_session, status="PUBLISHED", title="Has Labeled Authentic"
    )
    dataset3 = create_test_dataset(
        db_session, status="PUBLISHED", title="No Authentic Entries"
    )
    dataset4 = create_test_dataset(
        db_session, status="PUBLISHED", title="Mixed Authentic Entries"
    )

    entry1 = create_sample_data_dictionary_entry(
        dataset_id=dataset1.id, field_name="unlabeled_field", is_authentic_source=True
    )
    db_session.add(entry1)
    db_session.flush()

    entry2 = create_sample_data_dictionary_entry(
        dataset_id=dataset2.id, field_name="labeled_field", is_authentic_source=True
    )
    db_session.add(entry2)
    db_session.flush()

    entry3 = create_sample_data_dictionary_entry(
        dataset_id=dataset3.id, field_name="normal_field", is_authentic_source=False
    )
    db_session.add(entry3)
    db_session.flush()

    entry4 = create_sample_data_dictionary_entry(
        dataset_id=dataset4.id, field_name="unlabeled_field2", is_authentic_source=True
    )
    db_session.add(entry4)
    db_session.flush()

    entry5 = create_sample_data_dictionary_entry(
        dataset_id=dataset4.id, field_name="labeled_field2", is_authentic_source=True
    )
    db_session.add(entry5)
    db_session.flush()

    label1 = create_sample_authentic_source_label(id=None, name="Test Label 1")
    db_session.add(label1)
    db_session.flush()

    label2 = create_sample_authentic_source_label(id=None, name="Test Label 2")
    db_session.add(label2)
    db_session.flush()

    # Assign labels to some entries
    create_label_assignment(
        db_session, entry2.id, label1.id, is_active=True
    )  # dataset2 is fully labeled
    create_label_assignment(
        db_session, entry5.id, label2.id, is_active=True
    )  # dataset4 is partially labeled

    db_session.commit()

    # Your existing test
    datasets, count = dataset_repository.get_paginated_datasets(
        status="PUBLISHED", has_unlabeled_authentic_source=True
    )

    print(f"Filter returned {count} datasets:")
    for d in datasets:
        print(f"  - {d.title}")

    # Test filter for datasets with unlabeled authentic source entries
    datasets, count = dataset_repository.get_paginated_datasets(
        status="PUBLISHED", has_unlabeled_authentic_source=True
    )

    assert count == 2
    assert len(datasets) == 2
    unlabeled_titles = {d.title for d in datasets}
    assert "Has Unlabeled Authentic" in unlabeled_titles
    assert "Mixed Authentic Entries" in unlabeled_titles
    assert "Has Labeled Authentic" not in unlabeled_titles
    assert "No Authentic Entries" not in unlabeled_titles


def test_get_count_for_status_basic(dataset_repository, db_session):
    create_test_dataset(db_session, status="DRAFT", title="Draft Dataset 1")
    create_test_dataset(db_session, status="DRAFT", title="Draft Dataset 2")
    create_test_dataset(db_session, status="COMPLETED", title="Completed Dataset")

    assert dataset_repository.get_count_for_status("DRAFT") == 2
    assert dataset_repository.get_count_for_status("COMPLETED") == 1
    assert dataset_repository.get_count_for_status("PUBLISHED") == 0


def test_get_count_for_status_all_statuses(dataset_repository, db_session):
    create_test_dataset(db_session, status="DRAFT", title="Draft Dataset")
    create_test_dataset(db_session, status="COMPLETED", title="Completed Dataset")
    create_test_dataset(db_session, status="VALIDATED", title="Validated Dataset")
    create_test_dataset(db_session, status="APPROVED", title="Approved Dataset")
    create_test_dataset(db_session, status="PUBLISHED", title="Published Dataset")
    create_test_dataset(db_session, status="INTERNAL_ONLY", title="Internal Dataset")
    create_test_dataset(db_session, status="DEPRECATED", title="Deprecated Dataset")

    for status in DatasetStatus:
        assert dataset_repository.get_count_for_status(status.value) == 1


def test_get_count_for_status_by_user(dataset_repository, db_session):
    user_id_1 = 5001
    user_id_2 = 5002

    create_test_dataset(
        db_session, status="DRAFT", title="User1 Draft 1", user_id=user_id_1
    )
    create_test_dataset(
        db_session, status="DRAFT", title="User1 Draft 2", user_id=user_id_1
    )
    create_test_dataset(
        db_session, status="COMPLETED", title="User1 Completed", user_id=user_id_1
    )

    # Create datasets for user 2
    create_test_dataset(
        db_session, status="DRAFT", title="User2 Draft", user_id=user_id_2
    )
    create_test_dataset(
        db_session, status="VALIDATED", title="User2 Validated", user_id=user_id_2
    )

    # Test counts for user 1
    assert (
        dataset_repository.get_count_for_status("DRAFT", created_by_user_id=user_id_1)
        == 2
    )
    assert (
        dataset_repository.get_count_for_status(
            "COMPLETED", created_by_user_id=user_id_1
        )
        == 1
    )
    assert (
        dataset_repository.get_count_for_status(
            "VALIDATED", created_by_user_id=user_id_1
        )
        == 0
    )

    # Test counts for user 2
    assert (
        dataset_repository.get_count_for_status("DRAFT", created_by_user_id=user_id_2)
        == 1
    )
    assert (
        dataset_repository.get_count_for_status(
            "COMPLETED", created_by_user_id=user_id_2
        )
        == 0
    )
    assert (
        dataset_repository.get_count_for_status(
            "VALIDATED", created_by_user_id=user_id_2
        )
        == 1
    )


def test_get_count_for_status_by_group_manager(dataset_repository, db_session):
    # Create datasets with different statuses
    dataset1 = create_test_dataset(db_session, status="DRAFT", title="GM Dataset 1")
    dataset2 = create_test_dataset(db_session, status="COMPLETED", title="GM Dataset 2")
    dataset3 = create_test_dataset(db_session, status="DRAFT", title="Non-GM Dataset")

    # Set up group manager relationships
    manager_id = 6001
    group_manager1 = DatasetGroupManagers(dataset_id=dataset1.id, user_id=manager_id)
    group_manager2 = DatasetGroupManagers(dataset_id=dataset2.id, user_id=manager_id)

    db_session.add_all([group_manager1, group_manager2])
    db_session.commit()

    # Test counts filtered by group manager
    assert (
        dataset_repository.get_count_for_status(
            "DRAFT", group_manager_user_id=manager_id
        )
        == 1
    )
    assert (
        dataset_repository.get_count_for_status(
            "COMPLETED", group_manager_user_id=manager_id
        )
        == 1
    )
    assert (
        dataset_repository.get_count_for_status(
            "VALIDATED", group_manager_user_id=manager_id
        )
        == 0
    )

    # Test with a non-existent manager ID
    assert (
        dataset_repository.get_count_for_status("DRAFT", group_manager_user_id=9999)
        == 0
    )


def test_get_count_for_status_combined_filters(dataset_repository, db_session):
    """Test counting with both user ID and group manager ID filters."""
    user_id = 7001

    # Create datasets owned by the user
    user_dataset1 = create_test_dataset(
        db_session, status="DRAFT", title="User Dataset 1", user_id=user_id
    )
    user_dataset2 = create_test_dataset(
        db_session, status="COMPLETED", title="User Dataset 2", user_id=user_id
    )

    # Create datasets managed by the user but owned by others
    managed_dataset1 = create_test_dataset(
        db_session, status="DRAFT", title="Managed Dataset 1", user_id=7002
    )
    managed_dataset2 = create_test_dataset(
        db_session, status="VALIDATED", title="Managed Dataset 2", user_id=7003
    )

    # Create unrelated datasets
    create_test_dataset(
        db_session, status="DRAFT", title="Other Dataset 1", user_id=7004
    )
    create_test_dataset(
        db_session, status="PUBLISHED", title="Other Dataset 2", user_id=7005
    )

    # Set up group manager relationships
    group_manager1 = DatasetGroupManagers(
        dataset_id=managed_dataset1.id, user_id=user_id
    )
    group_manager2 = DatasetGroupManagers(
        dataset_id=managed_dataset2.id, user_id=user_id
    )

    db_session.add_all([group_manager1, group_manager2])
    db_session.commit()

    # Test with combined filters - should include both owned and managed datasets
    assert (
        dataset_repository.get_count_for_status(
            "DRAFT", created_by_user_id=user_id, group_manager_user_id=user_id
        )
        == 2
    )  # 1 owned + 1 managed

    assert (
        dataset_repository.get_count_for_status(
            "VALIDATED", created_by_user_id=user_id, group_manager_user_id=user_id
        )
        == 1
    )  # 0 owned + 1 managed

    assert (
        dataset_repository.get_count_for_status(
            "PUBLISHED", created_by_user_id=user_id, group_manager_user_id=user_id
        )
        == 0
    )  # No owned or managed


def test_has_published_newer_version_returns_true_when_newer_version_published(
    dataset_repository: DatasetRepository, db_session: Session
):
    # Create original dataset
    original_dataset = create_test_dataset(
        db_session, status="APPROVED", title="Original Dataset v1"
    )

    # Create newer version that references the original
    newer_dataset = create_test_dataset(
        db_session, status="PUBLISHED", title="Newer Dataset v2"
    )
    newer_dataset.previous_version_dataset_id = original_dataset.id
    db_session.commit()

    # Check that original dataset has a published newer version
    assert dataset_repository.has_published_newer_version(original_dataset.id) is True


def test_get_all_versions_of_dataset(
    dataset_repository: DatasetRepository, db_session: Session
):
    # Create version 1 (oldest)
    version1 = create_test_dataset(db_session, status="PUBLISHED", title="Dataset v1")

    # Create version 2 (middle)
    version2 = create_test_dataset(db_session, status="PUBLISHED", title="Dataset v2")
    version2.previous_version_dataset_id = version1.id

    # Create version 3 (latest)
    version3 = create_test_dataset(db_session, status="PUBLISHED", title="Dataset v3")
    version3.previous_version_dataset_id = version2.id

    db_session.commit()

    # Test getting all versions from the middle version
    all_versions = dataset_repository.get_all_versions_of_dataset(version2.id)

    assert len(all_versions) == 3
    assert all_versions[0].id == version1.id
    assert all_versions[1].id == version2.id
    assert all_versions[2].id == version3.id
    assert all_versions[0].title == "Dataset v1"
    assert all_versions[1].title == "Dataset v2"
    assert all_versions[2].title == "Dataset v3"


def test_get_dataset_by_source(
    dataset_repository: DatasetRepository, db_session: Session, sample_dataset: Dataset
):
    sample_dataset.source = "lnds-mdc"
    sample_dataset.source_dataset_id = 123
    db_session.add(sample_dataset)
    db_session.commit()

    actual = dataset_repository.get_dataset_by_source("lnds-mdc", 123)

    assert actual is not None
    assert actual.id == sample_dataset.id
    assert actual.source == "lnds-mdc"
    assert actual.source_dataset_id == 123
