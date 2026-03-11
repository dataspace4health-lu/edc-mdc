import pytest
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException
from models.identity_context import IdentityContext
from models.dataset import DatasetStatus
from models.organisation import Organisation
from repositories.dataset import DatasetRepository
from repositories.organisation import OrganisationRepository
from services.dataset_permissions_service import DatasetPermissionsService
from services.config import ConfigService

IMPORTED_DATASET_ERROR = "Imported datasets are read-only and cannot be modified."


@pytest.fixture
def dataset_repository():
    repository = Mock(spec=DatasetRepository)
    repository.is_dataset_imported.return_value = False
    return repository


@pytest.fixture
def service(dataset_repository):
    return DatasetPermissionsService(dataset_repository=dataset_repository)


def test_validate_edit_permissions_dataset_not_found(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(user_id=123, permissions=[])

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        None,
        None,
        None,
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_edit_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 404
    assert f"Dataset[{dataset_id}] not found" == exc_info.value.detail


def test_validate_edit_permissions_not_in_draft(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(user_id=123, permissions=[])

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "PUBLISHED",
        1,
        123,
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_edit_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 409
    assert (
        "This dataset cannot be edited anymore, as it is not in draft mode anymore"
        == exc_info.value.detail
    )


def test_validate_edit_permissions_has_no_permission(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(user_id=123, permissions=[])

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        1,
        123,
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_edit_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 403
    assert "You are not allowed to edit this dataset" == exc_info.value.detail


def test_validate_doesnot_have_permissions_to_edit(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(user_id=123, permissions=[])

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        1,
        123,
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_edit_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 403
    assert "You are not allowed to edit this dataset" == exc_info.value.detail


def test_validate_edit_permissions_doest_owns_dataset(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(user_id=999, permissions=["datasets:edit:draft:my"])

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        1,
        123,
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_edit_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 403
    assert "You are not allowed to edit this dataset" == exc_info.value.detail


def test_validate_edit_permissions_owns_dataset(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(user_id=123, permissions=["datasets:edit:draft:my"])

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        1,
        123,
    ]

    service.validate_edit_permissions(dataset_id, identity)


def test_validate_edit_permissions_imported_dataset(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(user_id=123, permissions=["datasets:edit:draft"])

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        1,
        123,
    ]
    dataset_repository.is_dataset_imported.return_value = True

    with pytest.raises(HTTPException) as exc_info:
        service.validate_edit_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == IMPORTED_DATASET_ERROR


def test_validate_edit_all_permissions(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(user_id=999, permissions=["datasets:edit:draft"])

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        1,
        123,
    ]

    service.validate_edit_permissions(dataset_id, identity)


def test_validate_edit_permissions_group_manager(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(user_id=123, permissions=["datasets:edit:draft:group"])

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        1,
        123,
    ]
    dataset_repository.get_dataset_group_manager_user_ids.return_value = [123]

    service.validate_edit_permissions(dataset_id, identity)


def test_validate_edit_permissions_organisation_same_org(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:edit:draft:organisation"],
        current_organisation_id=456,
    )

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        456,  # Same organization as identity
        789,  # Different user
    ]

    service.validate_edit_permissions(dataset_id, identity)


def test_validate_edit_permissions_organisation_different_org(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:edit:draft:organisation"],
        current_organisation_id=456,
    )

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        789,  # Different organization
        999,  # Different user
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_edit_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 403
    assert "You are not allowed to update this dataset" == exc_info.value.detail


def test_validate_read_permissions_dataset_not_found(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(user_id=123, permissions=["datasets:edit:draft"])

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        None,
        None,
        None,
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_read_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 404
    assert f"Dataset[{dataset_id}] not found" == exc_info.value.detail


def test_validate_read_permissions_has_read_permission(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(user_id=123, permissions=["datasets:edit:draft"])

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        1,
        123,
    ]

    service.validate_read_permissions(dataset_id, identity)


def test_validate_read_permissions_all_after_draft_and_dataset_is_published(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(
        user_id=123, permissions=["datasets:read:all-after-draft"]
    )

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "PUBLISHED",
        1,
        123,
    ]

    service.validate_read_permissions(dataset_id, identity)


def test_validate_read_permissions_all_after_draft_and_dataset_is_deprecated(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(
        user_id=123, permissions=["datasets:read:all-after-draft"]
    )

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DEPRECATED",
        1,
        123,
    ]

    service.validate_read_permissions(dataset_id, identity)


def test_validate_read_permissions_all_after_draft_and_dataset_is_draft(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(
        user_id=123, permissions=["datasets:read:all-after-draft"]
    )

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        1,
        456,
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_read_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 403
    assert "You are not allowed to retrieve this dataset" == exc_info.value.detail


def test_validate_read_permissions_all_after_completed_and_dataset_is_completed(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(
        user_id=123, permissions=["datasets:read:all-after-complete"]
    )

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "COMPLETED",
        1,
        456,
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_read_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 403
    assert "You are not allowed to retrieve this dataset" == exc_info.value.detail


def test_validate_doesnot_have_permissions_to_read(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(user_id=456, permissions=[])

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        1,
        123,
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_read_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 403
    assert "You are not allowed to retrieve this dataset" == exc_info.value.detail


def test_validate_read_permissions_doesnt_owns_dataset(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(user_id=999, permissions=["datasets:edit:draft:my"])

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        1,
        123,
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_read_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 403
    assert "You are not allowed to retrieve this dataset" == exc_info.value.detail


def test_validate_read_permissions_owns_dataset_regardless_of_status(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(user_id=123, permissions=[])

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "COMPLETED",
        1,
        123,
    ]

    service.validate_read_permissions(dataset_id, identity)


def test_validate_read_permissions_group_manager(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(user_id=123, permissions=["datasets:edit:draft:group"])

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        1,
        123,
    ]
    dataset_repository.get_dataset_group_manager_user_ids.return_value = [123]

    service.validate_read_permissions(dataset_id, identity)


def test_validate_read_permissions_group_manager_not_in_group(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(user_id=789, permissions=["datasets:edit:draft:group"])

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        1,
        123,
    ]
    dataset_repository.get_dataset_group_manager_user_ids.return_value = [456]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_read_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 403
    assert "You are not allowed to retrieve this dataset" == exc_info.value.detail


def test_validate_read_permissions_organisation_draft_same_org(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:edit:draft:organisation"],
        current_organisation_id=456,
    )

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        456,  # Same organization as identity
        789,  # Different user
    ]

    service.validate_read_permissions(dataset_id, identity)


def test_validate_read_permissions_organisation_draft_different_org(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:edit:draft:organisation"],
        current_organisation_id=456,
    )

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        789,  # Different organization
        999,  # Different user
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_read_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 403
    assert "You are not allowed to retrieve this dataset" == exc_info.value.detail


def test_validate_read_permissions_read_all_after_draft_organisation_same_org(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:read:all-after-draft:organisation"],
        current_organisation_id=456,
    )

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "COMPLETED",  # Any status after DRAFT
        456,  # Same organization as identity
        789,  # Different user
    ]

    service.validate_read_permissions(dataset_id, identity)


def test_validate_read_permissions_same_organization_completed_status(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:read:completed"],
        current_organisation_id=456,
    )

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "COMPLETED",
        456,  # Same organization as identity
        789,  # Different user
    ]

    service.validate_read_permissions(dataset_id, identity)


def test_validate_read_permissions_same_organization_validated_status(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:read:validated"],
        current_organisation_id=456,
    )

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "VALIDATED",
        456,  # Same organization as identity
        789,  # Different user
    ]

    service.validate_read_permissions(dataset_id, identity)


def test_validate_read_permissions_same_organization_approved_status(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(
        user_id=123, permissions=["datasets:read:approved"], current_organisation_id=456
    )

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "APPROVED",
        456,  # Same organization as identity
        789,  # Different user
    ]

    service.validate_read_permissions(dataset_id, identity)


def test_validate_read_permissions_same_organization_published_status(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:read:published"],
        current_organisation_id=456,
    )

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "PUBLISHED",
        456,  # Same organization as identity
        789,  # Different user
    ]

    service.validate_read_permissions(dataset_id, identity)


def test_validate_read_permissions_published_different_organization_allowed(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:read:published"],
        current_organisation_id=456,
    )

    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "PUBLISHED",
        789,  # Different organization
        999,  # Different user
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_read_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 403
    assert "You are not allowed to retrieve this dataset" in str(exc_info.value.detail)


def test_validate_delete_permissions_dataset_not_found(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(user_id=123, permissions=[])
    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        None,
        None,
        None,
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_delete_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 404
    assert f"Dataset[{dataset_id}] not found" == exc_info.value.detail


def test_validate_delete_permissions_not_in_draft(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(user_id=123, permissions=[])
    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "PUBLISHED",
        1,
        123,
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_delete_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 403
    assert (
        "This dataset cannot be deleted as it is not in the draft state."
        == exc_info.value.detail
    )


def test_validate_delete_permissions_has_no_permission(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(user_id=123, permissions=[])
    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        1,
        123,
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_delete_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 403
    assert "You do not have permission to delete this dataset." == exc_info.value.detail


def test_validate_delete_permissions_doest_owns_dataset(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(user_id=999, permissions=["datasets:delete:draft:my"])
    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        1,
        123,
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_delete_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 403
    assert "You do not have permission to delete this dataset." == exc_info.value.detail


def test_validate_delete_permissions_organisation_same_org(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:delete:draft:organisation"],
        current_organisation_id=456,
    )
    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        456,  # Same organization as identity
        789,  # Different user
    ]

    service.validate_delete_permissions(dataset_id, identity)


def test_validate_delete_permissions_imported_dataset(service, dataset_repository):
    dataset_id = 1
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:delete:draft"],
        current_organisation_id=456,
    )
    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        456,
        123,
    ]
    dataset_repository.is_dataset_imported.return_value = True

    with pytest.raises(HTTPException) as exc_info:
        service.validate_delete_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == IMPORTED_DATASET_ERROR


def test_validate_delete_permissions_organisation_different_org(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:delete:draft:organisation"],
        current_organisation_id=456,
    )
    dataset_repository.get_dataset_status_publisher_id_and_user_id.return_value = [
        "DRAFT",
        789,  # Different organization
        999,  # Different user
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_delete_permissions(dataset_id, identity)

    assert exc_info.value.status_code == 403
    assert "You are not allowed to delete this dataset" == exc_info.value.detail


def test_list_access_params_draft_with_edit_draft_permission(service):
    identity = IdentityContext(
        user_id=123, permissions=["datasets:edit:draft"], current_organisation_id=456
    )

    created_by_user_id, group_manager_user_id, organisation_id = (
        service.get_dataset_list_access_params(identity, DatasetStatus.DRAFT.value)
    )

    assert created_by_user_id is None
    assert group_manager_user_id is None
    assert organisation_id == 456


def test_list_access_params_draft_with_edit_draft_organisation_permission(service):
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:edit:draft:organisation"],
        current_organisation_id=456,
    )

    created_by_user_id, group_manager_user_id, organisation_id = (
        service.get_dataset_list_access_params(identity, DatasetStatus.DRAFT.value)
    )

    assert created_by_user_id is None
    assert group_manager_user_id is None
    assert organisation_id == 456


def test_list_access_params_draft_with_edit_draft_group_permission(service):
    identity = IdentityContext(user_id=123, permissions=["datasets:edit:draft:group"])

    created_by_user_id, group_manager_user_id, organisation_id = (
        service.get_dataset_list_access_params(identity, DatasetStatus.DRAFT.value)
    )

    assert created_by_user_id == 123
    assert group_manager_user_id == 123
    assert organisation_id is None


def test_list_access_params_draft_with_no_permission(service):
    identity = IdentityContext(user_id=123, permissions=[])

    created_by_user_id, group_manager_user_id, organisation_id = (
        service.get_dataset_list_access_params(identity, DatasetStatus.DRAFT.value)
    )

    assert created_by_user_id == 123
    assert group_manager_user_id is None
    assert organisation_id is None


def test_list_access_params_completed_with_read_all_after_draft_permission(service):
    identity = IdentityContext(
        user_id=123, permissions=["datasets:read:all-after-draft"]
    )

    created_by_user_id, group_manager_user_id, organisation_id = (
        service.get_dataset_list_access_params(identity, DatasetStatus.COMPLETED.value)
    )

    assert created_by_user_id is None
    assert group_manager_user_id is None
    assert organisation_id is None


def test_list_access_params_completed_with_validate_group_permission(service):
    identity = IdentityContext(
        user_id=123, permissions=["datasets:status-change:validate:group"]
    )

    created_by_user_id, group_manager_user_id, organisation_id = (
        service.get_dataset_list_access_params(identity, DatasetStatus.COMPLETED.value)
    )

    assert created_by_user_id == 123
    assert group_manager_user_id == 123
    assert organisation_id is None


def test_list_access_params_completed_with_no_permission(service):
    identity = IdentityContext(user_id=123, permissions=[])

    created_by_user_id, group_manager_user_id, organisation_id = (
        service.get_dataset_list_access_params(identity, DatasetStatus.COMPLETED.value)
    )

    assert created_by_user_id == 123
    assert group_manager_user_id is None
    assert organisation_id is None


def test_list_access_params_validated_with_read_all_after_draft_permission(service):
    identity = IdentityContext(
        user_id=123, permissions=["datasets:read:all-after-draft"]
    )

    created_by_user_id, group_manager_user_id, organisation_id = (
        service.get_dataset_list_access_params(identity, DatasetStatus.VALIDATED.value)
    )

    assert created_by_user_id is None
    assert group_manager_user_id is None
    assert organisation_id is None


def test_list_access_params_validated_with_read_all_after_complete_permission(service):
    identity = IdentityContext(
        user_id=123, permissions=["datasets:read:all-after-complete"]
    )

    created_by_user_id, group_manager_user_id, organisation_id = (
        service.get_dataset_list_access_params(identity, DatasetStatus.VALIDATED.value)
    )

    assert created_by_user_id is None
    assert group_manager_user_id is None
    assert organisation_id is None


def test_list_access_params_validated_with_no_permission(service):
    identity = IdentityContext(user_id=123, permissions=[])

    created_by_user_id, group_manager_user_id, organisation_id = (
        service.get_dataset_list_access_params(identity, DatasetStatus.VALIDATED.value)
    )

    assert created_by_user_id == 123
    assert group_manager_user_id is None
    assert organisation_id is None


def test_list_access_params_draft_with_multiple_permissions(service):
    identity = IdentityContext(
        user_id=123, permissions=["datasets:edit:draft:my", "datasets:edit:draft"]
    )

    created_by_user_id, group_manager_user_id, organisation_id = (
        service.get_dataset_list_access_params(identity, DatasetStatus.DRAFT.value)
    )

    assert created_by_user_id is None
    assert group_manager_user_id is None
    assert organisation_id is None


def test_list_access_params_draft_organisation_permission_takes_precedence_over_group(
    service,
):
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:edit:draft:organisation", "datasets:edit:draft:group"],
        current_organisation_id=456,
    )

    created_by_user_id, group_manager_user_id, organisation_id = (
        service.get_dataset_list_access_params(identity, DatasetStatus.DRAFT.value)
    )

    assert created_by_user_id is None
    assert group_manager_user_id is None
    assert organisation_id == 456


def test_list_access_params_completed_with_multiple_permissions(service):
    identity = IdentityContext(
        user_id=123,
        permissions=[
            "datasets:status-change:validate:group",
            "datasets:read:all-after-draft",
        ],
    )

    created_by_user_id, group_manager_user_id, organisation_id = (
        service.get_dataset_list_access_params(identity, DatasetStatus.COMPLETED.value)
    )

    assert created_by_user_id is None
    assert group_manager_user_id is None
    assert organisation_id is None


def test_list_access_params_completed_with_read_completed_permission_and_organization(
    service,
):
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:read:completed"],
        current_organisation_id=456,
    )

    created_by_user_id, group_manager_user_id, organisation_id = (
        service.get_dataset_list_access_params(identity, DatasetStatus.COMPLETED.value)
    )

    assert created_by_user_id is None
    assert group_manager_user_id is None
    assert organisation_id == 456


def test_list_access_params_completed_with_read_all_after_draft_organisation(service):
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:read:all-after-draft:organisation"],
        current_organisation_id=456,
    )

    created_by_user_id, group_manager_user_id, organisation_id = (
        service.get_dataset_list_access_params(identity, DatasetStatus.COMPLETED.value)
    )

    assert created_by_user_id is None
    assert group_manager_user_id is None
    assert organisation_id == 456


def test_list_access_params_validated_with_read_validated_permission_and_organization(
    service,
):
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:read:validated"],
        current_organisation_id=456,
    )

    created_by_user_id, group_manager_user_id, organisation_id = (
        service.get_dataset_list_access_params(identity, DatasetStatus.VALIDATED.value)
    )

    assert created_by_user_id is None
    assert group_manager_user_id is None
    assert organisation_id == 456


def test_list_access_params_approved_with_read_approved_permission_and_organization(
    service,
):
    identity = IdentityContext(
        user_id=123, permissions=["datasets:read:approved"], current_organisation_id=456
    )

    created_by_user_id, group_manager_user_id, organisation_id = (
        service.get_dataset_list_access_params(identity, DatasetStatus.APPROVED.value)
    )

    assert created_by_user_id is None
    assert group_manager_user_id is None
    assert organisation_id == 456


def test_list_access_params_published_with_read_published_permission_no_organization_filter(
    service,
):
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:read:published"],
        current_organisation_id=456,
    )

    created_by_user_id, group_manager_user_id, organisation_id = (
        service.get_dataset_list_access_params(identity, DatasetStatus.PUBLISHED.value)
    )

    assert created_by_user_id is None
    assert group_manager_user_id is None
    assert (
        organisation_id == 456
    )  # Published datasets should be filtered by organization


