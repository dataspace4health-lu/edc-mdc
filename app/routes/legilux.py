from fastapi import Depends, status, APIRouter
from typing import List
from services.legilux.legislation import LegiluxApplicableLegislationService
from schemas.legilux import LegiluxLegislation
from models.identity_context import IdentityContext
from routes.auth import validate_and_retrieve_identity_context

router = APIRouter()


@router.get(
    "/api/v1/legilux/legislation/search",
    response_model=List[LegiluxLegislation],
    tags=["legilux"],
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
) -> List[LegiluxLegislation]:
    """
    Search for legislation in LegiLux.

    Args:
        query: Search term to filter legislation by title, description, or URI

    Returns:
        List of matching legislation with id, label, description, and link (limited to 10 results)
    """
    service = LegiluxApplicableLegislationService()
    return await service.list_legislation(filter=query)
