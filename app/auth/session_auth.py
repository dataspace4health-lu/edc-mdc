import os
from typing import Annotated, List
from functools import reduce
from fastapi import Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from services.user import UserService
from services.config import ConfigService, get_config_service
from auth.oauth_client import authorize_access_token

APP_URL = os.getenv("APP_URL", "http://localhost:5173")


def is_org_deprecated(org) -> bool:
    return getattr(org, "is_deprecated", False)


def check_ctie_only_access(user, config_service: ConfigService) -> bool:
    # CATALOGUE_MANAGER users are exempt from this check
    user_roles = (
        user.iam_roles
        if isinstance(user.iam_roles, list)
        else user.iam_roles.split(",")
    )

    if "CATALOGUE_MANAGER" in user_roles:
        return False

    # Check if this is a CTIE instance
    is_ctie = config_service.is_ctie_instance()

    # Only check if this is NOT a CTIE instance
    if is_ctie:
        return False

    # Get all valid (non-deprecated) orgs
    if not user.organisation_assignments:
        return False

    valid_orgs = [
        ua
        for ua in user.organisation_assignments
        if not is_org_deprecated(ua.organisation)
    ]

    # Check if ANY org requires CTIE
    has_ctie_org = any(
        getattr(org.organisation, "accessible_within_ctie", False) is True
        for org in valid_orgs
    )

    return has_ctie_org


def extract_iam_roles(
    config_service: ConfigService, userinfo, validate_roles=True
) -> List[str]:
    client_id = os.getenv("OPENID_CLIENT_ID")

    roles_path = config_service.get_roles_path_in_access_token()
    roles_path = roles_path.format(client_id=client_id)

    roles_keys = roles_path.split(".")

    roles = reduce(lambda d, key: d.get(key, {}), roles_keys, userinfo)

    if isinstance(roles, str):
        roles = [roles]
    if not roles or not isinstance(roles, list):
        roles = []

    # Map IAM roles to application roles using iam_role_name field
    all_roles = config_service.get_roles()
    iam_to_app_role_map = {
        role.get("iam_role_name", role["name"]): role["name"] for role in all_roles
    }
    roles = [iam_to_app_role_map.get(role, role) for role in roles]

    # Only validate roles against config if validate_roles is True (single tenant)
    if validate_roles and len(roles) == 0:
        raise HTTPException(
            status_code=403,
            detail="You do not have correct permissions.",
        )

    return roles


async def extract_user_details(
    request: Request,
    user_service: Annotated[UserService, Depends(UserService)],
    config_service: Annotated[ConfigService, Depends(get_config_service)],
    validate_iam_roles: bool = True,
):
    try:
        userinfo = await authorize_access_token(request)
    except Exception as e:
        error_str = str(e).lower()
        if any(keyword in error_str for keyword in ["state", "csrf", "mismatch"]):
            request.session.clear()
            # State/CSRF issues - most common, just retry
            return RedirectResponse(url=APP_URL)
        return HTMLResponse(content=str(e), status_code=400)

    try:
        user_iam_role_names = extract_iam_roles(
            config_service, userinfo, validate_roles=validate_iam_roles
        )
    except HTTPException as e:
        return RedirectResponse(url=f"{APP_URL}/unauthorised")

    user = user_service.create_or_find(
        email=userinfo["email"],
        name=userinfo["name"],
        external_id=userinfo["sub"],
        iam_roles=user_iam_role_names,
    )

    return user, user_iam_role_names


async def authorize_single_tenant(
    request: Request,
    user_service: Annotated[UserService, Depends(UserService)],
    config_service: Annotated[ConfigService, Depends(get_config_service)],
):
    result = await extract_user_details(
        request, user_service, config_service, validate_iam_roles=True
    )
    if isinstance(result, (HTMLResponse, RedirectResponse)):
        return result

    user = result[0]

    request.session["user_id"] = user.id
    return RedirectResponse(url=f"{APP_URL}")


async def authorize_multi_tenant(
    request: Request,
    user_service: Annotated[UserService, Depends(UserService)],
    config_service: Annotated[ConfigService, Depends(get_config_service)],
):
    result = await extract_user_details(
        request, user_service, config_service, validate_iam_roles=False
    )
    if isinstance(result, (HTMLResponse, RedirectResponse)):
        return result

    user = result[0]
    user_iam_role_names = result[1]

    if "CATALOGUE_MANAGER" in user_iam_role_names:
        request.session["current_organisation_id"] = None
        request.session["user_id"] = user.id
        return RedirectResponse(url=f"{APP_URL}")

    if user.is_deprecated or (not user.organisation_assignments):
        return RedirectResponse(url=f"{APP_URL}/first-time-login")

    # Check if user has CTIE-only access
    if check_ctie_only_access(user, config_service):
        return RedirectResponse(url=f"{APP_URL}/ctie-only-access")

    # Get all valid (non-deprecated) orgs
    valid_orgs = [
        a
        for a in user.organisation_assignments
        if not is_org_deprecated(a.organisation)
    ]

    if not valid_orgs:
        return RedirectResponse(url=f"{APP_URL}/unauthorised")

    # Use first valid org
    valid_org = valid_orgs[0]

    request.session["current_organisation_id"] = valid_org.organisation_id
    request.session["user_id"] = user.id
    return RedirectResponse(url=f"{APP_URL}")
