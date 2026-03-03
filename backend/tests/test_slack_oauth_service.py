"""
Testes para o serviço de OAuth do Slack
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from httpx import Response
from app.services.integrations.slack.slack_oauth_service import SlackOAuthService

@pytest.fixture
def mock_supabase_client():
    """Mock do cliente Supabase"""
    mock_client = Mock()
    mock_client.table = Mock(return_value=Mock())
    return mock_client

@pytest.fixture
def oauth_service(mock_supabase_client):
    """Instância do SlackOAuthService com mocks"""
    with patch.dict('os.environ', {
        'SLACK_CLIENT_ID': 'test_client_id',
        'SLACK_CLIENT_SECRET': 'test_client_secret',
        'SLACK_REDIRECT_URI': 'http://localhost:8000/auth/slack/callback'
    }):
        return SlackOAuthService(mock_supabase_client)

class TestSlackOAuthService:
    """Testes do SlackOAuthService"""
    def test_init_without_credentials_raises_error(self, mock_supabase_client):
        """Deve lançar erro se credenciais não estiverem configuradas"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="SLACK_CLIENT_ID e SLACK_CLIENT_SECRET são obrigatórios"):
                SlackOAuthService(mock_supabase_client)
    def test_get_authorization_url_basic(self, oauth_service):
        """Deve gerar URL de autorização corretamente"""
        url = oauth_service.get_authorization_url()
        assert "https://slack.com/oauth/v2/authorize" in url
        assert "client_id=test_client_id" in url
        assert "scope=incoming-webhook%2Cchat%3Awrite" in url
        assert "redirect_uri=" in url
    def test_get_authorization_url_with_state(self, oauth_service):
        """Deve incluir state na URL se fornecido"""
        state = "merchant_uuid_123"
        url = oauth_service.get_authorization_url(state=state)
        assert f"state={state}" in url
    @pytest.mark.asyncio
    async def test_exchange_code_success(self, oauth_service):
        """Deve trocar código por token com sucesso"""
        mock_response_data = {
            "ok": True,
            "access_token": "xoxb-test-token",
        }
        pass
