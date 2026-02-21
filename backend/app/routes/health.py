"""
Rotas de health check e status
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["Health"])

@router.get("/", tags=["Health"])
async def root():
    """
    Endpoint raiz: status do serviço FeedFlow.
    """
    return {
        "status": "online",
        "service": "FeedFlow API",
        "version": "1.0.0"
    }

@router.get("/health", tags=["Health"])
async def health_check():
    """
    Health check simples.
    """
    return {"status": "healthy"}
