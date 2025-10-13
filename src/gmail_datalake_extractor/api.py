"""FastAPI endpoints for message extraction."""

import logging
import traceback
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel, Field

from gmail_datalake_extractor.extract.extract import get_messages, save_to_datalake
from gmail_datalake_extractor.models import FetchConfig

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,  # Changed from INFO to DEBUG
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Configure logging for this module
logger = logging.getLogger("message_extract.api")

# In-memory task status storage (in production, use Redis or database)
task_status: Dict[str, Dict[str, Any]] = {}


app = FastAPI(
    title="Gmail DataLake Extractor API",
    description="Gmail message extraction service with DuckLake storage",
    version="1.0.0",
)


class ExtractRequest(BaseModel):
    """Request model for message extraction."""

    query: str = Field(description="Gmail search query string", default="")
    max_results: int = Field(
        description="Maximum number of messages to return",
        default=500,
    )
    fetch_config: FetchConfig = Field(description="Configuration for message fetching")


class ExtractResponse(BaseModel):
    """Response model for message extraction."""

    success: bool
    message_count: int
    query: str


class TaskStartResponse(BaseModel):
    """Response model for starting a background task."""

    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    """Response model for task status."""

    task_id: str
    status: str
    progress: int
    message_count: int | None = None
    error: str | None = None
    started_at: datetime
    completed_at: datetime | None = None


async def run_extraction_task(task_id: str, request: ExtractRequest) -> None:
    """Run the extraction task in the background."""
    try:
        logger.info(f"Starting extraction task {task_id}")
        task_status[task_id].update(
            {
                "status": "running",
                "progress": 10,
                "message": "Fetching messages from Gmail API...",
            }
        )

        # Fetch messages
        messages = get_messages(
            search_query=request.query,
            max_results=request.max_results,
            fetch_config=request.fetch_config,
        )

        task_status[task_id].update(
            {
                "status": "running",
                "progress": 50,
                "message": f"Retrieved {len(messages)} messages, saving to datalake...",
            }
        )

        # Save to datalake
        save_to_datalake(messages)

        task_status[task_id].update(
            {
                "status": "completed",
                "progress": 100,
                "message": f"Successfully processed {len(messages)} messages",
                "message_count": len(messages),
                "completed_at": datetime.now(),
            }
        )

        logger.info(f"Completed extraction task {task_id}")

    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        task_status[task_id].update(
            {
                "status": "failed",
                "progress": 0,
                "error": str(e),
                "completed_at": datetime.now(),
            }
        )


@app.post("/extract", response_model=TaskStartResponse)
async def extract_messages(
    request: ExtractRequest, background_tasks: BackgroundTasks
) -> TaskStartResponse:
    """Start a background task to extract messages from Gmail.

    Args:
        request: ExtractRequest containing query, fetch_config, and list_config
        background_tasks: FastAPI background tasks

    Returns:
        TaskStartResponse with task ID and status
    """
    # Generate unique task ID
    task_id = str(uuid4())

    # Initialize task status
    task_status[task_id] = {
        "task_id": task_id,
        "status": "started",
        "progress": 0,
        "message": "Task started",
        "started_at": datetime.now(),
        "completed_at": None,
        "message_count": None,
        "error": None,
    }

    # Add background task
    background_tasks.add_task(run_extraction_task, task_id, request)

    logger.info(f"Started extraction task {task_id} for query: '{request.query}'")

    return TaskStartResponse(
        task_id=task_id,
        status="started",
        message="Extraction task started successfully",
    )


@app.get("/extract/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """Get the status of an extraction task.

    Args:
        task_id: The task ID returned from the extract endpoint

    Returns:
        TaskStatusResponse with current task status

    Raises:
        HTTPException: If task not found
    """
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")

    status = task_status[task_id]
    return TaskStatusResponse(**status)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
