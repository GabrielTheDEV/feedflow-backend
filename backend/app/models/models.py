"""
Modelos de dados do FeedFlow
Representam as entidades do banco de dados usando SQLAlchemy ORM
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Merchant(Base):
    """
    Entidade Merchant - Representa um lojista/tenant no sistema
    Cada lojista tem sua própria loja Shopify e token de API único
    """
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    shop_url = Column(String(255), unique=True, nullable=False, index=True)
    api_token = Column(String(255), unique=True, nullable=False, index=True)
    domain = Column(String(255), unique=False, nullable=False, index=True)  # Domínio autorizado para o token
    widget_config = Column(JSON, nullable=True)  # Configurações do widget
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(Integer, default=1, nullable=False)  # 1 = ativo, 0 = inativo

    # Relacionamento one-to-many com Feedback
    feedbacks = relationship("Feedback", back_populates="merchant", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Merchant(id={self.id}, shop_url='{self.shop_url}')>"


class Feedback(Base):
    """
    Entidade Feedback - Armazena feedbacks visuais capturados dos clientes
    Contém screenshot, metadados técnicos e informações do browser
    """
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)
    screenshot_path = Column(String(500), nullable=False)
    metadata_json = Column(JSON, nullable=True)  # Armazena user agent, URL, viewport, etc
    customer_email = Column(String(255), nullable=False, index=True)
    customer_message = Column(String(550), nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, reviewed, resolved
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relacionamento many-to-one com Merchant
    merchant = relationship("Merchant", back_populates="feedbacks")

    def __repr__(self) -> str:
        return f"<Feedback(id={self.id}, merchant_id={self.merchant_id}, status='{self.status}')>"
