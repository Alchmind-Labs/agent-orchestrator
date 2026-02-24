"""Application configuration using Pydantic BaseSettings.

All settings can be overridden via environment variables or a .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Top-level application settings.

    Attributes:
        app_name: Human-readable name shown in API docs.
        app_version: Semantic version string.
        debug: Enables debug-level logging when ``True``.
        log_level: Python logging level name (e.g. "INFO", "DEBUG").
        openai_api_key: API key for the OpenAI backend (not used in stub mode).
        openai_model: Model identifier forwarded to the LLM service.
        max_tokens: Maximum completion tokens to request from the LLM.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "Agent Orchestrator"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"

    # LLM settings (kept optional so the stub works without credentials)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    max_tokens: int = 1024


settings = Settings()
