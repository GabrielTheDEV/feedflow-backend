"""
Rotas de health check e status
"""

from fastapi import APIRouter
from app.docs.swagger.health_docs import ROOT_STATUS_DOCS, HEALTH_CHECK_DOCS

router = APIRouter(prefix="/api/v1", tags=["Health"])

@router.get("/", tags=["Health"], **ROOT_STATUS_DOCS)
async def root():
    """
    Endpoint raiz: status do serviço FeedFlow.
    """
    return {
        "status": "online",
        "service": "FeedFlow API",
        "version": "1.0.0"
    }

