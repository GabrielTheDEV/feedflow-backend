import os
import httpx
from typing import Dict, Any, Optional

from app.provider.base_provider import IntegrationProvider


class JiraProvider(IntegrationProvider):

    def __init__(self):
        self.client_id = os.getenv("JIRA_CLIENT_ID")
        self.client_secret = os.getenv("JIRA_CLIENT_SECRET")
        self.redirect_uri = os.getenv("JIRA_REDIRECT_URI")

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        state_value = state or "feedflow"

        return (
            "https://auth.atlassian.com/authorize"
            "?audience=api.atlassian.com"
            "&prompt=consent"
            "&scope=write:jira-work read:jira-work"
            f"&client_id={self.client_id}"
            "&response_type=code"
            f"&redirect_uri={self.redirect_uri}"
            f"&state={state_value}"
        )


    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        if not code:
            raise ValueError("OAuth code is required")

        async with httpx.AsyncClient() as client:

            response = await client.post(
                "https://auth.atlassian.com/oauth/token",
                json={
                    "grant_type": "authorization_code",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
            )
            response.raise_for_status()

        return response.json()


    async def create_issue(
        self,
        access_token: str,
        cloud_id: str,
        project_key: str,
        title: str,
        description: str,
    ):

        url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/issue"

        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": title,
                "description": description,
                "issuetype": {"name": "Bug"},
            }
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()


    async def send_event(self, config: Dict[str, Any], message: str) -> None:
        access_token = config.get("access_token")
        cloud_id = config.get("cloud_id")
        project_key = config.get("project_key")
        title = config.get("title", "FeedFlow Event")

        if not access_token or not cloud_id or not project_key:
            raise ValueError("access_token, cloud_id and project_key are required")

        await self.create_issue(
            access_token=access_token,
            cloud_id=cloud_id,
            project_key=project_key,
            title=title,
            description=message,
        )


    async def validate_connection(self, config: Dict[str, Any]) -> bool:
        access_token = config.get("access_token")
        cloud_id = config.get("cloud_id")
        if not access_token or not cloud_id:
            return False

        url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/myself"

        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        return response.status_code == 200