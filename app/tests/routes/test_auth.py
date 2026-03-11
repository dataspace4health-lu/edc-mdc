import os
import pytest
from fastapi.testclient import TestClient
from fastapi import Request
from main import app
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
from routes.auth import APP_URL
from auth.dependencies import (
    validate_and_retrieve_identity_context,
    validate_and_retrieve_identity_context_multi_tenant,
)
from unittest import mock
from services.user import UserService
from models.user import User
from services.config import ConfigService
from types import SimpleNamespace

config_service = ConfigService(config_file_path="./config.json")

app.state.config_service = config_service
client = TestClient(app)


@pytest.mark.asyncio
@patch("auth.session_auth.authorize_access_token")
@mock.patch.dict(os.environ, {"OPENID_CLIENT_ID": "test"}, clear=True)
async def test_auth_endpoint(authorize_access_token):
    mock_config_service = MagicMock()
    mock_config_service.get_enable_multi_tenants.return_value = False
    mock_config_service.get_roles_path_in_access_token.return_value = (
        "resource_access.{client_id}.roles"
    )
    mock_config_service.get_roles.return_value = [
        {"name": "DATA_MANAGER", "permissions": ["datasets:edit"]}
    ]
    mock_session = {}
    mock_userinfo = {
        "email": "test@example.com",
        "name": "Test User",
        "sub": "12345",
        "resource_access": {"test": {"roles": ["DATA_MANAGER"]}},
    }

    authorize_access_token.return_value = mock_userinfo

    with patch.object(
        UserService,
        "create_or_find",
        return_value=AsyncMock(id="12345", organisation_assignments=[]),
    ) as mock_create_or_find, patch.object(
        Request, "session", mock_session, create=True
    ), patch(
        "services.config.get_config_service", return_value=mock_config_service
    ), patch.object(
        app.state, "config_service", mock_config_service
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="https://test"
        ) as ac:
            response = await ac.get("/auth")

        assert response.status_code == 307
        assert response.headers["Location"] == f"{APP_URL}"

        mock_create_or_find.assert_called_once_with(
            email=mock_userinfo["email"],
            name=mock_userinfo["name"],
            external_id=mock_userinfo["sub"],
            iam_roles=["DATA_MANAGER"],
        )


@pytest.mark.asyncio
@patch("auth.session_auth.authorize_access_token")
@mock.patch.dict(os.environ, {"OPENID_CLIENT_ID": "test"}, clear=True)
async def test_auth_endpoint_with_roles_as_single_string(authorize_access_token):
    mock_config_service = MagicMock()
    mock_config_service.get_enable_multi_tenants.return_value = False
    mock_config_service.get_roles_path_in_access_token.return_value = (
        "resource_access.{client_id}.roles"
    )
    mock_config_service.get_roles.return_value = [
        {"name": "DATA_MANAGER", "permissions": ["datasets:edit"]}
    ]
    mock_session = {}
    mock_userinfo = {
        "email": "test@example.com",
        "name": "Test User",
        "sub": "12345",
        "resource_access": {"test": {"roles": "DATA_MANAGER"}},
    }

    authorize_access_token.return_value = mock_userinfo

    with patch.object(
        UserService, "create_or_find", return_value=AsyncMock(id="12345")
    ) as mock_create_or_find, patch.object(
        Request, "session", mock_session, create=True
    ), patch(
        "services.config.get_config_service", return_value=mock_config_service
    ), patch.object(
        app.state, "config_service", mock_config_service
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="https://test"
        ) as ac:
            response = await ac.get("/auth")

        assert response.status_code == 307
        assert response.headers["Location"] == f"{APP_URL}"

        mock_create_or_find.assert_called_once_with(
            email=mock_userinfo["email"],
            name=mock_userinfo["name"],
            external_id=mock_userinfo["sub"],
            iam_roles=["DATA_MANAGER"],
        )


