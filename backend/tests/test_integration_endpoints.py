from uuid import uuid4

from fastapi.testclient import TestClient

from app.models.enums.integrationsServices import IntegrationService as IntegrationServiceEnum
from app.routes.integration_router import get_integration_service
from app.database.auth_handlers import get_current_user
from main import app


client = TestClient(app)


def _override_user_id():
    return uuid4()


class SuccessIntegrationService:
    def create_integration(self, collection_id, user_id, service, config=None):
        return {
            "id": str(uuid4()),
            "service": service,
            "active": True,
        }

    def list_by_collection(self, collection_id, user_id):
        return [
            {
                "id": str(uuid4()),
                "service": IntegrationServiceEnum.slack,
                "active": True,
            }
        ]

    def delete_integration(self, integration_id, collection_id, user_id):
        return None


class PermissionDeniedIntegrationService:
    def create_integration(self, collection_id, user_id, service, config=None):
        raise PermissionError("You do not have access to this collection")

    def list_by_collection(self, collection_id, user_id):
        raise PermissionError("You do not have access to this collection")

    def delete_integration(self, integration_id, collection_id, user_id):
        raise PermissionError("You do not have access to this integration")


class NotFoundIntegrationService:
    def create_integration(self, collection_id, user_id, service, config=None):
        raise ValueError("Collection not found")

    def list_by_collection(self, collection_id, user_id):
        raise ValueError("Collection not found")

    def delete_integration(self, integration_id, collection_id, user_id):
        raise ValueError("Integration not found")


def test_create_integration_returns_201_when_valid():
    app.dependency_overrides[get_integration_service] = lambda: SuccessIntegrationService()
    app.dependency_overrides[get_current_user] = _override_user_id

    collection_id = str(uuid4())
    response = client.post(
        f"/integrations/{collection_id}",
        json={"service": "slack", "config": {}},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["service"] == "slack"
    assert body["active"] is True

    app.dependency_overrides.clear()


def test_create_integration_returns_403_when_not_owner():
    app.dependency_overrides[get_integration_service] = lambda: PermissionDeniedIntegrationService()
    app.dependency_overrides[get_current_user] = _override_user_id

    collection_id = str(uuid4())
    response = client.post(
        f"/integrations/{collection_id}",
        json={"service": "slack", "config": {}},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this collection"

    app.dependency_overrides.clear()


def test_create_integration_returns_404_when_collection_missing():
    app.dependency_overrides[get_integration_service] = lambda: NotFoundIntegrationService()
    app.dependency_overrides[get_current_user] = _override_user_id

    collection_id = str(uuid4())
    response = client.post(
        f"/integrations/{collection_id}",
        json={"service": "slack", "config": {}},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Collection not found"

    app.dependency_overrides.clear()


def test_list_integrations_returns_403_when_not_owner():
    app.dependency_overrides[get_integration_service] = lambda: PermissionDeniedIntegrationService()
    app.dependency_overrides[get_current_user] = _override_user_id

    collection_id = str(uuid4())
    response = client.get(f"/integrations/{collection_id}")

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this collection"

    app.dependency_overrides.clear()


def test_delete_integration_returns_404_when_missing():
    app.dependency_overrides[get_integration_service] = lambda: NotFoundIntegrationService()
    app.dependency_overrides[get_current_user] = _override_user_id

    collection_id = str(uuid4())
    integration_id = str(uuid4())
    response = client.delete(f"/integrations/{collection_id}/{integration_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Integration not found"

    app.dependency_overrides.clear()
