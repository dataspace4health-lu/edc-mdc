from unittest.mock import MagicMock
from auth.session_auth import extract_iam_roles, check_ctie_only_access
from fastapi import HTTPException
import pytest


def test_extract_iam_roles_success():
    mock_config = MagicMock()
    mock_config.get_roles_path_in_access_token.return_value = "roles"
    mock_config.get_roles.return_value = [
        {"name": "ADMIN", "permissions": ["read", "write"]},
    ]

    userinfo = {"roles": ["ADMIN"]}
    roles = extract_iam_roles(mock_config, userinfo, validate_roles=False)
    assert roles == ["ADMIN"]


def test_extract_iam_roles_with_mapping():
    mock_config = MagicMock()
    mock_config.get_roles_path_in_access_token.return_value = "roles"
    mock_config.get_roles.return_value = [
        {
            "name": "DATA_MANAGER",
            "iam_role_name": "iam-data-manager",
            "permissions": ["read"],
        },
    ]

    userinfo = {"roles": ["iam-data-manager"]}
    roles = extract_iam_roles(mock_config, userinfo, validate_roles=False)
    assert roles == ["DATA_MANAGER"]


def test_extract_iam_roles_nested_path():
    mock_config = MagicMock()
    mock_config.get_roles_path_in_access_token.return_value = (
        "resource_access.client.roles"
    )
    mock_config.get_roles.return_value = [
        {"name": "USER", "permissions": ["read"]},
    ]

    userinfo = {"resource_access": {"client": {"roles": ["USER"]}}}
    roles = extract_iam_roles(mock_config, userinfo, validate_roles=False)
    assert roles == ["USER"]


def test_extract_iam_roles_empty_with_validation():
    mock_config = MagicMock()
    mock_config.get_roles_path_in_access_token.return_value = "roles"
    mock_config.get_roles.return_value = []

    userinfo = {"roles": []}
    with pytest.raises(HTTPException) as exc:
        extract_iam_roles(mock_config, userinfo, validate_roles=True)
    assert exc.value.status_code == 403


def test_extract_iam_roles_empty_without_validation():
    mock_config = MagicMock()
    mock_config.get_roles_path_in_access_token.return_value = "roles"
    mock_config.get_roles.return_value = []

    userinfo = {"roles": []}
    roles = extract_iam_roles(mock_config, userinfo, validate_roles=False)
    assert roles == []


def test_extract_iam_roles_string_role():
    mock_config = MagicMock()
    mock_config.get_roles_path_in_access_token.return_value = "role"
    mock_config.get_roles.return_value = [
        {"name": "ADMIN", "permissions": ["read"]},
    ]

    userinfo = {"role": "ADMIN"}
    roles = extract_iam_roles(mock_config, userinfo, validate_roles=False)
    assert roles == ["ADMIN"]


def test_check_ctie_only_access_catalogue_manager_exempt():
    mock_user = MagicMock()
    mock_user.iam_roles = "CATALOGUE_MANAGER,OTHER_ROLE"
    mock_config = MagicMock()

    result = check_ctie_only_access(mock_user, mock_config)
    assert result is False


def test_check_ctie_only_access_on_ctie_instance():
    mock_user = MagicMock()
    mock_user.iam_roles = "DATA_MANAGER"
    mock_user.organisation_assignments = []
    mock_config = MagicMock()
    mock_config.is_ctie_instance.return_value = True

    result = check_ctie_only_access(mock_user, mock_config)
    assert result is False


def test_check_ctie_only_access_no_org_assignments():
    mock_user = MagicMock()
    mock_user.iam_roles = "DATA_MANAGER"
    mock_user.organisation_assignments = []
    mock_config = MagicMock()
    mock_config.is_ctie_instance.return_value = False

    result = check_ctie_only_access(mock_user, mock_config)
    assert result is False


def test_check_ctie_only_access_with_ctie_org():
    mock_org = MagicMock()
    mock_org.is_deprecated = False
    mock_org.accessible_within_ctie = True

    mock_assignment = MagicMock()
    mock_assignment.organisation = mock_org

    mock_user = MagicMock()
    mock_user.iam_roles = "DATA_MANAGER"
    mock_user.organisation_assignments = [mock_assignment]

    mock_config = MagicMock()
    mock_config.is_ctie_instance.return_value = False

    result = check_ctie_only_access(mock_user, mock_config)
    assert result is True


def test_check_ctie_only_access_with_non_ctie_org():
    mock_org = MagicMock()
    mock_org.is_deprecated = False
    mock_org.accessible_within_ctie = False

    mock_assignment = MagicMock()
    mock_assignment.organisation = mock_org

    mock_user = MagicMock()
    mock_user.iam_roles = "DATA_MANAGER"
    mock_user.organisation_assignments = [mock_assignment]

    mock_config = MagicMock()
    mock_config.is_ctie_instance.return_value = False

    result = check_ctie_only_access(mock_user, mock_config)
    assert result is False


def test_check_ctie_only_access_deprecated_org_ignored():
    mock_org = MagicMock()
    mock_org.is_deprecated = True
    mock_org.accessible_within_ctie = True

    mock_assignment = MagicMock()
    mock_assignment.organisation = mock_org

    mock_user = MagicMock()
    mock_user.iam_roles = "DATA_MANAGER"
    mock_user.organisation_assignments = [mock_assignment]

    mock_config = MagicMock()
    mock_config.is_ctie_instance.return_value = False

    result = check_ctie_only_access(mock_user, mock_config)
    assert result is False


def test_check_ctie_only_access_mixed_orgs():
    mock_org1 = MagicMock()
    mock_org1.is_deprecated = False
    mock_org1.accessible_within_ctie = False

    mock_org2 = MagicMock()
    mock_org2.is_deprecated = False
    mock_org2.accessible_within_ctie = True

    mock_assignment1 = MagicMock()
    mock_assignment1.organisation = mock_org1

    mock_assignment2 = MagicMock()
    mock_assignment2.organisation = mock_org2

    mock_user = MagicMock()
    mock_user.iam_roles = "DATA_MANAGER"
    mock_user.organisation_assignments = [mock_assignment1, mock_assignment2]

    mock_config = MagicMock()
    mock_config.is_ctie_instance.return_value = False

    result = check_ctie_only_access(mock_user, mock_config)
    assert result is True


def test_check_ctie_only_access_iam_roles_as_list():
    mock_org = MagicMock()
    mock_org.is_deprecated = False
    mock_org.accessible_within_ctie = True

    mock_assignment = MagicMock()
    mock_assignment.organisation = mock_org

    mock_user = MagicMock()
    mock_user.iam_roles = ["DATA_MANAGER", "OTHER_ROLE"]
    mock_user.organisation_assignments = [mock_assignment]

    mock_config = MagicMock()
    mock_config.is_ctie_instance.return_value = False

    result = check_ctie_only_access(mock_user, mock_config)
    assert result is True