def test_validate_create_permissions_allows_any_publisher_with_global(
    service, dataset_repository
):
    identity = IdentityContext(user_id=123, permissions=["datasets:edit:draft"])
    # Should not raise for any publisher
    service.validate_create_permissions(publisher_id=999, identity=identity)


def test_validate_create_permissions_allows_when_my_and_matching_org(
    service, dataset_repository
):
    identity = IdentityContext(
        user_id=123, permissions=["datasets:edit:draft:my"], current_organisation_id=42
    )
    # Matching publisher to current org -> allowed
    service.validate_create_permissions(publisher_id=42, identity=identity)


def test_validate_create_permissions_forbidden_when_my_and_different_org(
    service, dataset_repository
):
    identity = IdentityContext(
        user_id=123, permissions=["datasets:edit:draft:my"], current_organisation_id=42
    )

    with pytest.raises(HTTPException) as exc_info:
        service.validate_create_permissions(publisher_id=7, identity=identity)

    assert exc_info.value.status_code == 403
    assert (
        exc_info.value.detail
        == "You are not allowed to create a dataset for this publisher"
    )


def test_validate_status_change_permissions_forbidden_different_organisation(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:edit:draft:my"],
        current_organisation_id=456,
    )

    # Different publisher from current org -> forbidden
    with pytest.raises(HTTPException) as exc_info:
        service.validate_status_change_permissions(
            dataset_id=dataset_id, publisher_id=789, identity=identity
        )

    assert exc_info.value.status_code == 403
    assert (
        exc_info.value.detail
        == "You are not allowed to change the dataset status for this publisher"
    )


