"""
Rotas de feedbacks visuais
"""

from fastapi import APIRouter, File, UploadFile, Form, Header, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
import json
from app.services.feedback_service import FeedbackService
from app.dtos.schemas import FeedbackCreate, FeedbackMetadata, SuccessResponse, ErrorResponse, FeedbackResponse
from app.database.config import get_db
from app.docs.swagger.feedback_docs import SUBMIT_FEEDBACK_DOCS, GET_FEEDBACK_DOCS

router = APIRouter(prefix="/api/v1", tags=["Feedback"])

@router.post(
    "/submit-feedback",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    **SUBMIT_FEEDBACK_DOCS,
)
async def submit_feedback(
    screenshot: UploadFile = File(None, description="Screenshot capturado pelo widget"),
    api_token: Optional[str] = Form(None, description="Token de autenticação do merchant"),
    customer_email: Optional[str] = Form(None, description="Email do cliente (opcional)"),
    customer_message: Optional[str] = Form(None, description="Mensagem do cliente (opcional)"),
    metadata: Optional[str] = Form(None, description="Metadados técnicos em JSON"),
    x_api_token: Optional[str] = Header(None, description="Token de autenticação via header"),
    request: Request = None,
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """
    Submete um feedback visual, validando token e domínio autorizado.
    """
    token = x_api_token or api_token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de API não fornecido. Envie via header 'X-API-Token' ou form 'api_token'"
        )
    merchant = FeedbackService.validate_api_token(db, token)
    domain_header = request.headers.get('Origin') or request.headers.get('Referer') if request else None
    if domain_header:
        import urllib.parse
        parsed = urllib.parse.urlparse(domain_header)
        domain_from_header = parsed.hostname
        if domain_from_header and merchant.domain:
            if domain_from_header.lower() != merchant.domain.lower():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Domínio não autorizado para este token. Permitido: {merchant.domain}, recebido: {domain_from_header}"
                )
    FeedbackService.validate_file(screenshot)
    screenshot_path = await FeedbackService.save_screenshot(screenshot, merchant.id)
    metadata_obj = None
    if metadata:
        try:
            metadata_dict = json.loads(metadata)
            metadata_obj = FeedbackMetadata(**metadata_dict)
        except Exception:
            metadata_obj = None
    feedback_data = FeedbackCreate(
        customer_email=customer_email,
        customer_message=customer_message,
        metadata=metadata_obj
    )
    feedback = FeedbackService.create_feedback(db, merchant, screenshot_path, feedback_data)
    return SuccessResponse(
        message="Feedback recebido com sucesso!",
        data={
            "feedback_id": feedback.id,
            "status": feedback.status,
            "created_at": feedback.created_at.isoformat()
        }
    )

@router.get("/feedbacks/{feedback_id}", response_model=FeedbackResponse, **GET_FEEDBACK_DOCS)
async def get_feedback(
    feedback_id: int,
    x_api_token: Optional[str] = Header(None),
    api_token: Optional[str] = None,
    db: Session = Depends(get_db)
) -> FeedbackResponse:
    """
    Busca um feedback específico por ID, validando token e multi-tenancy.
    """
    token = x_api_token or api_token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de API não fornecido"
        )
    merchant = FeedbackService.validate_api_token(db, token)
    feedback = FeedbackService.get_feedback_by_id(db, feedback_id, merchant.id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback não encontrado"
        )
    return FeedbackResponse.model_validate(feedback)
