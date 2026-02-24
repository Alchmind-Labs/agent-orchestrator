"""Pytest configuration and shared fixtures for the test suite."""

import pytest
from fastapi.testclient import TestClient

from app.core.agent import Agent
from app.core.orchestrator import Orchestrator, register_agent
from app.core.tool_registry import ToolRegistry
from app.main import app
from app.services.llm_service import StubLLMService
from app.tools.calculator import CalculatorTool
from app.tools.mock_search import MockSearchTool


@pytest.fixture(scope="session")
def tool_registry() -> ToolRegistry:
    """Return a pre-populated ToolRegistry for use across the test session."""
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(MockSearchTool())
    return registry


@pytest.fixture(scope="session")
def llm_service() -> StubLLMService:
    """Return a StubLLMService instance."""
    return StubLLMService(model="stub", max_tokens=256)


@pytest.fixture(scope="session")
def orchestrator(tool_registry: ToolRegistry, llm_service: StubLLMService) -> Orchestrator:
    """Return a configured Orchestrator with the session-scoped dependencies."""
    # Register the agents the orchestrator tests rely on.
    register_agent(
        Agent(
            name="general",
            description="General purpose agent.",
            allowed_tools=["calculator", "mock_search"],
        )
    )
    register_agent(
        Agent(
            name="calculator_agent",
            description="Math only agent.",
            allowed_tools=["calculator"],
        )
    )
    return Orchestrator(tool_registry=tool_registry, llm_service=llm_service)


@pytest.fixture(scope="session")
def client(orchestrator: Orchestrator) -> TestClient:
    """Return a TestClient backed by the real FastAPI app.

    The orchestrator fixture is used to ensure agents are registered before
    the first request is made.
    """
    # Override the dependency so the test orchestrator is injected.
    from app.api.routes import get_orchestrator

    app.dependency_overrides[get_orchestrator] = lambda: orchestrator
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