@pytest.mark.asyncio
async def test_auth_endpoint_with_different_roles_path():
    mock_session = {}
    mock_config_service = MagicMock()
    mock_config_service.get_roles_path_in_access_token.return_value = "groups"
    mock_config_service.get_enable_multi_tenants.return_value = False
    mock_config_service.get_roles.return_value = [
        {"name": "DATA_MANAGER", "permissions": ["some:permission"]}
    ]

    mock_userinfo = {
        "email": "test@example.com",
        "name": "Test User",
        "sub": "12345",
        "groups": ["DATA_MANAGER"],
    }

    with patch(
        "auth.session_auth.authorize_access_token", return_value=mock_userinfo
    ), patch.dict(os.environ, {"OPENID_CLIENT_ID": "test"}, clear=True), patch(
        "services.config.get_config_service", return_value=mock_config_service
    ), patch.object(
        app.state, "config_service", mock_config_service
    ), patch.object(
        UserService, "create_or_find", return_value=MagicMock(id="12345")
    ), patch.object(
        Request, "session", mock_session, create=True
    ):

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="https://test"
        ) as ac:
            response = await ac.get("/auth")

        assert response.status_code == 307
        assert response.headers["Location"] == f"{APP_URL}"


@pytest.mark.asyncio
@patch("auth.session_auth.authorize_access_token")
@mock.patch.dict(os.environ, {"OPENID_CLIENT_ID": "test"}, clear=True)
async def test_auth_endpoint_with_iam_role_name_mapping(authorize_access_token):
    mock_config_service = MagicMock()
    mock_config_service.get_enable_multi_tenants.return_value = False
    mock_config_service.get_roles_path_in_access_token.return_value = (
        "resource_access.{client_id}.roles"
    )
    # Define role with iam_role_name mapping
    mock_config_service.get_roles.return_value = [
        {
            "name": "DATA_MANAGER",
            "iam_role_name": "iam-data-mgr",
            "permissions": ["datasets:edit"],
        }
    ]
    mock_session = {}
    # IAM returns "iam-data-mgr" but app expects "DATA_MANAGER"
    mock_userinfo = {
        "email": "test@example.com",
        "name": "Test User",
        "sub": "12345",
        "resource_access": {"test": {"roles": ["iam-data-mgr"]}},
    }

    authorize_access_token.return_value = mock_userinfo

    with patch.object(
        UserService,
        "create_or_find",
        return_value=AsyncMock(id="12345", organisation_assignments=[]),
    ) as mock_create_or_find, patch.object(
        Request, "session", mock_session, create=True
    ), patch(
        "services.config.get_config_service", return_value=mock_config_service
    ), patch.object(
        app.state, "config_service", mock_config_service
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="https://test"
        ) as ac:
            response = await ac.get("/auth")

        assert response.status_code == 307
        assert response.headers["Location"] == f"{APP_URL}"

        # Verify that the IAM role "iam-data-mgr" was mapped to "DATA_MANAGER"
        mock_create_or_find.assert_called_once_with(
            email=mock_userinfo["email"],
            name=mock_userinfo["name"],
            external_id=mock_userinfo["sub"],
            iam_roles=["DATA_MANAGER"],
        )


@pytest.mark.asyncio
@patch("auth.session_auth.authorize_access_token")
@mock.patch.dict(os.environ, {"OPENID_CLIENT_ID": "test"}, clear=True)
async def test_auth_endpoint_with_iam_role_name_mapping_catalogue_manager(
    authorize_access_token,
):
    mock_config_service = MagicMock()
    mock_config_service.get_enable_multi_tenants.return_value = True
    mock_config_service.get_roles_path_in_access_token.return_value = (
        "resource_access.{client_id}.roles"
    )
    # CATALOGUE_MANAGER has a different IAM role name
    mock_config_service.get_roles.return_value = [
        {
            "name": "CATALOGUE_MANAGER",
            "iam_role_name": "iam-catalogue-mgr",
            "permissions": ["catalogue:manage"],
        }
    ]
    mock_session = {}
    # IAM returns "iam-catalogue-mgr" but app expects "CATALOGUE_MANAGER"
    mock_userinfo = {
        "email": "test@example.com",
        "name": "Test User",
        "sub": "12345",
        "resource_access": {"test": {"roles": ["iam-catalogue-mgr"]}},
    }

    authorize_access_token.return_value = mock_userinfo

    mock_user = MagicMock()
    mock_user.id = "12345"
    mock_user.iam_roles = ["CATALOGUE_MANAGER"]
    mock_user.organisation_assignments = []
    mock_user.is_deprecated = False

    with patch.object(
        UserService,
        "create_or_find",
        return_value=mock_user,
    ) as mock_create_or_find, patch.object(
        Request, "session", mock_session, create=True
    ), patch(
        "services.config.get_config_service", return_value=mock_config_service
    ), patch.object(
        app.state, "config_service", mock_config_service
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="https://test"
        ) as ac:
            response = await ac.get("/auth")

        assert response.status_code == 307
        assert response.headers["Location"] == "http://localhost:5173"

        # Verify that the IAM role was mapped correctly
        mock_create_or_find.assert_called_once_with(
            email=mock_userinfo["email"],
            name=mock_userinfo["name"],
            external_id=mock_userinfo["sub"],
            iam_roles=["CATALOGUE_MANAGER"],
        )

        # Verify CATALOGUE_MANAGER gets no org assignment
        assert mock_session["current_organisation_id"] is None
        assert mock_session["user_id"] == "12345"


