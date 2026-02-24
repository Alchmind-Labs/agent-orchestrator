"""Mock web-search tool for development and testing.

Returns deterministic stub results so the system can be exercised without a
live search API.
"""

import logging

from app.tools.base import BaseTool

logger = logging.getLogger(__name__)


class MockSearchTool(BaseTool):
    """Simulate a web-search result without calling an external API.

    Expected ``input_data`` keys:

    - ``query`` (str): The search query string.
    """

    name: str = "mock_search"
    description: str = (
        "Search the web for information about a topic and return a summary. "
        "(Stub implementation for development.)"
    )

    # Mapping of lower-cased keywords to canned responses.
    _STUB_RESPONSES: dict[str, str] = {
        "python": (
            "Python is a high-level, general-purpose programming language "
            "known for its readability and broad ecosystem."
        ),
        "fastapi": (
            "FastAPI is a modern, high-performance web framework for building "
            "APIs with Python 3.8+ based on standard type hints."
        ),
        "openai": (
            "OpenAI is an AI research company that develops large language "
            "models including the GPT family and DALL-E."
        ),
    }
    _DEFAULT_RESPONSE = (
        "No specific information found. This is a mock search result for: {query}"
    )

    def execute(self, input_data: dict) -> str:
        """Return a canned search result for the given query.

        Args:
            input_data: Must contain a ``query`` key.

        Returns:
            A stub search-result string.

        Raises:
            ValueError: If the ``query`` key is absent.
        """
        if "query" not in input_data:
            raise ValueError("Missing required key 'query' for mock_search.")

        query: str = str(input_data["query"])
        logger.debug("MockSearchTool executing query: %r", query)

        query_lower = query.lower()
        for keyword, response in self._STUB_RESPONSES.items():
            if keyword in query_lower:
                return response

        return self._DEFAULT_RESPONSE.format(query=query)
