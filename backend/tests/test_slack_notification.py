"""
Testes para o serviço de notificação Slack atualizado
"""
import pytest
from unittest.mock import Mock, patch
import httpx
from app.services.integrations.slack.slack_service import send_slack_notification, build_slack_blocks

class TestBuildSlackBlocks:
    """Testes da função build_slack_blocks"""
    def test_build_blocks_basic(self):
        """Deve construir blocos básicos do Slack"""
        email = "test@example.com"
        comment = "Teste de feedback"
        payload = build_slack_blocks(email, comment, None, None)
        assert "blocks" in payload
        assert len(payload["blocks"]) >= 2
        header_block = payload["blocks"][0]
        assert header_block["type"] == "header"
        assert "Novo Feedback Recebido" in header_block["text"]["text"]
    def test_build_blocks_with_image(self):
        """Deve incluir imagem se fornecida"""
        image_url = "https://example.com/image.png"
        payload = build_slack_blocks("test@example.com", "Comment", None, image_url)
        image_blocks = [b for b in payload["blocks"] if b.get("type") == "image"]
        assert len(image_blocks) == 1
        assert image_blocks[0]["image_url"] == image_url
    def test_build_blocks_with_metadata(self):
        """Deve incluir metadados se fornecidos"""
        metadata = {
            "page_url": "https://example.com/page",
            "user_agent": "Mozilla/5.0",
            "viewport": "1920x1080"
        }
        payload = build_slack_blocks("test@example.com", "Comment", metadata, None)
        assert "blocks" in payload
        blocks_str = str(payload["blocks"])
        assert "test@example.com" in blocks_str
        assert "Comment" in blocks_str
    def test_build_blocks_with_email_button(self):
        """Deve incluir botão de resposta por email"""
        email = "customer@example.com"
        payload = build_slack_blocks(email, "Comment", None, None)
        blocks_str = str(payload["blocks"])
        assert "mailto:customer@example.com" in blocks_str

class TestSendSlackNotification:
    """Testes da função send_slack_notification"""
    def test_send_notification_with_webhook_url(self):
        """Deve enviar notificação usando webhook_url fornecido"""
        webhook_url = "https://hooks.slack.com/services/TEST123"
        with patch('httpx.post') as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            send_slack_notification(
                email="test@example.com",
                comment="Test comment",
                metadata=None,
                image_url=None,
                webhook_url=webhook_url
            )
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == webhook_url
            assert "json" in call_args[1]
    def test_send_notification_fallback_to_env(self):
        """Deve usar variável de ambiente se webhook_url não for fornecido"""
        env_webhook = "https://hooks.slack.com/services/ENV123"
        with patch.dict('os.environ', {'SLACK_WEBHOOK_URL': env_webhook}):
            with patch('httpx.post') as mock_post:
                mock_response = Mock()
                mock_response.raise_for_status = Mock()
                mock_post.return_value = mock_response
                send_slack_notification(
                    email="test@example.com",
                    comment="Test comment",
                    metadata=None,
                    image_url=None
                )
                mock_post.assert_called_once()
                call_args = mock_post.call_args
                assert call_args[0][0] == env_webhook
    def test_send_notification_no_webhook_raises_error(self):
        """Deve lançar erro se webhook_url não for fornecido e env não existir"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="webhook_url é obrigatório"):
                send_slack_notification(
                    email="test@example.com",
                    comment="Test comment",
                    metadata=None,
                    image_url=None
                )
    def test_send_notification_http_error(self):
        """Deve lançar exceção em caso de erro HTTP"""
        webhook_url = "https://hooks.slack.com/services/TEST123"
        with patch('httpx.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = "Not Found"
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "404", request=Mock(), response=mock_response
            )
            mock_post.return_value = mock_response
            with pytest.raises(httpx.HTTPStatusError):
                send_slack_notification(
                    email="test@example.com",
                    comment="Test comment",
                    metadata=None,
                    image_url=None,
                    webhook_url=webhook_url
                )
    def test_send_notification_includes_all_data(self):
        """Deve incluir todos os dados no payload"""
        webhook_url = "https://hooks.slack.com/services/TEST123"
        email = "test@example.com"
        comment = "Test feedback"
        metadata = {"page_url": "https://example.com"}
        image_url = "https://example.com/image.png"
        with patch('httpx.post') as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            send_slack_notification(
                email=email,
                comment=comment,
                metadata=metadata,
                image_url=image_url,
                webhook_url=webhook_url
            )
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            blocks_str = str(payload["blocks"])
            assert email in blocks_str
            assert comment in blocks_str
