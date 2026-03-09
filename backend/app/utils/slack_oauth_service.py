from __future__ import annotations

import os
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlencode

import httpx
from supabase import Client

logger = logging.getLogger(__name__)


"""
Serviço de integração OAuth 2.0 com Slack
"""

class SlackOAuthService:
    """Gerencia autenticação OAuth 2.0 do Slack"""

    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.client_id = os.getenv("SLACK_CLIENT_ID")
        self.client_secret = os.getenv("SLACK_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SLACK_REDIRECT_URI", "http://localhost:8000/auth/slack/callback")

        if not self.client_id or not self.client_secret:
            raise ValueError("SLACK_CLIENT_ID e SLACK_CLIENT_SECRET são obrigatórios")



    def get_authorization_url(self, state: Optional[str] = None) -> str:
        params = {
            "client_id": self.client_id,
            "scope": "chat:write,channels:read,channels:join,groups:read",
            "redirect_uri": self.redirect_uri,
        }
        if state:
            params["state"] = state
        return f"https://slack.com/oauth/v2/authorize?{urlencode(params)}"



    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://slack.com/api/oauth.v2.access",
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "redirect_uri": self.redirect_uri,
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                if not data.get("ok"):
                    error = data.get("error", "unknown_error")
                    logger.error("Slack OAuth error: %s", error)
                    raise ValueError(f"Slack OAuth failed: {error}")
                return {
                    "bot_token": data["access_token"],
                    "team_id": data["team"]["id"],
                    "team_name": data["team"]["name"],
                    "channel_id": data.get("channel_id"),
                    "channel_name": data.get("channel_name"),
                    "scope": data.get("scope", ""),
                    "bot_user_id": data.get("bot_user_id"),
                }
            except httpx.HTTPError as exc:
                logger.error("HTTP error during Slack OAuth: %s", str(exc))
                raise
            except Exception as exc:
                logger.error("Unexpected error during Slack OAuth: %s", str(exc))
                raise



    def save_integration(self, merchant_id: str, oauth_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            payload = {
                "merchant_id": merchant_id,
                "access_token": oauth_data["bot_token"],
                "team_id": oauth_data["team_id"],
                "team_name": oauth_data.get("team_name"),
                "channel_id": oauth_data.get("channel_id"),
                "channel_name": oauth_data.get("channel_name"),
                "scope": oauth_data.get("scope"),
                "bot_user_id": oauth_data.get("bot_user_id"),
            }
            response = (
                self.supabase.table("slack_integrations")
                .upsert(payload, on_conflict="merchant_id")
                .execute()
            )
            if response.data:
                logger.info("Slack integration saved for merchant %s", merchant_id)
                return response.data[0]
            else:
                raise ValueError("Failed to save Slack integration")
        except Exception as exc:
            logger.error("Error saving Slack integration: %s", str(exc))
            raise



    def get_integration(self, merchant_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = (
                self.supabase.table("slack_integrations")
                .select("*")
                .eq("merchant_id", merchant_id)
                .single()
                .execute()
            )
            return response.data if response.data else None
        except Exception as exc:
            logger.error("Error fetching Slack integration: %s", str(exc))
            return None



    def delete_integration(self, merchant_id: str) -> bool:
        try:
            self.supabase.table("slack_integrations").delete().eq("merchant_id", merchant_id).execute()
            logger.info("Slack integration deleted for merchant %s", merchant_id)
            return True
        except Exception as exc:
            logger.error("Error deleting Slack integration: %s", str(exc))
            return False
