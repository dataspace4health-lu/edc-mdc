from fastapi import APIRouter, Depends, HTTPException, Response
from typing import List, Dict, Any
from services.role import RoleService
from services.config import ConfigService, get_config_service
from schemas.user_assignment import ResourceRole

router = APIRouter()


@router.post(
    "/api/v1/roles",
    response_model=List[ResourceRole],
    tags=["roles"],
)
def get_roles(
    service: RoleService = Depends(RoleService),
):
    roles = service.get_all_roles()
    if not roles:
        raise HTTPException(status_code=404, detail="No roles found")
    return roles


@router.get(
    "/api/v1/config/roles",
    response_model=List[Dict[str, Any]],
    tags=["config", "roles"],
)
def get_config_roles(
    config_service: ConfigService = Depends(get_config_service),
):
    roles = config_service.get_roles()
    if not roles:
        raise HTTPException(status_code=404, detail="No roles found in configuration")
    return roles
