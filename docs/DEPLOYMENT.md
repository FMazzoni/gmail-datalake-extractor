# Message Extract Deployment Guide

This guide explains how to deploy the message-extract service using Docker with an external PostgreSQL server and DuckLake secrets.

## Prerequisites

- Docker and Docker Compose installed
- External PostgreSQL server accessible from the deployment environment
- Gmail API credentials (`token.json` file)

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

# PostgreSQL Configuration (external server)
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

### 5. Automatic DuckLake Secret Setup

The DuckLake secret is automatically created on first run. No manual intervention required.

## DuckLake Secret Management

The service uses DuckLake secrets to securely store PostgreSQL connection information. The secret is automatically created on first run and contains:

- PostgreSQL connection string
- Data storage path
- Metadata schema configuration
- Encryption settings

### Secret Structure

The DuckLake secret is created with the following configuration:

```sql
CREATE PERSISTENT SECRET message_extract_ducklake (
    TYPE ducklake,
    METADATA_PATH 'postgres://user:password@host:port/database',
    DATA_PATH '/app/data',
    METADATA_PARAMETERS MAP {
        'TYPE': 'postgres',
        'SECRET': 'message_extract_ducklake_postgres'
    }
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

- `POST /extract` - Extract messages from Gmail
- `GET /health` - Health check

### Example API Call

```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "from:example@gmail.com",
    "max_results": 100,
    "fetch_config": {
      "messages_per_batch": 50,
      "response_format": "metadata",
      "metadata_headers": ["From", "Subject", "Date", "To"],
      "max_retry_attempts": 3,
      "initial_retry_delay": 1.0
    }
  }'
```

## Troubleshooting

### Common Issues

1. **PostgreSQL Connection Failed**
   - Verify PostgreSQL server is accessible
   - Check credentials in `.env` file
   - Ensure database exists

2. **DuckLake Secret Creation Failed**
   - Check PostgreSQL permissions
   - Verify DuckLake extension is available
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

## Production Deployment

For production deployments:

1. Use a reverse proxy (nginx, traefik) for SSL termination
2. Implement proper logging and monitoring
3. Use Docker secrets or external secret management
4. Set up automated backups for PostgreSQL and DuckLake data
5. Configure proper resource limits and health checks
6. Use a container orchestration platform (Kubernetes, Docker Swarm)
