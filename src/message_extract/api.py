"""FastAPI endpoints for message extraction."""

import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from message_extract.extract.extract import get_messages, save_to_datalake
from message_extract.models import FetchConfig

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,  # Changed from INFO to DEBUG
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Configure logging for this module
logger = logging.getLogger("message_extract.api")


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
        logger.info(
            f"Starting message extraction - Query: '{request.query}', Max results: {request.max_results}"
        )

        messages = get_messages(
            search_query=request.query,
            max_results=request.max_results,
            fetch_config=request.fetch_config,
        )

        logger.info(f"Retrieved {len(messages)} messages from Gmail API")

        save_to_datalake(messages)
        logger.info(f"Successfully saved {len(messages)} messages to datalake")

        return ExtractResponse(
            success=True,
            message_count=len(messages),
            query=request.query,
        )

    except ValueError as e:
        logger.error(f"Value error during extraction: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during extraction: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
