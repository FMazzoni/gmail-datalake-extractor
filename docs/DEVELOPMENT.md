# Development Guide

This guide covers local development setup for the Gmail DataLake Extractor project.

## Prerequisites

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Gmail API credentials

## Local Development Setup

### 1. Install Dependencies

```bash
uv sync
```

### 2. Environment Configuration

```bash
cp env.template .env
# Edit .env with your settings
```

Required environment variables:

```env
# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_RELOAD=true
SERVER_LOG_LEVEL=INFO

# DuckLake Configuration
DUCKLAKE_SETUP_PATH=./secrets/ducklake_setup.dev.sql

# Gmail API Configuration
GMAIL_API_TOKEN_PATH=./secrets/token.json
GMAIL_API_SCOPES='["https://www.googleapis.com/auth/gmail.readonly"]'
```

### 3. Gmail API Setup

1. Create a Google Cloud Project and enable Gmail API
2. Create OAuth 2.0 credentials
3. Generate a token with `gmail.readonly` scope
4. Save the token as `secrets/token.json`

### 4. DuckLake Configuration

Create development DuckLake setup:

```bash
mkdir -p secrets
cat > secrets/ducklake_setup.dev.sql << EOF
CREATE secret my_ducklake (
    TYPE ducklake,
    metadata_path './data/messages.duckdb',
    data_path './data/',
    metadata_schema 'messages',
    encrypted FALSE
);
EOF
```

### 5. Run Development Server

```bash
uv run api-server
```

The server will start on `http://localhost:8000` with auto-reload enabled.

## Testing

### Running Tests

```bash
uv run pytest
```

### Writing Tests

Example test structure:

```python
import pytest
from fastapi.testclient import TestClient
from gmail_datalake_extractor.api import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
```
