"""Orchestrator — the central coordination layer.

The :class:`Orchestrator` ties together agent configuration, the tool registry,
guardrails, and the LLM service.  It is the *only* component in the system that
understands the full request lifecycle.
"""

import logging

from app.core.agent import Agent
from app.core.guardrails import enforce_no_pii
from app.core.tool_registry import ToolRegistry
from app.models.schemas import ChatResponse
from app.services.llm_service import BaseLLMService

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default agent registry (populated at startup in main.py)
# ---------------------------------------------------------------------------
_AGENT_REGISTRY: dict[str, Agent] = {}


def register_agent(agent: Agent) -> None:
    """Add an :class:`~app.core.agent.Agent` to the global agent registry.

    Args:
        agent: The agent to register.
    """
    _AGENT_REGISTRY[agent.name] = agent
    logger.info("Registered agent: %r", agent.name)


def get_agent(name: str) -> Agent | None:
    """Look up a registered agent by name.

    Args:
        name: The agent's unique identifier.

    Returns:
        The matching :class:`~app.core.agent.Agent`, or ``None`` if not found.
    """
    return _AGENT_REGISTRY.get(name)


class AgentNotFoundError(KeyError):
    """Raised when the requested agent name is not registered."""


class Orchestrator:
    """Coordinate tool selection, guardrail enforcement, and LLM interaction.

    The orchestrator follows this pipeline for every request:

    1. **Guardrails** — reject input that contains PII.
    2. **Agent lookup** — resolve the named agent from the registry.
    3. **Tool selection** — choose the best allowed tool for the message
       (keyword-based stub logic; replace with LLM function-calling in prod).
    4. **Tool execution** — run the selected tool when one was chosen.
    5. **LLM completion** — pass the (optionally enriched) context to the LLM.
    6. **Response assembly** — return a structured :class:`~app.models.schemas.ChatResponse`.

    Args:
        tool_registry: Populated :class:`~app.core.tool_registry.ToolRegistry`.
        llm_service: Any :class:`~app.services.llm_service.BaseLLMService` impl.
    """

    def __init__(
        self,
        tool_registry: ToolRegistry,
        llm_service: BaseLLMService,
    ) -> None:
        self._tool_registry = tool_registry
        self._llm_service = llm_service

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def handle(self, message: str, agent_name: str) -> ChatResponse:
        """Process a user message and return a structured response.

        Args:
            message: Raw user input.
            agent_name: Name of the agent that should handle the request.

        Returns:
            A :class:`~app.models.schemas.ChatResponse` containing the reply
            and the name of any tool that was invoked.

        Raises:
            PIIDetectedError: If the message contains PII.
            AgentNotFoundError: If *agent_name* is not registered.
        """
        logger.info("Orchestrator.handle: agent=%r message=%r", agent_name, message)

        # 1. Guardrails
        enforce_no_pii(message)

        # 2. Agent lookup
        agent = get_agent(agent_name)
        if agent is None:
            raise AgentNotFoundError(
                f"Agent '{agent_name}' is not registered. "
                f"Available agents: {list(_AGENT_REGISTRY.keys())}"
            )

        # 3. Tool selection (keyword-based stub; swap with LLM routing in prod)
        tool_name = self._select_tool(message, agent)
        tool_result: str | None = None

        # 4. Tool execution
        if tool_name:
            tool = self._tool_registry.get_tool(tool_name)
            tool_input = self._build_tool_input(message, tool_name)
            logger.info("Executing tool %r with input %r", tool_name, tool_input)
            tool_result = tool.execute(tool_input)

        # 5. LLM completion
        context = self._build_llm_context(message, tool_result)
        llm_response = self._llm_service.complete(
            system_prompt=agent.system_prompt,
            user_message=context,
        )

        # 6. Response assembly
        return ChatResponse(
            response=llm_response,
            tool_used=tool_name or "",
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _select_tool(self, message: str, agent: Agent) -> str | None:
        """Choose the most appropriate tool for *message* given *agent* constraints.

        This is intentionally a simple keyword-based stub.  In a production
        system this would call the LLM with a function-calling schema to let
        the model decide which tool (if any) to invoke.

        Args:
            message: The user's message.
            agent: The agent handling the request.

        Returns:
            The name of the chosen tool, or ``None`` if no tool should be used.
        """
        message_lower = message.lower()

        # Prefer calculator for arithmetic-flavoured messages.
        arithmetic_keywords = {
            "calculate", "compute", "math", "add", "subtract",
            "multiply", "divide", "sum", "plus", "minus", "times",
        }
        if any(kw in message_lower for kw in arithmetic_keywords):
            if agent.can_use_tool("calculator"):
                return "calculator"

        # Fall back to search for anything that looks like a knowledge query.
        search_keywords = {"search", "find", "lookup", "what is", "tell me about", "who is"}
        if any(kw in message_lower for kw in search_keywords):
            if agent.can_use_tool("mock_search"):
                return "mock_search"

        return None

    @staticmethod
    def _build_tool_input(message: str, tool_name: str) -> dict:
        """Construct the ``input_data`` dict to pass to the selected tool.

        This is a stub implementation.  In production the LLM would extract
        structured arguments from the message via function-calling.

        Args:
            message: The raw user message.
            tool_name: The name of the tool that will be invoked.

        Returns:
            A dict suitable for passing to :meth:`~app.tools.base.BaseTool.execute`.
        """
        if tool_name == "calculator":
            # Very naive extraction: try to detect two numbers and an operation word.
            import re  # noqa: PLC0415

            numbers = re.findall(r"-?\d+(?:\.\d+)?", message)
            operation = "add"  # default
            for op, keywords in {
                "add": ["add", "plus", "sum"],
                "subtract": ["subtract", "minus", "difference"],
                "multiply": ["multiply", "times", "product"],
                "divide": ["divide", "quotient"],
            }.items():
                if any(kw in message.lower() for kw in keywords):
                    operation = op
                    break

            return {
                "operation": operation,
                "a": numbers[0] if len(numbers) >= 1 else "0",
                "b": numbers[1] if len(numbers) >= 2 else "0",
            }

        if tool_name == "mock_search":
            return {"query": message}

        return {"input": message}

    @staticmethod
    def _build_llm_context(message: str, tool_result: str | None) -> str:
        """Combine the user message and optional tool output into an LLM prompt.

        Args:
            message: Original user message.
            tool_result: Result from the tool (``None`` if no tool was used).

        Returns:
            Enriched prompt string.
        """
        if tool_result:
            return (
                f"User question: {message}\n\n"
                f"Tool result: {tool_result}\n\n"
                "Please provide a helpful response based on the tool result."
            )
        return message
