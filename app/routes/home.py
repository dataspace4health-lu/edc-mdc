import os

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from models.identity_context import IdentityContext
from routes.auth import validate_and_retrieve_identity_context
from services.user import UserService
from typing import Annotated

from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="client/dist")

APP_URL = os.getenv("APP_URL", "http://localhost:5173")


@router.get("/", tags=["front-end"])
async def read_root(
    request: Request,
    user_service: Annotated[UserService, Depends(UserService)],
):
    try:
        identity = validate_and_retrieve_identity_context(
            [
                "datasets:edit:draft",
                "datasets:edit:draft:organisation",
                "datasets:edit:draft:my",
                "datasets:edit:draft:group",
                "datasets:read:all-after-draft",
                "datasets:read:all-after-draft:organisation",
                "datasets:read:all-after-complete",
                "form-fields:edit",
                "form-fields:edit:my",
                "form-fields:edit:organisation",
            ]
        )(request, user_service, request.app.state.config_service)
        service = request.app.state.config_service
        app_title = service.get_app_title()

        return templates.TemplateResponse(
            "index.html", {"request": request, "app_title": app_title}
        )
    except HTTPException as e:
        if e.status_code == 401:
            return RedirectResponse(url=f"{APP_URL}/login", status_code=303)
        raise e
