import os
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from typing import Annotated
from urllib.parse import urlencode

from schemas.user import ResourceUser, user_entity_to_resource
from models.identity_context import IdentityContext
from services.user import UserService
from services.config import ConfigService, get_config_service

# Import authentication functions from auth module
from auth.oauth_client import oauth
from auth.session_auth import (
    authorize_single_tenant,
    authorize_multi_tenant,
    check_ctie_only_access,
)
from auth.dependencies import validate_and_retrieve_identity_context

router = APIRouter()

APP_URL = os.getenv("APP_URL", "http://localhost:5173")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


@router.get("/login")
async def login(request: Request):
    if (
        ENVIRONMENT == "development"
        or ENVIRONMENT == "test"
        or ENVIRONMENT == "end2end"
    ):
        base_url = str(request.base_url)
    else:
        base_url = APP_URL.replace("http://", "https://")  # NOSONAR

    redirect_uri = base_url.rstrip("/") + "/auth"

    return await oauth.oidc.authorize_redirect(request, redirect_uri)


@router.get("/auth", name="auth")
async def auth(
    request: Request,
    user_service: Annotated[UserService, Depends(UserService)],
    config_service: Annotated[ConfigService, Depends(get_config_service)],
):
    enable_multi_tenants = config_service.get_enable_multi_tenants()

    if enable_multi_tenants:
        return await authorize_multi_tenant(request, user_service, config_service)
    else:
        return await authorize_single_tenant(request, user_service, config_service)


@router.get("/logout")
async def logout(request: Request):
    try:
        request.session.clear()
        endpoint = os.getenv("OPENID_END_SESSION_URL")
        params = {
            "client_id": os.getenv("OPENID_CLIENT_ID"),
        }

        logout_url = f"{endpoint}?{urlencode(params)}"

        return RedirectResponse(url=logout_url)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error during logout: {str(e)}"
        ) from e


@router.get(
    "/api/v1/user",
    response_model=ResourceUser,
    tags=["user"],
)
async def get_user(
    request: Request,
    service: Annotated[UserService, Depends(UserService)],
    config_service: Annotated[ConfigService, Depends(get_config_service)],
    identity: IdentityContext = Depends(validate_and_retrieve_identity_context([])),
):
    user_id = identity.user_id
    current_org_id = identity.current_organisation_id
    user = service.find_by_id(user_id)

    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_permissions = identity.permissions
    feature_flags = config_service.get_feature_flags()
    default_themes = config_service.get_default_themes()
    show_notice_on_homepage = config_service.get_show_notice_on_homepage()

    has_ctie_only_access = check_ctie_only_access(user, config_service)

    return user_entity_to_resource(
        user,
        user_permissions,
        feature_flags,
        default_themes,
        show_notice_on_homepage,
        current_org_id,
        has_ctie_only_access,
    )


@router.get(
    "/api/v1/ui_config",
)
async def get_ui_config(
    request: Request,
    config_service: Annotated[ConfigService, Depends(get_config_service)],
):
    unauthorised_message = config_service.get_unauthorised_message()
    technical_support_message = config_service.get_technical_support_message()
    source_instance_url = os.getenv("SOURCE_INSTANCE_URL", "")
    source_dataset_url_pattern = os.getenv("SOURCE_DATASET_URL_PATTERN", "/?id={id}")
    is_ctie_instance = config_service.is_ctie_instance()
    default_access_url = os.getenv("DEFAULT_ACCESS_URL", "")
    enable_health_dataset_selector = bool(config_service.get_health_data_access_body())
    return {
        "unauthorised_message": unauthorised_message,
        "technical_support_message": technical_support_message,
        "source_instance_url": source_instance_url,
        "source_dataset_url_pattern": source_dataset_url_pattern,
        "is_ctie_instance": is_ctie_instance,
        "default_access_url": default_access_url,
        "enable_health_dataset_selector": enable_health_dataset_selector,
    }
