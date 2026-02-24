"""FastAPI route definitions for the agent orchestrator.

All business logic is delegated to the :class:`~app.core.orchestrator.Orchestrator`
which is injected via FastAPI's dependency system.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.guardrails import PIIDetectedError
from app.core.orchestrator import AgentNotFoundError, Orchestrator
from app.core.tool_registry import ToolNotFoundError
from app.models.schemas import ChatRequest, ChatResponse, ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Dependency factories
# ---------------------------------------------------------------------------


def get_orchestrator() -> Orchestrator:
    """FastAPI dependency that supplies a configured :class:`Orchestrator`.

    The actual instance is created in :func:`app.main.lifespan` and stored on
    ``app.state`` so it is shared across the entire application lifetime.
    This function is overridden in tests to inject mock orchestrators.
    """
    # Import here to avoid a circular import at module load time.
    from app.main import app  # noqa: PLC0415

    return app.state.orchestrator


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Send a message to an agent",
    description=(
        "Submit a user message to the named agent.  "
        "The orchestrator selects an appropriate tool, executes it if needed, "
        "and returns the agent's response together with the name of the tool used."
    ),
)
def chat(
    request: ChatRequest,
    orchestrator: Orchestrator = Depends(get_orchestrator),
) -> ChatResponse:
    """Process a chat message and return the agent's reply.

    Args:
        request: Validated request body containing *message* and *agent_name*.
        orchestrator: Injected orchestrator instance.

    Returns:
        A :class:`~app.models.schemas.ChatResponse`.

    Raises:
        HTTPException: 400 if PII is detected in the message.
        HTTPException: 404 if the requested agent is not registered.
        HTTPException: 422 if a required tool is not found.
        HTTPException: 500 for unexpected internal errors.
    """
    logger.info(
        "POST /chat  agent=%r  message=%r",
        request.agent_name,
        request.message,
    )
    try:
        return orchestrator.handle(
            message=request.message,
            agent_name=request.agent_name,
        )
    except PIIDetectedError as exc:
        logger.warning("PII detected in request: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except AgentNotFoundError as exc:
        logger.warning("Agent not found: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ToolNotFoundError as exc:
        logger.warning("Tool not found: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error in POST /chat: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        ) from exc


@router.get(
    "/tools",
    summary="List available tools",
    description="Return metadata for every tool registered in the tool registry.",
)
def list_tools(
    orchestrator: Orchestrator = Depends(get_orchestrator),
) -> list[dict[str, str]]:
    """Return all registered tools with their names and descriptions.

    Args:
        orchestrator: Injected orchestrator instance.

    Returns:
        A list of ``{"name": ..., "description": ...}`` dicts.
    """
    return orchestrator._tool_registry.list_tools()  # noqa: SLF001
