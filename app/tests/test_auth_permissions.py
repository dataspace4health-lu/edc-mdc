from unittest.mock import MagicMock
from auth.permissions import get_permissions_from_roles, has_permissions


def test_get_permissions_from_roles_with_list():
    mock_config = MagicMock()
    mock_config.get_roles.return_value = [
        {"name": "ADMIN", "permissions": ["read", "write", "delete"]},
        {"name": "USER", "permissions": ["read"]},
    ]

    permissions = get_permissions_from_roles(["ADMIN", "USER"], mock_config)
    assert set(permissions) == {"read", "write", "delete"}


def test_get_permissions_from_roles_with_string():
    mock_config = MagicMock()
    mock_config.get_roles.return_value = [
        {"name": "ADMIN", "permissions": ["read", "write"]},
        {"name": "USER", "permissions": ["read"]},
    ]

    permissions = get_permissions_from_roles("ADMIN, USER", mock_config)
    assert set(permissions) == {"read", "write"}


def test_get_permissions_from_roles_with_none():
    mock_config = MagicMock()
    mock_config.get_roles.return_value = []

    permissions = get_permissions_from_roles(None, mock_config)
    assert permissions == []


def test_get_permissions_from_roles_no_match():
    mock_config = MagicMock()
    mock_config.get_roles.return_value = [
        {"name": "ADMIN", "permissions": ["read", "write"]},
    ]

    permissions = get_permissions_from_roles(["UNKNOWN"], mock_config)
    assert permissions == []


def test_has_permissions_with_match():
    user_perms = ["read", "write", "delete"]
    required_perms = ["write"]
    assert has_permissions(user_perms, required_perms) is True


def test_has_permissions_with_multiple_required():
    user_perms = ["read", "write"]
    required_perms = ["write", "delete"]
    assert has_permissions(user_perms, required_perms) is True


def test_has_permissions_no_match():
    user_perms = ["read"]
    required_perms = ["write", "delete"]
    assert has_permissions(user_perms, required_perms) is False


def test_has_permissions_empty_required():
    user_perms = ["read", "write"]
    required_perms = []
    assert has_permissions(user_perms, required_perms) is False


def test_has_permissions_empty_user():
    user_perms = []
    required_perms = ["read"]
    assert has_permissions(user_perms, required_perms) is False
