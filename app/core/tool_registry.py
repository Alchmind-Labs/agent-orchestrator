"""Thread-safe registry for :class:`~app.tools.base.BaseTool` implementations.

Tools are keyed by their :attr:`~app.tools.base.BaseTool.name` attribute.
The registry is instantiated once at application startup and injected into the
:class:`~app.core.orchestrator.Orchestrator` via FastAPI's dependency system.
"""

import logging
from typing import Iterator

from app.tools.base import BaseTool

logger = logging.getLogger(__name__)


class ToolNotFoundError(KeyError):
    """Raised when a requested tool name is not in the registry."""


class ToolRegistry:
    """Manage the collection of available :class:`~app.tools.base.BaseTool` instances.

    Usage::

        registry = ToolRegistry()
        registry.register(CalculatorTool())
        tool = registry.get_tool("calculator")
        result = tool.execute({"operation": "add", "a": 1, "b": 2})
    """

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------

    def register(self, tool: BaseTool) -> None:
        """Add a tool to the registry.

        If a tool with the same name is already registered it will be
        replaced and a warning will be emitted.

        Args:
            tool: A concrete :class:`~app.tools.base.BaseTool` instance.
        """
        if tool.name in self._tools:
            logger.warning(
                "Tool %r is already registered and will be replaced.", tool.name
            )
        self._tools[tool.name] = tool
        logger.info("Registered tool: %r (%s)", tool.name, type(tool).__name__)

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def get_tool(self, name: str) -> BaseTool:
        """Retrieve a registered tool by name.

        Args:
            name: The :attr:`~app.tools.base.BaseTool.name` of the tool.

        Returns:
            The matching :class:`~app.tools.base.BaseTool` instance.

        Raises:
            ToolNotFoundError: If no tool with *name* is registered.
        """
        try:
            return self._tools[name]
        except KeyError as exc:
            available = list(self._tools.keys())
            raise ToolNotFoundError(
                f"Tool '{name}' not found. Available tools: {available}"
            ) from exc

    def list_tools(self) -> list[dict[str, str]]:
        """Return metadata for every registered tool.

        Returns:
            A list of dicts, each with ``"name"`` and ``"description"`` keys,
            sorted alphabetically by name.
        """
        return sorted(
            [{"name": t.name, "description": t.description} for t in self._tools.values()],
            key=lambda d: d["name"],
        )

    def __iter__(self) -> Iterator[BaseTool]:
        """Iterate over registered tools in insertion order."""
        return iter(self._tools.values())

    def __len__(self) -> int:
        return len(self._tools)
