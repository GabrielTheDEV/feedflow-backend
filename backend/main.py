"""
FeedFlow - API Principal
Sistema de captura de feedbacks visuais para lojas Shopify
"""
from typing import Optional, Dict, Any
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status, Header, Form
from pydantic import EmailStr
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import logging
import json
import os
from contextlib import asynccontextmanager

from app.database import get_db, init_db
from app.schemas.schemas import FeedbackResponse, ErrorResponse, SuccessResponse, FeedbackCreate, FeedbackMetadata
from app.services.feedback_service import FeedbackService
from app.services.supabase_service import SupabaseManager
from app.services.slack_service import send_slack_notification

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação
    Inicializa o banco de dados na startup
    """
    logger.info("Inicializando FeedFlow API...")
    use_supabase = os.getenv("USE_SUPABASE") == "true" or bool(os.getenv("SUPABASE_URL"))
    if use_supabase:
        logger.info("Supabase habilitado. Pulando init_db do PostgreSQL local.")
    else:
        init_db()
        logger.info("Banco de dados inicializado com sucesso!")
    yield
    logger.info("Encerrando FeedFlow API...")


# Inicialização do FastAPI
app = FastAPI(
    title="FeedFlow API",
    description="API para captura e gerenciamento de feedbacks visuais de lojas Shopify",
    version="1.0.0",
    lifespan=lifespan
)

# Configuração do CORS para aceitar requisições de domínios externos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Servir arquivos estáticos (screenshots)
uploads_dir = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Registrar rotas de autenticação Slack
from app.routes import slack_auth
app.include_router(slack_auth.router)


# ==================== Exception Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException) -> JSONResponse:
    """Handler global para HTTPException"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            status_code=exc.status_code
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception) -> JSONResponse:
    """Handler global para exceções não tratadas"""
    logger.error(f"Erro não tratado: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Erro interno do servidor",
            detail=str(exc) if os.getenv("DEBUG") == "true" else None,
            status_code=500
        ).model_dump()
    )


# ==================== Rotas ====================

@app.get("/", tags=["Health"])
async def root() -> Dict[str, str]:
    """
    Endpoint raiz para health check
    """
    return {
        "status": "online",
        "service": "FeedFlow API",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """
    Endpoint de health check
    """
    return {"status": "healthy"}


@app.post(
    "/submit-feedback",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Feedback criado com sucesso"},
        400: {"model": ErrorResponse, "description": "Requisição inválida"},
        422: {"model": ErrorResponse, "description": "Dados inválidos"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    },
    tags=["Feedback"]
)
async def submit_feedback_supabase(
    screenshot: Optional[UploadFile] = File(None, description="Screenshot capturado pelo widget"),
    customer_email: EmailStr = Form(..., description="Email do cliente"),
    comment: Optional[str] = Form(None, description="Comentário do cliente"),
    customer_message: Optional[str] = Form(None, description="Mensagem do cliente"),
    metadata: Optional[str] = Form(None, description="Metadados técnicos em JSON"),
    merchant_id: Optional[str] = Form(None, description="UUID do merchant (lojista)"),
) -> SuccessResponse:
    """
    Endpoint para submissão de feedbacks usando Supabase e Slack
    """
    feedback_comment = (comment or customer_message or "").strip()
    if not feedback_comment:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Comentário é obrigatório"
        )

    metadata_obj: Optional[Dict[str, Any]] = None
    if metadata:
        try:
            metadata_obj = json.loads(metadata)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Metadados inválidos"
            )

    supabase = SupabaseManager()
    image_url: Optional[str] = None

    if screenshot:
        try:
            image_bytes = await screenshot.read()
            image_url = supabase.upload_image(
                image_bytes=image_bytes,
                content_type=screenshot.content_type or "image/png",
            )
        except Exception as exc:
            logger.error("Erro ao fazer upload da imagem: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao fazer upload da imagem"
            )

    try:
        feedback = supabase.save_feedback(
            email=customer_email,
            comment=feedback_comment,
            metadata=metadata_obj,
            image_url=image_url,
        )
    except Exception as exc:
        logger.error("Erro ao salvar feedback no Supabase: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao salvar feedback no banco"
        )

    try:
        # Buscar webhook específico do merchant se fornecido
        webhook_url = None
        if merchant_id:
            from app.services.slack_oauth_service import SlackOAuthService
            oauth_service = SlackOAuthService(supabase.client)
            integration = oauth_service.get_integration(merchant_id)
            if integration:
                webhook_url = integration.get("webhook_url")
                logger.info("Using merchant-specific webhook for %s", merchant_id)
        
        send_slack_notification(
            email=customer_email,
            comment=feedback_comment,
            metadata=metadata_obj,
            image_url=image_url,
            webhook_url=webhook_url,
        )
    except Exception as exc:
        logger.error("Erro ao enviar notificação para o Slack: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao enviar notificação para o Slack"
        )

    return SuccessResponse(
        message="Feedback recebido com sucesso!",
        data={
            "feedback_id": feedback.get("id"),
            "image_url": image_url,
        }
    )