@pytest.mark.asyncio
@patch("auth.session_auth.authorize_access_token")
@mock.patch.dict(os.environ, {"OPENID_CLIENT_ID": "test"}, clear=True)
async def test_auth_endpoint_without_iam_role_name_field(authorize_access_token):
    """Test that roles work correctly when iam_role_name field is not present (backward compatibility)"""
    mock_config_service = MagicMock()
    mock_config_service.get_enable_multi_tenants.return_value = False
    mock_config_service.get_roles_path_in_access_token.return_value = (
        "resource_access.{client_id}.roles"
    )
    # Role without iam_role_name field - should work normally
    mock_config_service.get_roles.return_value = [
        {
            "name": "DATA_MANAGER",
            "permissions": ["datasets:edit"],
        }
    ]
    mock_session = {}
    mock_userinfo = {
        "email": "test@example.com",
        "name": "Test User",
        "sub": "12345",
        "resource_access": {"test": {"roles": ["DATA_MANAGER"]}},
    }

    authorize_access_token.return_value = mock_userinfo

    with patch.object(
        UserService,
        "create_or_find",
        return_value=AsyncMock(id="12345", organisation_assignments=[]),
    ) as mock_create_or_find, patch.object(
        Request, "session", mock_session, create=True
    ), patch(
        "services.config.get_config_service", return_value=mock_config_service
    ), patch.object(
        app.state, "config_service", mock_config_service
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="https://test"
        ) as ac:
            response = await ac.get("/auth")

        assert response.status_code == 307
        assert response.headers["Location"] == f"{APP_URL}"

        # Verify that the role works without iam_role_name field
        mock_create_or_find.assert_called_once_with(
            email=mock_userinfo["email"],
            name=mock_userinfo["name"],
            external_id=mock_userinfo["sub"],
            iam_roles=["DATA_MANAGER"],
        )


@pytest.mark.asyncio
@patch("auth.session_auth.authorize_access_token")
@mock.patch.dict(os.environ, {"OPENID_CLIENT_ID": "test"}, clear=True)
async def test_auth_endpoint_with_empty_roles(authorize_access_token):
    mock_config_service = MagicMock()
    mock_config_service.get_enable_multi_tenants.return_value = False
    mock_config_service.get_roles_path_in_access_token.return_value = "groups"
    mock_config_service.get_roles.return_value = []

    mock_userinfo = {
        "email": "test@example.com",
        "name": "Test User",
        "sub": "12345",
        "groups": [],
    }

    authorize_access_token.return_value = mock_userinfo

    with patch(
        "services.config.get_config_service", return_value=mock_config_service
    ), patch.object(app.state, "config_service", mock_config_service):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="https://test"
        ) as ac:
            response = await ac.get("/auth")
            assert response.status_code == 307
            assert response.headers["Location"] == f"{APP_URL}/unauthorised"


def mock_user_service_find_by_id(user_id):
    return User(id=user_id, email="user@example.com", name="Test User")


