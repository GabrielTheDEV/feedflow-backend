"""
Serviço de autenticação com Supabase
Senhas são automaticamente criptografadas (bcrypt) pelo Supabase
"""
import logging
import asyncio
from typing import Dict, Any
from supabase import Client

logger = logging.getLogger(__name__)


class AuthService:
    """Serviço de autenticação com Supabase Auth"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def _retry_with_backoff(self, func, max_retries=3):
        """Retry com exponential backoff para rate limit"""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as exc:
                error_str = str(exc).lower()
                
                # Se for rate limit e ainda tem tentativas, aguarda e tenta novamente
                if "rate" in error_str and attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 2  # 2s, 4s, 8s (antes era 0.5s, 1s, 2s)
                    logger.warning(f"Rate limit detected, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
                
                # Se não for rate limit ou esgotou tentativas, relança
                raise exc
        
        raise ValueError("Muitas tentativas. Tente novamente em alguns minutos.")
    
    async def register(self, email: str, password: str) -> Dict[str, Any]:
        """
        Cria nova conta.
        Senha é automaticamente criptografada pelo Supabase (bcrypt).
        
        Args:
            email: Email do novo usuário
            password: Senha do novo usuário
            
        Returns:
            Dados do usuário + token de acesso
        """
        email = email.strip().lower()
        
        try:
            response = await self._retry_with_backoff(
                lambda: self.supabase.auth.sign_up({
                    "email": email,
                    "password": password
                })
            )
            
            if not response or not response.user:
                logger.error(f"Register failed for: {email[:5]}***")
                raise ValueError("Erro ao criar conta")
            
            logger.info(f"User registration successful: {response.user.id}")
            
            return {
                "access_token": response.session.access_token if response.session else "",
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "created_at": str(response.user.created_at) if hasattr(response.user, "created_at") else None,
                }
            }
            
        except Exception as exc:
            error_str = str(exc).lower()
            logger.error(f"Register error: {error_str}")
            
            if "already registered" in error_str or "exists" in error_str:
                raise ValueError("Email já cadastrado")
            elif "rate" in error_str:
                raise ValueError("Muitas tentativas. Tente novamente em alguns minutos.")
            
            raise ValueError("Erro ao criar conta")
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Faz login.
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            
        Returns:
            Token de acesso + dados do usuário
        """
        email = email.strip().lower()
        
        try:
            response = await self._retry_with_backoff(
                lambda: self.supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
            )
            
            if not response or not response.user or not response.session:
                logger.warning(f"Failed login: {email[:5]}***")
                raise ValueError("Email ou senha incorretos")
            
            logger.info(f"Login successful: {response.user.id}")
            
            return {
                "access_token": response.session.access_token,
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                }
            }
            
        except Exception as exc:
            logger.error(f"Login error: {str(exc)}")
            raise ValueError("Email ou senha incorretos")
