import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Heuristic Evaluation API",
        "version": "1.0.0"
    }

@router.get("/ready")
async def readiness_check():
    return {
        "status": "ready",
        "timestamp": "2024-01-01T00:00:00Z"
    }