def test_get_user_authenticated_and_authorized():
    user_id = 123
    mock_user = MagicMock()
    mock_user.id = user_id
    mock_user.email = "user@example.com"
    mock_user.name = "Test User"
    mock_user.iam_roles = "CATALOGUE_MANAGER"
    mock_user.is_deprecated = False
    mock_user.organisation_assignments = []

    with patch.object(
        UserService, "find_by_id", return_value=mock_user
    ) as mock_find_by_id, patch.object(
        Request,
        "session",
        {"user_id": user_id},
    ):
        response = client.get("/api/v1/user")
        assert response.status_code == 200
        actual_response = response.json()

        expected_response = {
            "id": user_id,
            "is_deprecated": False,
            "last_login_at": [],
            "email": "user@example.com",
            "name": "Test User",
            "default_themes": [
                "http://publications.europa.eu/resource/authority/data-theme/ENVI"
            ],
            "show_notice_on_homepage": "",
            "feature_options": {
                "enable_notes": False,
                "enable_distribution_notes": False,
                "enable_distribution_path": True,
                "enable_duration_of_data": True,
                "enable_conventions": True,
                "enable_area_of_work_and_competence": True,
                "enable_validation_via_group_manager": True,
                "enable_monitoring_location": True,
                "enable_authentic_source": True,
                "enable_multi_tenants": True,
                "enable_upload_datasets_to_front_office": True,
                "enable_dual_instance": False,
            },
            "assignments": [],
            "iam_roles": ["CATALOGUE_MANAGER"],
            "can_edit_form_fields": True,
            "current_organisation": None,
            "has_ctie_only_access": False,
            "permissions": [
                "datasets:edit:draft",
                "datasets:delete:draft",
                "datasets:read:all-after-draft",
                "datasets:status-change:complete",
                "datasets:status-change:draft",
                "datasets:status-change:validate",
                "datasets:status-change:approve",
                "datasets:status-change:publish",
                "datasets:status-change:internal-only",
                "datasets:status-change:deprecate",
                "form-fields:edit",
                "organisations:edit",
                "contacts:edit",
                "catalogue:generate-rdf",
                "catalogue:upload-rdf:s3",
                "roles:manage",
                "authentic-source:assign",
                "comments:delete",
            ],
        }
        actual_response["permissions"].sort()
        expected_response["permissions"].sort()
        assert actual_response == expected_response


def test_get_user_not_authenticated():
    with patch.object(
        Request, "session", {"user_id": None, "user_permissions": None}
    ) as mock_session:
        response = client.get("/api/v1/user")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_authorize_multi_tenant_with_catalogue_manager():
    mock_session = {}
    mock_config_service = MagicMock()
    mock_config_service.get_roles_path_in_access_token.return_value = "groups"
    mock_config_service.get_enable_multi_tenants.return_value = True
    mock_config_service.get_roles.return_value = [
        {"name": "CATALOGUE_MANAGER", "permissions": ["catalogue:manage"]}
    ]

    mock_userinfo = {
        "email": "test@example.com",
        "name": "Test User",
        "sub": "12345",
        "groups": ["CATALOGUE_MANAGER"],
    }

    mock_user = MagicMock()
    mock_user.id = "12345"
    mock_user.iam_roles = ["CATALOGUEL_MANAGER"]
    mock_user.organisation_assignments = []
    mock_user.is_deprecated = False

    with patch(
        "auth.session_auth.authorize_access_token", return_value=mock_userinfo
    ), patch.dict(
        os.environ,
        {"OPENID_CLIENT_ID": "test", "APP_URL": "https://localhost:5173"},
        clear=True,
    ), patch(
        "services.config.get_config_service", return_value=mock_config_service
    ), patch.object(
        app.state, "config_service", mock_config_service
    ), patch.object(
        UserService, "create_or_find", return_value=mock_user
    ), patch.object(
        Request, "session", mock_session, create=True
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="https://test"
        ) as ac:
            response = await ac.get("/auth")

        assert response.status_code == 307
        assert response.headers["Location"] == "http://localhost:5173"
        assert mock_session["user_id"] == "12345"


