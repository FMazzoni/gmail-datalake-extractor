"""FastAPI endpoints for message extraction."""

import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from message_extract.extract.extract import get_messages, save_to_datalake
from message_extract.models import FetchConfig

log = logging.getLogger(__name__)

app = FastAPI(
    title="Message Extract API",
    description="Gmail message extraction service",
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


@app.post("/extract", response_model=ExtractResponse)
async def extract_messages(request: ExtractRequest) -> ExtractResponse:
    """Extract messages from Gmail based on the provided query.

    Args:
        request: ExtractRequest containing query, fetch_config, and list_config

    Returns:
        ExtractResponse with extracted messages

    Raises:
        HTTPException: If extraction fails or no messages found
    """
    try:
        log.info(f"Extracting messages with query: {request.query}")

        # Extract messages
        messages = get_messages(
            search_query=request.query,
            max_results=request.max_results,
            fetch_config=request.fetch_config,
        )
        log.info(f"Saving {len(messages)} messages to DuckLake")
        save_to_datalake(messages)
        log.info(f"Successfully extracted {len(messages)} messages")

        return ExtractResponse(
            success=True,
            message_count=len(messages),
            query=request.query,
        )

    except ValueError as e:
        log.error(f"Value error during extraction: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log.error(f"Unexpected error during extraction: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
