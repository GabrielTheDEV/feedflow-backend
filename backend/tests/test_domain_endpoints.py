from datetime import datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from main import app
from app.routes.domain_router import get_service
from app.database.auth_handlers import get_current_user

client = TestClient(app)


class FakeDomainService:
    def __init__(self):
        self.domain_id = uuid4()

    def add_domain(self, collection_id, domain, user_id):
        return {
            "id": self.domain_id,
            "domain": domain,
            "verified": False,
            "active": True,
            "created_at": datetime.utcnow(),
        }

    def list_domains(self, collection_id, user_id):
        return [
            {
                "id": self.domain_id,
                "domain": "example.com",
                "verified": True,
                "active": True,
                "created_at": datetime.utcnow(),
            }
        ]

    def verify_domain(self, domain_id):
        return {
            "id": domain_id,
            "domain": "example.com",
            "verified": True,
            "active": True,
            "created_at": datetime.utcnow(),
        }

    def deactivate_domain(self, domain_id, user_id):
        return {
            "id": domain_id,
            "domain": "example.com",
            "verified": True,
            "active": False,
            "created_at": datetime.utcnow(),
        }


def _override_user_id():
    return uuid4()


def test_domain_endpoints_flow():
    app.dependency_overrides[get_service] = lambda: FakeDomainService()
    app.dependency_overrides[get_current_user] = _override_user_id
    collection_id = str(uuid4())
    domain_id = str(uuid4())

    create_response = client.post(f"/domains/{collection_id}", json={"domain": "example.com"})
    assert create_response.status_code == 200
    assert create_response.json()["domain"] == "example.com"

    list_response = client.get(f"/domains/{collection_id}")
    assert list_response.status_code == 200
    assert isinstance(list_response.json(), list)

    verify_response = client.patch(f"/domains/{domain_id}/verify")
    assert verify_response.status_code == 200
    assert verify_response.json()["verified"] is True

    deactivate_response = client.patch(f"/domains/{domain_id}/deactivate")
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["active"] is False

    app.dependency_overrides.clear()
