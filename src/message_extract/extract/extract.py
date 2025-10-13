import logging
from pathlib import Path
from typing import List

import duckdb
import pyarrow as pa
from jinja2 import Template

from message_extract.auth import get_service
from message_extract.config import config
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

    # Load and template SQL files
    sql_dir = Path(__file__).parent.parent / "sql"
    if config.database.mode == "duckdb":
        log.info(f"DuckDB file: {config.database.duckdb_file}")
    else:
        log.info(f"PostgreSQL host: {config.database.host}:{config.database.port}")
        log.info(f"PostgreSQL database: {config.database.database}")

    # Load and template attach SQL file with Jinja2
    attach_sql_template = load_sql_file(sql_dir / "attach_ducklake.sql")
    template = Template(attach_sql_template)
    attach_sql = template.render(
        db_mode=config.database.mode,
        DB_DUCKDB_FILE=config.database.duckdb_file,
        POSTGRES_USER=config.database.user,
        POSTGRES_PASSWORD=config.database.password,
        POSTGRES_HOST=config.database.host,
        POSTGRES_PORT=config.database.port,
        POSTGRES_DB=config.database.database,
    )
    # Load ingest SQL file
    ingest_sql = load_sql_file(sql_dir / "create_and_insert_messages.sql")

    log.info("Running SQL files")
    log.info(f"Database mode: {config.database.mode}")

    # Execute database operations
    with duckdb.connect() as con:
        con.sql(attach_sql)
        con.register("message_table", message_table)
        con.sql(ingest_sql)
    log.info("All SQL files executed successfully")
