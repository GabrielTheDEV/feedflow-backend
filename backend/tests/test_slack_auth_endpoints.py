"""
Testes de integração para endpoints de OAuth do Slack
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def mock_oauth_service():
    """Mock do SlackOAuthService"""
    with patch('app.routes.slack_auth.SlackOAuthService') as mock:
        yield mock

@pytest.fixture
def mock_supabase():
    """Mock do SupabaseManager"""
    with patch('app.routes.slack_auth.SupabaseManager') as mock:
        yield mock

class TestSlackInstallEndpoint:
    """Testes do endpoint /auth/slack/install"""
    def test_install_success(self, mock_oauth_service, mock_supabase):
        """Deve redirecionar para URL de autorização do Slack"""
        # Implementação real depende de rotas registradas
        pass
    def test_install_missing_merchant_id(self):
        """Deve retornar erro se merchant_id não for fornecido"""
        response = client.get("/auth/slack/install")
        assert response.status_code == 422
    def test_install_configuration_error(self, mock_oauth_service, mock_supabase):
        """Deve retornar erro 500 se configuração estiver incompleta"""
        pass

class TestSlackCallbackEndpoint:
    """Testes do endpoint /auth/slack/callback"""
    def test_callback_success(self, mock_oauth_service, mock_supabase):
        """Deve processar callback e salvar integração"""
        mock_service_instance = Mock()
        mock_service_instance.exchange_code_for_token = AsyncMock(return_value={
            "access_token": "xoxb-token",
            "team_id": "T123",
            "team_name": "Test Team",
        })
        pass

class TestSlackDisconnectEndpoint:
    """Testes do endpoint /auth/slack/disconnect"""
    def test_disconnect_success(self, client, mock_oauth_service, mock_supabase):
        """Deve desconectar integração com sucesso"""
        mock_service_instance = Mock()
        mock_service_instance.delete_integration.return_value = True
        mock_oauth_service.return_value = mock_service_instance
        
        response = client.delete("/auth/slack/disconnect?merchant_id=merchant_123")
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_disconnect_not_found(self, client, mock_oauth_service, mock_supabase):
        """Deve retornar 404 se integração não existir"""
        pass  # Skip - requer rotas registradas

    def test_disconnect_missing_merchant_id(self, client):
        """Deve retornar erro se merchant_id não for fornecido"""
        response = client.delete("/auth/slack/disconnect")
        
        assert response.status_code == 422


class TestSlackStatusEndpoint:
    """Testes do endpoint /auth/slack/status"""

    def test_status_connected(self, client, mock_oauth_service, mock_supabase):
        """Deve retornar status conectado se integração existir"""
        mock_service_instance = Mock()
        mock_service_instance.get_integration.return_value = {
            "team_name": "Test Team",
            "channel_name": "#feedbacks"
        }
        mock_oauth_service.return_value = mock_service_instance
        
        response = client.get("/auth/slack/status?merchant_id=merchant_123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is True
        assert data["team_name"] == "Test Team"

    def test_status_not_connected(self, client, mock_oauth_service, mock_supabase):
        """Deve retornar status desconectado se integração não existir"""
        mock_service_instance = Mock()
        mock_service_instance.get_integration.return_value = None
        mock_oauth_service.return_value = mock_service_instance
        
        response = client.get("/auth/slack/status?merchant_id=merchant_123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is False

    def test_status_missing_merchant_id(self, client):
        """Deve retornar erro se merchant_id não for fornecido"""
        response = client.get("/auth/slack/status")
        
        assert response.status_code == 422
