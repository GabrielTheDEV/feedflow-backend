from fastapi import APIRouter, HTTPException, status, Depends
import logging
from app.database.auth_handlers import get_current_user
from app.docs.swagger.auth_docs import ME_DOCS


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])



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
