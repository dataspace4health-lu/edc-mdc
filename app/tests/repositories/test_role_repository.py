from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.user_assignment import Role
import pytest
from repositories.role import RoleRepository


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    db_session.query(Role).delete()
    db_session.commit()
    yield


@pytest.fixture
def role_repository(db_session: Session) -> RoleRepository:
    return RoleRepository(db_session)


def test_get_all_roles_empty_db(role_repository: RoleRepository):
    roles = role_repository.get_all_roles()
    assert roles == []
    assert isinstance(roles, list)


def test_get_all_roles(role_repository: RoleRepository, db_session: Session):
    role1 = Role(name="Role 1")
    role2 = Role(name="Role 2")
    db_session.add_all([role1, role2])
    db_session.commit()

    roles = role_repository.get_all_roles()
    assert len(roles) == 2
    assert roles[0].name == "Role 1"
    assert roles[1].name == "Role 2"
