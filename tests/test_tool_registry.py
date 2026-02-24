"""Tests for ToolRegistry."""

import pytest

from app.core.tool_registry import ToolNotFoundError, ToolRegistry
from app.tools.calculator import CalculatorTool
from app.tools.mock_search import MockSearchTool


class TestToolRegistry:
    """Unit tests for the ToolRegistry class."""

    def setup_method(self) -> None:
        self.registry = ToolRegistry()
        self.calc = CalculatorTool()
        self.search = MockSearchTool()

    def test_register_and_get(self) -> None:
        self.registry.register(self.calc)
        tool = self.registry.get_tool("calculator")
        assert tool is self.calc

    def test_get_unknown_raises(self) -> None:
        with pytest.raises(ToolNotFoundError):
            self.registry.get_tool("nonexistent")

    def test_list_tools_empty(self) -> None:
        assert self.registry.list_tools() == []

    def test_list_tools_returns_metadata(self) -> None:
        self.registry.register(self.calc)
        self.registry.register(self.search)
        tools = self.registry.list_tools()
        names = [t["name"] for t in tools]
        assert "calculator" in names
        assert "mock_search" in names
        # Each entry must have name and description.
        for entry in tools:
            assert "name" in entry
            assert "description" in entry

    def test_list_tools_sorted_alphabetically(self) -> None:
        self.registry.register(self.search)
        self.registry.register(self.calc)
        names = [t["name"] for t in self.registry.list_tools()]
        assert names == sorted(names)

    def test_len(self) -> None:
        assert len(self.registry) == 0
        self.registry.register(self.calc)
        assert len(self.registry) == 1

    def test_iter(self) -> None:
        self.registry.register(self.calc)
        self.registry.register(self.search)
        tools = list(self.registry)
        assert self.calc in tools
        assert self.search in tools

    def test_duplicate_registration_replaces(self) -> None:
        self.registry.register(self.calc)
        new_calc = CalculatorTool()
        self.registry.register(new_calc)
        assert len(self.registry) == 1
        assert self.registry.get_tool("calculator") is new_calc
