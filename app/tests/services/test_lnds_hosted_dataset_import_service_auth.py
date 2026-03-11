import os
from unittest.mock import MagicMock, patch

import httpx
import pytest

from services.lnds_hosted_dataset_import_service import LNDSHostedDatasetImportService
from auth.service_account_user import create_or_find_service_account_user


@pytest.fixture
def mock_env_vars():
    env_vars = {
        "SOURCE_INSTANCE_URL": "http://test-instance:8000",
        "SOURCE_INSTANCE_NAME": "test-instance",
        "SYNC_USER_ID": "1",
        "SOURCE_OIDC_ISSUER_URL": "http://test-oidc:8080/realms/test-realm",
        "SOURCE_SERVICE_ACCOUNT_CLIENT_ID": "test-client",
        "SOURCE_SERVICE_ACCOUNT_CLIENT_SECRET": "test-secret",
        "ENVIRONMENT": "test",
    }
    with patch.dict(os.environ, env_vars, clear=False):
        yield env_vars


def test_obtain_access_token(mock_env_vars):
    mock_dataset_repo = MagicMock()
    mock_rdf_import_service = MagicMock()
    mock_db_session_manager = MagicMock()
    mock_activity_log_service = MagicMock()

    mock_user_service = MagicMock()
    mock_config_service = MagicMock()

    service = LNDSHostedDatasetImportService(
        dataset_repository=mock_dataset_repo,
        dataset_rdf_import_service=mock_rdf_import_service,
        database_session_manager=mock_db_session_manager,
        dataset_activity_log_service=mock_activity_log_service,
        user_service=mock_user_service,
        config_service=mock_config_service,
    )

    # Mock the HTTP client's post method to return a token
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "test-token-12345"}
    mock_response.raise_for_status = MagicMock()

    with patch.object(
        service._http_client, "post", return_value=mock_response
    ) as mock_post, patch(
        "services.lnds_hosted_dataset_import_service.create_or_find_service_account_user",
        return_value=1,
    ):
        token = service._obtain_access_token()

        assert token == "test-token-12345"

        # Verify the token endpoint was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert (
            "test-oidc:8080/realms/test-realm/protocol/openid-connect/token"
            in call_args[0][0]
        )
        assert call_args[1]["data"]["grant_type"] == "client_credentials"
        assert call_args[1]["data"]["client_id"] == "test-client"
        assert call_args[1]["data"]["client_secret"] == "test-secret"


def test_get_auth_headers_with_token(mock_env_vars):
    mock_dataset_repo = MagicMock()
    mock_rdf_import_service = MagicMock()
    mock_db_session_manager = MagicMock()
    mock_activity_log_service = MagicMock()

    mock_user_service = MagicMock()
    mock_config_service = MagicMock()

    service = LNDSHostedDatasetImportService(
        dataset_repository=mock_dataset_repo,
        dataset_rdf_import_service=mock_rdf_import_service,
        database_session_manager=mock_db_session_manager,
        dataset_activity_log_service=mock_activity_log_service,
        user_service=mock_user_service,
        config_service=mock_config_service,
    )

    # Mock the obtain_access_token method
    with patch.object(service, "_obtain_access_token", return_value="test-token"):
        headers = service._get_auth_headers()

        assert headers == {"Authorization": "Bearer test-token"}


