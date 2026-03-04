from uuid import uuid4

from fastapi.testclient import TestClient

from main import app
from app.routes.collection_router import get_collection_service
from app.utils.auth_handlers import get_current_user_id


client = TestClient(app)


class PermissionDeniedCollectionService:
    def deactivate_collection(self, collection_id, user_id):
        raise PermissionError("You do not have access to this collection")

    def rotate_api_key(self, collection_id, user_id):
        raise PermissionError("You do not have access to this collection")


def _override_user_id():
    return uuid4()


def test_deactivate_collection_returns_403_when_not_owner():
    app.dependency_overrides[get_collection_service] = lambda: PermissionDeniedCollectionService()
    app.dependency_overrides[get_current_user_id] = _override_user_id

    collection_id = str(uuid4())
    response = client.patch(f"/collections/{collection_id}/deactivate")

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this collection"

    app.dependency_overrides.clear()


def test_rotate_key_returns_403_when_not_owner():
    app.dependency_overrides[get_collection_service] = lambda: PermissionDeniedCollectionService()
    app.dependency_overrides[get_current_user_id] = _override_user_id

    collection_id = str(uuid4())
    response = client.post(f"/collections/{collection_id}/rotate-key")

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this collection"

    app.dependency_overrides.clear()
