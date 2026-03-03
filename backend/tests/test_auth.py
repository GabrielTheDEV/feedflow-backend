from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from main import app
from app.utils.auth_handlers import get_current_user

client = TestClient(app)


def test_get_me_success():
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "user-123",
        "email": "test@example.com",
    }
    response = client.get("/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["id"] == "user-123"
    assert data["user"]["email"] == "test@example.com"
    app.dependency_overrides.clear()


def test_get_me_no_token():
    app.dependency_overrides.clear()
    response = client.get("/auth/me")
    assert response.status_code == 403


def test_logout_success():
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "user-123",
        "email": "test@example.com",
    }

    with patch("app.routes.auth.get_supabase_client") as mock_get_client:
        mock_client = Mock()
        mock_client.auth.sign_out.return_value = None
        mock_get_client.return_value = mock_client

        response = client.post("/auth/logout")

    assert response.status_code == 200
    assert response.json()["message"] == "Logout realizado com sucesso"
    app.dependency_overrides.clear()
