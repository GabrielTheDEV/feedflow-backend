import os
import httpx
from urllib.parse import urlencode
from typing import Optional, Dict, Any

from app.provider.base_provider import IntegrationProvider


class SlackProvider(IntegrationProvider):

    def __init__(self):
        self.provider_id = os.getenv("SLACK_CLIENT_ID")
        self.provider_secret = os.getenv("SLACK_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SLACK_REDIRECT_URI")




    def get_authorization_url(self, state: Optional[str] = None) -> str:

        params = {
            "client_id": self.provider_id,
            "scope": "chat:write,channels:read,channels:join,groups:read",
            "redirect_uri": self.redirect_uri,
        }

        if state:
            params["state"] = state

        return f"https://slack.com/oauth/v2/authorize?{urlencode(params)}"


    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        if not code:
            raise ValueError("OAuth code is required")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://slack.com/api/oauth.v2.access",
                data={
                    "client_id": self.provider_id,
                    "client_secret": self.provider_secret,
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
            )
            response.raise_for_status()

        data = response.json()

        if not data.get("ok"):
            raise ValueError(f"Slack OAuth failed: {data.get('error', 'unknown_error')}")

        return {
            "bot_token": data["access_token"],
            "team_id": data["team"]["id"],
            "team_name": data["team"].get("name"),
            "app_id": data["app_id"],
            "bot_user_id": data.get("bot_user_id"),
            "scope": data.get("scope", ""),
        }


    async def send_event(self, config: Dict[str, Any], message: str) -> None:
        token = config.get("bot_token") or config.get("access_token")
        channel = config.get("channel_id")

        if not token :
            raise ValueError("Bot token is required")
       
        if not channel:
            raise ValueError("Channel Id required")


        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://slack.com/api/chat.postMessage",
                headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
                },
                json={
                    "channel": channel,
                    "text": message
                }
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("ok"):
                raise ValueError(f"Slack postMessage failed: {data.get('error', 'unknown_error')}")


    async def validate_connection(self, config: Dict[str, Any]) -> bool:
        try:
            token = config.get("bot_token") or config.get("access_token")

            if not token:
                raise ValueError("Bot token is required")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://slack.com/api/auth.test",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                )
                response.raise_for_status()
                data = response.json()

                if not data.get("ok"):
                    return False

            return True
        except (httpx.HTTPError, ValueError):
            return False