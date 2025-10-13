# Message Extract

A FastAPI service for extracting Gmail messages and storing them in DuckLake with PostgreSQL metadata catalog.

## Quick Start

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

### Local Development

1. **Setup Environment**

   ```bash
   cp env.template .env
   # Edit .env with your PostgreSQL and Gmail API settings
   # Include POSTGRES_PASSWORD for local development
   ```

2. **Prepare Gmail Token**

   ```bash
   # Ensure secrets/ directory contains:
   # - token.json (Gmail API token)
   ```

3. **Run Server**

   ```bash
   uv run api-server
   ```

   DuckLake will be attached automatically on first use.

## Documentation

- **[Deployment Guide](docs/DEPLOYMENT.md)** - Complete deployment instructions
- **[API Documentation](docs/API_README.md)** - API endpoints and usage

## Project Structure

```
message-extract/
├── src/message_extract/     # Main application code
├── docs/                    # Documentation
│   ├── DEPLOYMENT.md
│   └── API_README.md
├── secrets/                 # Sensitive credentials
├── data/                   # DuckLake data storage
├── docker-compose.yml      # Docker orchestration
├── Dockerfile             # Container definition
└── env.template           # Environment configuration template
```

## Features

- **Gmail API Integration**: Extract messages with batch processing and retry logic
- **DuckLake Storage**: Store messages in DuckLake with PostgreSQL metadata catalog
- **Secret Management**: Secure credential handling with Docker secrets
- **Docker Deployment**: Containerized service with automatic DuckLake setup
- **REST API**: FastAPI-based service with health checks
