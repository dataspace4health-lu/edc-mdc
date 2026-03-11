import pytest
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from services.authentic_source_assignment import AuthenticSourceAssignmentService
from repositories.authentic_source_label import AuthenticSourceLabelRepository
from repositories.authentic_source_assignment import AuthenticSourceAssignmentRepository
from models.authentic_source_label import AuthenticSourceLabel
from models.authentic_source_assignment import AuthenticSourceAssignment
from models.data_dictionary import DataDictionaryEntry
from models.identity_context import IdentityContext
from schemas.authentic_source_assignment import (
    BulkLabelAssignmentDto,
    LabelAssignmentDto,
)
from schemas.authentic_source_label import ResourceAuthenticSourceLabel
from repositories.dataset import DatasetRepository
from services.database_session_manager import DatabaseSessionManager
from models.dataset import Dataset
from factories.data_dictionary_entry import create_sample_data_dictionary_entry
from test_factory import sample_dataset
from unittest.mock import Mock
from factories.authentic_source_label import create_sample_authentic_source_label
from services.activity_logs.authentic_source_label_activity_log import (
    AuthenticSourceLabelActivityLogService,
)


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    yield
    db_session.query(AuthenticSourceAssignment).delete()
    db_session.query(AuthenticSourceLabel).delete()
    db_session.query(DataDictionaryEntry).delete()
    db_session.commit()


@pytest.fixture
def authentic_source_label_repository(
    db_session: Session,
) -> AuthenticSourceLabelRepository:
    return AuthenticSourceLabelRepository(db_session)


@pytest.fixture
def authentic_source_assignment_repository(
    db_session: Session,
) -> AuthenticSourceAssignmentRepository:
    return AuthenticSourceAssignmentRepository(db_session)


@pytest.fixture
def dataset_repository(
    db_session: Session,
) -> DatasetRepository:
    return DatasetRepository(db_session)


@pytest.fixture
def db_session_manager(
    db_session: Session,
) -> DatabaseSessionManager:
    return DatabaseSessionManager(db_session=db_session)


@pytest.fixture
def service(
    authentic_source_label_repository: AuthenticSourceLabelRepository,
    authentic_source_assignment_repository: AuthenticSourceAssignmentRepository,
    dataset_repository: DatasetRepository,
    db_session_manager: DatabaseSessionManager,
) -> AuthenticSourceAssignmentService:
    mock_dictionary_repo = Mock()
    mock_activity_log_service = Mock()
    mock_email_service = Mock()
    return AuthenticSourceAssignmentService(
        label_repo=authentic_source_label_repository,
        assignment_repo=authentic_source_assignment_repository,
        dataset_repo=dataset_repository,
        db_session_manager=db_session_manager,
        dictionary_repo=mock_dictionary_repo,
        activity_log_service=mock_activity_log_service,
        email_service=mock_email_service,
    )


@pytest.fixture
def identity_context() -> IdentityContext:
    mock_identity = Mock(spec=IdentityContext)
    mock_identity.user_id = 1
    return mock_identity


@pytest.fixture
def sample_data_dictionary_entry(
    db_session: Session, sample_dataset: Dataset
) -> DataDictionaryEntry:

    sample_dataset2 = sample_dataset
    db_session.add(sample_dataset2)
    db_session.flush()

    entry = create_sample_data_dictionary_entry(dataset_id=sample_dataset2.id)
    db_session.add(entry)
    db_session.commit()
    db_session.refresh(entry)
    return entry


@pytest.fixture
def another_data_dictionary_entry(
    db_session: Session, sample_dataset: Dataset
) -> DataDictionaryEntry:
    entry = create_sample_data_dictionary_entry(
        dataset_id=sample_dataset.id, field_name="another"
    )
    db_session.add(entry)
    db_session.commit()
    db_session.refresh(entry)
    return entry


@pytest.fixture
def sample_authentic_source_label(db_session: Session) -> AuthenticSourceLabel:
    label = create_sample_authentic_source_label(id=1, name="Government Records")
    db_session.add(label)
    db_session.commit()
    db_session.refresh(label)
    return label


