import os
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from services.config import ConfigService, get_config_service

router = APIRouter(prefix="/api/v1/test", tags=["test"])


class ConfigUpdateRequest(BaseModel):
    key_path: str
    value: Any


class FeatureFlagUpdateRequest(BaseModel):
    flag_name: str
    enabled: bool


def _check_e2e_environment():
    if os.getenv("ENVIRONMENT") != "end2end":
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only available in E2E test environment",
        )


@router.post(
    "/config/update",
    response_model=dict,
)
def update_config_for_test(
    request: Annotated[ConfigUpdateRequest, Body()],
    config_service: Annotated[ConfigService, Depends(get_config_service)],
):
    _check_e2e_environment()
    try:
        config_service.update_config_value(request.key_path, request.value)
        return {
            "success": True,
            "message": f"Config updated: {request.key_path} = {request.value}",
        }
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to update config: {str(e)}"
        )


@router.post(
    "/config/feature-flag",
    response_model=dict,
)
def update_feature_flag_for_test(
    request: Annotated[FeatureFlagUpdateRequest, Body()],
    config_service: Annotated[ConfigService, Depends(get_config_service)],
):
    _check_e2e_environment()
    try:
        config_service.update_feature_flag(request.flag_name, request.enabled)
        return {
            "success": True,
            "message": f"Feature flag updated: {request.flag_name} = {request.enabled}",
        }
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to update feature flag: {str(e)}"
        )


@router.get(
    "/config/reset",
    response_model=dict,
)
def reset_config_for_test(
    config_service: Annotated[ConfigService, Depends(get_config_service)],
):
    _check_e2e_environment()
    try:
        config_service.reset_config()
        return {"success": True, "message": "Config reset to original state"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to reset config: {str(e)}")
