"""Pydantic data models for Gmail API responses."""

from typing import Literal

from pydantic import BaseModel


class Header(BaseModel):
    """Gmail API Header model."""

    name: str
    value: str


class MessagePartBody(BaseModel):
    """Gmail API MessagePartBody model."""

    attachmentId: str | None = None
    size: int | None = None
    data: str | None = None


class MessagePart(BaseModel):
    """Gmail API MessagePart model."""

    partId: str | None = None
    mimeType: str | None = None
    filename: str | None = None
    headers: list[Header] | None = None
    body: MessagePartBody | None = None
    parts: list["MessagePart"] | None = None


class Message(BaseModel):
    """Gmail API Message model."""

    id: str
    threadId: str
    labelIds: list[str] | None = None
    snippet: str | None = None
    historyId: str | None = None
    internalDate: str | None = None
    payload: MessagePart | None = None
    sizeEstimate: int | None = None
    raw: str | None = None


class ListMessagesResponse(BaseModel):
    """Response model for Gmail messages list API."""

    messages: list[Message]
    nextPageToken: str | None = None
    resultSizeEstimate: int | None = None


class FetchConfig(BaseModel):
    """Configuration model for message fetching operations.

    Args:
        messages_per_batch: Number of messages per batch (recommended max 50)
        response_format: Message format ('metadata', 'full', 'minimal', 'raw')
        metadata_headers: Headers to include when format is 'metadata'
        max_retry_attempts: Maximum number of retry attempts for failed batches
        initial_retry_delay: Base delay in seconds for exponential backoff
    """

    messages_per_batch: int = 25
    response_format: Literal["metadata", "full", "minimal", "raw"] = "full"
    metadata_headers: list[str] | None = None
    max_retry_attempts: int = 3
    initial_retry_delay: float = 1.0
