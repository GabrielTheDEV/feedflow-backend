"""
Rotas de geração de widget
"""

from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from app.dtos.schemas import WidgetGenerateRequest, WidgetConfig
from app.database.config import get_db
from app.docs.swagger.widget_docs import GENERATE_WIDGET_DOCS


router = APIRouter(prefix="/api/v1", tags=["Widget"])

@router.post("/generate-widget", status_code=status.HTTP_201_CREATED, **GENERATE_WIDGET_DOCS)
async def generate_widget(
    request: WidgetGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Gera um widget script e token para o merchant, salva configs e domínio.
    """
    
    # Checa se domínio já existe
    if service.domain_exists(request.domain):
        raise HTTPException(status_code=400, detail="Domínio já cadastrado")
    merchant, widget_script = service.create_widget(
        domain=request.domain,
        widget_config=request.widgetConfig
    )
    return {
        "apiToken": merchant.api_token,
        "widgetScript": widget_script
    }