@app.post(
    "/api/v1/submit-feedback",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Feedback criado com sucesso"},
        400: {"model": ErrorResponse, "description": "Requisição inválida"},
        401: {"model": ErrorResponse, "description": "Token de API inválido"},
        413: {"model": ErrorResponse, "description": "Arquivo muito grande"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    },
    tags=["Feedback"]
)
async def submit_feedback(
    screenshot: UploadFile = File(..., description="Screenshot capturado pelo widget"),
    api_token: Optional[str] = Form(None, description="Token de autenticação do merchant"),
    customer_email: Optional[str] = Form(None, description="Email do cliente (opcional)"),
    customer_message: Optional[str] = Form(None, description="Mensagem do cliente (opcional)"),
    metadata: Optional[str] = Form(None, description="Metadados técnicos em JSON"),
    x_api_token: Optional[str] = Header(None, description="Token de autenticação via header"),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """
    Endpoint principal para submissão de feedbacks visuais
    
    Aceita multipart/form-data com:
    - screenshot: Arquivo de imagem (obrigatório)
    - api_token: Token do merchant (obrigatório - via form ou header)
    - customer_email: Email do cliente (opcional)
    - customer_message: Mensagem do cliente (opcional)
    - metadata: JSON com informações técnicas (opcional)
    
    Implementa multi-tenancy através do api_token
    """
    
    # 1. Obter token (prioridade: header > form)
    token = x_api_token or api_token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de API não fornecido. Envie via header 'X-API-Token' ou form 'api_token'"
        )

    # 2. Validar token e obter merchant (Multi-tenancy)
    merchant = FeedbackService.validate_api_token(db, token)

    # 3. Validar arquivo
    FeedbackService.validate_file(screenshot)

    # 4. Salvar screenshot
    screenshot_path = await FeedbackService.save_screenshot(screenshot, merchant.id)

    # 5. Processar metadados
    metadata_obj = None
    if metadata:
        try:
            metadata_dict = json.loads(metadata)
            metadata_obj = FeedbackMetadata(**metadata_dict)
        except json.JSONDecodeError:
            logger.warning("Metadados JSON inválidos recebidos")
        except Exception as e:
            logger.warning(f"Erro ao processar metadados: {str(e)}")

    # 6. Criar objeto de feedback
    feedback_data = FeedbackCreate(
        customer_email=customer_email,
        customer_message=customer_message,
        metadata=metadata_obj
    )

    # 7. Salvar feedback no banco
    feedback = FeedbackService.create_feedback(db, merchant, screenshot_path, feedback_data)

    # 8. Retornar resposta de sucesso
    return SuccessResponse(
        message="Feedback recebido com sucesso!",
        data={
            "feedback_id": feedback.id,
            "status": feedback.status,
            "created_at": feedback.created_at.isoformat()
        }
    )


@app.get(
    "/api/v1/feedbacks/{feedback_id}",
    response_model=FeedbackResponse,
    responses={
        200: {"description": "Feedback encontrado"},
        401: {"model": ErrorResponse, "description": "Token de API inválido"},
        404: {"model": ErrorResponse, "description": "Feedback não encontrado"}
    },
    tags=["Feedback"]
)
async def get_feedback(
    feedback_id: int,
    x_api_token: Optional[str] = Header(None),
    api_token: Optional[str] = None,
    db: Session = Depends(get_db)
) -> FeedbackResponse:
    """
    Busca um feedback específico por ID
    Implementa multi-tenancy (apenas o merchant dono pode acessar)
    """
    # Validar token
    token = x_api_token or api_token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de API não fornecido"
        )

    merchant = FeedbackService.validate_api_token(db, token)

    # Buscar feedback
    feedback = FeedbackService.get_feedback_by_id(db, feedback_id, merchant.id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback não encontrado"
        )

    return FeedbackResponse.model_validate(feedback)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
