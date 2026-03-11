import pytest
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.identity_context import IdentityContext
from models.user import User
from models.organisation import Organisation
from models.user_assignment import UserOrganisationAssignment, RoleAssignment, Role
from repositories.user_assignment import UserAssignmentRepository
from repositories.organisation import OrganisationRepository
from repositories.user import UserRepository
from services.user_assignment_permissions import UserAssignmentPermissionsService
from services.config import ConfigService


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    yield
    db_session.query(RoleAssignment).delete()
    db_session.query(UserOrganisationAssignment).delete()
    db_session.query(Role).delete()
    db_session.query(User).delete()
    db_session.query(Organisation).delete()
    db_session.commit()


@pytest.fixture
def user_assignment_repository(db_session: Session) -> UserAssignmentRepository:
    return UserAssignmentRepository(db_session)


@pytest.fixture
def organisation_repository(db_session: Session) -> OrganisationRepository:
    return OrganisationRepository(db_session)


@pytest.fixture
def user_repository(db_session: Session) -> UserRepository:
    return UserRepository(db_session)


@pytest.fixture
def service(user_assignment_repository, organisation_repository, user_repository):
    return UserAssignmentPermissionsService(
        user_assignment_repository=user_assignment_repository,
        organisation_repository=organisation_repository,
        user_repository=user_repository,
    )


