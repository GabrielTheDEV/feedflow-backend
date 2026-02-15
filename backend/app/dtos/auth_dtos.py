"""
DTOs de autenticação com validações básicas
Senhas são criptografadas pelo Supabase (bcrypt)
"""
from pydantic import BaseModel, EmailStr, Field, validator


class RegisterRequest(BaseModel):
    """Request para criar nova conta"""
    email: EmailStr = Field(..., description="Email válido")
    password: str = Field(
        ..., 
        min_length=6,
        max_length=128,
        description="Senha (será criptografada)"
    )
    
    @validator('email', pre=True)
    def email_lowercase(cls, v):
        return v.strip().lower() if v else v
    
    @validator('password', pre=True)
    def password_strip(cls, v):
        return v.strip() if v else v


class LoginRequest(BaseModel):
    """Request para fazer login"""
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., min_length=1, max_length=128)
    
    @validator('email', pre=True)
    def email_lowercase(cls, v):
        return v.strip().lower() if v else v
    
    @validator('password', pre=True)
    def password_strip(cls, v):
        return v.strip() if v else v


class UserResponse(BaseModel):
    """Dados do usuário"""
    id: str
    email: str
    created_at: str = None


class AuthResponse(BaseModel):
    """Response de autenticação"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

