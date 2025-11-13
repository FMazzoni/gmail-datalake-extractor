"""Task status storage using DuckDB."""

import logging
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any

import duckdb

from gmail_datalake_extractor.config import config

logger = logging.getLogger(__name__)


@contextmanager
def get_task_db():
    """Get a DuckDB connection for task storage."""
    db_path = config.task.db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(db_path)) as con:
        _init_task_table(con)
        yield con


def _init_task_table(con: duckdb.DuckDBPyConnection) -> None:
    """Initialize the task status table if it doesn't exist."""
    con.execute("""
        CREATE TABLE IF NOT EXISTS task_status (
            task_id VARCHAR PRIMARY KEY,
            status VARCHAR NOT NULL,
            progress INTEGER NOT NULL,
            message VARCHAR,
            message_count INTEGER,
            error VARCHAR,
            started_at TIMESTAMP NOT NULL,
            completed_at TIMESTAMP
        )
    """)


def create_task(task_id: str, status: str, progress: int, message: str) -> None:
    """Create a new task status entry."""
    with get_task_db() as con:
        con.execute(
            """
            INSERT INTO task_status (task_id, status, progress, message, started_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            [task_id, status, progress, message, datetime.now()],
        )


def update_task(
    task_id: str,
    status: str | None = None,
    progress: int | None = None,
    message: str | None = None,
    message_count: int | None = None,
    error: str | None = None,
    completed_at: datetime | None = None,
) -> None:
    """Update task status fields."""
    updates = []
    params = []

    if status is not None:
        updates.append("status = ?")
        params.append(status)
    if progress is not None:
        updates.append("progress = ?")
        params.append(progress)
    if message is not None:
        updates.append("message = ?")
        params.append(message)
    if message_count is not None:
        updates.append("message_count = ?")
        params.append(message_count)
    if error is not None:
        updates.append("error = ?")
        params.append(error)
    if completed_at is not None:
        updates.append("completed_at = ?")
        params.append(completed_at)

    if not updates:
        return

    params.append(task_id)
    query = f"UPDATE task_status SET {', '.join(updates)} WHERE task_id = ?"

    with get_task_db() as con:
        con.execute(query, params)


def get_task(task_id: str) -> dict[str, Any] | None:
    """Get task status by ID."""
    with get_task_db() as con:
        result = con.execute(
            """
            SELECT task_id, status, progress, message, message_count, error,
                   started_at, completed_at
            FROM task_status
            WHERE task_id = ?
            """,
            [task_id],
        ).fetchone()

        if not result:
            return None

        return {
            "task_id": result[0],
            "status": result[1],
            "progress": result[2],
            "message": result[3],
            "message_count": result[4],
            "error": result[5],
            "started_at": result[6],
            "completed_at": result[7],
        }


def cleanup_old_tasks() -> int:
    """Remove old completed/failed tasks and enforce max size limit using SQL.

    Returns:
        Number of tasks removed
    """
    ttl_threshold = datetime.now() - timedelta(hours=config.task.ttl_hours)

    with get_task_db() as con:
        # Count expired tasks before deletion
        expired_count_result = con.execute(
            """
            SELECT COUNT(*)
            FROM task_status
            WHERE status IN ('completed', 'failed')
              AND completed_at IS NOT NULL
              AND completed_at < ?
            """,
            [ttl_threshold],
        ).fetchone()
        expired_count = expired_count_result[0] if expired_count_result else 0

        # Remove expired tasks
        if expired_count > 0:
            con.execute(
                """
                DELETE FROM task_status
                WHERE status IN ('completed', 'failed')
                  AND completed_at IS NOT NULL
                  AND completed_at < ?
                """,
                [ttl_threshold],
            )

        # Check current count after expired cleanup
        count_result = con.execute("SELECT COUNT(*) FROM task_status").fetchone()
        current_count = count_result[0] if count_result else 0

        # Remove oldest tasks if over limit
        excess_count = 0
        if current_count > config.task.max_tasks:
            excess = current_count - config.task.max_tasks
            con.execute(
                """
                DELETE FROM task_status
                WHERE task_id IN (
                    SELECT task_id
                    FROM task_status
                    ORDER BY started_at ASC
                    LIMIT ?
                )
                """,
                [excess],
            )
            excess_count = excess

        total_removed = expired_count + excess_count
        if total_removed > 0:
            final_count = current_count - excess_count
            logger.info(
                f"Cleaned up {total_removed} old tasks. "
                f"Current task count: {final_count}"
            )

        return total_removed
