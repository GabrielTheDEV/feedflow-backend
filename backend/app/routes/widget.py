"""
Rotas de geração de widget
"""

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.schemas.schemas import WidgetGenerateRequest, WidgetConfig
from app.models.models import Merchant
from app.database import get_db
import secrets

router = APIRouter(prefix="/api/v1", tags=["Widget"])

@router.post("/generate-widget", status_code=status.HTTP_201_CREATED)
async def generate_widget(
    request: WidgetGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Gera um widget script e token para o merchant, salva configs e domínio.
    """
    api_token = secrets.token_urlsafe(32)
    merchant = Merchant(
        shop_url=f"https://{request.domain}",
        api_token=api_token,
        domain=request.domain,
        widget_config=request.widgetConfig.dict()
    )
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    widget_script = (
        f"<script src='https://seu-backend.com/static/widget.js'></script>"
        f"<script>FeedFlowWidget.init({{ apiToken: '{api_token}', buttonText: '{request.widgetConfig.buttonText}', "
        f"buttonPosition: '{request.widgetConfig.buttonPosition}', primaryColor: '{request.widgetConfig.primaryColor}' }});</script>"
    )
    return {
        "apiToken": api_token,
        "widgetScript": widget_script
    }
