"""Tests for the CalculatorTool and MockSearchTool implementations."""

import pytest

from app.tools.calculator import CalculatorTool
from app.tools.mock_search import MockSearchTool


class TestCalculatorTool:
    """Unit tests for CalculatorTool."""

    def setup_method(self) -> None:
        self.tool = CalculatorTool()

    def test_name_and_description(self) -> None:
        assert self.tool.name == "calculator"
        assert "arithmetic" in self.tool.description.lower()

    def test_add(self) -> None:
        result = self.tool.execute({"operation": "add", "a": 3, "b": 4})
        assert result == "Result: 7.0"

    def test_subtract(self) -> None:
        result = self.tool.execute({"operation": "subtract", "a": 10, "b": 3})
        assert result == "Result: 7.0"

    def test_multiply(self) -> None:
        result = self.tool.execute({"operation": "multiply", "a": 6, "b": 7})
        assert result == "Result: 42.0"

    def test_divide(self) -> None:
        result = self.tool.execute({"operation": "divide", "a": 10, "b": 2})
        assert result == "Result: 5.0"

    def test_divide_by_zero_raises(self) -> None:
        with pytest.raises(ZeroDivisionError, match="Division by zero"):
            self.tool.execute({"operation": "divide", "a": 5, "b": 0})

    def test_unknown_operation_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown operation"):
            self.tool.execute({"operation": "modulo", "a": 5, "b": 3})

    def test_missing_keys_raises(self) -> None:
        with pytest.raises(ValueError, match="Missing required keys"):
            self.tool.execute({"operation": "add", "a": 1})

    def test_non_numeric_operand_raises(self) -> None:
        with pytest.raises(ValueError, match="numeric"):
            self.tool.execute({"operation": "add", "a": "foo", "b": 2})

    def test_string_numbers_accepted(self) -> None:
        result = self.tool.execute({"operation": "add", "a": "10", "b": "20"})
        assert result == "Result: 30.0"


class TestMockSearchTool:
    """Unit tests for MockSearchTool."""

    def setup_method(self) -> None:
        self.tool = MockSearchTool()

    def test_name_and_description(self) -> None:
        assert self.tool.name == "mock_search"
        assert "search" in self.tool.description.lower()

    def test_known_keyword_python(self) -> None:
        result = self.tool.execute({"query": "Tell me about Python"})
        assert "python" in result.lower()

    def test_known_keyword_fastapi(self) -> None:
        result = self.tool.execute({"query": "What is FastAPI?"})
        assert "fastapi" in result.lower()

    def test_unknown_query_returns_default(self) -> None:
        result = self.tool.execute({"query": "some obscure topic xyz"})
        assert "some obscure topic xyz" in result

    def test_missing_query_raises(self) -> None:
        with pytest.raises(ValueError, match="query"):
            self.tool.execute({})
