import logging
from datetime import datetime, timedelta

from message_extract.auth import get_service
from message_extract.messages import fetch_messages_with_retry, get_message_list

log = logging.getLogger(__name__)


def main():
    """Shows basic usage of the Gmail API with batch message fetching.
    Lists recent messages and fetches their metadata efficiently.
    """

    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now()
    query = f"after:{start_date.strftime('%Y/%m/%d')} before:{end_date.strftime('%Y/%m/%d')}"

    # Get Gmail API service
    service = get_service()

    # List messages to get IDs
    messages_response = get_message_list(
        service, search_query=query, handle_error=False
    )

    if not messages_response.messages or len(messages_response.messages) == 0:
        log.info("No messages found.")
        return

    log.info(f"Found {len(messages_response.messages)} messages")

    # Extract message IDs
    message_ids = [msg.id for msg in messages_response.messages]

    # Fetch message metadata in batches with exponential backoff
    log.info("Fetching message metadata...")
    messages_metadata = fetch_messages_with_retry(
        service,
        message_ids,
        messages_per_batch=25,  # Smaller batch to avoid rate limits (100 is the max)
        response_format="full",
        max_retry_attempts=3,  # Only seem to occur on more than 25 messages
        initial_retry_delay=1.0,
    )

    log.info(f"Successfully fetched {len(messages_metadata)} messages:")
    for message in messages_metadata:
        log.info(f"ID: {message.id}, Thread: {message.threadId}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
