# Gmail DataLake Extractor

A FastAPI service for extracting Gmail messages and storing them in DuckLake with configurable backend support (DuckDB for development, PostgreSQL for production).

## Features

- **Gmail API Integration**: Extract messages with batch processing and retry logic
- **Background Task Processing**: Non-blocking API with progress tracking
- **DuckLake Storage**: Modern data lake storage with DuckDB (dev) or PostgreSQL (prod) metadata catalog
- **Configurable Storage**: Customizable data paths and metadata schemas
- **Docker Support**: Containerized deployment with secret management
- **REST API**: FastAPI-based service with comprehensive error handling
- **Type Safety**: Full type hints and Pydantic models for robust data validation

## Quick Start

### Local Development

1. **Setup Environment**

   ```bash
   cp env.template .env
   # Edit .env with your Gmail API settings
   ```

2. **Prepare Gmail Token**

   ```bash
   # Ensure secrets/ directory contains:
   # - token.json (Gmail API token)
   # - ducklake_setup.dev.sql (DuckLake configuration for development)
   ```

3. **Install Dependencies**

   ```bash
   uv sync
   ```

4. **Run Server**

   ```bash
   uv run api-server
   ```

   Server will start on `http://localhost:8000` with DuckDB backend and DuckLake storage.

### Docker Deployment

1. **Setup Environment**

   ```bash
   cp env.template .env
   # Edit .env with your Gmail API settings
   ```

2. **Prepare Secrets**

   ```bash
   # Ensure secrets/ directory contains:
   # - token.json (Gmail API token)
   # - ducklake_setup.sql (DuckLake configuration for production)
   ```

3. **Deploy**

   ```bash
   docker-compose up -d
   ```

4. **Verify**

   ```bash
   curl http://localhost:8080/health
   ```

## API Usage

### Start Message Extraction

```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "from:example@gmail.com",
    "max_results": 1000,
    "fetch_config": {
      "messages_per_batch": 25,
      "response_format": "full",
      "max_retry_attempts": 3,
      "initial_retry_delay": 1.0
    }
  }'
```

**Response:**

```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "started",
  "message": "Extraction task started successfully"
}
```

> **Note**: The API returns immediately with a task ID. Use the status endpoint to track progress.

### Check Task Status

```bash
curl "http://localhost:8000/extract/abc123-def456-ghi789/status"
```

**Response:**

```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "running",
  "progress": 50,
  "message": "Retrieved 500 messages, saving to datalake...",
  "started_at": "2025-01-13T10:30:00",
  "completed_at": null
}
```

## Configuration

### Environment Variables

```bash
# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_RELOAD=false
SERVER_LOG_LEVEL=INFO

# DuckLake Configuration
DUCKLAKE_SETUP_PATH=/path/to/your/ducklake_setup.sql

# Gmail API Configuration
GMAIL_API_TOKEN_PATH=/path/to/your/gmail/token.json
GMAIL_API_SCOPES='["https://www.googleapis.com/auth/gmail.readonly"]'
```

### DuckLake Setup

DuckLake configuration is managed through SQL setup files:

- **Development**: `secrets/ducklake_setup.dev.sql` - Uses local DuckDB for metadata catalog
- **Production**: `secrets/ducklake_setup.sql` - Uses PostgreSQL for metadata catalog with S3 storage

The setup files define:

- Metadata catalog location (DuckDB file or PostgreSQL connection)
- Data storage path (local filesystem or S3)
- Schema configuration
- Encryption settings

## Project Structure

```text
message-extract/
├── src/gmail_datalake_extractor/ # Main application code
│   ├── api.py                   # FastAPI endpoints with background tasks
│   ├── auth.py                  # Gmail API authentication
│   ├── config.py                # Configuration management with Pydantic
│   ├── extract/                 # Message extraction logic
│   │   └── extract.py           # Core extraction and DuckLake integration
│   ├── messages.py              # Gmail API message operations
│   ├── models.py                # Pydantic data models for API
│   ├── server.py                # Server startup and configuration
│   └── sql/                     # SQL templates
│       └── attach_ducklake.sql  # DuckLake attachment script
├── docs/                        # Documentation
│   ├── DEPLOYMENT.md            # Docker deployment guide
│   └── API_README.md            # API reference
├── secrets/                     # Sensitive credentials and configs
│   ├── token.json               # Gmail API token
│   ├── ducklake_setup.sql       # Production DuckLake config
│   └── ducklake_setup.dev.sql   # Development DuckLake config
├── data/                        # DuckLake data storage
│   ├── main/messages/           # Parquet files
│   └── messages.duckdb          # DuckDB metadata catalog (dev)
├── notebooks/                   # Jupyter notebooks for exploration
├── tests/                       # Test files
├── docker-compose.yml           # Docker orchestration
├── Dockerfile                   # Container definition
├── pyproject.toml               # Python project configuration
└── env.template                 # Environment configuration template
```

## Troubleshooting

### Authentication Errors

If you encounter an `invalid_grant` or `RefreshError` when using the Gmail API, it means your refresh token has expired or been revoked. This typically happens when:

- The refresh token hasn't been used for 6+ months
- The token was revoked in your Google Account settings
- The OAuth client credentials changed

**To fix this, re-authenticate:**

1. **Using the auth helper script** (recommended):

   ```bash
   uv run gmail-auth
   ```

   The script will:
   - Extract client credentials from your existing token (if available)
   - Open a browser for OAuth authorization
   - Generate and save a new token

   If you have a separate `credentials.json` file from Google Cloud Console:

   ```bash
   uv run gmail-auth --credentials /path/to/credentials.json
   ```

2. **Manual re-authentication**:

   - Delete or rename your current `token.json` file
   - Re-run the OAuth flow using Google's OAuth 2.0 Playground or your own script
   - Save the new token to the configured path

The improved error messages will now provide specific guidance when authentication fails.

## Documentation

- **[API Documentation](docs/API_README.md)** - Complete API reference with examples
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Docker deployment and configuration
- **[Architecture Guide](docs/ARCHITECTURE.md)** - System design and DuckLake integration

## Interactive API Documentation

Once the server is running, visit:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

## Technology Stack

- **FastAPI**: Modern Python web framework with automatic API documentation
- **DuckLake**: Modern data lake storage with ACID transactions
- **DuckDB**: High-performance analytical database for metadata catalog
- **PostgreSQL**: Production metadata catalog backend
- **Pydantic**: Data validation and settings management
- **Gmail API**: Google's RESTful API for Gmail access
- **Docker**: Containerized deployment
- **uv**: Fast Python package manager
