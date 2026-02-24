"""Simple arithmetic calculator tool.

Supports addition, subtraction, multiplication, and division of two operands.
"""

import logging

from app.tools.base import BaseTool

logger = logging.getLogger(__name__)


class CalculatorTool(BaseTool):
    """Evaluate a basic arithmetic expression consisting of two operands.

    Expected ``input_data`` keys:

    - ``operation`` (str): One of ``"add"``, ``"subtract"``, ``"multiply"``,
      ``"divide"``.
    - ``a`` (float | int | str): Left-hand operand.
    - ``b`` (float | int | str): Right-hand operand.
    """

    name: str = "calculator"
    description: str = (
        "Perform basic arithmetic operations (add, subtract, multiply, divide) "
        "on two numbers."
    )

    def execute(self, input_data: dict) -> str:
        """Compute the result of the requested arithmetic operation.

        Args:
            input_data: Must contain ``operation``, ``a``, and ``b``.

        Returns:
            A human-readable result string, e.g. ``"Result: 42.0"``.

        Raises:
            ValueError: If a required key is absent or the operation is unknown.
            ZeroDivisionError: If ``b`` is zero and ``operation`` is ``"divide"``.
        """
        required_keys = {"operation", "a", "b"}
        missing = required_keys - input_data.keys()
        if missing:
            raise ValueError(f"Missing required keys for calculator: {missing}")

        operation: str = str(input_data["operation"]).lower()
        try:
            a = float(input_data["a"])
            b = float(input_data["b"])
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Operands 'a' and 'b' must be numeric, got: "
                f"a={input_data['a']!r}, b={input_data['b']!r}"
            ) from exc

        logger.debug("Calculator: %s %s %s", a, operation, b)

        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                raise ZeroDivisionError("Division by zero is not allowed.")
            result = a / b
        else:
            raise ValueError(
                f"Unknown operation '{operation}'. "
                "Supported: add, subtract, multiply, divide."
            )

        return f"Result: {result}"
