import pytest
from unittest.mock import Mock
from fastapi import HTTPException
from models.identity_context import IdentityContext
from repositories.keyword import KeywordRepository
from repositories.applicable_legislation import ApplicableLegislationRepository
from repositories.user_assignment import UserAssignmentRepository
from repositories.keyword_assignment import KeywordAssignmentRepository
from repositories.applicable_legislation_assignment import (
    ApplicableLegislationAssignmentRepository,
)
from services.form_fields_permission import FormFieldsPermissionsService


@pytest.fixture
def keyword_repository():
    return Mock(spec=KeywordRepository)


@pytest.fixture
def applicable_legislation_repository():
    return Mock(spec=ApplicableLegislationRepository)


@pytest.fixture
def user_assignment_repository():
    return Mock(spec=UserAssignmentRepository)


@pytest.fixture
def keyword_assignment_repository():
    return Mock(spec=KeywordAssignmentRepository)


@pytest.fixture
def applicable_legislation_assignment_repository():
    return Mock(spec=ApplicableLegislationAssignmentRepository)


@pytest.fixture
def service(
    keyword_repository,
    applicable_legislation_repository,
    user_assignment_repository,
    keyword_assignment_repository,
    applicable_legislation_assignment_repository,
):
    return FormFieldsPermissionsService(
        keyword_repository=keyword_repository,
        keyword_assignment_repository=keyword_assignment_repository,
        applicable_legislation_repository=applicable_legislation_repository,
        applicable_legislation_assignment_repository=applicable_legislation_assignment_repository,
        user_assignment_repository=user_assignment_repository,
    )


def test_validate_edit_and_delete_permissions_form_field_not_found(
    service, keyword_repository
):
    org_id = None
    field_type = "keyword"
    key = "test-key"
    identity = IdentityContext(user_id=123, permissions=[])

    keyword_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.validate_edit_and_delete_permissions(field_type, key, org_id, identity)

    assert exc_info.value.status_code == 404
    assert f"{field_type.capitalize()}[{key}] not found" == exc_info.value.detail


def test_validate_edit_and_delete_permissions_has_general_edit_permission(
    service, keyword_repository
):
    org_id = None
    field_type = "keyword"
    key = "test-key"
    identity = IdentityContext(user_id=123, permissions=["form-fields:edit"])

    keyword_repository.get.return_value = Mock(created_by_id=456)

    service.validate_edit_and_delete_permissions(field_type, key, org_id, identity)


def test_validate_edit_and_delete_permissions_no_org_context_required(
    service, keyword_repository, keyword_assignment_repository
):
    org_id = None
    field_type = "keyword"
    key = "test-key"
    identity = IdentityContext(user_id=123, permissions=["form-fields:edit:my"])

    keyword_repository.get.return_value = Mock(created_by_id=123)

    keyword_assignment_repository.get_keyword_organisation_assignments.return_value = []

    with pytest.raises(HTTPException) as exc_info:
        service.validate_edit_and_delete_permissions(field_type, key, org_id, identity)

    assert exc_info.value.status_code == 403
    assert (
        "You must be in an organization context to edit form fields"
        in exc_info.value.detail
    )


def test_validate_edit_and_delete_permissions_keyword_global_field_owner(
    service,
    keyword_repository,
    keyword_assignment_repository,
    user_assignment_repository,
):
    org_id = 1
    field_type = "keyword"
    key = "test-key"
    identity = IdentityContext(user_id=123, permissions=["form-fields:edit:my"])

    keyword_repository.get.return_value = Mock(created_by_id=123)
    keyword_assignment_repository.get_keyword_organisation_assignment.return_value = (
        None
    )
    keyword_assignment_repository.get_keyword_organisation_assignments.return_value = []
    user_assignment_repository.get_user_organisation_assignment.return_value = Mock()

    service.validate_edit_and_delete_permissions(field_type, key, org_id, identity)


def test_validate_edit_and_delete_permissions_keyword_not_assigned_not_global(
    service, keyword_repository, keyword_assignment_repository
):
    org_id = 1
    field_type = "keyword"
    key = "test-key"
    identity = IdentityContext(user_id=123, permissions=["form-fields:edit:my"])

    keyword_repository.get.return_value = Mock(created_by_id=123)
    keyword_assignment_repository.get_keyword_organisation_assignment.return_value = (
        None  # Not assigned to org
    )
    keyword_assignment_repository.get_keyword_organisation_assignments.return_value = [
        Mock()
    ]  # Has other assignments

    with pytest.raises(HTTPException) as exc_info:
        service.validate_edit_and_delete_permissions(field_type, key, org_id, identity)

    assert exc_info.value.status_code == 403
    assert "This keyword is not assigned to your organization" in exc_info.value.detail


def test_validate_create_permissions_global_permission(service):
    field_type = "keyword"
    selected_org_ids = []
    identity = IdentityContext(user_id=123, permissions=["form-fields:edit"])

    service.validate_create_permissions(field_type, selected_org_ids, identity)


