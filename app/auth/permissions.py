from typing import List
from itertools import chain
from functools import reduce
from services.config import ConfigService


def get_permissions_from_roles(
    roles: List[str] | str | None, config_service: ConfigService
) -> List[str]:
    normalized_roles: List[str] = []
    if isinstance(roles, str):
        normalized_roles = [role.strip() for role in roles.split(",") if role.strip()]
    elif roles:
        normalized_roles = roles

    all_roles = config_service.get_roles()
    return list(
        set(
            chain.from_iterable(
                role["permissions"]
                for role in all_roles
                if role["name"] in normalized_roles
            )
        )
    )


def has_permissions(
    user_permissions: List[str], required_permissions: List[str]
) -> bool:
    return any(permission in user_permissions for permission in required_permissions)
