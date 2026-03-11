import os
from typing import Optional, List
from fastapi import Request, HTTPException
import jwt

from models.identity_context import IdentityContext
from services.user import UserService
from services.config import ConfigService
from auth.jwt_helpers import extract_bearer_token
from auth.permissions import get_permissions_from_roles, has_permissions
from auth.oauth_client import jwks_client
from auth.session_auth import extract_iam_roles
from auth.service_account_user import create_or_find_service_account_user


def authenticate_service_account_if_present(
    request: Request,
    permissions: List[str],
    user_service: UserService,
    config_service: ConfigService,
) -> Optional[IdentityContext]:
    bot_client_id = os.getenv("BOT_SERVICE_CLIENT_ID")
    if not bot_client_id:
        return None

    token = extract_bearer_token(request)
    if not token:
        return None

    bot_audience = os.getenv("BOT_SERVICE_AUDIENCE", os.getenv("OPENID_CLIENT_ID"))

    # Validate and decode JWT token
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        decode_kwargs = {
            "algorithms": ["RS256"],
            "options": {"verify_exp": True, "verify_iat": False},
        }
        if bot_audience:
            decode_kwargs["audience"] = bot_audience
        else:
            decode_kwargs["options"]["verify_aud"] = False

        payload = jwt.decode(token, signing_key.key, **decode_kwargs)
    except Exception as exc:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(
            f"Service account JWT validation failed: {type(exc).__name__}: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication token: {type(exc).__name__}",
        ) from exc

    # Verify client ID matches expected service account
    token_client_id = payload.get("client_id") or payload.get("azp")
    if token_client_id != bot_client_id:
        raise HTTPException(status_code=403, detail="Unauthorized service account")

    # Create or find user for this service account using shared utility
    # This will extract and assign IAM roles from the token
    user_id = create_or_find_service_account_user(
        user_service,
        token,
        token_client_id,
        config_service,
    )

    # Extract IAM roles from JWT token for permissions
    user_iam_roles = extract_iam_roles(config_service, payload, validate_roles=False)

    # Get permissions from extracted roles
    user_permissions = get_permissions_from_roles(user_iam_roles, config_service)
    if permissions and not has_permissions(user_permissions, permissions):
        raise HTTPException(status_code=403, detail="Unauthorized")

    return IdentityContext(
        user_id=user_id,
        permissions=user_permissions,
        current_organisation_id=None,
    )
