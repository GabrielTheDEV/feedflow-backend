"""
Dependências de autenticação para proteger rotas
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
import logging

from app.services.supabase_service import SupabaseManager

logger = logging.getLogger(__name__)

# Security scheme para extrair Bearer token do header
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """
    Valida JWT token do Supabase e retorna dados do usuário autenticado.
    
    Args:
        credentials: Token Bearer do header Authorization
        
    Returns:
        Dados do usuário autenticado (id, email, etc)
        
    Raises:
        HTTPException 401: Token inválido ou expirado
    """
    token = credentials.credentials
    
    try:
        supabase = SupabaseManager()
        
        # Validar token e obter usuário
        response = supabase.client.auth.get_user(token)
        
        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = response.user
        logger.info("User authenticated: %s", user.id)
        
        return {
            "id": user.id,
            "email": user.email,
            "role": user.role if hasattr(user, "role") else None,
            "created_at": str(user.created_at) if hasattr(user, "created_at") else None,
        }
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error validating token: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro ao validar autenticação",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
) -> Optional[Dict[str, Any]]:
    """
    Valida JWT token se presente, retorna None se não houver token.
    Útil para rotas que aceitam autenticação opcional.
    
    Args:
        credentials: Token Bearer opcional do header Authorization
        
    Returns:
        Dados do usuário autenticado ou None
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    
    try:
        supabase = SupabaseManager()
        response = supabase.client.auth.get_user(token)
        
        if not response or not response.user:
            return None
        
        user = response.user
        logger.info("User authenticated: %s", user.id)
        
        return {
            "id": user.id,
            "email": user.email,
            "role": user.role if hasattr(user, "role") else None,
            "created_at": str(user.created_at) if hasattr(user, "created_at") else None,
        }
        
    except Exception as exc:
        logger.warning("Optional auth failed: %s", str(exc))
        return None