@pytest.mark.asyncio
async def test_authorize_multi_tenant_with_regular_user_no_org():
    mock_session = {}
    mock_config_service = MagicMock()
    mock_config_service.get_enable_multi_tenants.return_value = True
    mock_config_service.get_roles.return_value = [
        {"name": "METADATA_EDITOR", "permissions": ["datasets:edit"]}
    ]

    mock_userinfo = {
        "email": "test@example.com",
        "name": "Test User",
        "sub": "12345",
        "groups": ["METADATA_EDITOR"],
    }

    mock_user = MagicMock()
    mock_user.id = "12345"
    mock_user.iam_roles = ["METADATA_EDITOR"]
    mock_user.organisation_assignments = []

    with patch(
        "auth.session_auth.authorize_access_token", return_value=mock_userinfo
    ), patch.dict(
        os.environ,
        {"OPENID_CLIENT_ID": "test", "APP_URL": "https://localhost:5173"},
        clear=True,
    ), patch(
        "services.config.get_config_service", return_value=mock_config_service
    ), patch.object(
        app.state, "config_service", mock_config_service
    ), patch.object(
        UserService, "create_or_find", return_value=mock_user
    ), patch.object(
        Request, "session", mock_session, create=True
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="https://test"
        ) as ac:
            response = await ac.get("/auth")

        assert response.status_code == 307
        assert response.headers["Location"] == "http://localhost:5173/first-time-login"


@pytest.mark.asyncio
async def test_authorize_multi_tenant_with_deprecated_user():
    mock_session = {}
    mock_config_service = MagicMock()
    mock_config_service.get_roles_path_in_access_token.return_value = "groups"
    mock_config_service.get_enable_multi_tenants.return_value = True
    mock_config_service.get_roles.return_value = [
        {"name": "METADATA_EDITOR", "permissions": ["datasets:edit"]}
    ]

    mock_userinfo = {
        "email": "test@example.com",
        "name": "Test User",
        "sub": "12345",
        "groups": ["METADATA_EDITOR"],
    }

    mock_user = MagicMock()
    mock_user.id = "12345"
    mock_user.iam_roles = []
    mock_user.is_deprecated = True

    with patch(
        "auth.session_auth.authorize_access_token", return_value=mock_userinfo
    ), patch.dict(
        os.environ,
        {"OPENID_CLIENT_ID": "test", "APP_URL": "https://localhost:5173"},
        clear=True,
    ), patch(
        "services.config.get_config_service", return_value=mock_config_service
    ), patch.object(
        app.state, "config_service", mock_config_service
    ), patch.object(
        UserService,
        "create_or_find",
        return_value=mock_user,
    ), patch.object(
        Request, "session", mock_session, create=True
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="https://test"
        ) as ac:
            response = await ac.get("/auth")

        assert response.status_code == 307
        assert response.headers["Location"] == "http://localhost:5173/first-time-login"


@pytest.mark.asyncio
async def test_authorize_multi_tenant_with_regular_user_with_org():
    mock_session = {}
    mock_config_service = MagicMock()
    mock_config_service.get_roles_path_in_access_token.return_value = "groups"
    mock_config_service.get_enable_multi_tenants.return_value = True
    mock_config_service.get_roles.return_value = [
        {"name": "METADATA_EDITOR", "permissions": ["datasets:edit"]}
    ]

    mock_userinfo = {
        "email": "test@example.com",
        "name": "Test User",
        "sub": "12345",
        "groups": ["METADATA_EDITOR"],
    }

    mock_org = SimpleNamespace(id=1, name="Org 1", is_deprecated=False)
    mock_assignment = SimpleNamespace(organisation_id=1, organisation=mock_org)

    mock_user = MagicMock()
    mock_user.id = "12345"
    mock_user.iam_roles = []
    mock_user.organisation_assignments = [mock_assignment]
    mock_user.is_deprecated = False

    with patch(
        "auth.session_auth.authorize_access_token", return_value=mock_userinfo
    ), patch.dict(
        os.environ,
        {"OPENID_CLIENT_ID": "test", "APP_URL": "https://localhost:5173"},
        clear=True,
    ), patch(
        "services.config.get_config_service", return_value=mock_config_service
    ), patch.object(
        app.state, "config_service", mock_config_service
    ), patch.object(
        UserService,
        "create_or_find",
        return_value=mock_user,
    ), patch.object(
        Request, "session", mock_session, create=True
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="https://test"
        ) as ac:
            response = await ac.get("/auth")

        assert response.status_code == 307
        assert response.headers["Location"] == "http://localhost:5173"
        assert mock_session["user_id"] == "12345"


