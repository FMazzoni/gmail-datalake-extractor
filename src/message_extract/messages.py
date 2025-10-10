"""Gmail message operations and utilities."""

import logging
import time
from functools import lru_cache
from typing import Any, Literal

from googleapiclient.errors import HttpError

from message_extract.models import ListMessagesResponse, Message

log = logging.getLogger(__name__)


@lru_cache(maxsize=10)
def get_message_list(
    gmail_service: Any,
    search_query: str = "",
    max_results: int = 500,
    handle_error: bool = True,
) -> ListMessagesResponse:
    """Get message list with LRU caching to reduce API calls during development.

    Args:
        gmail_service: Authenticated Gmail API service
        search_query: Gmail search query string
        max_results: Maximum number of messages to return
        handle_error: Whether to handle errors gracefully by returning empty list

    Returns:
        ListMessagesResponse: List of messages matching the query

    Raises:
        HttpError: If handle_error is False and API call fails
    """
    try:
        log.info(f"Making API call for query: {search_query}")
        response = (
            gmail_service.users()
            .messages()
            .list(userId="me", q=search_query, maxResults=max_results)
            .execute()
        )
        messages = ListMessagesResponse.model_validate(response)
        return messages
    except HttpError as error:
        if handle_error:
            return ListMessagesResponse(messages=[])
        raise error


def execute_single_batch(
    gmail_service: Any,
    message_ids_to_fetch: list[str],
    response_format: Literal["metadata", "full", "minimal", "raw"] = "metadata",
    metadata_headers: list[str] | None = None,
) -> tuple[list[Message], set[str]]:
    """Execute a single batch request to fetch multiple messages.

    Args:
        gmail_service: Authenticated Gmail API service
        message_ids_to_fetch: List of message IDs to fetch in this batch
        response_format: Message format ('metadata', 'full', 'minimal', 'raw')
        metadata_headers: Headers to include when format is 'metadata'

    Returns:
        tuple: (successfully_fetched_messages, failed_message_ids)
    """

    successfully_fetched_messages = []
    failed_message_ids = set()

    def batch_callback(
        message_id: str, api_response: Any, error: Exception | None
    ) -> None:
        """Handle individual message responses within the batch."""
        if error:
            log.warning(f"Error fetching message {message_id}: {error}")
            failed_message_ids.add(message_id)
        else:
            try:
                message_data = Message.model_validate(api_response)
                successfully_fetched_messages.append(message_data)
            except Exception as e:
                log.error(f"Parsing error for message {message_id}: {e}")
                failed_message_ids.add(message_id)

    batch_request = gmail_service.new_batch_http_request(callback=batch_callback)
    for message_id in message_ids_to_fetch:
        batch_request.add(
            gmail_service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format=response_format,
                metadataHeaders=metadata_headers
                if response_format == "metadata"
                else None,
            ),
            request_id=message_id,
        )

    try:
        batch_request.execute()
    except HttpError as error:
        log.error(f"Batch execution failed: {error}")
        # Only mark unprocessed messages as failed
        successfully_processed_ids = {msg.id for msg in successfully_fetched_messages}
        unprocessed_message_ids = {
            msg_id
            for msg_id in message_ids_to_fetch
            if msg_id not in successfully_processed_ids
        }
        failed_message_ids.update(unprocessed_message_ids)

    return successfully_fetched_messages, failed_message_ids


def fetch_messages_with_retry(
    gmail_service: Any,
    message_ids_to_fetch: list[str],
    messages_per_batch: int = 50,
    response_format: Literal["metadata", "full", "minimal", "raw"] = "metadata",
    metadata_headers: list[str] | None = None,
    max_retry_attempts: int = 3,
    initial_retry_delay: float = 1.0,
) -> list[Message]:
    """Fetch multiple messages efficiently using batch requests with automatic retry.

    Args:
        gmail_service: Authenticated Gmail API service
        message_ids_to_fetch: List of message IDs to fetch
        messages_per_batch: Number of messages per batch (recommended max 50)
        response_format: Message format ('metadata', 'full', 'minimal', 'raw')
        metadata_headers: Headers to include when format is 'metadata'
        max_retry_attempts: Maximum number of retry attempts for failed batches
        initial_retry_delay: Base delay in seconds for exponential backoff

    Returns:
        list[Message]: List of successfully fetched messages
    """
    if metadata_headers is None:
        metadata_headers = ["From", "Subject", "Date", "To"]

    all_successfully_fetched_messages = []

    # Process messages in batches
    for batch_start_index in range(0, len(message_ids_to_fetch), messages_per_batch):
        current_batch_message_ids = message_ids_to_fetch[
            batch_start_index : batch_start_index + messages_per_batch
        ]
        batch_number = batch_start_index // messages_per_batch + 1

        retry_attempt = 0

        while (
            len(current_batch_message_ids) > 0 and retry_attempt <= max_retry_attempts
        ):
            batch_results, failed_message_ids = execute_single_batch(
                gmail_service,
                current_batch_message_ids,
                response_format,
                metadata_headers,
            )
            all_successfully_fetched_messages.extend(batch_results)

            if len(failed_message_ids) == 0:
                break

            current_batch_message_ids = list(failed_message_ids)
            retry_attempt += 1

            if retry_attempt <= max_retry_attempts:
                # Exponential backoff: 1s, 2s, 4s...
                retry_delay = initial_retry_delay * (2 ** (retry_attempt - 1))
                log.warning(
                    f"Retrying batch {batch_number} in {retry_delay}s (attempt {retry_attempt}/{max_retry_attempts + 1})"
                )
                time.sleep(retry_delay)
            else:
                log.error(
                    f"Max retries exceeded for batch {batch_number}. Giving up on {len(failed_message_ids)} messages."
                )

    log.info(
        f"Successfully fetched {len(all_successfully_fetched_messages)} out of {len(message_ids_to_fetch)} messages"
    )
    return all_successfully_fetched_messages
