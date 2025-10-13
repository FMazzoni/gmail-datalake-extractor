# Message Extract

A FastAPI service for extracting Gmail messages and storing them in DuckLake with configurable backend support (DuckDB for development, PostgreSQL for production).

## Features

- **Gmail API Integration**: Extract messages with batch processing and retry logic
- **Background Task Processing**: Non-blocking API with progress tracking
- **Flexible Storage**: DuckLake with DuckDB (dev) or PostgreSQL (prod) backend
- **Configurable Paths**: Customizable data paths and metadata schemas
- **Docker Support**: Containerized deployment with secret management
- **REST API**: FastAPI-based service with comprehensive error handling

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
   ```

3. **Install Dependencies**

   ```bash
   uv sync
   ```

4. **Run Server**

   ```bash
   uv run api-server
   ```

   Server will start on `http://localhost:8000` with DuckDB backend.

### Docker Deployment

1. **Setup Environment**

   ```bash
   cp env.template .env
   # Edit .env with your PostgreSQL and Gmail API settings
   ```

2. **Prepare Secrets**

   ```bash
   # Ensure secrets/ directory contains:
   # - token.json (Gmail API token)
   # - db_password.txt (PostgreSQL password)
   ```

3. **Deploy**

   ```bash
   docker-compose up -d
   ```

4. **Verify**

   ```bash
   curl http://localhost:8000/health
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

# Database Configuration
DB_MODE=duckdb                    # 'duckdb' for dev, 'postgres' for prod
DB_DUCKDB_FILE=data/messages.duckdb

# DuckLake Configuration
DUCKLAKE_DATA_PATH=data/          # Custom data storage path
DUCKLAKE_METADATA_SCHEMA=messages # Custom metadata schema name

# PostgreSQL Configuration (for production)
POSTGRES_HOST=your_postgres_server_host
POSTGRES_PORT=5432
POSTGRES_USER=your_postgres_username
POSTGRES_DB=your_database_name

# Gmail API Configuration
GMAIL_API_TOKEN_PATH=/run/secrets/gmail_token
GMAIL_API_SCOPES=https://www.googleapis.com/auth/gmail.readonly
```

## Project Structure

```
message-extract/
├── src/message_extract/          # Main application code
│   ├── api.py                   # FastAPI endpoints with background tasks
│   ├── auth.py                  # Gmail API authentication
│   ├── config.py                # Configuration management
│   ├── extract/                 # Message extraction logic
│   │   └── extract.py
│   ├── messages.py              # Gmail API message operations
│   ├── models.py                # Pydantic data models
│   ├── server.py                # Server startup
│   └── sql/                     # SQL templates
│       ├── attach_ducklake.sql
│       └── create_and_insert_messages.sql
├── docs/                        # Documentation
│   ├── DEPLOYMENT.md
│   └── API_README.md
├── secrets/                     # Sensitive credentials
├── data/                        # DuckLake data storage
├── tests/                       # Test files
├── docker-compose.yml           # Docker orchestration
├── Dockerfile                   # Container definition
└── env.template                 # Environment configuration template
```

## Documentation

- **[API Documentation](docs/API_README.md)** - Complete API reference
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions

## Interactive API Documentation

Once the server is running, visit:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
