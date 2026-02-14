"""
Schemas (DTOs) do FeedFlow usando Pydantic
Define contratos de entrada e saída da API
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator


class MerchantBase(BaseModel):
    """Schema base para Merchant"""
    shop_url: str = Field(..., min_length=1, max_length=255, description="URL da loja Shopify")


class MerchantCreate(MerchantBase):
    """Schema para criação de Merchant"""
    pass


class MerchantResponse(MerchantBase):
    """Schema de resposta para Merchant"""
    id: int
    api_token: str
    is_active: int
    created_at: datetime

    class Config:
        from_attributes = True  # Suporta ORM models


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


class FeedbackCreate(BaseModel):
    """Schema para criação de Feedback"""
    customer_email: EmailStr
    customer_message: str = Field(..., max_length=550, min_length=1)
    metadata: Optional[FeedbackMetadata] = None


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


class ErrorResponse(BaseModel):
    """Schema padrão para respostas de erro"""
    error: str
    detail: Optional[str] = None
    status_code: int


class SuccessResponse(BaseModel):
    """Schema padrão para respostas de sucesso"""
    message: str
    data: Optional[Dict[str, Any]] = None
