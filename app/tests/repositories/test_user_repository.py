from fastapi import HTTPException
from sqlalchemy.orm import Session

# Have to import these models toinitialize the models properly
from models.dataset import User
from models.dataset import Dataset
from models.dataset_comment import DatasetComment
from models.user_assignment import UserOrganisationAssignment, RoleAssignment
import pytest
from repositories.user import UserRepository


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    yield
    db_session.query(User).delete()
    db_session.commit()


@pytest.fixture
def user_repository(db_session: Session) -> UserRepository:
    return UserRepository(db_session)


def test_get_users_with_roles(user_repository: UserRepository, db_session: Session):
    user1 = User(name="Bob", iam_roles="GUEST", external_id="456")
    user2 = User(name="Monica", iam_roles="ADMIN,MANAGER", external_id="123")
    user3 = User(name="Alice", iam_roles="ADMIN", external_id="789")
    db_session.add_all([user1, user2, user3])
    db_session.commit()

    users_with_admin = user_repository.get_users_with_roles(["ADMIN"])
    assert len(users_with_admin) == 2
    assert users_with_admin[0].name == "Alice"
    assert users_with_admin[1].name == "Monica"

    users_with_unknown = user_repository.get_users_with_roles(["UNKNOWN"])
    assert len(users_with_unknown) == 0


def test_get_users_no_roles_provided(user_repository: UserRepository):
    users_with_no_roles = user_repository.get_users_with_roles([])
    assert len(users_with_no_roles) == 0


def test_get_users_excludes_system_user(
    user_repository: UserRepository, db_session: Session
):
    user_system = User(name="system", external_id="001")
    user_normal = User(name="Charlie", email="charlie@example.com", external_id="002")
    db_session.add_all([user_system, user_normal])
    db_session.commit()

    users, total = user_repository.get_users()

    assert total == 1
    assert len(users) == 1
    assert users[0].name != "system"


def test_get_users_filter_by_organisation_ids(
    user_repository: UserRepository, db_session: Session
):
    user1 = User(name="Alice", email="alice@test.com", external_id="1")
    user2 = User(name="Bob", email="bob@test.com", external_id="2")
    db_session.add_all([user1, user2])
    db_session.commit()

    assignment = UserOrganisationAssignment(user_id=user1.id, organisation_id=1)
    db_session.add(assignment)
    db_session.commit()

    users, total = user_repository.get_users(organisation_ids=[1])
    assert total == 1
    assert users[0].name == "Alice"


def test_get_users_filter_by_role_ids_and_unassigned(
    user_repository: UserRepository, db_session: Session
):
    user1 = User(name="Alice", email="alice@test.com", external_id="1")
    user2 = User(name="Bob", email="bob@test.com", external_id="2")
    db_session.add_all([user1, user2])
    db_session.commit()

    assignment = UserOrganisationAssignment(user_id=user1.id, organisation_id=1)
    assignment.roles.add(RoleAssignment(role_id=10))
    db_session.add(assignment)
    db_session.commit()

    users, total = user_repository.get_users(role_ids=[10])
    unassigned, total_unassigned = user_repository.get_users(only_unassigned="true")
    assert total == 1
    assert total_unassigned == 1
    assert users[0].name == "Alice"
    assert unassigned[0].name == "Bob"


def test_get_users_with_roles_manage_permission(
    user_repository: UserRepository, db_session: Session
):
    user1 = User(name="Alice", email="alice@test.com", external_id="1")
    user2 = User(name="Bob", email="bob@test.com", external_id="2")
    db_session.add_all([user1, user2])
    db_session.commit()

    assignment = UserOrganisationAssignment(user_id=user1.id, organisation_id=1)
    assignment.roles.add(RoleAssignment(role_id=10))
    db_session.add(assignment)
    db_session.commit()

    users, total = user_repository.get_users(permission_filter=None)

    assert total == 2
    assert set(u.name for u in users) == {"Alice", "Bob"}


def test_get_users_with_roles_manage_organisation_permission(
    user_repository: UserRepository, db_session: Session
):
    user1 = User(name="Alice", email="alice@test.com", external_id="1")
    user2 = User(name="Bob", email="bob@test.com", external_id="2")
    user3 = User(name="Charlie", email="charlie@test.com", external_id="3")
    db_session.add_all([user1, user2, user3])
    db_session.commit()

    assignment1 = UserOrganisationAssignment(user_id=user1.id, organisation_id=1)
    db_session.add(assignment1)

    assignment2 = UserOrganisationAssignment(user_id=user2.id, organisation_id=2)
    db_session.add(assignment2)

    db_session.commit()

    permission_filter = {"organisation_ids": [1], "include_unassigned": True}

    users, total = user_repository.get_users(permission_filter=permission_filter)

    assert total == 2
    assert set(u.name for u in users) == {"Alice", "Charlie"}


def test_delete_unassigned_user(user_repository: UserRepository, db_session: Session):
    user = User(name="toDelete", email="delete@email.com", external_id="111")
    db_session.add(user)
    db_session.commit()

    retrieved_user = user_repository.get_user(user.id)
    assert retrieved_user is not None
    assert retrieved_user.name == "toDelete"

    user_repository.delete_user(user.id)
    assert user_repository.get_user(user.id) is None
