import pytest
import json
from unittest.mock import Mock, MagicMock, call
from fastapi import HTTPException, status

from models.qualified_attribution import DatasetQualifiedAttribution
from models.identity_context import IdentityContext
from repositories.qualified_attribution import QualifiedAttributionRepository
from repositories.organisation import OrganisationRepository
from repositories.dataset import DatasetRepository
from schemas.qualified_attribution import (
    QualifiedAttributionDto,
    ResourceQualifiedAttribution,
)
from services.qualified_attribution import QualifiedAttributionService
from services.database_session_manager import DatabaseSessionManager
from services.dataset_permissions_service import DatasetPermissionsService
from services.activity_logs.qualifiedAttributionActivityLogService import (
    QualifiedAttributionActivityLogService,
)
from test_factory import sample_dataset, sample_organisation


@pytest.fixture
def mock_repository():
    return Mock(spec=QualifiedAttributionRepository)


@pytest.fixture
def mock_organisation_repository(sample_organisation):
    mock_repo = Mock(spec=OrganisationRepository)
    mock_repo.get_organisation.return_value = sample_organisation
    return mock_repo


@pytest.fixture
def mock_dataset_repository(sample_dataset):
    mock_repo = Mock(spec=DatasetRepository)
    mock_repo.get_dataset.return_value = sample_dataset
    return mock_repo


@pytest.fixture
def mock_session_manager():
    return Mock(spec=DatabaseSessionManager)


@pytest.fixture
def mock_permissions_service():
    mock_service = Mock(spec=DatasetPermissionsService)
    mock_service.validate_read_permissions.return_value = None
    mock_service.validate_edit_permissions.return_value = None
    return mock_service


@pytest.fixture
def mock_qualified_attribution_activity_log_service():
    return Mock(spec=QualifiedAttributionActivityLogService)


@pytest.fixture
def qualified_attribution_service(
    mock_qualified_attribution_activity_log_service,
) -> QualifiedAttributionService:
    return QualifiedAttributionService(
        repository=Mock(spec=QualifiedAttributionRepository),
        database_session_manager=Mock(spec=DatabaseSessionManager),
        dataset_permissions_service=Mock(spec=DatasetPermissionsService),
        organisation_repository=Mock(spec=OrganisationRepository),
        dataset_repository=Mock(spec=DatasetRepository),
        qualified_attribution_activity_log_service=mock_qualified_attribution_activity_log_service,
    )


@pytest.fixture
def qa_service(
    mock_repository,
    mock_session_manager,
    mock_permissions_service,
    mock_organisation_repository,
    mock_dataset_repository,
    mock_qualified_attribution_activity_log_service,
):
    return QualifiedAttributionService(
        repository=mock_repository,
        database_session_manager=mock_session_manager,
        dataset_permissions_service=mock_permissions_service,
        organisation_repository=mock_organisation_repository,
        dataset_repository=mock_dataset_repository,
        qualified_attribution_activity_log_service=mock_qualified_attribution_activity_log_service,
    )


@pytest.fixture
def identity():
    return IdentityContext(user_id=1, permissions=["datasets:edit:all"])


@pytest.fixture
def qa_dto():
    return QualifiedAttributionDto(organisation_id=1, role="author")


def test_get_qualified_attributions_by_dataset_id(
    qa_service, mock_repository, mock_permissions_service, identity
):
    dataset_id = 1

    qa1 = DatasetQualifiedAttribution(
        id=1, dataset_id=dataset_id, organisation_id=1, role="author"
    )
    qa2 = DatasetQualifiedAttribution(
        id=2, dataset_id=dataset_id, organisation_id=2, role="contributor"
    )
    mock_repository.get_attributions_by_dataset_id.return_value = [qa1, qa2]
    result = qa_service.get_qualified_attributions_by_dataset_id(dataset_id, identity)
    mock_permissions_service.validate_read_permissions.assert_called_once_with(
        dataset_id, identity
    )
    mock_repository.get_attributions_by_dataset_id.assert_called_once_with(dataset_id)
    assert len(result) == 2


