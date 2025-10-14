import logging
from pathlib import Path
from typing import List

import duckdb
import pyarrow as pa

from gmail_datalake_extractor.auth import get_service
from gmail_datalake_extractor.config import config
from gmail_datalake_extractor.messages import (
    fetch_messages_with_retry,
    get_message_list,
)
from gmail_datalake_extractor.models import FetchConfig, Message

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
        log.debug(f"ID: {message.id}, Thread: {message.threadId}")

    return messages


def load_sql_file(sql_file_path: Path) -> str:
    """Load SQL from file."""
    with sql_file_path.open("r", encoding="utf-8") as f:
        return f.read().strip()


def save_to_datalake(messages: List[Message]) -> None:
    """Saves messages to DuckLake (duckdb data lake) using external SQL files."""
    # Convert messages to PyArrow table
    message_data = [msg.model_dump() for msg in messages]
    message_table = pa.Table.from_pylist(message_data)

    # Load SQL files
    sql_dir = Path(__file__).parent.parent / "sql"

    # Load DuckLake setup SQL from config path
    ducklake_setup_sql = load_sql_file(config.database.ducklake_setup_path)
    # Load attach SQL file (now simplified)
    attach_sql = load_sql_file(sql_dir / "attach_ducklake.sql")
    # Load ingest SQL file
    ingest_sql = load_sql_file(sql_dir / "create_and_insert_messages.sql")

    log.info("Running SQL files")

    # Execute database operations
    with duckdb.connect() as con:
        con.install_extension("httpfs")
        # Initialize DuckLake setup first
        con.sql(ducklake_setup_sql)
        # Then attach and insert data
        con.sql(attach_sql)
        con.register("message_table", message_table)
        con.sql(ingest_sql)
    log.info("All SQL files executed successfully")
