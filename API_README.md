# Message Extract API

A FastAPI service for extracting Gmail messages using the Gmail API.

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

Extract messages from Gmail based on a search query.

**Request Body:**

```json
{
  "query": "from:example@gmail.com subject:important",
  "list_config": {
    "max_results": 100,
    "handle_error": true
  },
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
  "success": true,
  "message_count": 5,
  "query": "from:example@gmail.com subject:important",
  "messages": [
    {
      "id": "message_id_1",
      "threadId": "thread_id_1",
      "labelIds": ["INBOX"],
      "snippet": "Message preview...",
      "historyId": "12345",
      "internalDate": "2025-01-01T00:00:00Z",
      "payload": {...},
      "sizeEstimate": 1024,
      "raw": null
    }
  ]
}
```

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy"
}
```

## Configuration

### ListConfig

Controls message listing behavior:

- `max_results`: Maximum number of messages to return (default: 500)
- `handle_error`: Whether to handle errors gracefully by returning empty list (default: true)

### FetchConfig

Controls message fetching behavior:

- `messages_per_batch`: Number of messages per batch (default: 25)
- `response_format`: Message format - "metadata", "full", "minimal", "raw" (default: "full")
- `metadata_headers`: Headers to include when format is "metadata" (default: null)
- `max_retry_attempts`: Maximum retry attempts (default: 3)
- `initial_retry_delay`: Base delay for exponential backoff (default: 1.0)

## Authentication

Make sure you have Gmail API credentials set up in the `secrets/` directory before running the API.

## Interactive API Documentation

Once the server is running, visit:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