@pytest.fixture
def another_authentic_source_label(db_session: Session) -> AuthenticSourceLabel:
    label = create_sample_authentic_source_label(id=2, name="Financial Institution")
    db_session.add(label)
    db_session.commit()
    db_session.refresh(label)
    return label


@pytest.fixture
def third_authentic_source_label(db_session: Session) -> AuthenticSourceLabel:
    label = create_sample_authentic_source_label(id=3, name="Academic Research")
    db_session.add(label)
    db_session.commit()
    db_session.refresh(label)
    return label


def test_assign_labels_single_label_to_entry(
    db_session: Session,
    service: AuthenticSourceAssignmentService,
    identity_context: IdentityContext,
    sample_data_dictionary_entry: DataDictionaryEntry,
    sample_authentic_source_label: AuthenticSourceLabel,
):
    bulk_dto = BulkLabelAssignmentDto(
        label_assignments=[
            LabelAssignmentDto(
                label_id=sample_authentic_source_label.id,
                assigned_entry_id=sample_data_dictionary_entry.id,
            )
        ]
    )

    mock_entry = Mock()
    mock_entry.dataset_id = sample_data_dictionary_entry.dataset_id
    service._dictionary_repo.get_data_dictionary_entry.return_value = mock_entry

    result = service.assign_labels(bulk_dto, identity_context)

    # Verify assignment was created
    assignment = db_session.query(AuthenticSourceAssignment).first()
    assert assignment is not None
    assert assignment.data_dictionary_entry_id == sample_data_dictionary_entry.id
    assert assignment.authentic_source_label_id == sample_authentic_source_label.id
    assert assignment.assigned_by == identity_context.user_id
    assert assignment.is_active == True

    service._activity_log_service.log_label_assigned.assert_called_once_with(
        user_id=identity_context.user_id,
        label_id=sample_authentic_source_label.id,
        label_name=sample_authentic_source_label.name,
        entry_id=sample_data_dictionary_entry.id,
        old_entry_id=None,
        dataset_id=sample_data_dictionary_entry.dataset_id,
        old_dataset_id=None,
    )


def test_assign_labels_multiple_labels_to_different_entries(
    db_session: Session,
    service: AuthenticSourceAssignmentService,
    identity_context: IdentityContext,
    sample_data_dictionary_entry: DataDictionaryEntry,
    another_data_dictionary_entry: DataDictionaryEntry,
    sample_authentic_source_label: AuthenticSourceLabel,
    another_authentic_source_label: AuthenticSourceLabel,
):
    bulk_dto = BulkLabelAssignmentDto(
        label_assignments=[
            LabelAssignmentDto(
                label_id=sample_authentic_source_label.id,
                assigned_entry_id=sample_data_dictionary_entry.id,
            ),
            LabelAssignmentDto(
                label_id=another_authentic_source_label.id,
                assigned_entry_id=another_data_dictionary_entry.id,
            ),
        ]
    )

    def mock_get_entry(entry_id):
        if entry_id == sample_data_dictionary_entry.id:
            mock_entry = Mock()
            mock_entry.dataset_id = sample_data_dictionary_entry.dataset_id
            return mock_entry
        elif entry_id == another_data_dictionary_entry.id:
            mock_entry = Mock()
            mock_entry.dataset_id = another_data_dictionary_entry.dataset_id
            return mock_entry
        return None

    service._dictionary_repo.get_data_dictionary_entry.side_effect = mock_get_entry

    result = service.assign_labels(bulk_dto, identity_context)

    assignments = db_session.query(AuthenticSourceAssignment).all()
    assert len(assignments) == 2

    assignment_1 = next(
        a
        for a in assignments
        if a.authentic_source_label_id == sample_authentic_source_label.id
    )
    assignment_2 = next(
        a
        for a in assignments
        if a.authentic_source_label_id == another_authentic_source_label.id
    )

    assert assignment_1.data_dictionary_entry_id == sample_data_dictionary_entry.id
    assert assignment_2.data_dictionary_entry_id == another_data_dictionary_entry.id
    assert assignment_1.is_active == True
    assert assignment_2.is_active == True

    assert service._activity_log_service.log_label_assigned.call_count == 2

    calls = service._activity_log_service.log_label_assigned.call_args_list
    assert any(
        call.kwargs["label_id"] == sample_authentic_source_label.id for call in calls
    )
    assert any(
        call.kwargs["label_id"] == another_authentic_source_label.id for call in calls
    )


