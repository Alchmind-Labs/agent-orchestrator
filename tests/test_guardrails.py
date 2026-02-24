"""Tests for guardrails (PII detection)."""

import pytest

from app.core.guardrails import PIIDetectedError, detect_pii, enforce_no_pii


class TestDetectPII:
    """Unit tests for detect_pii."""

    def test_email_detected(self) -> None:
        assert detect_pii("Contact me at alice@example.com") is True

    def test_phone_detected(self) -> None:
        assert detect_pii("Call me at 555-867-5309") is True

    def test_phone_with_parentheses(self) -> None:
        assert detect_pii("My number is (800) 555-1234") is True

    def test_clean_text_returns_false(self) -> None:
        assert detect_pii("What is the capital of France?") is False

    def test_empty_string_returns_false(self) -> None:
        assert detect_pii("") is False


class TestEnforceNoPII:
    """Unit tests for enforce_no_pii."""

    def test_raises_on_email(self) -> None:
        with pytest.raises(PIIDetectedError):
            enforce_no_pii("Send results to user@test.org")

    def test_raises_on_phone(self) -> None:
        with pytest.raises(PIIDetectedError):
            enforce_no_pii("I am at +1 800-555-0100")

    def test_clean_input_passes(self) -> None:
        # Should not raise.
        enforce_no_pii("What is the weather like today?")
