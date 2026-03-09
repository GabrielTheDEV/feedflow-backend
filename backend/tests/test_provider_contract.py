from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.models.enums.integrationsServices import IntegrationService
from app.provider.provider_factory import ProviderFactory
from app.provider.services.jira_provider import JiraProvider
from app.provider.services.slack_provider import SlackProvider
from app.provider.services.trello_provider import TrelloProvider


def test_provider_factory_returns_provider_by_string():
    assert isinstance(ProviderFactory.get_provider("slack"), SlackProvider)
    assert isinstance(ProviderFactory.get_provider("jira"), JiraProvider)
    assert isinstance(ProviderFactory.get_provider("trello"), TrelloProvider)


def test_provider_factory_returns_provider_by_enum():
    assert isinstance(ProviderFactory.get_provider(IntegrationService.slack), SlackProvider)
    assert isinstance(ProviderFactory.get_provider(IntegrationService.jira), JiraProvider)
    assert isinstance(ProviderFactory.get_provider(IntegrationService.trello), TrelloProvider)


def test_provider_factory_unsupported_service_raises():
    with pytest.raises(ValueError, match="Provider not supported"):
        ProviderFactory.get_provider("discord")


@pytest.fixture
def slack_provider():
    with patch.dict(
        "os.environ",
        {
            "SLACK_CLIENT_ID": "slack_client",
            "SLACK_CLIENT_SECRET": "slack_secret",
            "SLACK_REDIRECT_URI": "http://localhost/slack/callback",
        },
    ):
        yield SlackProvider()


@pytest.fixture
def jira_provider():
    with patch.dict(
        "os.environ",
        {
            "JIRA_CLIENT_ID": "jira_client",
            "JIRA_CLIENT_SECRET": "jira_secret",
            "JIRA_REDIRECT_URI": "http://localhost/jira/callback",
        },
    ):
        yield JiraProvider()


@pytest.fixture
def trello_provider():
    with patch.dict(
        "os.environ",
        {
            "TRELLO_API_KEY": "trello_key",
            "TRELLO_API_SECRET": "trello_secret",
        },
    ):
        yield TrelloProvider()


def test_slack_get_authorization_url(slack_provider):
    url = slack_provider.get_authorization_url(state="abc")
    assert "https://slack.com/oauth/v2/authorize" in url
    assert "state=abc" in url


@pytest.mark.asyncio
async def test_slack_send_event_requires_bot_token(slack_provider):
    with pytest.raises(ValueError, match="Bot token is required"):
        await slack_provider.send_event({}, "hello")


@pytest.mark.asyncio
async def test_slack_send_event_requires_channel(slack_provider):
    with pytest.raises(ValueError, match="Channel Id required"):
        await slack_provider.send_event({"bot_token": "xoxb-test"}, "hello")


@pytest.mark.asyncio
async def test_slack_exchange_code_success(slack_provider):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "ok": True,
        "access_token": "xoxb-token",
        "team": {"id": "T1", "name": "Workspace"},
        "app_id": "A1",
    }

    async_client = Mock()
    async_client.post = AsyncMock(return_value=mock_response)

    with patch("app.provider.services.slack_provider.httpx.AsyncClient") as mock_async_client:
        mock_async_client.return_value.__aenter__.return_value = async_client
        data = await slack_provider.exchange_code_for_token("code123")

    assert data["bot_token"] == "xoxb-token"


@pytest.mark.asyncio
async def test_jira_send_event_requires_config(jira_provider):
    with pytest.raises(ValueError, match="access_token, cloud_id and project_key are required"):
        await jira_provider.send_event({}, "hello")


@pytest.mark.asyncio
async def test_jira_send_event_calls_create_issue(jira_provider):
    jira_provider.create_issue = AsyncMock(return_value=None)
    await jira_provider.send_event(
        {
            "access_token": "token",
            "cloud_id": "cloud",
            "project_key": "PRJ",
            "title": "FeedFlow",
        },
        "evento",
    )
    jira_provider.create_issue.assert_awaited_once()


@pytest.mark.asyncio
async def test_jira_validate_connection_false_without_config(jira_provider):
    assert await jira_provider.validate_connection({}) is False


@pytest.mark.asyncio
async def test_trello_send_event_requires_config(trello_provider):
    with pytest.raises(ValueError, match="token and list_id are required"):
        await trello_provider.send_event({}, "hello")


@pytest.mark.asyncio
async def test_trello_send_event_calls_create_card(trello_provider):
    trello_provider.create_card = AsyncMock(return_value=None)
    await trello_provider.send_event(
        {
            "token": "token123",
            "list_id": "list123",
            "title": "FeedFlow",
        },
        "evento",
    )
    trello_provider.create_card.assert_awaited_once()


@pytest.mark.asyncio
async def test_trello_exchange_code_returns_token_payload(trello_provider):
    data = await trello_provider.exchange_code_for_token("token_abc")
    assert data["access_token"] == "token_abc"
