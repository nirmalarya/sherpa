# SHERPA V1 - Docker Deployment Guide

## Overview

This guide provides instructions for building and running SHERPA V1 in Docker containers.

## Prerequisites

- Docker installed (version 20.10 or higher)
- Docker Compose (optional, for multi-container setup)
- 2GB free disk space for images

## Quick Start

### Build the Image

```bash
docker build -t sherpa-backend:latest .
```

This creates a production-ready Docker image with:
- Python 3.12 slim base
- All dependencies installed
- Multi-stage build for optimization
- Non-root user for security
- Health checks configured

### Run the Container

**Basic Run:**
```bash
docker run -p 8000:8000 sherpa-backend:latest
```

**With Environment Variables:**
```bash
docker run -p 8000:8000 \
  -e SHERPA_ENV=production \
  -e SHERPA_PORT=8000 \
  sherpa-backend:latest
```

**With Volume Mounts (Persistent Data):**
```bash
docker run -p 8000:8000 \
  -v $(pwd)/sherpa/data:/app/sherpa/data \
  -v $(pwd)/sherpa/logs:/app/sherpa/logs \
  -v $(pwd)/sherpa/snippets.local:/app/sherpa/snippets.local \
  sherpa-backend:latest
```

**Development Mode (Live Reload):**
```bash
docker run -p 8001:8000 \
  -e SHERPA_ENV=development \
  -v $(pwd)/sherpa:/app/sherpa \
  sherpa-backend:latest
```

## Verification Steps

### Step 1: Build the Image

```bash
docker build -t sherpa-backend:latest .
```

Expected output:
- Multi-stage build completes successfully
- Image size approximately 500-600MB
- No errors during dependency installation

### Step 2: Verify Image Built Successfully

```bash
docker images | grep sherpa-backend
```

Expected output:
```
sherpa-backend   latest   <image-id>   <time>   ~500MB
```

### Step 3: Run the Container

```bash
docker run -d --name sherpa-test -p 8000:8000 sherpa-backend:latest
```

Expected output:
- Container ID displayed
- Container starts without errors

### Step 4: Verify Application Starts

```bash
docker logs sherpa-test
```

Expected output:
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 5: Verify API Accessible from Host

```bash
curl http://localhost:8000/health
```

Expected output:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-12-23T...",
  "environment": "production"
}
```

### Step 6: Verify Environment Variables Work

```bash
docker run -p 8000:8000 \
  -e SHERPA_ENV=staging \
  sherpa-backend:latest
```

Then check:
```bash
curl http://localhost:8000/api/environment
```

Expected output should show `"environment": "staging"`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SHERPA_ENV` | `production` | Environment mode (development/staging/production) |
| `SHERPA_HOST` | `0.0.0.0` | Host to bind to |
| `SHERPA_PORT` | `8000` | Port to listen on |
| `ANTHROPIC_API_KEY` | - | API key for Anthropic services (optional) |
| `AWS_ACCESS_KEY_ID` | - | AWS access key for Bedrock (optional) |
| `AWS_SECRET_ACCESS_KEY` | - | AWS secret key for Bedrock (optional) |
| `AWS_REGION` | `us-east-1` | AWS region for Bedrock (optional) |

## Volume Mounts

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `./sherpa/data` | `/app/sherpa/data` | SQLite database persistence |
| `./sherpa/logs` | `/app/sherpa/logs` | Application logs |
| `./sherpa/snippets.local` | `/app/sherpa/snippets.local` | Local code snippets |

## Health Checks

The container includes built-in health checks:

```bash
docker inspect --format='{{.State.Health.Status}}' sherpa-test
```

Expected output: `healthy`

Health check configuration:
- **Interval:** 30 seconds
- **Timeout:** 3 seconds
- **Start Period:** 5 seconds
- **Retries:** 3

## Container Management

### Start Container
```bash
docker start sherpa-test
```

### Stop Container
```bash
docker stop sherpa-test
```

### View Logs
```bash
docker logs -f sherpa-test
```

### Execute Commands in Container
```bash
docker exec -it sherpa-test /bin/bash
```

### Remove Container
```bash
docker rm -f sherpa-test
```

### Remove Image
```bash
docker rmi sherpa-backend:latest
```

## Multi-Stage Build Details

The Dockerfile uses a multi-stage build for optimization:

1. **Base Stage:** Sets up Python 3.12 and system dependencies
2. **Builder Stage:** Installs Python packages
3. **Production Stage:** Copies only necessary files

Benefits:
- Smaller final image size
- Faster builds (layer caching)
- Better security (minimal attack surface)
- Non-root user execution

## Security Features

- **Non-root User:** Application runs as user `sherpa` (UID 1000)
- **Minimal Base Image:** Uses `python:3.12-slim` (not full Python image)
- **No Unnecessary Files:** `.dockerignore` excludes development files
- **Health Checks:** Automatic container health monitoring
- **Production Defaults:** Secure defaults for environment variables

## Troubleshooting

### Container Won't Start

Check logs:
```bash
docker logs sherpa-test
```

Common issues:
- Port 8000 already in use (change with `-p 8001:8000`)
- Missing database directory (create with `mkdir -p sherpa/data`)

### API Not Accessible

Verify container is running:
```bash
docker ps | grep sherpa-test
```

Check port mapping:
```bash
docker port sherpa-test
```

Test health endpoint:
```bash
curl http://localhost:8000/health
```

### Database Permission Issues

Ensure volumes have correct permissions:
```bash
chmod -R 755 sherpa/data sherpa/logs sherpa/snippets.local
```

### Build Fails

Check Docker version:
```bash
docker --version
```

Clean build cache:
```bash
docker build --no-cache -t sherpa-backend:latest .
```

## Production Deployment

### Best Practices

1. **Use Environment Variables:** Don't hardcode secrets
2. **Mount Volumes:** Persist data outside containers
3. **Set Resource Limits:** Prevent resource exhaustion
4. **Enable Health Checks:** Monitor container health
5. **Use Docker Compose:** For multi-container setups
6. **Implement Logging:** Centralize logs with volume mounts
7. **Regular Updates:** Keep base image updated

### Example Production Run

```bash
docker run -d \
  --name sherpa-production \
  --restart unless-stopped \
  -p 8000:8000 \
  -e SHERPA_ENV=production \
  -e ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY} \
  -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
  -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
  -v /var/sherpa/data:/app/sherpa/data \
  -v /var/sherpa/logs:/app/sherpa/logs \
  --memory="2g" \
  --cpus="2" \
  --health-cmd="python -c 'import requests; requests.get(\"http://localhost:8000/health\").raise_for_status()'" \
  --health-interval=30s \
  --health-timeout=3s \
  --health-retries=3 \
  sherpa-backend:latest
```

## Next Steps

- See `docker-compose.yml` for multi-container setup
- See `.github/workflows/` for CI/CD integration
- See `README.md` for general documentation

## Support

For issues or questions:
- Check logs: `docker logs sherpa-test`
- Verify health: `docker inspect sherpa-test`
- Review documentation: This file and `README.md`