def test_assign_labels_reassign_entry_to_different_label(
    db_session: Session,
    service: AuthenticSourceAssignmentService,
    identity_context: IdentityContext,
    sample_data_dictionary_entry: DataDictionaryEntry,
    sample_authentic_source_label: AuthenticSourceLabel,
    another_authentic_source_label: AuthenticSourceLabel,
):
    initial_assignment = AuthenticSourceAssignment(
        data_dictionary_entry_id=sample_data_dictionary_entry.id,
        authentic_source_label_id=sample_authentic_source_label.id,
        assigned_by=identity_context.user_id,
        assigned_at=datetime.now(timezone.utc),
        is_active=True,
    )
    db_session.add(initial_assignment)
    db_session.commit()

    bulk_dto = BulkLabelAssignmentDto(
        label_assignments=[
            LabelAssignmentDto(
                label_id=another_authentic_source_label.id,
                assigned_entry_id=sample_data_dictionary_entry.id,
            )
        ]
    )

    mock_entry = Mock()
    mock_entry.dataset_id = sample_data_dictionary_entry.dataset_id
    service._dictionary_repo.get_data_dictionary_entry.return_value = mock_entry

    result = service.assign_labels(bulk_dto, identity_context)

    assignments = (
        db_session.query(AuthenticSourceAssignment)
        .order_by(AuthenticSourceAssignment.assigned_at)
        .all()
    )
    assert len(assignments) == 2

    old_assignment = assignments[0]
    new_assignment = assignments[1]

    assert old_assignment.is_active == False
    assert old_assignment.authentic_source_label_id == sample_authentic_source_label.id

    assert new_assignment.is_active == True
    assert new_assignment.authentic_source_label_id == another_authentic_source_label.id
    assert new_assignment.data_dictionary_entry_id == sample_data_dictionary_entry.id

    service._activity_log_service.log_label_assigned.assert_called_once_with(
        user_id=identity_context.user_id,
        label_id=another_authentic_source_label.id,
        label_name=another_authentic_source_label.name,
        entry_id=sample_data_dictionary_entry.id,
        old_entry_id=None,
        dataset_id=sample_data_dictionary_entry.dataset_id,
        old_dataset_id=None,
    )


def test_assign_labels_unassign_label(
    db_session: Session,
    service: AuthenticSourceAssignmentService,
    identity_context: IdentityContext,
    sample_data_dictionary_entry: DataDictionaryEntry,
    sample_authentic_source_label: AuthenticSourceLabel,
):
    initial_assignment = AuthenticSourceAssignment(
        data_dictionary_entry_id=sample_data_dictionary_entry.id,
        authentic_source_label_id=sample_authentic_source_label.id,
        assigned_by=identity_context.user_id,
        assigned_at=datetime.now(timezone.utc),
        is_active=True,
    )
    db_session.add(initial_assignment)
    db_session.commit()

    # Unassign the label
    bulk_dto = BulkLabelAssignmentDto(
        label_assignments=[
            LabelAssignmentDto(
                label_id=sample_authentic_source_label.id,
                assigned_entry_id=None,  # Unassign
            )
        ]
    )

    def mock_get_entry(entry_id):
        if entry_id == sample_data_dictionary_entry.id:
            mock_entry = Mock()
            mock_entry.dataset_id = sample_data_dictionary_entry.dataset_id
            return mock_entry
        return None

    service._dictionary_repo.get_data_dictionary_entry.side_effect = mock_get_entry

    result = service.assign_labels(bulk_dto, identity_context)

    # Verify assignment is deactivated
    assignment = db_session.query(AuthenticSourceAssignment).first()
    assert assignment.is_active == False

    service._activity_log_service.log_label_unassigned.assert_called_once_with(
        user_id=identity_context.user_id,
        label_id=sample_authentic_source_label.id,
        label_name=sample_authentic_source_label.name,
        old_entry_id=sample_data_dictionary_entry.id,
        old_dataset_id=sample_data_dictionary_entry.dataset_id,
    )


