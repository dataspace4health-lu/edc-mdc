from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter()


@router.get(
    "/api/health",
    tags=["health-check"],
)
def health_check() -> Response:
    return Response(
        content="OK",
        media_type="text/plain",
        status_code=200,
    )
