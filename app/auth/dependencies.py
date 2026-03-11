from typing import Annotated, List
from fastapi import Request, Depends, HTTPException

from models.identity_context import IdentityContext
from services.user import UserService
from services.config import ConfigService, get_config_service
from auth.service_account import authenticate_service_account_if_present
from auth.permissions import get_permissions_from_roles, has_permissions


def validate_and_retrieve_identity_context(permissions: List[str]):
    def dependency(
        request: Request,
        user_service: Annotated[UserService, Depends(UserService)],
        config_service: Annotated[ConfigService, Depends(get_config_service)],
    ) -> IdentityContext:
        # First check for service account authentication
        service_identity = authenticate_service_account_if_present(
            request=request,
            permissions=permissions,
            user_service=user_service,
            config_service=config_service,
        )
        if service_identity:
            return service_identity

        # Fall back to session-based authentication
        enable_multi_tenants = config_service.get_enable_multi_tenants()

        if enable_multi_tenants:
            return validate_and_retrieve_identity_context_multi_tenant(
                request,
                permissions,
                user_service,
                config_service,
            )
        else:
            return validate_and_retrieve_identity_context_single_tenant(
                request,
                permissions,
                user_service,
                config_service,
            )

    return dependency


def validate_and_retrieve_identity_context_multi_tenant(
    request: Request,
    permissions: List[str],
    user_service: Annotated[UserService, Depends(UserService)],
    config_service: Annotated[ConfigService, Depends(get_config_service)],
) -> IdentityContext:
    user_id = request.session.get("user_id")
    current_org_id = request.session.get("current_organisation_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = user_service.find_by_id(user_id)

    if "CATALOGUE_MANAGER" not in user.iam_roles and not user.organisation_assignments:
        raise HTTPException(status_code=401, detail="Tenant not found")

    user_roles = []

    if "CATALOGUE_MANAGER" in user.iam_roles:
        user_roles.append("CATALOGUE_MANAGER")
    else:
        for ua in user.organisation_assignments:
            if ua.organisation_id == current_org_id:
                for ra in ua.roles:
                    user_roles.append(ra.role.name)
                break

    user_permissions = get_permissions_from_roles(user_roles, config_service)

    if permissions and not has_permissions(user_permissions, permissions):
        raise HTTPException(status_code=403, detail="Unauthorized")

    return IdentityContext(
        user_id=user_id,
        permissions=user_permissions,
        current_organisation_id=current_org_id,
    )


def validate_and_retrieve_identity_context_single_tenant(
    request: Request,
    permissions: List[str],
    user_service: Annotated[UserService, Depends(UserService)],
    config_service: Annotated[ConfigService, Depends(get_config_service)],
) -> IdentityContext:
    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = user_service.find_by_id(user_id)

    if not user:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_permissions = get_permissions_from_roles(user.iam_roles, config_service)

    if permissions and not has_permissions(user_permissions, permissions):
        raise HTTPException(status_code=403, detail="Unauthorized")

    return IdentityContext(user_id=user_id, permissions=user_permissions)