def test_validate_status_change_permissions_imported_dataset(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:edit:draft"],
        current_organisation_id=456,
    )

    dataset_repository.is_dataset_imported.return_value = True

    with pytest.raises(HTTPException) as exc_info:
        service.validate_status_change_permissions(
            dataset_id=dataset_id, publisher_id=456, identity=identity
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == IMPORTED_DATASET_ERROR


def test_validate_status_change_permissions_none_organisation_id_allowed(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(
        user_id=123,
        permissions=["datasets:status-change:complete:my"],
        current_organisation_id=None,
    )

    service.validate_status_change_permissions(
        dataset_id=dataset_id, publisher_id=456, identity=identity
    )

    dataset_repository.is_dataset_imported.assert_called_once_with(dataset_id)


def test_validate_organisation_ctie_access_lnds_only_org_in_ctie_instance():
    dataset_repo = Mock(spec=DatasetRepository)
    org_repo = Mock(spec=OrganisationRepository)
    config_service = Mock(spec=ConfigService)

    service = DatasetPermissionsService(
        dataset_repository=dataset_repo,
        organisation_repository=org_repo,
        config_service=config_service,
    )

    lnds_only_org = MagicMock()
    lnds_only_org.name = "LNDS-Only Org"
    lnds_only_org.accessible_within_ctie = False

    org_repo.get_organisation.return_value = lnds_only_org
    config_service.get_enable_multi_tenants.return_value = True
    config_service.is_ctie_instance.return_value = True
    config_service.get_enable_dual_instance.return_value = True

    with pytest.raises(HTTPException) as exc_info:
        service._validate_organisation_ctie_access(1)

    assert exc_info.value.status_code == 403
    assert "cannot be used in CTIE instance" in exc_info.value.detail


def test_validate_organisation_ctie_access_ctie_only_org_in_lnds_instance():
    dataset_repo = Mock(spec=DatasetRepository)
    org_repo = Mock(spec=OrganisationRepository)
    config_service = Mock(spec=ConfigService)

    service = DatasetPermissionsService(
        dataset_repository=dataset_repo,
        organisation_repository=org_repo,
        config_service=config_service,
    )

    ctie_only_org = MagicMock()
    ctie_only_org.name = "CTIE-Only Org"
    ctie_only_org.accessible_within_ctie = True

    org_repo.get_organisation.return_value = ctie_only_org
    config_service.get_enable_multi_tenants.return_value = True
    config_service.is_ctie_instance.return_value = False
    config_service.get_enable_dual_instance.return_value = True

    with pytest.raises(HTTPException) as exc_info:
        service._validate_organisation_ctie_access(1)

    assert exc_info.value.status_code == 403
    assert "is CTIE-only and cannot be used here" in exc_info.value.detail


def test_validate_organisation_ctie_access_skipped_when_feature_disabled():
    dataset_repo = Mock(spec=DatasetRepository)
    org_repo = Mock(spec=OrganisationRepository)
    config_service = Mock(spec=ConfigService)

    service = DatasetPermissionsService(
        dataset_repository=dataset_repo,
        organisation_repository=org_repo,
        config_service=config_service,
    )

    ctie_only_org = MagicMock()
    ctie_only_org.name = "CTIE-Only Org"
    ctie_only_org.accessible_within_ctie = True

    org_repo.get_organisation.return_value = ctie_only_org
    config_service.get_enable_multi_tenants.return_value = False
    config_service.is_ctie_instance.return_value = False

    service._validate_organisation_ctie_access(1)

    org_repo.get_organisation.assert_not_called()


# System Admin Tests - Bypasses all permission checks
def test_validate_read_permissions_system_admin_bypasses_all_checks(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(user_id=123, permissions=["system:admin"])

    # Don't even setup repository mocks - they shouldn't be called
    service.validate_read_permissions(dataset_id, identity)

    # Verify repository was never queried
    dataset_repository.get_dataset_status_publisher_id_and_user_id.assert_not_called()


def test_validate_edit_permissions_system_admin_bypasses_all_checks(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(user_id=123, permissions=["system:admin"])

    # Don't setup repository mocks - they shouldn't be called
    service.validate_edit_permissions(dataset_id, identity)

    # Verify repository was never queried
    dataset_repository.get_dataset_status_publisher_id_and_user_id.assert_not_called()


def test_validate_delete_permissions_system_admin_bypasses_all_checks(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(user_id=123, permissions=["system:admin"])

    service.validate_delete_permissions(dataset_id, identity)

    # Verify repository was never queried
    dataset_repository.get_dataset_status_publisher_id_and_user_id.assert_not_called()


def test_validate_create_permissions_system_admin_bypasses_all_checks(
    service, dataset_repository
):
    identity = IdentityContext(user_id=123, permissions=["system:admin"])

    # Should not raise for any publisher
    service.validate_create_permissions(publisher_id=999, identity=identity)

    # No repository calls should be made
    dataset_repository.get_dataset_status_publisher_id_and_user_id.assert_not_called()


def test_validate_status_change_permissions_system_admin_bypasses_all_checks(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(user_id=123, permissions=["system:admin"])

    service.validate_status_change_permissions(
        dataset_id=dataset_id, publisher_id=999, identity=identity
    )

    # Verify imported check was never called
    dataset_repository.is_dataset_imported.assert_not_called()


def test_validate_bulk_update_authentic_source_permissions_system_admin_bypasses_all_checks(
    service, dataset_repository
):
    dataset_id = 1
    identity = IdentityContext(user_id=123, permissions=["system:admin"])

    service.validate_bulk_update_authentic_source_permissions(
        dataset_id=dataset_id, identity=identity
    )

    # Verify repository was never queried
    dataset_repository.get_dataset_status_publisher_id_and_user_id.assert_not_called()
