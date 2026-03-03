"""
Rotas de autenticação OAuth 2.0 com Slack
"""

from fastapi import APIRouter, HTTPException, Query, status, Depends
from fastapi.responses import RedirectResponse
from typing import Optional, Dict, Any
import logging
from app.database.config import get_supabase_client
from app.services.integrations.slack.slack_oauth_service import SlackOAuthService
from app.utils.auth_handlers import get_current_user_optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/slack", tags=["Slack OAuth"])


@router.get("/install")
async def slack_install(
    merchant_id: Optional[str] = Query(None, description="UUID do merchant (opcional se autenticado)"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Inicia o fluxo OAuth redirecionando para a página de autorização do Slack.
    Pode ser usado de duas formas:
    1. Com autenticação (Bearer token) - usa user_id do token
    2. Sem autenticação - requer merchant_id como query param

    Query Parameters:
        merchant_id: UUID do merchant (obrigatório se não autenticado)
    """
    try:
        user_id = current_user["id"] if current_user else merchant_id
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="merchant_id é obrigatório quando não autenticado"
            )

        supabase = get_supabase_client()
        oauth_service = SlackOAuthService(supabase)

        auth_url = oauth_service.get_authorization_url(state=user_id)
        logger.info("Redirecting user %s to Slack OAuth", user_id)
        return RedirectResponse(url=auth_url)

    except ValueError as exc:
        logger.error("Configuration error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuração do Slack OAuth está incompleta"
        )
    except Exception as exc:
        logger.error("Slack install error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao iniciar OAuth com Slack"
        )


@router.get("/callback")
async def slack_callback(
    code: str = Query(..., description="Código de autorização retornado pelo Slack"),
    state: str = Query(None, description="State contendo merchant_id"),
    error: str = Query(None, description="Erro retornado pelo Slack se autorização falhou"),
):
    """
    Callback do OAuth do Slack. Troca o código pelo access_token e salva no banco.
    Query Parameters:
        code: Código de autorização temporário
        state: merchant_id passado no /install
        error: Mensagem de erro se o usuário negou acesso
    """
    if error:
        logger.warning("Slack OAuth denied: %s", error)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Autorização negada pelo usuário: {error}"
        )

    if not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parâmetro 'state' (merchant_id) é obrigatório"
        )

    merchant_id = state

    try:
        supabase = get_supabase_client()
        oauth_service = SlackOAuthService(supabase)

        oauth_data = await oauth_service.exchange_code_for_token(code)
        integration = oauth_service.save_integration(merchant_id, oauth_data)

        logger.info(
            "Slack integration completed for merchant %s - Team: %s, Channel: %s",
            merchant_id,
            integration.get("team_name"),
            integration.get("channel_name"),
        )

        team_id = oauth_data.get("team", {}).get("id")
        slack_url = f"https://app.slack.com/client/{team_id}" if team_id else "https://slack.com/signin"

        return RedirectResponse(url=slack_url, status_code=status.HTTP_303_SEE_OTHER)

    except ValueError as exc:
        logger.error("OAuth exchange error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    except Exception as exc:
        logger.error("Error in /callback: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao completar integração com Slack"
        )


@router.delete("/disconnect")
async def slack_disconnect(merchant_id: str = Query(..., description="UUID do merchant")):
    """
    Desconecta a integração do Slack para um merchant.
    """
    try:
        supabase = get_supabase_client()
        oauth_service = SlackOAuthService(supabase)

        success = oauth_service.delete_integration(merchant_id)

        if success:
            return {"status": "success", "message": "Slack desconectado com sucesso"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integração não encontrada"
            )

    except Exception as exc:
        logger.error("Error disconnecting Slack: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao desconectar Slack"
        )


@router.get("/status")
async def slack_status(merchant_id: str = Query(..., description="UUID do merchant")):
    """
    Verifica se o merchant tem integração ativa com Slack.
    """
    try:
        supabase = get_supabase_client()
        oauth_service = SlackOAuthService(supabase)

        integration = oauth_service.get_integration(merchant_id)

        if integration:
            return {
                "connected": True,
                "team_name": integration.get("team_name"),
                "channel_name": integration.get("channel_name"),
            }
        else:
            return {"connected": False}

    except Exception as exc:
        logger.error("Error checking Slack status: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao verificar status do Slack"
        )
