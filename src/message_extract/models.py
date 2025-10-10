"""Pydantic data models for Gmail API responses."""

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
