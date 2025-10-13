# Message Extract API

A FastAPI service for extracting Gmail messages using the Gmail API with background task processing and DuckLake storage.

## Installation

Install dependencies:

```bash
uv sync
```

## Running the API

### Using uv run

```bash
uv run api-server
```

This will start the FastAPI server on `http://localhost:8000` with auto-reload enabled.

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

- `started`: Task initialized
- `running`: In progress (progress 10-90%)
- `completed`: Finished successfully (progress 100%)
- `failed`: Error occurred

**Progress Tracking:**

- **10%**: Started fetching from Gmail API
- **50%**: Messages retrieved, saving to datalake
- **100%**: Completed successfully

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy"
}
```

## Configuration

### ExtractRequest

Request model for message extraction:

- `query`: Gmail search query string (default: "")
- `max_results`: Maximum number of messages to return (default: 500)
- `fetch_config`: Configuration for message fetching

### FetchConfig

Controls message fetching behavior:

- `messages_per_batch`: Number of messages per batch (default: 25, max recommended: 50)
- `response_format`: Message format - "metadata", "full", "minimal", "raw" (default: "full")
- `metadata_headers`: Headers to include when format is "metadata" (default: null)
- `max_retry_attempts`: Maximum retry attempts (default: 5)
- `initial_retry_delay`: Base delay for exponential backoff (default: 1.0)

### TaskStatusResponse

Response model for task status:

- `task_id`: Unique task identifier
- `status`: Current task status
- `progress`: Progress percentage (0-100)
- `message`: Current status message
- `message_count`: Number of messages processed (when completed)
- `error`: Error message (if failed)
- `started_at`: Task start timestamp
- `completed_at`: Task completion timestamp (when finished)

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

Make sure you have Gmail API credentials set up in the `secrets/` directory before running the API:

- `secrets/token.json`: Gmail API authentication token
- Gmail API scopes: `https://www.googleapis.com/auth/gmail.readonly`

## Background Task Processing

The API uses FastAPI's background tasks to handle long-running operations:

- **Non-blocking**: API calls return immediately with a task ID
- **Progress tracking**: Real-time progress updates via status endpoint
- **Error handling**: Comprehensive error reporting with stack traces
- **Scalable**: Handles large message batches without timeouts

## Interactive API Documentation

Once the server is running, visit:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
