"""Pydantic v2 request/response schemas for the agent orchestrator API."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming payload for the POST /chat endpoint.

    Attributes:
        message: The user's natural-language message.
        agent_name: Name of the registered agent that should handle the request.
    """

    message: str = Field(..., min_length=1, description="User message to process.")
    agent_name: str = Field(..., min_length=1, description="Target agent identifier.")


class ChatResponse(BaseModel):
    """Response payload returned by the POST /chat endpoint.

    Attributes:
        response: The agent's generated reply.
        tool_used: Name of the tool invoked during processing, or an empty string
            when no tool was used.
    """

    response: str = Field(..., description="Agent's response to the user message.")
    tool_used: str = Field(
        default="",
        description="Tool that was invoked to produce the response.",
    )


class ErrorResponse(BaseModel):
    """Structured error payload returned on validation or processing failures.

    Attributes:
        detail: Human-readable description of the error.
        error_type: Short machine-readable error category.
    """

    detail: str = Field(..., description="Human-readable error message.")
    error_type: str = Field(..., description="Machine-readable error category.")