def test_validate_identity_context_multi_tenant_catalogue_manager():
    mock_config_service = MagicMock()
    mock_config_service.get_enable_multi_tenants.return_value = True
    mock_config_service.get_roles.return_value = [
        {"name": "CATALOGUE_MANAGER", "permissions": ["catalogue:manage"]}
    ]

    mock_user = MagicMock()
    mock_user.id = 12345
    mock_user.iam_roles = ["CATALOGUE_MANAGER"]
    mock_user.organisation_assignments = []

    mock_request = MagicMock()
    mock_request.session = {"user_id": 12345}

    mock_user_service = MagicMock()
    mock_user_service.find_by_id.return_value = mock_user

    identity_context = validate_and_retrieve_identity_context_multi_tenant(
        mock_request,
        ["catalogue:manage"],
        mock_user_service,
        mock_config_service,
    )

    assert identity_context.user_id == 12345
    assert identity_context.permissions == ["catalogue:manage"]


def test_validate_identity_context_multi_tenant_regular_user():
    mock_config_service = MagicMock()
    mock_config_service.get_enable_multi_tenants.return_value = True
    mock_config_service.get_roles.return_value = [
        {"name": "METADATA_EDITOR", "permissions": ["datasets:edit"]}
    ]

    mock_role_assignment = MagicMock()
    mock_role_assignment.role = MagicMock()
    mock_role_assignment.role.name = "METADATA_EDITOR"

    mock_org_assignment = MagicMock()
    mock_org_assignment.organisation_id = 1234
    mock_org_assignment.roles = [mock_role_assignment]

    mock_user = MagicMock()
    mock_user.id = "12345"
    mock_user.iam_roles = []
    mock_user.organisation_assignments = [mock_org_assignment]

    mock_request = MagicMock()
    mock_request.session = {"user_id": "12345", "current_organisation_id": 1234}

    mock_user_service = MagicMock()
    mock_user_service.find_by_id.return_value = mock_user

    identity_context = validate_and_retrieve_identity_context_multi_tenant(
        mock_request,
        ["datasets:edit"],
        mock_user_service,
        mock_config_service,
    )

    assert identity_context.user_id == 12345
    assert identity_context.permissions == ["datasets:edit"]


def test_validate_identity_context_with_service_account_token():
    mock_config_service = MagicMock()
    mock_config_service.get_enable_multi_tenants.return_value = False
    mock_config_service.get_roles.return_value = [
        {"name": "DATA_MANAGER", "permissions": ["datasets:edit"]}
    ]
    mock_config_service.get_roles_path_in_access_token.return_value = (
        "resource_access.{client_id}.roles"
    )

    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.iam_roles = "DATA_MANAGER"

    mock_user_service = MagicMock()
    mock_user_service.create_or_find.return_value = mock_user

    mock_request = MagicMock()
    mock_request.headers = {"Authorization": "Bearer fake-token"}
    mock_request.session = {}

    dependency = validate_and_retrieve_identity_context(["datasets:edit"])

    with patch.dict(
        os.environ,
        {
            "BOT_SERVICE_CLIENT_ID": "bot-mdc-service-client",
            "BOT_SERVICE_AUDIENCE": "dca-metadata-capture-local",
            "OPENID_CLIENT_ID": "dca-metadata-capture-local",
        },
        clear=False,
    ), patch(
        "auth.oauth_client.jwks_client.get_signing_key_from_jwt",
        return_value=SimpleNamespace(key="secret"),
    ), patch(
        "auth.service_account.jwt.decode",
        return_value={
            "client_id": "bot-mdc-service-client",
            "sub": "service-account-bot-mdc-service-client",
            "resource_access": {
                "dca-metadata-capture-local": {"roles": ["DATA_MANAGER"]}
            },
        },
    ):
        identity_context = dependency(
            mock_request, mock_user_service, mock_config_service
        )

    assert identity_context.user_id == 1
    assert identity_context.permissions == ["datasets:edit"]

    # Verify create_or_find was called with correct parameters
    mock_user_service.create_or_find.assert_called_once_with(
        email=None,
        name="Service Account (bot-mdc-service-client)",
        external_id="service-account-bot-mdc-service-client",
        iam_roles=["DATA_MANAGER"],
    )