def test_add_qualified_attribution_success(
    qa_service,
    mock_repository,
    mock_session_manager,
    mock_permissions_service,
    mock_organisation_repository,
    mock_qualified_attribution_activity_log_service,
    sample_organisation,
    identity,
    qa_dto,
):
    dataset_id = 1

    mock_repository.exists.return_value = False
    mock_organisation_repository.get_organisation.return_value = sample_organisation
    mock_session_manager.refresh.side_effect = lambda x: setattr(x, "id", 1)

    result = qa_service.add_qualified_attribution(dataset_id, qa_dto, identity)

    mock_permissions_service.validate_edit_permissions.assert_called_once_with(
        dataset_id, identity
    )
    mock_repository.exists.assert_called_once_with(dataset_id, 1, "author")
    mock_repository.add.assert_called_once()
    mock_session_manager.commit.assert_called_once()

    mock_qualified_attribution_activity_log_service.log_qualified_attribution_added.assert_called_once_with(  # FIX METHOD NAME
        user_id=identity.user_id,
        dataset_id=dataset_id,
        organisation_name=sample_organisation.name,
        role="author",
    )


def test_add_qualified_attribution_already_exists(
    qa_service,
    mock_repository,
    mock_organisation_repository,
    sample_organisation,
    identity,
    qa_dto,
):
    dataset_id = 1

    mock_repository.exists.return_value = True
    mock_organisation_repository.get_organisation.return_value = sample_organisation

    with pytest.raises(HTTPException) as exc_info:
        qa_service.add_qualified_attribution(dataset_id, qa_dto, identity)

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert sample_organisation.name in exc_info.value.detail
    assert "author" in exc_info.value.detail


def test_update_qualified_attribution_success(
    qa_service,
    mock_repository,
    mock_session_manager,
    mock_permissions_service,
    mock_organisation_repository,
    mock_qualified_attribution_activity_log_service,
    sample_organisation,
    identity,
):
    dataset_id = 1
    attribution_id = 1

    old_qa = DatasetQualifiedAttribution(
        id=attribution_id,
        dataset_id=dataset_id,
        organisation_id=1,
        role="author",
    )
    mock_repository.get_qualified_attribution.return_value = old_qa
    mock_repository.exists.return_value = False
    mock_organisation_repository.get_organisation.return_value = sample_organisation

    new_dto = QualifiedAttributionDto(organisation_id=1, role="contributor")

    result = qa_service.update_qualified_attribution(
        dataset_id, attribution_id, new_dto, identity
    )

    mock_permissions_service.validate_edit_permissions.assert_called_once_with(
        dataset_id, identity
    )
    mock_repository.update.assert_called_once()
    mock_session_manager.commit.assert_called_once()

    mock_qualified_attribution_activity_log_service.log_qualified_attribution_updated.assert_called_once_with(  # FIX METHOD NAME
        user_id=identity.user_id,
        dataset_id=dataset_id,
        old_organisation_name=sample_organisation.name,
        old_role="author",
        new_organisation_name=sample_organisation.name,
        new_role="contributor",
    )


def test_delete_qualified_attribution_success(
    qa_service,
    mock_repository,
    mock_session_manager,
    mock_permissions_service,
    mock_organisation_repository,
    mock_qualified_attribution_activity_log_service,
    sample_organisation,
    identity,
):
    dataset_id = 1
    attribution_id = 1

    qa = DatasetQualifiedAttribution(
        id=attribution_id,
        dataset_id=dataset_id,
        organisation_id=1,
        role="author",
    )

    mock_repository.get_qualified_attribution.return_value = qa
    mock_organisation_repository.get_organisation.return_value = sample_organisation

    qa_service.delete_qualified_attribution(dataset_id, attribution_id, identity)

    mock_permissions_service.validate_edit_permissions.assert_called_once_with(
        dataset_id, identity
    )
    mock_repository.delete.assert_called_once_with(attribution_id)
    mock_session_manager.commit.assert_called_once()

    mock_qualified_attribution_activity_log_service.log_qualified_attribution_removed.assert_called_once_with(  # FIX METHOD NAME
        user_id=identity.user_id,
        dataset_id=dataset_id,
        organisation_name=sample_organisation.name,
        role="author",
    )