@pytest.fixture
def sample_user(db_session: Session) -> User:
    user = User(name="Test User", email="test@example.com", external_id="test-123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_target_user(db_session: Session) -> User:
    user = User(
        name="Target User", email="target@example.com", external_id="target-456"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_organisation(db_session: Session) -> Organisation:
    organisation = Organisation(name="Test Organisation")
    db_session.add(organisation)
    db_session.commit()
    db_session.refresh(organisation)
    return organisation


@pytest.fixture
def sample_role(db_session: Session) -> Role:
    role = Role(name="Admin")
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


def create_user_organisation_assignment(
    db_session: Session,
    user: User,
    organisation: Organisation,
    roles: list[Role] = None,
):
    assignment = UserOrganisationAssignment(
        user_id=user.id, organisation_id=organisation.id
    )
    db_session.add(assignment)
    db_session.flush()

    if roles:
        for role in roles:
            role_assignment = RoleAssignment(
                user_organisation_assignment_id=assignment.id, role_id=role.id
            )
            assignment.roles.add(role_assignment)

    db_session.commit()
    db_session.refresh(assignment)
    return assignment


def test_validate_role_assignment_permissions_organisation_not_found(
    service, sample_user, sample_target_user, db_session
):
    non_existent_org_id = 99999
    identity = IdentityContext(user_id=sample_user.id, permissions=["roles:manage"])
    with pytest.raises(HTTPException) as exc_info:
        service.validate_role_assignment_permissions(
            non_existent_org_id, sample_target_user.id, identity
        )

    assert exc_info.value.status_code == 404
    assert f"Organisation[{non_existent_org_id}] not found" == exc_info.value.detail


def test_validate_role_assignment_permissions_user_not_found(
    service, sample_user, sample_organisation, db_session
):
    non_existent_user_id = 99999
    identity = IdentityContext(user_id=sample_user.id, permissions=["roles:manage"])

    with pytest.raises(HTTPException) as exc_info:
        service.validate_role_assignment_permissions(
            sample_organisation.id, non_existent_user_id, identity
        )

    assert exc_info.value.status_code == 404
    assert f"User[{non_existent_user_id}] not found" == exc_info.value.detail


def test_validate_role_assignment_permissions_global_permission_allows_access(
    service, sample_user, sample_target_user, sample_organisation
):
    identity = IdentityContext(user_id=sample_user.id, permissions=["roles:manage"])

    # Should not raise any exception
    service.validate_role_assignment_permissions(
        sample_organisation.id, sample_target_user.id, identity
    )


def test_validate_role_assignment_permissions_organisation_permission_user_belongs_to_organisation(
    service,
    sample_user,
    sample_target_user,
    sample_organisation,
    sample_role,
    db_session,
):
    identity = IdentityContext(
        user_id=sample_user.id, permissions=["roles:manage:organisation"]
    )

    # Create assignment so user belongs to organisation
    create_user_organisation_assignment(
        db_session, sample_user, sample_organisation, [sample_role]
    )

    # Should not raise any exception
    service.validate_role_assignment_permissions(
        sample_organisation.id, sample_target_user.id, identity
    )


def test_validate_role_assignment_permissions_organisation_permission_user_does_not_belong_to_organisation(
    service, sample_user, sample_target_user, sample_organisation
):
    identity = IdentityContext(
        user_id=sample_user.id, permissions=["roles:manage:organisation"]
    )

    with pytest.raises(HTTPException) as exc_info:
        service.validate_role_assignment_permissions(
            sample_organisation.id, sample_target_user.id, identity
        )

    assert exc_info.value.status_code == 403
    assert (
        "You can only manage roles within organisations you belong to"
        == exc_info.value.detail
    )


def test_validate_role_assignment_permissions_no_permissions(
    service, sample_user, sample_target_user, sample_organisation
):
    identity = IdentityContext(user_id=sample_user.id, permissions=[])

    with pytest.raises(HTTPException) as exc_info:
        service.validate_role_assignment_permissions(
            sample_organisation.id, sample_target_user.id, identity
        )

    assert exc_info.value.status_code == 403
    assert (
        "You do not have permission to manage role assignments" == exc_info.value.detail
    )


def test_validate_role_assignment_permissions_multiple_permissions_global_takes_precedence(
    service, sample_user, sample_target_user, sample_organisation
):
    identity = IdentityContext(
        user_id=sample_user.id,
        permissions=["roles:manage", "roles:manage:organisation"],
    )

    # Should not raise any exception - global permission allows access
    # Note: User doesn't need to belong to organisation since global permission takes precedence
    service.validate_role_assignment_permissions(
        sample_organisation.id, sample_target_user.id, identity
    )


def test_validate_role_assignment_permissions_same_user_as_target(
    service, sample_user, sample_organisation, sample_role, db_session
):
    """Test when the user is managing their own role assignment"""
    identity = IdentityContext(
        user_id=sample_user.id, permissions=["roles:manage:organisation"]
    )

    # Create assignment so user belongs to organisation
    create_user_organisation_assignment(
        db_session, sample_user, sample_organisation, [sample_role]
    )

    # Should not raise any exception when managing own roles
    service.validate_role_assignment_permissions(
        sample_organisation.id, sample_user.id, identity
    )


def test_multiple_organisations_user_belongs_to_one(
    service, sample_user, sample_target_user, sample_role, db_session
):
    """Test user with organisation permission can only manage roles in orgs they belong to"""
    org1 = Organisation(name="Org 1")
    org2 = Organisation(name="Org 2")
    db_session.add_all([org1, org2])
    db_session.commit()
    db_session.refresh(org1)
    db_session.refresh(org2)

    identity = IdentityContext(
        user_id=sample_user.id, permissions=["roles:manage:organisation"]
    )

    # User belongs to org1 only
    create_user_organisation_assignment(db_session, sample_user, org1, [sample_role])

    # Should succeed for org1
    service.validate_role_assignment_permissions(
        org1.id, sample_target_user.id, identity
    )

    # Should fail for org2
    with pytest.raises(HTTPException) as exc_info:
        service.validate_role_assignment_permissions(
            org2.id, sample_target_user.id, identity
        )

    assert exc_info.value.status_code == 403
    assert (
        "You can only manage roles within organisations you belong to"
        == exc_info.value.detail
    )


def test_user_with_multiple_role_assignments(
    service, sample_user, sample_target_user, sample_organisation, db_session
):
    """Test user with multiple roles in same organisation"""
    # Create multiple roles
    admin_role = Role(name="Admin")
    manager_role = Role(name="Manager")
    db_session.add_all([admin_role, manager_role])
    db_session.commit()

    identity = IdentityContext(
        user_id=sample_user.id, permissions=["roles:manage:organisation"]
    )

    # User has multiple roles in organisation
    create_user_organisation_assignment(
        db_session, sample_user, sample_organisation, [admin_role, manager_role]
    )

    # Should succeed
    service.validate_role_assignment_permissions(
        sample_organisation.id, sample_target_user.id, identity
    )


def test_validate_organisation_ctie_access_lnds_only_org_in_ctie_instance():
    user_assignment_repo = Mock(spec=UserAssignmentRepository)
    org_repo = Mock(spec=OrganisationRepository)
    user_repo = Mock(spec=UserRepository)
    config_service = Mock(spec=ConfigService)

    service = UserAssignmentPermissionsService(
        user_assignment_repository=user_assignment_repo,
        organisation_repository=org_repo,
        user_repository=user_repo,
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
    user_assignment_repo = Mock(spec=UserAssignmentRepository)
    org_repo = Mock(spec=OrganisationRepository)
    user_repo = Mock(spec=UserRepository)
    config_service = Mock(spec=ConfigService)

    service = UserAssignmentPermissionsService(
        user_assignment_repository=user_assignment_repo,
        organisation_repository=org_repo,
        user_repository=user_repo,
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
    user_assignment_repo = Mock(spec=UserAssignmentRepository)
    org_repo = Mock(spec=OrganisationRepository)
    user_repo = Mock(spec=UserRepository)
    config_service = Mock(spec=ConfigService)

    service = UserAssignmentPermissionsService(
        user_assignment_repository=user_assignment_repo,
        organisation_repository=org_repo,
        user_repository=user_repo,
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