def test_assign_labels_move_label_to_different_entry(
    db_session: Session,
    service: AuthenticSourceAssignmentService,
    identity_context: IdentityContext,
    sample_data_dictionary_entry: DataDictionaryEntry,
    another_data_dictionary_entry: DataDictionaryEntry,
    sample_authentic_source_label: AuthenticSourceLabel,
):
    initial_assignment = AuthenticSourceAssignment(
        data_dictionary_entry_id=sample_data_dictionary_entry.id,
        authentic_source_label_id=sample_authentic_source_label.id,
        assigned_by=identity_context.user_id,
        assigned_at=datetime.now(timezone.utc),
        is_active=True,
    )
    db_session.add(initial_assignment)
    db_session.commit()

    bulk_dto = BulkLabelAssignmentDto(
        label_assignments=[
            LabelAssignmentDto(
                label_id=sample_authentic_source_label.id,
                assigned_entry_id=another_data_dictionary_entry.id,
            )
        ]
    )

    def mock_get_entry(entry_id):
        if entry_id == sample_data_dictionary_entry.id:
            mock_entry = Mock()
            mock_entry.dataset_id = sample_data_dictionary_entry.dataset_id
            return mock_entry
        elif entry_id == another_data_dictionary_entry.id:
            mock_entry = Mock()
            mock_entry.dataset_id = another_data_dictionary_entry.dataset_id
            return mock_entry
        return None

    service._dictionary_repo.get_data_dictionary_entry.side_effect = mock_get_entry

    result = service.assign_labels(bulk_dto, identity_context)

    # Verify old assignment is deactivated and new one created
    assignments = (
        db_session.query(AuthenticSourceAssignment)
        .order_by(AuthenticSourceAssignment.assigned_at)
        .all()
    )
    assert len(assignments) == 2

    old_assignment = assignments[0]
    new_assignment = assignments[1]

    assert old_assignment.is_active == False
    assert old_assignment.data_dictionary_entry_id == sample_data_dictionary_entry.id

    assert new_assignment.is_active == True
    assert new_assignment.data_dictionary_entry_id == another_data_dictionary_entry.id
    assert new_assignment.authentic_source_label_id == sample_authentic_source_label.id


def test_assign_labels_same_assignment_no_change(
    db_session: Session,
    service: AuthenticSourceAssignmentService,
    identity_context: IdentityContext,
    sample_data_dictionary_entry: DataDictionaryEntry,
    sample_authentic_source_label: AuthenticSourceLabel,
):
    initial_assignment = AuthenticSourceAssignment(
        data_dictionary_entry_id=sample_data_dictionary_entry.id,
        authentic_source_label_id=sample_authentic_source_label.id,
        assigned_by=identity_context.user_id,
        assigned_at=datetime.now(timezone.utc),
        is_active=True,
    )
    db_session.add(initial_assignment)
    db_session.commit()
    initial_time = initial_assignment.assigned_at

    bulk_dto = BulkLabelAssignmentDto(
        label_assignments=[
            LabelAssignmentDto(
                label_id=sample_authentic_source_label.id,
                assigned_entry_id=sample_data_dictionary_entry.id,
            )
        ]
    )

    result = service.assign_labels(bulk_dto, identity_context)

    assignments = db_session.query(AuthenticSourceAssignment).all()
    assert len(assignments) == 1
    assert assignments[0].is_active == True
    assert assignments[0].assigned_at == initial_time  # No new assignment created


def test_complete_authentic_source_review_success(
    db_session: Session,
    service: AuthenticSourceAssignmentService,
    identity_context: IdentityContext,
    sample_dataset: Dataset,
):
    db_session.add(sample_dataset)
    db_session.commit()

    assert sample_dataset.authentic_source_reviewed_at is None

    service.complete_authentic_source_review(sample_dataset.id)

    db_session.refresh(sample_dataset)

    assert sample_dataset.authentic_source_reviewed_at is not None
    assert isinstance(sample_dataset.authentic_source_reviewed_at, datetime)
