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
    """Configuration for database operations."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_assignment=True,
        use_enum_values=True,
    )

    ducklake_setup_path: Path = Field(
        description="Path to DuckLake setup SQL file",
        alias="ducklake_setup_path",
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


class TaskConfig(BaseSettings):
    """Configuration for task status storage."""

    model_config = SettingsConfigDict(
        env_prefix="TASK_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_assignment=True,
        use_enum_values=True,
    )

    ttl_hours: int = Field(
        default=800, description="Hours to keep completed/failed tasks before cleanup"
    )
    max_tasks: int = Field(
        default=10000, description="Maximum number of tasks to store"
    )
    db_path: Path = Field(
        default=Path("./data/tasks.duckdb"),
        description="Path to task status database file",
    )


class Config:
    """Main configuration class that combines all configuration models."""

    def __init__(self):
        """Initialize all configuration sections."""
        self.gmail_api = GmailApiConfig.model_validate({})
        self.database = DatabaseConfig.model_validate({})
        self.server = ServerConfig.model_validate({})
        self.task = TaskConfig.model_validate({})


# Global config instance
config = Config()
