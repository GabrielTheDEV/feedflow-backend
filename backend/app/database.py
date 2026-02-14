"""
Configuração do banco de dados SQLAlchemy
Gerencia conexões e sessões do PostgreSQL
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração da URL do banco de dados
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://feedflow_user:feedflow_pass@localhost:5432/feedflow_db"
)

# Engine do SQLAlchemy com pool de conexões
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verifica conexões antes de usar
    echo=False  # Mude para True para debug SQL
)

# SessionLocal factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obter sessão do banco de dados
    Garante que a sessão seja fechada após o uso
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa o banco de dados criando todas as tabelas
    """
    from app.models.models import Base
    Base.metadata.create_all(bind=engine)
