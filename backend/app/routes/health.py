from fastapi import APIRouter, HTTPException, status, Depends
from app.docs.swagger.health_docs import ROOT_STATUS_DOCS, HEALTH_CHECK_DOCS
from app.docs.swagger.auth_docs import ME_DOCS
import logging
from app.database.auth_handlers import get_current_user


logger = logging.getLogger(__name__)



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


@router.get("/me", **ME_DOCS)
async def get_me(user_id: str = Depends(get_current_user)):
    try:
        return {"user_id": user_id}
    except Exception as exc:
        logger.error("Get me error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter informações do usuário"
        )