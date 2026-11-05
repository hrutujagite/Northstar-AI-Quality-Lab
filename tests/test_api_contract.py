"""API schema, status-code and input-boundary tests."""
import pytest
from framework.assertions import assert_chat_payload


def test_health_contract(api_client):
    response = api_client.health()
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "northstar-ai-support", "version": "2.0.0"}


def test_knowledge_endpoint_exposes_document_metadata(api_client):
    response = api_client.knowledge()
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()["documents"]}
    assert {"returns", "shipping", "warranty", "support", "payments", "products"} <= ids


def test_chat_response_obeys_contract(api_client):
    response = api_client.ask("What is the return window?")
    assert response.status_code == 200
    assert_chat_payload(response.json())


@pytest.mark.parametrize("body", [{}, {"message": ""}, {"message": "   "}, {"message": "x" * 2001}, {"message": 42}])
def test_invalid_chat_payloads_are_rejected(raw_test_client, body):
    response = raw_test_client.post("/api/chat", json=body)
    assert response.status_code == 422


def test_unknown_route_returns_404(raw_test_client):
    assert raw_test_client.get("/api/missing").status_code == 404


def test_home_page_serves_accessible_chat_interface(raw_test_client):
    response = raw_test_client.get("/")
    assert response.status_code == 200
    assert "Northstar AI Quality Lab" in response.text
    assert 'data-testid="assistant-response"' in response.text
    assert 'data-testid="trace-metadata"' in response.text
