import logging

from message_extract.auth import get_service
from message_extract.messages import fetch_messages_with_retry, get_message_list
from message_extract.models import FetchConfig, Message

log = logging.getLogger(__name__)


def get_messages(
    search_query: str,
    max_results: int,
    fetch_config: FetchConfig,
):
    """Gets messages from Gmail API.
    Lists recent messages and fetches their metadata efficiently.

    Args:
        search_query: Gmail search query string
        max_results: Maximum number of messages to return
        fetch_config: Configuration for message fetching
    """

    # Get Gmail API service
    service = get_service()

    # List messages to get IDs
    messages_response = get_message_list(
        service,
        search_query=search_query,
        max_results=max_results,
    )

    if not messages_response.messages or len(messages_response.messages) == 0:
        log.error("No messages found.")
        raise ValueError("No messages found.")

    log.info(f"Found {len(messages_response.messages)} messages")

    # Extract message IDs
    message_ids = [msg.id for msg in messages_response.messages]

    # Fetch message metadata in batches with exponential backoff
    log.info("Fetching message metadata...")
    messages = fetch_messages_with_retry(
        service,
        message_ids,
        fetch_config=fetch_config,
    )

    log.info(f"Successfully fetched {len(messages)} messages:")
    for message in messages:
        log.info(f"ID: {message.id}, Thread: {message.threadId}")

    return messages


def save_to_datalake(messages: list[Message]):
    """Saves messages a DuckLake (duckdb data lake)."""
    pass
