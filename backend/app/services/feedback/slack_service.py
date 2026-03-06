"""
Serviço de envio de notificações para o Slack
"""
from __future__ import annotations

import os
import logging
from typing import Dict, Any, Optional

import httpx

logger = logging.getLogger(__name__)

def build_slack_blocks(
    email: str,
    comment: str,
    metadata: Optional[Dict[str, Any]],
    image_url: Optional[str],
) -> Dict[str, Any]:
    metadata = metadata or {}
    fields = [
        {"type": "mrkdwn", "text": f"*E-mail:*\n{email}"},
        {"type": "mrkdwn", "text": f"*Comentário:*\n{comment}"},
    ]
    page_url = metadata.get("page_url")
    user_agent = metadata.get("user_agent")
    viewport = None
    if metadata.get("viewport_width") and metadata.get("viewport_height"):
        viewport = f"{metadata.get('viewport_width')}x{metadata.get('viewport_height')}"
    if page_url:
        fields.append({"type": "mrkdwn", "text": f"*Página:*\n{page_url}"})
    if user_agent:
        fields.append({"type": "mrkdwn", "text": f"*User Agent:*\n{user_agent}"})
    if viewport:
        fields.append({"type": "mrkdwn", "text": f"*Viewport:*\n{viewport}"})
    blocks: list[Dict[str, Any]] = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Novo Feedback Recebido", "emoji": True},
        },
    ]
    if image_url:
        blocks.append(
            {
                "type": "image",
                "image_url": image_url,
                "alt_text": "Screenshot do feedback",
            }
        )
    blocks.append(
        {
            "type": "section",
            "fields": fields,
        }
    )
    blocks.append(
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Responder via E-mail"},
                    "url": f"mailto:{email}?subject=Feedback%20Recebido",
                }
            ],
        }
    )
    return {"blocks": blocks}

def send_slack_notification(
    email: str,
    comment: str,
    metadata: Optional[Dict[str, Any]],
    image_url: Optional[str],
    webhook_url: Optional[str] = None,
) -> None:
    if not webhook_url:
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not webhook_url:
            raise ValueError("webhook_url é obrigatório ou SLACK_WEBHOOK_URL deve estar configurada")
    payload = build_slack_blocks(email, comment, metadata, image_url)
    try:
        response = httpx.post(webhook_url, json=payload, timeout=10.0)
        response.raise_for_status()
        logger.info("Notificação enviada com sucesso para o Slack")
    except httpx.HTTPStatusError as exc:
        logger.error("Erro HTTP ao enviar notificação para o Slack: %s - %s", exc.response.status_code, exc.response.text)
        raise
    except Exception as exc:
        logger.error("Erro ao enviar notificação para o Slack: %s", str(exc))
        raise
