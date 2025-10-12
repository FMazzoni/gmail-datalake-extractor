from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GmailApiConfig(BaseSettings):
    """Configuration for Gmail API operations."""

    model_config = SettingsConfigDict(
        env_prefix="GMAIL_API_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_assignment=True,
        use_enum_values=True,
    )

    # Gmail API authentication
    token_path: Path = Field(description="Gmail API token path for Gmail API")
    scopes: list[str] = Field(description="Gmail API scopes for Gmail API")


class DatabaseConfig(BaseSettings):
    """Configuration for PostgreSQL database operations.

    Below describes the configuration for the PostgreSQL metadata database.
    It is used to store the metadata of the messages extracted from Gmail.

    """

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_assignment=True,
        use_enum_values=True,
    )

    # PostgreSQL connection settings
    host: str = Field(description="PostgreSQL host")
    port: str = Field(description="PostgreSQL port")
    user: str = Field(description="PostgreSQL username")
    password: str = Field(description="PostgreSQL password")
    database: str = Field(
        description="PostgreSQL database name",
        alias="postgres_db",
    )


class ServerConfig(BaseSettings):
    """Configuration for FastAPI server settings."""

    model_config = SettingsConfigDict(
        env_prefix="SERVER_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_assignment=True,
        use_enum_values=True,
    )

    # Server settings
    host: str = Field(description="Server host address")
    port: int = Field(description="Server port number")
    reload: bool = Field(description="Enable auto-reload for development")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        description="Server log level"
    )


class Config:
    """Main configuration class that combines all configuration models."""

    def __init__(self):
        """Initialize all configuration sections."""
        self.gmail_api = GmailApiConfig.model_validate({})
        self.database = DatabaseConfig.model_validate({})
        self.server = ServerConfig.model_validate({})


# Global config instance
config = Config()
