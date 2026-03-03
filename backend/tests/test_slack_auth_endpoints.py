from unittest.mock import Mock, AsyncMock, patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_install_missing_merchant_id():
    response = client.get("/auth/slack/install")
    assert response.status_code == 500


def test_install_success_with_merchant_id():
    with patch("app.routes.slack_auth.get_supabase_client") as mock_get_client, patch(
        "app.routes.slack_auth.SlackOAuthService"
    ) as mock_service:
        mock_get_client.return_value = Mock()
        mock_service.return_value.get_authorization_url.return_value = "https://slack.com/oauth/v2/authorize?x=1"

        response = client.get("/auth/slack/install?merchant_id=merchant_123", allow_redirects=False)

    assert response.status_code in (302, 307)


def test_callback_missing_state():
    response = client.get("/auth/slack/callback?code=abc")
    assert response.status_code == 400


def test_callback_success_redirect():
    with patch("app.routes.slack_auth.get_supabase_client") as mock_get_client, patch(
        "app.routes.slack_auth.SlackOAuthService"
    ) as mock_service:
        mock_get_client.return_value = Mock()
        service = Mock()
        service.exchange_code_for_token = AsyncMock(
            return_value={
                "team": {"id": "T123", "name": "My Team"},
                "access_token": "xoxb-test",
            }
        )
        service.save_integration.return_value = {"team_name": "My Team", "channel_name": "#general"}
        mock_service.return_value = service

        response = client.get("/auth/slack/callback?code=abc&state=merchant_123", allow_redirects=False)

    assert response.status_code == 303


def test_disconnect_missing_merchant_id():
    response = client.delete("/auth/slack/disconnect")
    assert response.status_code == 422


def test_disconnect_success():
    with patch("app.routes.slack_auth.get_supabase_client") as mock_get_client, patch(
        "app.routes.slack_auth.SlackOAuthService"
    ) as mock_service:
        mock_get_client.return_value = Mock()
        mock_service.return_value.delete_integration.return_value = True

        response = client.delete("/auth/slack/disconnect?merchant_id=merchant_123")

    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_status_not_connected():
    with patch("app.routes.slack_auth.get_supabase_client") as mock_get_client, patch(
        "app.routes.slack_auth.SlackOAuthService"
    ) as mock_service:
        mock_get_client.return_value = Mock()
        mock_service.return_value.get_integration.return_value = None

        response = client.get("/auth/slack/status?merchant_id=merchant_123")

    assert response.status_code == 200
    assert response.json()["connected"] is False
