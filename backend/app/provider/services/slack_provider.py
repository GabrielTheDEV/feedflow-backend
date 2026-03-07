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
            "scope": "incoming-webhook,chat:write",
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
            "access_token": data["access_token"],
            "webhook_url": data["incoming_webhook"]["url"],
            "team_id": data["team"]["id"],
            "channel_id": data["incoming_webhook"]["channel_id"],
        }


    async def send_event(self, config: Dict[str, Any], message: str) -> None:
        webhook_url = config.get("webhook_url")
        if not webhook_url:
            raise ValueError("webhook_url is required")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json={"text": message}
            )
            response.raise_for_status()


    async def validate_connection(self, config: Dict[str, Any]) -> bool:

        try:
            await self.send_event(config, "FeedFlow connection test")
            return True
        except (httpx.HTTPError, ValueError):
            return False