import pytest
from sqlalchemy.orm import Session
from models.user_assignment import UserOrganisationAssignment, RoleAssignment, Role
from repositories.user_assignment import UserAssignmentRepository


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    yield
    db_session.query(RoleAssignment).delete()
    db_session.query(UserOrganisationAssignment).delete()
    db_session.query(Role).delete()
    db_session.commit()


@pytest.fixture
def user_assignment_repository(db_session: Session) -> UserAssignmentRepository:
    return UserAssignmentRepository(db_session)


def test_get_user_organisation_assignments_by_roles(
    user_assignment_repository: UserAssignmentRepository, db_session: Session
):
    # Create test roles
    admin_role = Role(name="ADMIN")
    manager_role = Role(name="MANAGER")
    guest_role = Role(name="GUEST")
    db_session.add_all([admin_role, manager_role, guest_role])
    db_session.commit()

    # Create test assignments
    assignment1 = UserOrganisationAssignment(user_id=1, organisation_id=1)
    assignment2 = UserOrganisationAssignment(user_id=2, organisation_id=1)
    assignment3 = UserOrganisationAssignment(user_id=3, organisation_id=1)
    assignment4 = UserOrganisationAssignment(
        user_id=4, organisation_id=2
    )  # Different org

    db_session.add_all([assignment1, assignment2, assignment3, assignment4])
    db_session.commit()

    # Add role assignments
    role_assignment1 = RoleAssignment(
        user_organisation_assignment_id=assignment1.id, role_id=admin_role.id
    )
    role_assignment2 = RoleAssignment(
        user_organisation_assignment_id=assignment2.id, role_id=manager_role.id
    )
    role_assignment3 = RoleAssignment(
        user_organisation_assignment_id=assignment3.id, role_id=guest_role.id
    )
    role_assignment4 = RoleAssignment(
        user_organisation_assignment_id=assignment4.id, role_id=admin_role.id
    )

    db_session.add_all(
        [role_assignment1, role_assignment2, role_assignment3, role_assignment4]
    )
    db_session.commit()

    # Test filtering by single role
    admin_assignments = (
        user_assignment_repository.get_user_organisation_assignments_by_roles(
            organisation_id=1, roles=["ADMIN"]
        )
    )
    assert len(admin_assignments) == 1
    assert admin_assignments[0].user_id == 1

    # Test filtering by multiple roles
    admin_manager_assignments = (
        user_assignment_repository.get_user_organisation_assignments_by_roles(
            organisation_id=1, roles=["ADMIN", "MANAGER"]
        )
    )
    assert len(admin_manager_assignments) == 2
    user_ids = [assignment.user_id for assignment in admin_manager_assignments]
    assert 1 in user_ids  # User with ADMIN role
    assert 2 in user_ids  # User with MANAGER role

    # Test filtering by non-existent role
    unknown_assignments = (
        user_assignment_repository.get_user_organisation_assignments_by_roles(
            organisation_id=1, roles=["UNKNOWN"]
        )
    )
    assert len(unknown_assignments) == 0

    # Test filtering by empty roles list
    empty_assignments = (
        user_assignment_repository.get_user_organisation_assignments_by_roles(
            organisation_id=1, roles=[]
        )
    )
    assert len(empty_assignments) == 0

    # Test filtering by correct role but wrong organisation
    wrong_org_assignments = (
        user_assignment_repository.get_user_organisation_assignments_by_roles(
            organisation_id=999, roles=["ADMIN"]
        )
    )
    assert len(wrong_org_assignments) == 0

    # Test that organisation filtering works correctly
    org2_assignments = (
        user_assignment_repository.get_user_organisation_assignments_by_roles(
            organisation_id=2, roles=["ADMIN"]
        )
    )
    assert len(org2_assignments) == 1
    assert org2_assignments[0].user_id == 4


def test_get_user_organisation_assignments_by_roles_multiple_roles_per_user(
    user_assignment_repository: UserAssignmentRepository, db_session: Session
):
    # Create test roles
    admin_role = Role(name="ADMIN")
    manager_role = Role(name="MANAGER")
    db_session.add_all([admin_role, manager_role])
    db_session.commit()

    # Create assignment for user with multiple roles
    assignment = UserOrganisationAssignment(user_id=1, organisation_id=1)
    db_session.add(assignment)
    db_session.commit()

    # Add multiple role assignments to the same user
    role_assignment1 = RoleAssignment(
        user_organisation_assignment_id=assignment.id, role_id=admin_role.id
    )
    role_assignment2 = RoleAssignment(
        user_organisation_assignment_id=assignment.id, role_id=manager_role.id
    )

    db_session.add_all([role_assignment1, role_assignment2])
    db_session.commit()

    # Test that user with multiple roles is returned only once
    assignments = user_assignment_repository.get_user_organisation_assignments_by_roles(
        organisation_id=1, roles=["ADMIN", "MANAGER"]
    )
    assert len(assignments) == 1
    assert assignments[0].user_id == 1
