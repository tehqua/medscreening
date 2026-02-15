"""
Health check router.
"""

from fastapi import APIRouter, Depends
from datetime import datetime
import logging

from ..config import get_settings
from ..database import get_db
from ..schemas import HealthResponse
from ..services.orchestrator_service import check_ollama_status

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(
    settings = Depends(get_settings),
    db = Depends(get_db)
):
    """
    Health check endpoint.
    
    Returns status of all system components.
    """
    # Check database
    try:
        await db.client.admin.command('ping')
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    # Check Ollama
    ollama_status = await check_ollama_status(settings.OLLAMA_BASE_URL)
    
    return HealthResponse(
        status="healthy" if db_status == "healthy" and ollama_status == "healthy" else "degraded",
        version=settings.VERSION,
        timestamp=datetime.utcnow().isoformat(),
        orchestrator_status="ready",
        database_status=db_status,
        ollama_status=ollama_status
    )