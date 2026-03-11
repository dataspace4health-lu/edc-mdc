from fastapi import Depends, status, APIRouter, HTTPException
from typing import List
import httpx
from services.eurlex.legislation import EurlexApplicableLegislationService
from schemas.eurlex import EurlexLegislation
from models.identity_context import IdentityContext
from routes.auth import validate_and_retrieve_identity_context

router = APIRouter()


@router.get(
    "/api/v1/eurlex/legislation/search",
    response_model=List[EurlexLegislation],
    tags=["eurlex"],
    status_code=status.HTTP_200_OK,
)
async def search_legislation(
    query: str = "",
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(
            [
                "form-fields:edit",
                "form-fields:edit:my",
                "form-fields:edit:organisation",
            ]
        )
    ),
) -> List[EurlexLegislation]:
    try:
        service = EurlexApplicableLegislationService()
        return await service.list_legislation(filter=query)
    except httpx.HTTPStatusError as e:
        # Handle EUR-Lex service errors (redirects, unavailability, etc.)
        if e.response.status_code in (301, 302, 307, 308):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="EUR-Lex web service is temporarily unavailable. Please try again later.",
            )
        elif e.response.status_code == 500:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="EUR-Lex web service encountered an error. Please try again later.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"EUR-Lex service error: {str(e)}",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )
