from uuid import uuid4

from fastapi.testclient import TestClient

from main import app
from app.routes.report_router import get_widget_validator, get_dispatcher


client = TestClient(app)


class SuccessWidgetValidator:
    def validate(self, api_key, origin):
        return type("Collection", (), {"id": uuid4()})()


class MissingApiKeyWidgetValidator:
    def validate(self, api_key, origin):
        raise ValueError("api_key is required")


class InvalidApiKeyWidgetValidator:
    def validate(self, api_key, origin):
        raise ValueError("Collection not found")


class DomainDeniedWidgetValidator:
    def validate(self, api_key, origin):
        raise PermissionError("Domain not allowed")


class SuccessDispatcher:
    async def dispatch(self, collection_id, report_body, origin):
        return 1


class NoIntegrationDispatcher:
    async def dispatch(self, collection_id, report_body, origin):
        raise LookupError("No active integrations for this collection")


class BrokenDispatcher:
    async def dispatch(self, collection_id, report_body, origin):
        raise RuntimeError("provider down")


def test_send_report_returns_204_when_valid():
    app.dependency_overrides[get_widget_validator] = lambda: SuccessWidgetValidator()
    app.dependency_overrides[get_dispatcher] = lambda: SuccessDispatcher()

    response = client.post(
        "/reports/?api_key=valid-key",
        headers={"origin": "https://example.com"},
        json={"title": "bug", "message": "something broke"},
    )

    assert response.status_code == 204

    app.dependency_overrides.clear()


def test_send_report_returns_400_when_missing_api_key():
    app.dependency_overrides[get_widget_validator] = lambda: MissingApiKeyWidgetValidator()
    app.dependency_overrides[get_dispatcher] = lambda: SuccessDispatcher()

    response = client.post(
        "/reports/?api_key=",
        headers={"origin": "https://example.com"},
        json={"title": "bug"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "api_key is required"

    app.dependency_overrides.clear()


def test_send_report_returns_403_when_api_key_invalid():
    app.dependency_overrides[get_widget_validator] = lambda: InvalidApiKeyWidgetValidator()
    app.dependency_overrides[get_dispatcher] = lambda: SuccessDispatcher()

    response = client.post(
        "/reports/?api_key=invalid",
        headers={"origin": "https://example.com"},
        json={"title": "bug"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API key"

    app.dependency_overrides.clear()


def test_send_report_returns_403_when_domain_not_allowed():
    app.dependency_overrides[get_widget_validator] = lambda: DomainDeniedWidgetValidator()
    app.dependency_overrides[get_dispatcher] = lambda: SuccessDispatcher()

    response = client.post(
        "/reports/?api_key=valid-key",
        headers={"origin": "https://blocked.example.com"},
        json={"title": "bug"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Domain not allowed"

    app.dependency_overrides.clear()


def test_send_report_returns_404_when_no_active_integrations():
    app.dependency_overrides[get_widget_validator] = lambda: SuccessWidgetValidator()
    app.dependency_overrides[get_dispatcher] = lambda: NoIntegrationDispatcher()

    response = client.post(
        "/reports/?api_key=valid-key",
        headers={"origin": "https://example.com"},
        json={"title": "bug"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "No active integrations for this collection"

    app.dependency_overrides.clear()


def test_send_report_returns_500_when_unexpected_error():
    app.dependency_overrides[get_widget_validator] = lambda: SuccessWidgetValidator()
    app.dependency_overrides[get_dispatcher] = lambda: BrokenDispatcher()

    response = client.post(
        "/reports/?api_key=valid-key",
        headers={"origin": "https://example.com"},
        json={"title": "bug"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"

    app.dependency_overrides.clear()
