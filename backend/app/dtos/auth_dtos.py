"""
DTO de resposta de autenticação
"""
from pydantic import BaseModel

class AuthResponse(BaseModel):
    """Response de autenticação"""
    access_token: str
    token_type: str = "bearer"

