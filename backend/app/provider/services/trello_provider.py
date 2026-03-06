import os
import httpx
from typing import Dict, Any, Optional

from app.provider.base_provider import IntegrationProvider


class TrelloProvider(IntegrationProvider):

    def __init__(self):
        self.api_key = os.getenv("TRELLO_API_KEY")
        self.api_secret = os.getenv("TRELLO_API_SECRET")

    def get_authorization_url(self, state: Optional[str] = None) -> str:

        return (
            "https://trello.com/1/authorize"
            f"?key={self.api_key}"
            "&scope=read,write"
            "&expiration=never"
            "&response_type=token"
        )


    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        if not code:
            raise ValueError("Token is required")

        return {"access_token": code}



    async def create_card(
        self,
        token: str,
        list_id: str,
        title: str,
        description: str,
    ):

        url = "https://api.trello.com/1/cards"

        params = {
            "key": self.api_key,
            "token": token,
            "idList": list_id,
            "name": title,
            "desc": description,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, params=params)
            response.raise_for_status()



    async def send_event(self, config: Dict[str, Any], message: str) -> None:
        token = config.get("token")
        list_id = config.get("list_id")
        title = config.get("title", "FeedFlow Event")

        if not token or not list_id:
            raise ValueError("token and list_id are required")

        await self.create_card(
            token=token,
            list_id=list_id,
            title=title,
            description=message,
        )


    async def validate_connection(self, config: Dict[str, Any]) -> bool:
        token = config.get("token")
        if not token:
            return False

        url = "https://api.trello.com/1/members/me"

        params = {
            "key": self.api_key,
            "token": token,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)

        return response.status_code == 200