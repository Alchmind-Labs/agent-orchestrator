"""Integration tests for the POST /chat and GET /tools endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for the /health liveness probe."""

    def test_health_ok(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestChatEndpoint:
    """Tests for POST /api/v1/chat."""

    def test_general_agent_no_tool(self, client: TestClient) -> None:
        payload = {"message": "Hello, how are you?", "agent_name": "general"}
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "tool_used" in data

    def test_general_agent_uses_calculator(self, client: TestClient) -> None:
        payload = {"message": "Please add 5 and 7", "agent_name": "general"}
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["tool_used"] == "calculator"
        assert "response" in data

    def test_general_agent_uses_search(self, client: TestClient) -> None:
        payload = {"message": "Search for Python programming", "agent_name": "general"}
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["tool_used"] == "mock_search"

    def test_calculator_agent_uses_calculator(self, client: TestClient) -> None:
        payload = {"message": "Multiply 6 by 7", "agent_name": "calculator_agent"}
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["tool_used"] == "calculator"

    def test_unknown_agent_returns_404(self, client: TestClient) -> None:
        payload = {"message": "Hello", "agent_name": "nonexistent_agent"}
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 404

    def test_pii_in_message_returns_400(self, client: TestClient) -> None:
        payload = {"message": "Email me at test@example.com", "agent_name": "general"}
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 400

    def test_empty_message_returns_422(self, client: TestClient) -> None:
        payload = {"message": "", "agent_name": "general"}
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 422

    def test_missing_agent_name_returns_422(self, client: TestClient) -> None:
        payload = {"message": "Hello"}
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 422


class TestToolsEndpoint:
    """Tests for GET /api/v1/tools."""

    def test_list_tools_returns_list(self, client: TestClient) -> None:
        response = client.get("/api/v1/tools")
        assert response.status_code == 200
        tools = response.json()
        assert isinstance(tools, list)
        names = [t["name"] for t in tools]
        assert "calculator" in names
        assert "mock_search" in names

    def test_tools_have_name_and_description(self, client: TestClient) -> None:
        response = client.get("/api/v1/tools")
        for tool in response.json():
            assert "name" in tool
            assert "description" in tool