def test_validate_create_permissions_empty_orgs_no_global_permission(service):
    field_type = "keyword"
    selected_org_ids = []
    identity = IdentityContext(user_id=123, permissions=["form-fields:edit:my"])

    with pytest.raises(HTTPException) as exc_info:
        service.validate_create_permissions(field_type, selected_org_ids, identity)

    assert exc_info.value.status_code == 403
    assert "Only Catalogue Managers can create global keyword" in exc_info.value.detail


def test_validate_create_permissions_user_not_in_selected_org(
    service, user_assignment_repository
):
    field_type = "keyword"
    selected_org_ids = [1, 2]
    identity = IdentityContext(user_id=123, permissions=["form-fields:edit:my"])

    user_assignment_repository.get_user_organisation_assignments.return_value = [
        Mock(organisation_id=1)
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_create_permissions(field_type, selected_org_ids, identity)

    assert exc_info.value.status_code == 403
    assert (
        "You don't have permission to create keyword for organization ID 2"
        in exc_info.value.detail
    )


def test_validate_create_permissions_user_in_all_selected_orgs(
    service, user_assignment_repository
):
    field_type = "keyword"
    selected_org_ids = [1, 2]
    identity = IdentityContext(user_id=123, permissions=["form-fields:edit:my"])

    user_assignment_repository.get_user_organisation_assignments.return_value = [
        Mock(organisation_id=1),
        Mock(organisation_id=2),
        Mock(organisation_id=3),
    ]

    service.validate_create_permissions(field_type, selected_org_ids, identity)


def test_get_user_organisation_ids_global_permission(service):
    identity = IdentityContext(user_id=123, permissions=["form-fields:edit"])

    result = service.get_user_organisation_ids(identity)

    assert result is None  # Global permission should return None


def test_get_user_organisation_ids_my_permission(service, user_assignment_repository):
    identity = IdentityContext(
        user_id=123, permissions=["form-fields:edit:my"], current_organisation_id=456
    )

    result = service.get_user_organisation_ids(identity)

    assert result == [456]


def test_get_user_organisation_ids_no_permission(service):
    identity = IdentityContext(user_id=123, permissions=["some-other:permission"])

    with pytest.raises(HTTPException) as exc_info:
        service.get_user_organisation_ids(identity)

    assert exc_info.value.status_code == 403
    assert "You do not have permission to edit form fields" in exc_info.value.detail


def test_can_create_global_fields_true(service):
    identity = IdentityContext(user_id=123, permissions=["form-fields:edit"])

    result = service.can_create_global_fields(identity)

    assert result is True


def test_can_create_global_fields_false(service):
    identity = IdentityContext(user_id=123, permissions=["some-other:permission"])

    result = service.can_create_global_fields(identity)

    assert result is False


def test_validate_selected_organizations_global_permission(service):
    identity = IdentityContext(user_id=123, permissions=["form-fields:edit"])
    selected_org_ids = [1, 2, 3]

    service.validate_selected_organizations(identity, selected_org_ids)


def test_validate_selected_organizations_user_has_access(
    service, user_assignment_repository
):
    identity = IdentityContext(user_id=123, permissions=["form-fields:edit:my"])
    selected_org_ids = [1, 2]

    user_assignment_repository.get_user_organisation_assignments.return_value = [
        Mock(organisation_id=1),
        Mock(organisation_id=2),
        Mock(organisation_id=3),
    ]

    service.validate_selected_organizations(identity, selected_org_ids)


def test_validate_selected_organizations_user_no_access(
    service, user_assignment_repository
):
    identity = IdentityContext(user_id=123, permissions=["form-fields:edit:my"])
    selected_org_ids = [1, 2, 4]  # User doesn't have access to org 4

    user_assignment_repository.get_user_organisation_assignments.return_value = [
        Mock(organisation_id=1),
        Mock(organisation_id=2),
        Mock(organisation_id=3),
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_selected_organizations(identity, selected_org_ids)

    assert exc_info.value.status_code == 403
    assert "You don't have access to organization with ID 4" in exc_info.value.detail


def test_validate_edit_and_delete_permissions_multi_org_blocked_for_non_catalogue_managers(
    service, keyword_repository, keyword_assignment_repository
):
    field_type = "keyword"
    key = "test-keyword"
    org_id = 1
    identity = IdentityContext(
        user_id=123,
        permissions=["form-fields:edit:organisation"],
        current_organisation_id=org_id,
    )

    # Mock field exists
    keyword_repository.get.return_value = Mock(created_by_id=123)

    # Mock multiple organization assignments
    keyword_assignment_repository.get_keyword_organisation_assignments.return_value = [
        Mock(organisation_id=1),
        Mock(organisation_id=2),
    ]

    with pytest.raises(HTTPException) as exc_info:
        service.validate_edit_and_delete_permissions(field_type, key, org_id, identity)

    assert exc_info.value.status_code == 403
    assert (
        "Only Catalogue Managers can update form fields assigned to multiple organisations"
        in exc_info.value.detail
    )
