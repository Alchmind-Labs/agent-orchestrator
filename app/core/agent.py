"""Agent data model.

An :class:`Agent` is a declarative configuration object that describes *who*
should handle a request: which tools it may use, how it should behave, and what
its role is within the system.  Execution logic lives in the
:class:`~app.core.orchestrator.Orchestrator`.
"""

from dataclasses import dataclass, field


@dataclass
class Agent:
    """Describe an AI agent and its operational constraints.

    Attributes:
        name: Unique identifier for the agent used during routing.
        description: Short prose description of the agent's purpose.
        allowed_tools: Names of :class:`~app.tools.base.BaseTool` instances
            this agent is permitted to invoke.  An empty list means the agent
            may not call any tools.
        system_prompt: The system-level instruction prepended to every LLM
            conversation for this agent.
    """

    name: str
    description: str
    allowed_tools: list[str] = field(default_factory=list)
    system_prompt: str = (
        "You are a helpful AI assistant. "
        "Answer the user's question clearly and concisely."
    )

    def can_use_tool(self, tool_name: str) -> bool:
        """Return ``True`` if *tool_name* is in the agent's allowed tool list.

        Args:
            tool_name: The :attr:`~app.tools.base.BaseTool.name` to check.
        """
        return tool_name in self.allowed_tools
