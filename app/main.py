"""Application entry-point.

Bootstraps the FastAPI application, configures structured logging, registers
agents and tools, and wires up the dependency-injection graph.
"""

import logging
import logging.config
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.agent import Agent
from app.core.config import settings
from app.core.orchestrator import Orchestrator, register_agent
from app.core.tool_registry import ToolRegistry
from app.services.llm_service import StubLLMService
from app.tools.calculator import CalculatorTool
from app.tools.mock_search import MockSearchTool

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

LOGGING_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "logging.Formatter",
            "fmt": (
                '{"time": "%(asctime)s", "level": "%(levelname)s", '
                '"name": "%(name)s", "message": "%(message)s"}'
            ),
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": settings.log_level.upper(),
        "handlers": ["console"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown.

    On startup:
    * Build and populate the :class:`~app.core.tool_registry.ToolRegistry`.
    * Register default :class:`~app.core.agent.Agent` instances.
    * Construct the :class:`~app.core.orchestrator.Orchestrator` and attach it
      to ``application.state`` for injection into route handlers.

    On shutdown:
    * Any cleanup (DB connections, thread pools, etc.) would go here.
    """
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)

    # --- Tool registry ---
    tool_registry = ToolRegistry()
    tool_registry.register(CalculatorTool())
    tool_registry.register(MockSearchTool())

    # --- LLM service (stub; swap for OpenAILLMService when credentials are ready) ---
    llm_service = StubLLMService(
        model=settings.openai_model,
        max_tokens=settings.max_tokens,
    )

    # --- Orchestrator ---
    orchestrator = Orchestrator(
        tool_registry=tool_registry,
        llm_service=llm_service,
    )
    application.state.orchestrator = orchestrator

    # --- Default agents ---
    register_agent(
        Agent(
            name="general",
            description="A general-purpose assistant that can search and calculate.",
            allowed_tools=["calculator", "mock_search"],
            system_prompt=(
                "You are a knowledgeable and helpful AI assistant. "
                "Use the available tools when they will improve the accuracy of your answer. "
                "Be concise and precise."
            ),
        )
    )
    register_agent(
        Agent(
            name="calculator_agent",
            description="A specialised agent for mathematical computations.",
            allowed_tools=["calculator"],
            system_prompt=(
                "You are a precise mathematical assistant. "
                "Always use the calculator tool for arithmetic operations."
            ),
        )
    )

    logger.info("Application startup complete.")
    yield

    logger.info("Application shutdown.")


# ---------------------------------------------------------------------------
# FastAPI app factory
# ---------------------------------------------------------------------------


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "A production-grade AI Agent Orchestrator that routes user requests "
        "to specialized agents and tools."
    ),
    lifespan=lifespan,
)

# Allow all origins in development; tighten in production via environment config.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Lightweight liveness probe used by orchestration platforms.

    Returns:
        ``{"status": "ok"}`` when the service is running.
    """
    return {"status": "ok"}
