"""Input guardrails for the agent orchestrator.

Guardrails are applied *before* user input reaches the LLM or any tool.
They act as a first line of defence against misuse and unintended data leakage.
"""

import logging
import re

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Compiled regex patterns
# ---------------------------------------------------------------------------

# Matches common e-mail address formats (RFC 5322 simplified).
_EMAIL_PATTERN: re.Pattern[str] = re.compile(
    r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"
)

# Matches common US and international phone number formats.
_PHONE_PATTERN: re.Pattern[str] = re.compile(
    r"""
    (?:
        \+?1?[-.\s]?          # optional country code
        \(?\d{3}\)?           # area code (optionally wrapped in parentheses)
        [-.\s]?               # separator
        \d{3}                 # exchange
        [-.\s]?               # separator
        \d{4}                 # subscriber number
    )
    """,
    re.VERBOSE,
)


class PIIDetectedError(ValueError):
    """Raised when personally identifiable information is found in user input."""


def detect_pii(text: str) -> bool:
    """Return ``True`` if *text* appears to contain PII.

    Currently detects:

    * E-mail addresses (RFC 5322 simplified pattern).
    * US / international phone numbers.

    Args:
        text: Arbitrary input string to inspect.

    Returns:
        ``True`` if at least one PII pattern is matched, ``False`` otherwise.
    """
    if _EMAIL_PATTERN.search(text):
        logger.warning("PII detected: email address found in input.")
        return True

    if _PHONE_PATTERN.search(text):
        logger.warning("PII detected: phone number found in input.")
        return True

    return False


def enforce_no_pii(text: str) -> None:
    """Raise :class:`PIIDetectedError` if *text* contains PII.

    This is the primary entry-point used by the orchestrator.  Call it with
    the raw user message before forwarding to any downstream service.

    Args:
        text: User-supplied input to validate.

    Raises:
        PIIDetectedError: If :func:`detect_pii` returns ``True``.
    """
    if detect_pii(text):
        raise PIIDetectedError(
            "The input contains personally identifiable information (PII) "
            "such as an email address or phone number. "
            "Please remove PII before submitting your request."
        )
