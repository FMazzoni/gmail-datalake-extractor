# Gmail DataLake Extractor API

A FastAPI service for extracting Gmail messages using the Gmail API with background task processing and DuckLake storage.

## Overview

The API provides asynchronous message extraction from Gmail with:

- **Background Task Processing**: Non-blocking operations with progress tracking
- **DuckLake Integration**: Modern data lake storage with ACID transactions
- **Configurable Fetching**: Flexible message retrieval with retry logic
- **Type Safety**: Full Pydantic models for request/response validation

## Installation

Install dependencies:

```bash
uv sync
```

## Running the API

### Local Development

```bash
uv run api-server
```

This will start the FastAPI server on `http://localhost:8000` with auto-reload enabled.

### Docker Deployment

```bash
docker-compose up -d
```

The service will be available on `http://localhost:8080`.

## API Endpoints

### POST /extract

Start a background task to extract messages from Gmail based on a search query.

**Request Body:**

```json
{
  "query": "from:example@gmail.com subject:important",
  "max_results": 1000,
  "fetch_config": {
    "messages_per_batch": 25,
    "response_format": "full",
    "max_retry_attempts": 3,
    "initial_retry_delay": 1.0
  }
}
```

**Response:**

```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "started",
  "message": "Extraction task started successfully"
}
```

### GET /extract/{task_id}/status

Get the status of an extraction task.

**Path Parameters:**

- `task_id`: The task ID returned from the extract endpoint

**Response:**

```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "running",
  "progress": 50,
  "message": "Retrieved 500 messages, saving to datalake...",
  "message_count": null,
  "error": null,
  "started_at": "2025-01-13T10:30:00",
  "completed_at": null
}
```

**Task Status States:**

- `started`: Task initialized and queued
- `running`: In progress (progress 10-90%)
- `completed`: Finished successfully (progress 100%)
- `failed`: Error occurred during processing

**Progress Tracking:**

- **0%**: Task queued and initialized
- **10%**: Started fetching from Gmail API
- **50%**: Messages retrieved, saving to DuckLake
- **100%**: Completed successfully with message count

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy"
}
```

## Data Models

### ExtractRequest

Request model for message extraction:

```python
class ExtractRequest(BaseModel):
    query: str = ""                    # Gmail search query string
    max_results: int = 500             # Maximum number of messages to return
    fetch_config: FetchConfig          # Configuration for message fetching
```

### FetchConfig

Controls message fetching behavior:

```python
class FetchConfig(BaseModel):
    messages_per_batch: int = 25       # Messages per batch (max recommended: 50)
    response_format: Literal["metadata", "full", "minimal", "raw"] = "full"
    metadata_headers: list[str] | None = None  # Headers for metadata format
    max_retry_attempts: int = 5        # Maximum retry attempts
    initial_retry_delay: float = 1.0   # Base delay for exponential backoff
```

### TaskStatusResponse

Response model for task status:

```python
class TaskStatusResponse(BaseModel):
    task_id: str                        # Unique task identifier
    status: str                         # Current task status
    progress: int                       # Progress percentage (0-100)
    message: str                        # Current status message
    message_count: int | None = None    # Number of messages processed (when completed)
    error: str | None = None            # Error message (if failed)
    started_at: datetime                # Task start timestamp
    completed_at: datetime | None = None # Task completion timestamp (when finished)
```

## Usage Examples

### Basic Message Extraction

```bash
# Start extraction
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "from:important@company.com",
    "max_results": 500,
    "fetch_config": {
      "messages_per_batch": 25,
      "response_format": "full"
    }
  }'

# Check status (poll this endpoint)
curl "http://localhost:8000/extract/abc123-def456-ghi789/status"
```

### Large Batch Processing

```bash
# Start large extraction
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "after:2024/01/01",
    "max_results": 10000,
    "fetch_config": {
      "messages_per_batch": 50,
      "response_format": "metadata",
      "metadata_headers": ["From", "Subject", "Date", "To"],
      "max_retry_attempts": 5,
      "initial_retry_delay": 2.0
    }
  }'
```

### Error Handling

The API provides comprehensive error handling with full stack traces:

```json
{
  "detail": "Error: Conversion Error: Could not convert string '...' to INT32\n\nTraceback:\nTraceback (most recent call last):\n  File \"/path/to/api.py\", line 76, in extract_messages\n    save_to_datalake(messages)\n..."
}
```

## Authentication

Make sure you have Gmail API credentials set up before running the API:

### Required Files

- `secrets/token.json`: Gmail API authentication token
- `secrets/ducklake_setup.dev.sql`: DuckLake configuration for development
- `secrets/ducklake_setup.sql`: DuckLake configuration for production

### Gmail API Setup

1. Create a Google Cloud Project
2. Enable the Gmail API
3. Create OAuth 2.0 credentials
4. Generate a token with `https://www.googleapis.com/auth/gmail.readonly` scope
5. Save the token as `secrets/token.json`

## Background Task Processing

The API uses FastAPI's background tasks to handle long-running operations:

- **Non-blocking**: API calls return immediately with a task ID
- **Progress tracking**: Real-time progress updates via status endpoint
- **Error handling**: Comprehensive error reporting with stack traces
- **Scalable**: Handles large message batches without timeouts
- **DuckLake Integration**: Automatic data lake storage with ACID transactions

## DuckLake Storage

Messages are automatically stored in DuckLake with:

- **Parquet Format**: Efficient columnar storage for analytics
- **ACID Transactions**: Consistent data writes
- **Metadata Catalog**: DuckDB (dev) or PostgreSQL (prod) for metadata
- **Configurable Storage**: Local filesystem or S3 backend

## Interactive API Documentation

Once the server is running, visit:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
