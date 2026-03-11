import pytest
from sqlalchemy.orm import Session
from models.user_assignment import Role
from repositories.role import RoleRepository
from services.role import RoleService
from schemas.user_assignment import ResourceRole


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    db_session.query(Role).delete()
    db_session.commit()


@pytest.fixture
def role_repository(db_session: Session):
    return RoleRepository(db_session=db_session)


@pytest.fixture
def role_service(role_repository: RoleRepository):
    return RoleService(
        role_repository=role_repository,
    )


def test_get_all_roles_returns_roles(db_session: Session, role_service: RoleService):
    role1 = Role(name="Admin")
    role2 = Role(name="User")
    db_session.add_all([role1, role2])
    db_session.commit()

    result = role_service.get_all_roles()

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(r, ResourceRole) for r in result)

    names = {r.name for r in result}
    assert "Admin" in names
    assert "User" in names


def test_get_all_roles_empty(role_service: RoleService):

    result = role_service.get_all_roles()
    assert result == []