def test_fetch_datasets_with_authentication(mock_env_vars):
    mock_dataset_repo = MagicMock()
    mock_rdf_import_service = MagicMock()
    mock_db_session_manager = MagicMock()
    mock_activity_log_service = MagicMock()

    mock_user_service = MagicMock()
    mock_config_service = MagicMock()

    service = LNDSHostedDatasetImportService(
        dataset_repository=mock_dataset_repo,
        dataset_rdf_import_service=mock_rdf_import_service,
        database_session_manager=mock_db_session_manager,
        dataset_activity_log_service=mock_activity_log_service,
        user_service=mock_user_service,
        config_service=mock_config_service,
    )

    # Mock successful token acquisition
    mock_token_response = MagicMock()
    mock_token_response.json.return_value = {"access_token": "test-token"}
    mock_token_response.raise_for_status = MagicMock()

    # Mock successful datasets fetch
    mock_datasets_response = MagicMock()
    mock_datasets_response.json.return_value = {
        "items": [{"id": 1, "identifier": "test-dataset", "status": "PUBLISHED"}],
        "meta": {"total_items": 1},
    }
    mock_datasets_response.raise_for_status = MagicMock()

    with patch.object(
        service._http_client, "post", return_value=mock_token_response
    ), patch(
        "services.lnds_hosted_dataset_import_service.create_or_find_service_account_user",
        return_value=1,
    ):
        with patch.object(
            service._http_client, "get", return_value=mock_datasets_response
        ) as mock_get:
            datasets = service._fetch_released_datasets_page(1)

            assert len(datasets) == 1
            assert datasets[0]["identifier"] == "test-dataset"

            # Verify authentication header was included
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["headers"]["Authorization"] == "Bearer test-token"


def test_token_refresh_on_401(mock_env_vars):
    mock_dataset_repo = MagicMock()
    mock_rdf_import_service = MagicMock()
    mock_db_session_manager = MagicMock()
    mock_activity_log_service = MagicMock()

    mock_user_service = MagicMock()
    mock_config_service = MagicMock()

    service = LNDSHostedDatasetImportService(
        dataset_repository=mock_dataset_repo,
        dataset_rdf_import_service=mock_rdf_import_service,
        database_session_manager=mock_db_session_manager,
        dataset_activity_log_service=mock_activity_log_service,
        user_service=mock_user_service,
        config_service=mock_config_service,
    )

    # Mock token responses
    mock_token_response = MagicMock()
    mock_token_response.json.return_value = {"access_token": "new-token"}
    mock_token_response.raise_for_status = MagicMock()

    # First GET fails with 401, second succeeds
    mock_401_response = MagicMock()
    mock_401_response.status_code = 401
    mock_401_error = httpx.HTTPStatusError(
        "Unauthorized", request=MagicMock(), response=mock_401_response
    )

    mock_success_response = MagicMock()
    mock_success_response.json.return_value = {"items": [], "meta": {"total_items": 0}}
    mock_success_response.raise_for_status = MagicMock()

    with patch.object(
        service._http_client, "post", return_value=mock_token_response
    ), patch(
        "services.lnds_hosted_dataset_import_service.create_or_find_service_account_user",
        return_value=1,
    ):
        with patch.object(
            service._http_client,
            "get",
            side_effect=[mock_401_error, mock_success_response],
        ) as mock_get:
            datasets = service._fetch_released_datasets_page(1)

            # Should have made two GET attempts (first failed, second succeeded)
            assert mock_get.call_count == 2
            assert datasets == []


def test_missing_credentials_warning(caplog):
    mock_dataset_repo = MagicMock()
    mock_rdf_import_service = MagicMock()
    mock_db_session_manager = MagicMock()
    mock_activity_log_service = MagicMock()
    mock_user_service = MagicMock()
    mock_config_service = MagicMock()

    # Create service without setting environment variables
    with patch.dict(
        os.environ,
        {"SOURCE_INSTANCE_URL": "http://test:8000", "ENVIRONMENT": "test"},
        clear=True,
    ):
        service = LNDSHostedDatasetImportService(
            dataset_repository=mock_dataset_repo,
            dataset_rdf_import_service=mock_rdf_import_service,
            database_session_manager=mock_db_session_manager,
            dataset_activity_log_service=mock_activity_log_service,
            user_service=mock_user_service,
            config_service=mock_config_service,
        )

        # Attempting to get token should raise error
        with pytest.raises(
            RuntimeError, match="Service account credentials not configured"
        ):
            service._obtain_access_token()
