"""Abstract base class for all agent tools.

Every concrete tool must inherit from :class:`BaseTool` and implement the
:meth:`execute` method.  The ``name`` and ``description`` class attributes are
used by the :class:`~app.core.tool_registry.ToolRegistry` to discover and
advertise available tools.
"""

from abc import ABC, abstractmethod


class BaseTool(ABC):
    """Contract that every tool implementation must satisfy.

    Attributes:
        name: Unique, snake_case identifier for the tool.  Used as the lookup
            key in :class:`~app.core.tool_registry.ToolRegistry`.
        description: One-sentence summary of what the tool does.  Surfaced in
            API responses and LLM prompts so it should be clear and concise.
    """

    name: str
    description: str

    @abstractmethod
    def execute(self, input_data: dict) -> str:
        """Execute the tool with the provided input and return a text result.

        Args:
            input_data: Arbitrary key/value pairs consumed by the tool.
                Concrete implementations should document the expected keys.

        Returns:
            A plain-text result string that will be forwarded to the caller.

        Raises:
            ValueError: If required keys are missing from *input_data*.
        """
