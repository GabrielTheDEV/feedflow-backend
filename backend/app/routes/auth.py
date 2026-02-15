"""
Rotas de autenticação com Supabase Auth
Senhas são criptografadas automaticamente (bcrypt) pelo Supabase
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any
import logging

from app.services.supabase_service import SupabaseManager
from app.services.auth_security_service import AuthService
from app.dependencies.auth import get_current_user
from app.dtos.auth_dtos import RegisterRequest, LoginRequest, AuthResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """
    Criar nova conta de usuário
    
    - Senha será criptografada automaticamente (bcrypt) pelo Supabase
    - Email deve ser válido
    
    Args:
        request: RegisterRequest com email e senha
        
    Returns:
        Token de acesso e dados do usuário criado
    """
    try:
        supabase = SupabaseManager()
        auth_service = AuthService(supabase.client)
        
        result = await auth_service.register(request.email, request.password)
        
        return AuthResponse(
            access_token=result["access_token"],
            user=result["user"]
        )
        
    except ValueError as exc:
        error_msg = str(exc)
        status_code = status.HTTP_400_BAD_REQUEST
        
        if "muitas tentativas" in error_msg.lower():
            status_code = status.HTTP_429_TOO_MANY_REQUESTS
        
        logger.warning(f"Register validation error: {error_msg}")
        raise HTTPException(
            status_code=status_code,
            detail=error_msg
        )
        
    except Exception as exc:
        logger.error(f"Register error: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar conta"
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Fazer login com email e senha
    
    Args:
        request: LoginRequest com email e senha
        
    Returns:
        Token de acesso e dados do usuário
    """
    try:
        supabase = SupabaseManager()
        auth_service = AuthService(supabase.client)
        
        result = await auth_service.login(request.email, request.password)
        
        logger.info(f"Successful login for user: {result['user']['id']}")
        
        return AuthResponse(
            access_token=result["access_token"],
            user=result["user"]
        )
        
    except ValueError as exc:
        logger.warning(f"Login error: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
        
    except Exception as exc:
        logger.error(f"Login error: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao fazer login"
        )


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
