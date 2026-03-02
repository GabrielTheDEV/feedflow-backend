import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def created_domain():
    data = {"domain": "example.com"}
    response = client.post("/domains/", json=data)
    assert response.status_code == 201
    return response.json()

def test_list_domains_empty():
    response = client.get("/domains/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_domain(created_domain):
    assert created_domain["domain"] == "example.com"
    assert "token" in created_domain

def test_list_domains_after_create(created_domain):
    response = client.get("/domains/")
    assert response.status_code == 200
    domains = response.json()
    assert any(d["domain"] == "example.com" for d in domains)

def test_regenerate_token(created_domain):
    domain_id = created_domain["id"]
    response = client.post(f"/domains/{domain_id}/regenerate-token")
    assert response.status_code == 200
    assert "token" in response.json()

def test_delete_domain(created_domain):
    domain_id = created_domain["id"]
    response = client.delete(f"/domains/{domain_id}")
    assert response.status_code == 204

def test_list_domains_empty_again():
    response = client.get("/domains/")
    assert response.status_code == 200
    assert all(d["domain"] != "example.com" for d in response.json())
