# Gmail DataLake Extractor Deployment Guide

This guide explains how to deploy the gmail-datalake-extractor service using Docker with configurable backend support (DuckDB for development, PostgreSQL for production).

## Prerequisites

- Docker and Docker Compose installed
- Gmail API credentials (`token.json` file)
- For production: External PostgreSQL server accessible from the deployment environment

## Setup Instructions

### 1. Environment Configuration

Copy the environment template and configure your settings:

```bash
cp env.template .env
```

Edit `.env` with your actual values:

```env
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
# Note: POSTGRES_PASSWORD is read from Docker secret /run/secrets/postgres_password

# Gmail API Configuration
GMAIL_API_TOKEN_PATH=/run/secrets/gmail_token
GMAIL_API_SCOPES=https://www.googleapis.com/auth/gmail.readonly
```

### 2. Prepare Secrets Directory

Ensure your `secrets/` directory contains:

- `token.json` - Gmail API authentication token
- `db_password.txt` - Database password

### 3. Create Data Directory

```bash
mkdir -p data
```

### 4. Deploy the Service

```bash
# Build and start the service
docker-compose up -d

# View logs
docker-compose logs -f message-extract

# Check service health
curl http://localhost:8000/health
```

### 5. Automatic DuckLake Setup

DuckLake is automatically configured on first run based on your configuration:

- **Development (DuckDB)**: Uses local DuckDB file for metadata catalog
- **Production (PostgreSQL)**: Uses external PostgreSQL server for metadata catalog

## DuckLake Configuration

The service supports flexible DuckLake configuration:

### Development Mode (DuckDB)

```env
DB_MODE=duckdb
DB_DUCKDB_FILE=data/messages.duckdb
DUCKLAKE_DATA_PATH=data/
DUCKLAKE_METADATA_SCHEMA=messages
```

### Production Mode (PostgreSQL)

```env
DB_MODE=postgres
POSTGRES_HOST=your_postgres_server_host
POSTGRES_PORT=5432
POSTGRES_USER=your_postgres_username
POSTGRES_DB=your_database_name
DUCKLAKE_DATA_PATH=/var/lib/message-extract/data/
DUCKLAKE_METADATA_SCHEMA=gmail_messages
```

### Custom Configuration

You can customize data paths and schema names:

```env
# Custom data storage location
DUCKLAKE_DATA_PATH=/custom/data/path/

# Custom metadata schema
DUCKLAKE_METADATA_SCHEMA=custom_schema_name
```

## Service Management

### Start Service

```bash
docker-compose up -d
```

### Stop Service

```bash
docker-compose down
```

### Restart Service

```bash
docker-compose restart
```

### View Logs

```bash
docker-compose logs -f message-extract
```

### Update Service

```bash
docker-compose pull
docker-compose up -d --build
```

## API Usage

Once deployed, the service provides the following endpoints:

- `POST /extract` - Start background task to extract messages from Gmail
- `GET /extract/{task_id}/status` - Check task status and progress
- `GET /health` - Health check

### Example API Usage

```bash
# Start extraction task
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "from:example@gmail.com",
    "max_results": 1000,
    "fetch_config": {
      "messages_per_batch": 50,
      "response_format": "full",
      "max_retry_attempts": 3,
      "initial_retry_delay": 1.0
    }
  }'

# Check task status (poll this endpoint)
curl "http://localhost:8000/extract/abc123-def456-ghi789/status"
```

## Troubleshooting

### Common Issues

1. **PostgreSQL Connection Failed**
   - Verify PostgreSQL server is accessible
   - Check credentials in `.env` file
   - Ensure database exists

2. **DuckLake Configuration Failed**
   - Check database configuration in `.env` file
   - Verify PostgreSQL connection (for production mode)
   - Check DuckDB file permissions (for development mode)
   - Review logs for detailed error messages

3. **Gmail API Authentication Failed**
   - Ensure `token.json` is valid and not expired
   - Check Gmail API scopes configuration

### Logs

Check service logs for detailed error information:

```bash
docker-compose logs message-extract
```

### Health Check

Verify service is running:

```bash
curl http://localhost:8000/health
```

## Security Considerations

- Store sensitive credentials in environment variables or secret management systems
- Use encrypted DuckLake storage for production deployments
- Regularly rotate Gmail API tokens
- Secure PostgreSQL server with proper authentication and network access controls
- Consider using Docker secrets for production deployments
- Configure appropriate data paths and schema names for your environment

## Production Deployment

For production deployments:

1. Use a reverse proxy (nginx, traefik) for SSL termination
2. Implement proper logging and monitoring
3. Use Docker secrets or external secret management
4. Set up automated backups for PostgreSQL and DuckLake data
5. Configure proper resource limits and health checks
6. Use a container orchestration platform (Kubernetes, Docker Swarm)
7. Configure custom data paths and schema names for your environment
8. Monitor background task processing and implement task persistence (Redis/database)
