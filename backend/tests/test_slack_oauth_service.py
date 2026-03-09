from unittest.mock import Mock, AsyncMock, patch

import pytest

from app.utils.slack_oauth_service import SlackOAuthService


@pytest.fixture
def mock_supabase_client():
    return Mock()


@pytest.fixture
def oauth_service(mock_supabase_client):
    with patch.dict(
        "os.environ",
        {
            "SLACK_CLIENT_ID": "test_client_id",
            "SLACK_CLIENT_SECRET": "test_client_secret",
            "SLACK_REDIRECT_URI": "http://localhost:8000/auth/slack/callback",
        },
    ):
        return SlackOAuthService(mock_supabase_client)


def test_init_without_credentials_raises_error(mock_supabase_client):
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="SLACK_CLIENT_ID e SLACK_CLIENT_SECRET são obrigatórios"):
            SlackOAuthService(mock_supabase_client)


def test_get_authorization_url_basic(oauth_service):
    url = oauth_service.get_authorization_url()
    assert "https://slack.com/oauth/v2/authorize" in url
    assert "client_id=test_client_id" in url
    assert "scope=chat%3Awrite%2Cchannels%3Aread%2Cchannels%3Ajoin%2Cgroups%3Aread" in url


def test_get_authorization_url_with_state(oauth_service):
    url = oauth_service.get_authorization_url(state="merchant_123")
    assert "state=merchant_123" in url


@pytest.mark.asyncio
async def test_exchange_code_success(oauth_service):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "ok": True,
        "access_token": "xoxb-token",
        "team": {"id": "T123", "name": "Team"},
        "bot_user_id": "B123",
    }

    async_client = Mock()
    async_client.post = AsyncMock(return_value=mock_response)

    with patch("app.services.integrations.slack.slack_oauth_service.httpx.AsyncClient") as mock_async_client:
        mock_async_client.return_value.__aenter__.return_value = async_client
        data = await oauth_service.exchange_code_for_token("code123")

    assert data["bot_token"] == "xoxb-token"
    assert data["team_id"] == "T123"


def test_save_integration_success(oauth_service, mock_supabase_client):
    mock_exec = Mock()
    mock_exec.execute.return_value = Mock(data=[{"merchant_id": "m1"}])
    mock_exec.upsert.return_value = mock_exec
    mock_supabase_client.table.return_value = mock_exec

    result = oauth_service.save_integration(
        "m1",
        {
            "bot_token": "x",
            "team_id": "T1",
            "team_name": "Team",
            "channel_id": "C1",
            "channel_name": "#g",
            "scope": "chat:write",
            "bot_user_id": "B1",
        },
    )

    assert result["merchant_id"] == "m1"


def test_get_integration_none(oauth_service, mock_supabase_client):
    mock_chain = Mock()
    mock_chain.select.return_value = mock_chain
    mock_chain.eq.return_value = mock_chain
    mock_chain.single.return_value = mock_chain
    mock_chain.execute.return_value = Mock(data=None)
    mock_supabase_client.table.return_value = mock_chain

    result = oauth_service.get_integration("m1")
    assert result is None
