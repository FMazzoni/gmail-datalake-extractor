"""Pydantic data models for Gmail API responses."""

import json
import tempfile
from typing import Annotated, Literal, Self

import pyarrow as pa
import pyarrow.json as pajson
from pydantic import BaseModel, BeforeValidator, PlainSerializer


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


def serialize_payload_to_json(value: MessagePart | dict | None) -> str | None:
    """Serialize payload to JSON string when dumping to JSON format.

    This ensures that when model_dump_json() is called, the payload field
    is serialized as a JSON string rather than a nested object.

    Args:
        value: The MessagePart object or dict to serialize

    Returns:
        JSON string representation of the payload, or None if payload is None
    """
    if value is None:
        return None

    # Handle both MessagePart instances and dicts
    if isinstance(value, MessagePart):
        return value.model_dump_json()
    elif isinstance(value, dict):
        return json.dumps(value)
    else:
        # Fallback: try to serialize as JSON
        return json.dumps(value)


def deserialize_payload_from_json(
    value: str | dict | MessagePart | None,
) -> dict | MessagePart | None:
    """Deserialize payload from JSON string if it's a string.

    This allows payload to be automatically deserialized when reading from PyArrow
    or other sources where it's stored as a JSON string.

    Args:
        value: The payload value (can be a JSON string, dict, MessagePart, or None)

    Returns:
        Deserialized payload (dict or MessagePart) or None
    """
    if value is None:
        return None

    # If it's already a dict or MessagePart, pass it through
    if isinstance(value, (dict, MessagePart)):
        return value

    # If it's a string, try to parse it as JSON
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # If JSON parsing fails, return None
            # (fallback for backwards compatibility)
            return None

    return value


MessagePartJsonSerialized = Annotated[
    MessagePart | None,
    BeforeValidator(deserialize_payload_from_json),
    PlainSerializer(serialize_payload_to_json, when_used="json"),
]


class Message(BaseModel):
    """Gmail API Message model."""

    id: str
    threadId: str
    labelIds: list[str] | None = None
    snippet: str | None = None
    historyId: str | None = None
    internalDate: str | None = None
    payload: MessagePartJsonSerialized = None
    sizeEstimate: int | None = None
    raw: str | None = None

    @classmethod
    def pyarrow_schema(cls) -> pa.Schema:
        """Get the PyArrow schema for Message table.

        Defines the explicit schema for storing Message data in PyArrow tables.
        Nested objects (like payload) are stored as JSON strings.

        Returns:
            PyArrow schema matching the Message model structure
        """
        return pa.schema(
            [
                pa.field("id", pa.string(), nullable=False),
                pa.field("threadId", pa.string(), nullable=False),
                pa.field("labelIds", pa.list_(pa.string()), nullable=True),
                pa.field("snippet", pa.string(), nullable=True),
                pa.field("historyId", pa.string(), nullable=True),
                pa.field("internalDate", pa.string(), nullable=True),
                pa.field("payload", pa.string(), nullable=True),  # JSON string
                pa.field("sizeEstimate", pa.int64(), nullable=True),
                pa.field("raw", pa.string(), nullable=True),
            ]
        )

    @classmethod
    def messages_to_pyarrow_table(cls, messages: list[Self]) -> pa.Table:
        """Convert a list of Messages to a PyArrow table using PyArrow's JSON reader.

        Leverages PyArrow's JSON reading with automatic type inference.
        Serializes nested objects (like payload) to JSON strings for proper storage
        in PyArrow tables, which don't handle complex nested structures well.

        Args:
            messages: List of Message instances to convert

        Returns:
            PyArrow table with messages, with nested objects serialized to JSON strings
        """
        if not messages:
            # Return empty table with schema if no messages
            return pa.Table.from_pylist([], schema=cls.pyarrow_schema())

        # Convert messages to line-delimited JSON format
        messages_lines = "\n".join([msg.model_dump_json() for msg in messages])

        # Use PyArrow's JSON reader with explicit schema for consistency
        # This ensures payload is stored as string (JSON) rather than inferred as struct
        schema = cls.pyarrow_schema()
        parse_options = pajson.ParseOptions(explicit_schema=schema)

        # Write to temporary file and read with PyArrow
        # PyArrow's JSON reader works better with actual files than StringIO
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=True
        ) as tmp_file:
            tmp_file.write(messages_lines)
            tmp_file.flush()  # Ensure data is written to disk

            # Read JSON using PyArrow's JSON reader
            table = pajson.read_json(tmp_file.name, parse_options=parse_options)

        return table

    @classmethod
    def pyarrow_to_messages(cls, data: pa.Table) -> list[Self]:
        """Create Message instances from a PyArrow table.

        The payload field will be automatically deserialized from JSON strings
        by the field validator.

        Args:
            data: PyArrow table with messages (payload stored as JSON strings)

        Returns:
            List of Message instances with properly deserialized nested objects
        """
        messages_tbl = data.to_pylist()
        # The field validator will automatically deserialize JSON strings
        return [cls.model_validate(msg_dict) for msg_dict in messages_tbl]


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
    max_retry_attempts: int = 5
    initial_retry_delay: float = 1.0
