"""GET /health — liveness + configuration check."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import get_settings

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    google_configured: bool
    qdrant_configured: bool


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["ops"],
)
async def health() -> HealthResponse:
    """
    Returns 200 with service status.

    ``google_configured`` and ``qdrant_configured`` are booleans indicating
    whether the respective credentials are present in the environment.
    Secret values are NEVER included in this response.
    """
    settings = get_settings()
    return HealthResponse(
        status="ok",
        google_configured=settings.google_configured,
        qdrant_configured=settings.qdrant_configured,
    )
