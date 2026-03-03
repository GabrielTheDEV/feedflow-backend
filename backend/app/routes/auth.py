"""
Rotas de autenticação com Supabase Auth
Senhas são criptografadas automaticamente (bcrypt) pelo Supabase
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any
import logging
from app.services.superbase.supabase_service import SupabaseManager
from app.dependencies.auth_handlers import get_current_user
from app.dtos.schemas import AuthResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Fazer logout (invalidar token)
    Requer autenticação via Bearer token
    """
    try:
        supabase = SupabaseManager()
        supabase.client.auth.sign_out()
        logger.info("User logged out: %s", current_user["id"])
        return {"message": "Logout realizado com sucesso"}
    except Exception as exc:
        logger.error("Logout error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao fazer logout"
        )

@router.get("/me")
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Obter dados do usuário autenticado
    Requer autenticação via Bearer token
    """
    return {
        "user": current_user
    }
