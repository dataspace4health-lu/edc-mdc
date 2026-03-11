from fastapi import APIRouter, Depends, File, UploadFile, status
from typing import Annotated
from services.antivirus import AntivirusService
from routes.auth import validate_and_retrieve_identity_context
from models.identity_context import IdentityContext

router = APIRouter()


@router.post(
    "/api/v1/antivirus/scan",
    tags=["antivirus"],
    status_code=status.HTTP_200_OK,
)
async def scan_file(
    antivirus_service: Annotated[AntivirusService, Depends(AntivirusService)],
    file: UploadFile = File(...),
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "datasets:edit:draft:my",
                "datasets:edit:draft:organisation",
                "datasets:edit:draft:group",
                "datasets:edit:draft",
            ]
        )
    ),
) -> dict:
    is_clean, message = await antivirus_service.scan_file(file)

    return {"is_clean": is_clean, "message": message}
