"""Gmail DataLake Extractor - Gmail API utilities for extracting and processing messages with DuckLake storage."""

from gmail_datalake_extractor.api import app
from gmail_datalake_extractor.auth import get_credentials, get_service
from gmail_datalake_extractor.messages import (
    fetch_messages_with_retry,
    get_message_list,
)
from gmail_datalake_extractor.models import FetchConfig, ListMessagesResponse, Message

__all__ = [
    "app",
    "get_credentials",
    "get_service",
    "get_message_list",
    "fetch_messages_with_retry",
    "FetchConfig",
    "Message",
    "ListMessagesResponse",
]
