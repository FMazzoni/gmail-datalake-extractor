from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GmailApiConfig(BaseSettings):
    """Configuration for external API keys."""

    model_config = SettingsConfigDict(
        env_prefix="GMAIL_API_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Gmail API key
    token_path: Path = Field(description="Gmail API token path for Gmail API")
    scopes: list[str] = Field(
        description="Gmail API scopes for Gmail API",
    )


config = GmailApiConfig()  # type: ignore
