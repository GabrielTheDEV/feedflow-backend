"""
Testes para o serviço de OAuth do Slack
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from httpx import Response

from app.services.slack_oauth_service import SlackOAuthService


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
            "team": {"id": "T123456", "name": "Test Team"},
            "incoming_webhook": {
                "url": "https://hooks.slack.com/services/test",
                "channel_id": "C123",
                "channel": "#feedbacks"
            },
            "scope": "incoming-webhook,chat:write",
            "bot_user_id": "U123"
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_post = AsyncMock()
            mock_post.return_value.raise_for_status = Mock()
            mock_post.return_value.json = Mock(return_value=mock_response_data)
            mock_client.return_value.__aenter__.return_value.post = mock_post
            
            result = await oauth_service.exchange_code_for_token("test_code")
            
            assert result["access_token"] == "xoxb-test-token"
            assert result["team_id"] == "T123456"
            assert result["team_name"] == "Test Team"
            assert result["webhook_url"] == "https://hooks.slack.com/services/test"
            assert result["channel_id"] == "C123"

    @pytest.mark.asyncio
    async def test_exchange_code_slack_error(self, oauth_service):
        """Deve lançar erro quando Slack retorna erro"""
        mock_response_data = {
            "ok": False,
            "error": "invalid_code"
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_post = AsyncMock()
            mock_post.return_value.raise_for_status = Mock()
            mock_post.return_value.json = Mock(return_value=mock_response_data)
            mock_client.return_value.__aenter__.return_value.post = mock_post
            
            with pytest.raises(ValueError, match="Slack OAuth failed: invalid_code"):
                await oauth_service.exchange_code_for_token("bad_code")

    def test_save_integration_success(self, oauth_service, mock_supabase_client):
        """Deve salvar integração no banco com sucesso"""
        merchant_id = "merchant_123"
        oauth_data = {
            "access_token": "xoxb-token",
            "webhook_url": "https://hooks.slack.com/test",
            "team_id": "T123",
            "team_name": "Test Team",
            "channel_id": "C123",
            "channel_name": "#feedbacks",
            "scope": "incoming-webhook",
            "bot_user_id": "U123"
        }
        
        mock_response = Mock()
        mock_response.data = [{"id": "int_123", **oauth_data, "merchant_id": merchant_id}]
        
        mock_table = Mock()
        mock_table.upsert.return_value.execute.return_value = mock_response
        mock_supabase_client.table.return_value = mock_table
        
        result = oauth_service.save_integration(merchant_id, oauth_data)
        
        assert result["access_token"] == "xoxb-token"
        assert result["merchant_id"] == merchant_id
        mock_table.upsert.assert_called_once()

    def test_save_integration_failure(self, oauth_service, mock_supabase_client):
        """Deve lançar erro se falhar ao salvar"""
        mock_response = Mock()
        mock_response.data = None
        
        mock_table = Mock()
        mock_table.upsert.return_value.execute.return_value = mock_response
        mock_supabase_client.table.return_value = mock_table
        
        with pytest.raises(ValueError, match="Failed to save Slack integration"):
            oauth_service.save_integration("merchant_123", {
                "access_token": "xoxb-token",
                "team_id": "T123"
            })

    def test_get_integration_found(self, oauth_service, mock_supabase_client):
        """Deve retornar integração se existir"""
        merchant_id = "merchant_123"
        expected_data = {
            "id": "int_123",
            "merchant_id": merchant_id,
            "access_token": "xoxb-token",
            "webhook_url": "https://hooks.slack.com/test"
        }
        
        mock_response = Mock()
        mock_response.data = expected_data
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        mock_supabase_client.table.return_value = mock_table
        
        result = oauth_service.get_integration(merchant_id)
        
        assert result == expected_data
        mock_table.select.assert_called_once_with("*")

    def test_get_integration_not_found(self, oauth_service, mock_supabase_client):
        """Deve retornar None se integração não existir"""
        mock_response = Mock()
        mock_response.data = None
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        mock_supabase_client.table.return_value = mock_table
        
        result = oauth_service.get_integration("nonexistent_merchant")
        
        assert result is None

    def test_delete_integration_success(self, oauth_service, mock_supabase_client):
        """Deve deletar integração com sucesso"""
        merchant_id = "merchant_123"
        
        mock_table = Mock()
        mock_table.delete.return_value.eq.return_value.execute.return_value = Mock()
        mock_supabase_client.table.return_value = mock_table
        
        result = oauth_service.delete_integration(merchant_id)
        
        assert result is True
        mock_table.delete.assert_called_once()

    def test_delete_integration_handles_exception(self, oauth_service, mock_supabase_client):
        """Deve retornar False se deletar falhar"""
        mock_table = Mock()
        mock_table.delete.return_value.eq.return_value.execute.side_effect = Exception("DB error")
        mock_supabase_client.table.return_value = mock_table
        
        result = oauth_service.delete_integration("merchant_123")
        
        assert result is False
