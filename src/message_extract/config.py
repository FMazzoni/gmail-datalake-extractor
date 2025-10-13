from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field
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
    """Configuration for database operations."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_assignment=True,
        use_enum_values=True,
        secrets_dir="/run/secrets",  # Enable Docker secrets support
    )

    # Database mode: 'duckdb' for development, 'postgres' for production
    mode: Literal["duckdb", "postgres"] = Field(
        default="duckdb", description="Database mode", alias="db_mode"
    )

    # DuckDB file path (for development)
    duckdb_file: str = Field(
        default="data/messages.duckdb",
        description="DuckDB file path",
        alias="db_duckdb_file",
    )

    # PostgreSQL settings (for production)
    host: str = Field(default="", description="PostgreSQL host", alias="postgres_host")
    port: str = Field(
        default="5432", description="PostgreSQL port", alias="postgres_port"
    )
    user: str = Field(
        default="", description="PostgreSQL username", alias="postgres_user"
    )
    password: str = Field(
        default="",
        description="PostgreSQL password",
        validation_alias=AliasChoices("postgres_password"),
    )
    database: str = Field(
        default="",
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
