"""Abstract LLM service layer.

Concrete backends (OpenAI, Anthropic, local models, …) should subclass
:class:`BaseLLMService` and implement :meth:`complete`.  The rest of the
application always depends on the abstract interface so swapping providers
requires no changes outside this package.
"""

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseLLMService(ABC):
    """Define the contract for all LLM service implementations.

    Attributes:
        model: Model identifier string (e.g. ``"gpt-4o"``).
        max_tokens: Upper bound on completion tokens.
    """

    def __init__(self, model: str, max_tokens: int) -> None:
        self.model = model
        self.max_tokens = max_tokens

    @abstractmethod
    def complete(self, system_prompt: str, user_message: str) -> str:
        """Generate a completion for *user_message* under *system_prompt*.

        Args:
            system_prompt: Instruction text prepended as the system role.
            user_message: The user's turn in the conversation.

        Returns:
            The model's text response.
        """


class StubLLMService(BaseLLMService):
    """Deterministic stub that returns canned responses without any API call.

    This implementation is safe to use in development and CI environments
    where real API credentials are unavailable.
    """

    def complete(self, system_prompt: str, user_message: str) -> str:  # noqa: ARG002
        """Return a deterministic stub response.

        Args:
            system_prompt: Ignored by this implementation.
            user_message: Echoed back in the stub response.

        Returns:
            A fixed string acknowledging the user message.
        """
        logger.debug(
            "StubLLMService.complete called (model=%r, max_tokens=%d)",
            self.model,
            self.max_tokens,
        )
        return (
            f"[STUB] I received your message: '{user_message}'. "
            "Configure a real LLM service to get a meaningful response."
        )


class OpenAILLMService(BaseLLMService):
    """OpenAI-backed LLM service.

    This class shows how a real backend would be wired in.  It is intentionally
    left as a stub (raises :class:`NotImplementedError`) so that the rest of
    the application can be built and tested without valid API credentials.

    To enable it:

    1. ``pip install openai``
    2. Set the ``OPENAI_API_KEY`` environment variable.
    3. Replace the ``raise NotImplementedError`` with the actual SDK call.
    """

    def __init__(self, api_key: str, model: str, max_tokens: int) -> None:
        super().__init__(model=model, max_tokens=max_tokens)
        self._api_key = api_key

    def complete(self, system_prompt: str, user_message: str) -> str:
        """Call the OpenAI Chat Completions API.

        Args:
            system_prompt: System-role instruction for the model.
            user_message: User-turn message.

        Returns:
            The model's text response.

        Raises:
            NotImplementedError: Until a real implementation is provided.
        """
        # Example wiring (uncomment when credentials are available):
        #
        # from openai import OpenAI
        # client = OpenAI(api_key=self._api_key)
        # response = client.chat.completions.create(
        #     model=self.model,
        #     max_tokens=self.max_tokens,
        #     messages=[
        #         {"role": "system", "content": system_prompt},
        #         {"role": "user", "content": user_message},
        #     ],
        # )
        # return response.choices[0].message.content or ""
        raise NotImplementedError(
            "OpenAILLMService.complete is not yet implemented. "
            "Use StubLLMService for development."
        )
