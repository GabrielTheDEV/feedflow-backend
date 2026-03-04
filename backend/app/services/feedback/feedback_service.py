"""
Service Layer para Feedback
Contém a lógica de negócio para processamento de feedbacks
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status
from datetime import datetime
import os
import uuid
import logging

from app.models.models import Feedback, Merchant
from app.dtos.schemas import FeedbackCreate, FeedbackResponse

logger = logging.getLogger(__name__)

# Diretório para armazenar screenshots
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads/screenshots")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Tipos de arquivo permitidos
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class FeedbackService:
    """
    Service para gerenciar operações de Feedback
    Segue o padrão Service Layer do Spring Boot
    """

    @staticmethod
    def validate_api_token(db: Session, api_token: str) -> Merchant:
        """
        Valida o token da API e retorna o Merchant associado
        
        Args:
            db: Sessão do banco de dados
            api_token: Token de autenticação do merchant
            
        Returns:
            Merchant: Objeto do lojista autenticado
            
        Raises:
            HTTPException: Se token inválido ou merchant inativo
        """
        merchant = db.query(Merchant).filter(
            Merchant.api_token == api_token,
            Merchant.is_active == 1
        ).first()

        if not merchant:
            logger.warning(f"Tentativa de acesso com token inválido: {api_token[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de API inválido ou merchant inativo"
            )

        return merchant

    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """
        Valida o arquivo de upload (tipo e tamanho)
        
        Args:
            file: Arquivo enviado pelo cliente
            
        Raises:
            HTTPException: Se arquivo inválido
        """
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome do arquivo não fornecido"
            )

        # Verifica extensão
        extension = file.filename.split(".")[-1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de arquivo não permitido. Use: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Verifica content type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O arquivo deve ser uma imagem"
            )

    @staticmethod
    async def save_screenshot(file: UploadFile, merchant_id: int) -> str:
        """
        Salva o screenshot no sistema de arquivos
        
        Args:
            file: Arquivo de imagem
            merchant_id: ID do merchant
            
        Returns:
            str: Caminho relativo do arquivo salvo
            
        Raises:
            HTTPException: Se erro ao salvar arquivo
        """
        try:
            # Gera nome único para o arquivo
            extension = file.filename.split(".")[-1].lower()
            unique_filename = f"{merchant_id}_{uuid.uuid4().hex}_{int(datetime.utcnow().timestamp())}.{extension}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)

            # Salva o arquivo em chunks para evitar problemas de memória
            with open(file_path, "wb") as buffer:
                chunk_size = 1024 * 1024  # 1MB chunks
                while True:
                    chunk = await file.read(chunk_size)
                    if not chunk:
                        break
                    
                    # Verifica tamanho máximo
                    if buffer.tell() > MAX_FILE_SIZE:
                        os.remove(file_path)
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"Arquivo muito grande. Máximo: {MAX_FILE_SIZE / 1024 / 1024}MB"
                        )
                    
                    buffer.write(chunk)

            logger.info(f"Screenshot salvo com sucesso: {file_path}")
            return f"/uploads/screenshots/{unique_filename}"

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao salvar screenshot: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao processar o arquivo"
            )

    @staticmethod
    def create_feedback(
        db: Session,
        merchant: Merchant,
        screenshot_path: str,
        feedback_data: FeedbackCreate
    ) -> Feedback:
        """
        Cria um novo registro de feedback no banco de dados
        
        Args:
            db: Sessão do banco de dados
            merchant: Merchant autenticado
            screenshot_path: Caminho do screenshot salvo
            feedback_data: Dados do feedback
            
        Returns:
            Feedback: Objeto do feedback criado
            
        Raises:
            HTTPException: Se erro ao criar feedback
        """
        try:
            # Converte metadados para dict
            metadata_dict = None
            if feedback_data.metadata:
                metadata_dict = feedback_data.metadata.model_dump(exclude_none=True)

            # Cria o feedback
            feedback = Feedback(
                merchant_id=merchant.id,
                screenshot_path=screenshot_path,
                metadata_json=metadata_dict,
                customer_email=feedback_data.customer_email,
                customer_message=feedback_data.customer_message,
                status="pending"
            )

            db.add(feedback)
            db.commit()
            db.refresh(feedback)

            logger.info(f"Feedback criado: ID={feedback.id}, Merchant={merchant.id}")
            return feedback

        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao criar feedback: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao salvar feedback no banco de dados"
            )

    @staticmethod
    def get_feedback_by_id(db: Session, feedback_id: int, merchant_id: int) -> Optional[Feedback]:
        """
        Busca um feedback por ID garantindo multi-tenancy
        
        Args:
            db: Sessão do banco de dados
            feedback_id: ID do feedback
            merchant_id: ID do merchant (para garantir acesso apenas aos próprios dados)
            
        Returns:
            Optional[Feedback]: Feedback encontrado ou None
        """
        return db.query(Feedback).filter(
            Feedback.id == feedback_id,
            Feedback.merchant_id == merchant_id
        ).first()
