from fastapi import Depends
from repositories.role import RoleRepository
from models.user_assignment import Role
from schemas.user_assignment import ResourceRole
from typing import List


class RoleService:
    def __init__(
        self,
        role_repository: RoleRepository = Depends(RoleRepository),
    ):
        self._role_repository = role_repository

    def get_all_roles(self) -> List[ResourceRole]:
        roles = self._role_repository._db_session.query(Role).distinct().all()
        return [ResourceRole(id=role.id, name=role.name) for role in roles]
