"""
Testes para rotas de autenticação
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from main import app

client = TestClient(app)

@pytest.fixture
def mock_supabase_register():
    """Mock para register do Supabase"""
    with patch("app.routes.auth.SupabaseManager") as mock_manager:
        mock_client = Mock()
        mock_auth = Mock()
        # Mock successful register
        mock_user = Mock()
        mock_user.id = "user-123-uuid"
        mock_user.email = "test@example.com"
        mock_user.created_at = "2024-01-01T00:00:00Z"
        mock_session = Mock()
        mock_session.access_token = "fake-access-token"
        mock_response = Mock()
        mock_response.user = mock_user
        mock_response.session = mock_session
        mock_auth.sign_up.return_value = mock_response
        mock_client.auth = mock_auth
        mock_manager.return_value.client = mock_client
        yield mock_auth

@pytest.fixture
def mock_supabase_login():
    """Mock para login do Supabase"""
    with patch("app.routes.auth.SupabaseManager") as mock_manager:
        mock_client = Mock()
        mock_auth = Mock()
        # Mock successful login
        mock_user = Mock()
        mock_user.id = "user-123-uuid"
        mock_user.email = "test@example.com"
        mock_session = Mock()
        mock_session.access_token = "fake-access-token"
        mock_response = Mock()
        mock_response.user = mock_user
        mock_response.session = mock_session
        mock_auth.sign_in_with_password.return_value = mock_response
        mock_client.auth = mock_auth
        mock_manager.return_value.client = mock_client
        yield mock_auth

@pytest.fixture
def mock_supabase_get_user():
    """Mock para get_user do Supabase"""
    with patch("app.dependencies.auth.SupabaseManager") as mock_manager:
        mock_client = Mock()
        mock_auth = Mock()
        # Mock user validation
        mock_user = Mock()
        mock_user.id = "user-123-uuid"
        mock_user.email = "test@example.com"
        mock_user.role = "authenticated"
        mock_user.created_at = "2024-01-01T00:00:00Z"
        mock_response = Mock()
        mock_response.user = mock_user
        mock_auth.get_user.return_value = mock_response
        mock_client.auth = mock_auth
        mock_manager.return_value.client = mock_client
        yield mock_auth

class TestRegister:
    """Testes para /auth/register"""
    
    def test_register_success(self, mock_supabase_register):
        """Deve criar conta com sucesso"""
        response = client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securePassword123"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["access_token"] == "fake-access-token"
        assert data["token_type"] == "bearer"
        assert data["user"]["id"] == "user-123-uuid"
        assert data["user"]["email"] == "test@example.com"
        
        mock_supabase_register.sign_up.assert_called_once()
    
    def test_register_invalid_email(self):
        """Deve rejeitar email inválido"""
        response = client.post(
            "/auth/register",
            json={
                "email": "invalid-email",
                "password": "securePassword123"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_register_missing_password(self):
        """Deve rejeitar requisição sem senha"""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com"
            }
        )
        
        assert response.status_code == 422
    
    def test_register_existing_user(self):
        """Deve retornar erro para email já cadastrado"""
        with patch("app.routes.auth.SupabaseManager") as mock_manager:
            mock_client = Mock()
            mock_auth = Mock()
            mock_auth.sign_up.side_effect = Exception("User already registered")
            mock_client.auth = mock_auth
            mock_manager.return_value.client = mock_client
            
            response = client.post(
                "/auth/register",
                json={
                    "email": "existing@example.com",
                    "password": "password123"
                }
            )
            
            assert response.status_code == 400
            assert "já cadastrado" in response.json()["error"]


class TestLogin:
    """Testes para /auth/login"""
    
    def test_login_success(self, mock_supabase_login):
        """Deve fazer login com sucesso"""
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "correctPassword123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "fake-access-token"
        assert data["token_type"] == "bearer"
        assert data["user"]["id"] == "user-123-uuid"
        
        mock_supabase_login.sign_in_with_password.assert_called_once()
    
    def test_login_wrong_password(self):
        """Deve rejeitar senha incorreta"""
        with patch("app.routes.auth.SupabaseManager") as mock_manager:
            mock_client = Mock()
            mock_auth = Mock()
            mock_auth.sign_in_with_password.side_effect = Exception("Invalid credentials")
            mock_client.auth = mock_auth
            mock_manager.return_value.client = mock_client
            
            response = client.post(
                "/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "wrongPassword"
                }
            )
            
            assert response.status_code == 401
            assert "incorretos" in response.json()["error"]
    
    def test_login_nonexistent_user(self):
        """Deve rejeitar usuário inexistente"""
        with patch("app.dependencies.auth.SupabaseManager") as mock_manager:
            mock_client = Mock()
            mock_auth = Mock()
            
            mock_response = Mock()
            mock_response.user = None
            mock_response.session = None
            
            mock_auth.sign_in_with_password.return_value = mock_response
            mock_client.auth = mock_auth
            mock_manager.return_value.client = mock_client
            
            response = client.post(
                "/auth/login",
                json={
                    "email": "nonexistent@example.com",
                    "password": "password123"
                }
            )
            
            assert response.status_code == 401


class TestProtectedRoutes:
    """Testes para rotas protegidas"""
    
    def test_get_me_success(self, mock_supabase_get_user):
        """Deve retornar dados do usuário autenticado"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer fake-valid-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["id"] == "user-123-uuid"
        assert data["user"]["email"] == "test@example.com"
    
    def test_get_me_no_token(self):
        """Deve rejeitar requisição sem token"""
        response = client.get("/auth/me")
        
        assert response.status_code == 403  # No credentials
    
    def test_get_me_invalid_token(self):
        """Deve rejeitar token inválido"""
        with patch("app.routes.auth.SupabaseManager") as mock_manager:
            mock_client = Mock()
            mock_auth = Mock()
            
            mock_response = Mock()
            mock_response.user = None
            
            mock_auth.get_user.return_value = mock_response
            mock_client.auth = mock_auth
            mock_manager.return_value.client = mock_client
            
            response = client.get(
                "/auth/me",
                headers={"Authorization": "Bearer invalid-token"}
            )
            
            assert response.status_code == 401
    
    def test_logout_success(self, mock_supabase_get_user):
        """Deve fazer logout com sucesso"""
        with patch("app.routes.auth.SupabaseManager") as mock_manager:
            mock_client = Mock()
            mock_auth = Mock()
            
            # Mock get_user for authentication
            mock_user = Mock()
            mock_user.id = "user-123-uuid"
            mock_user.email = "test@example.com"
            mock_user.role = "authenticated"
            
            mock_response = Mock()
            mock_response.user = mock_user
            
            mock_auth.get_user.return_value = mock_response
            mock_auth.sign_out.return_value = None
            mock_client.auth = mock_auth
            mock_manager.return_value.client = mock_client
            
            response = client.post(
                "/auth/logout",
                headers={"Authorization": "Bearer fake-valid-token"}
            )
            
            assert response.status_code == 200
            assert "sucesso" in response.json()["message"]
            mock_auth.sign_out.assert_called_once()
