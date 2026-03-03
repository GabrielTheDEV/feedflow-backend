from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator


"""
DTOs (Schemas) do FeedFlow usando Pydantic
Define contratos de entrada e saída da API
"""


# DTO de resposta de autenticação
class AuthResponse(BaseModel):
    """Response de autenticação"""
    access_token: str
    token_type: str = "bearer"


# DTO de configuração do widget para customização visual
class WidgetConfig(BaseModel):
    buttonText: Optional[str] = "Reportar Problema"
    buttonPosition: Optional[str] = "bottom-right"
    primaryColor: Optional[str] = "#4F46E5"


# DTO de requisição para geração do widget
class WidgetGenerateRequest(BaseModel):
    domain: str
    widgetConfig: WidgetConfig


# DTO para metadados adicionais do feedback
class FeedbackMetadata(BaseModel):
    """Schema para metadados do feedback"""
    page_url: Optional[str] = None
    user_agent: Optional[str] = None
    viewport_width: Optional[int] = None
    viewport_height: Optional[int] = None
    screen_width: Optional[int] = None
    screen_height: Optional[int] = None
    timestamp: Optional[str] = None
    browser_language: Optional[str] = None
    referrer: Optional[str] = None


# DTO para criação de um novo feedback
class FeedbackCreate(BaseModel):
    """Schema para criação de Feedback"""
    customer_email: EmailStr
    customer_message: str = Field(..., max_length=550, min_length=1)
    metadata: Optional[FeedbackMetadata] = None


# DTO de resposta detalhada de feedback
class FeedbackResponse(BaseModel):
    """Schema de resposta para Feedback"""
    id: int
    merchant_id: int
    screenshot_path: str
    metadata_json: Optional[Dict[str, Any]] = None
    customer_email: Optional[str] = None
    customer_message: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True



# DTO padrão para respostas de erro da API
class ErrorResponse(BaseModel):
    """Schema padrão para respostas de erro"""
    error: str
    detail: Optional[str] = None
    status_code: int


# DTO padrão para respostas de sucesso da API
class SuccessResponse(BaseModel):
    """Schema padrão para respostas de sucesso"""
    message: str
    data: Optional[Dict[str, Any]] = None


# DTO base para domínio autorizado
class DomainBase(BaseModel):
    domain: str = Field(..., description="Domínio autorizado")


# DTO para criação de domínio autorizado
class DomainCreate(DomainBase):
    pass
    

# DTO de resposta detalhada de domínio autorizado
class DomainResponse(DomainBase):
    id: int
    token: str
    is_active: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
