# Gmail DataLake Extractor Deployment Guide

This guide explains how to deploy the message-extract service using Docker with DuckLake integration and configurable storage backends.

## Prerequisites

- Docker and Docker Compose installed
- Gmail API credentials (`token.json` file)
- DuckLake setup configuration files
- For production: External PostgreSQL server and S3-compatible storage (optional)

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

# DuckLake Configuration
DUCKLAKE_SETUP_PATH=/app/data/ducklake_setup

# Gmail API Configuration
GMAIL_API_TOKEN_PATH=/app/data/token.json
GMAIL_API_SCOPES='["https://www.googleapis.com/auth/gmail.readonly"]'
```

### 2. Prepare Secrets Directory

Ensure your `secrets/` directory contains:

- `token.json` - Gmail API authentication token
- `ducklake_setup.sql` - DuckLake configuration for production
- `ducklake_setup.dev.sql` - DuckLake configuration for development

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
curl http://localhost:8080/health
```

### 5. Automatic DuckLake Setup

DuckLake is automatically configured on first run using the setup SQL files:

- **Development**: Uses `ducklake_setup.dev.sql` with local DuckDB for metadata catalog
- **Production**: Uses `ducklake_setup.sql` with PostgreSQL for metadata catalog and S3 storage

## DuckLake Configuration

The service uses SQL setup files to configure DuckLake:

### Development Configuration (`ducklake_setup.dev.sql`)

```sql
CREATE secret my_ducklake (
    TYPE ducklake,
    metadata_path './data/messages.duckdb',
    data_path './data/',
    metadata_schema 'messages',
    encrypted FALSE
);
```

### Production Configuration (`ducklake_setup.sql`)

```sql
SET s3_region = 'your-s3-region';
SET s3_url_style = 'path';
SET s3_endpoint = 'your-s3-endpoint:port';
SET s3_use_ssl = true;
SET s3_access_key_id = 'your-s3-access-key';
SET s3_secret_access_key = 'your-s3-secret-key';
CREATE secret my_ducklake (
    TYPE ducklake,
    metadata_path 'postgres: user=your-postgres-user password=your-postgres-password host=your-postgres-host port=your-postgres-port dbname=your-postgres-db',
    data_path 's3://your-bucket-name',
    metadata_schema 'your-schema-name',
    encrypted true
);
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
curl -X POST "http://localhost:8080/extract" \
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
curl "http://localhost:8080/extract/abc123-def456-ghi789/status"
```

## Troubleshooting

### Common Issues

1. **DuckLake Configuration Failed**
   - Verify DuckLake setup SQL files are present in `secrets/` directory
   - Check PostgreSQL connection (for production mode)
   - Verify S3 credentials and endpoint (for production mode)
   - Check DuckDB file permissions (for development mode)
   - Review logs for detailed error messages

2. **Gmail API Authentication Failed**
   - Ensure `token.json` is valid and not expired
   - Check Gmail API scopes configuration
   - Verify token has `gmail.readonly` scope

3. **Container Startup Issues**
   - Check Docker secrets are properly mounted
   - Verify environment variables are set correctly
   - Ensure data directory has proper permissions

### Logs

Check service logs for detailed error information:

```bash
docker-compose logs message-extract
```

### Health Check

Verify service is running:

```bash
curl http://localhost:8080/health
```

## Security Considerations

- Store sensitive credentials in Docker secrets or secret management systems
- Use encrypted DuckLake storage for production deployments
- Regularly rotate Gmail API tokens
- Secure PostgreSQL server with proper authentication and network access controls
- Use S3-compatible storage with proper IAM policies
- Configure appropriate data paths and schema names for your environment
- Keep DuckLake setup SQL files secure and version-controlled

## Production Deployment

For production deployments:

1. Use a reverse proxy (nginx, traefik) for SSL termination
2. Implement proper logging and monitoring
3. Use Docker secrets or external secret management
4. Set up automated backups for PostgreSQL and S3 storage
5. Configure proper resource limits and health checks
6. Use a container orchestration platform (Kubernetes, Docker Swarm)
7. Configure DuckLake with encrypted storage and proper access controls
8. Monitor background task processing and implement task persistence (Redis/database)
9. Set up proper S3 bucket policies and IAM roles
10. Configure PostgreSQL with connection pooling and proper security
