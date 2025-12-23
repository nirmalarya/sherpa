# Docker Compose Guide for SHERPA

This guide explains how to run SHERPA using Docker Compose for multi-container local development and production deployments.

## Overview

The Docker Compose setup includes three services:

1. **Backend** - FastAPI application (Python 3.12)
2. **Frontend** - React + Vite dashboard (Node 20)
3. **Database** - Volume for SQLite persistence

All services are connected via a private network and communicate seamlessly.

## Quick Start

### Prerequisites

- Docker 20.10+ installed
- Docker Compose 2.0+ installed
- 4GB+ RAM available
- Ports 8000, 3001 available

### Start All Services

```bash
# Start all services in detached mode
docker-compose up -d

# View logs from all services
docker-compose logs -f

# View logs from specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Access the Application

- **Frontend Dashboard**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Stop All Services

```bash
# Stop services (keeps containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop, remove containers, and remove volumes
docker-compose down -v
```

## Service Details

### Backend Service

**Configuration:**
- **Container Name**: `sherpa-backend`
- **Port**: 8000
- **Base Image**: python:3.12-slim
- **Build Context**: Project root
- **Dockerfile**: ./Dockerfile

**Environment Variables:**
- `SHERPA_ENV` - Environment (development/staging/production)
- `SHERPA_HOST` - Host binding (default: 0.0.0.0)
- `SHERPA_PORT` - Port binding (default: 8000)
- `ANTHROPIC_API_KEY` - Optional, for AI services
- `AWS_ACCESS_KEY_ID` - Optional, for Bedrock KB
- `AWS_SECRET_ACCESS_KEY` - Optional, for Bedrock KB
- `AWS_REGION` - AWS region (default: us-east-1)

**Volume Mounts:**
- `./sherpa/data:/app/sherpa/data` - Database persistence
- `./sherpa/logs:/app/sherpa/logs` - Application logs
- `./sherpa/snippets.local:/app/sherpa/snippets.local` - Local snippets

**Health Check:**
- Endpoint: `/health`
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3

### Frontend Service

**Configuration:**
- **Container Name**: `sherpa-frontend`
- **Port**: 3001
- **Base Image**: node:20-alpine
- **Build Context**: ./sherpa/frontend
- **Dockerfile**: ./sherpa/frontend/Dockerfile

**Environment Variables:**
- `VITE_API_URL` - Backend API URL (default: http://localhost:8000)
- `NODE_ENV` - Node environment (production)

**Build Process:**
1. Install dependencies with `npm ci`
2. Build production bundle with `npm run build`
3. Serve static files with `serve` package
4. Runs on port 3001

**Health Check:**
- Endpoint: `/` (root)
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3

### Database Service

**Configuration:**
- **Container Name**: `sherpa-db`
- **Base Image**: alpine:3.18
- **Purpose**: Volume mount placeholder for SQLite

**Volume:**
- `db-data:/data` - Named volume for database files

**Note:** SHERPA uses SQLite which is file-based. This service provides a placeholder for future PostgreSQL/MySQL integration. The actual database file is stored in the backend's `./sherpa/data` volume mount.

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# SHERPA Environment Configuration
SHERPA_ENV=development

# API Keys (Optional)
ANTHROPIC_API_KEY=your_api_key_here

# AWS Credentials (Optional)
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
```

Docker Compose automatically loads this file.

### Development Mode

For development with live code reloading:

```bash
# Override with development compose file (if created)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Or set environment variable
SHERPA_ENV=development docker-compose up
```

### Production Mode

For production deployment:

```bash
# Set production environment
SHERPA_ENV=production docker-compose up -d

# View production logs
docker-compose logs -f
```

## Common Commands

### Building

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend

# Build without cache
docker-compose build --no-cache

# Pull latest images
docker-compose pull
```

### Running

```bash
# Start services
docker-compose up                  # Foreground
docker-compose up -d               # Detached mode
docker-compose up --build          # Rebuild before starting

# Start specific service
docker-compose up backend
docker-compose up frontend

# Scale service (if stateless)
docker-compose up --scale backend=3
```

### Monitoring

```bash
# View running containers
docker-compose ps

# View resource usage
docker stats

# View logs
docker-compose logs                # All services
docker-compose logs -f backend     # Follow backend logs
docker-compose logs --tail=100     # Last 100 lines
docker-compose logs --since 10m    # Last 10 minutes

# Execute commands in containers
docker-compose exec backend /bin/sh
docker-compose exec frontend /bin/sh
```

### Cleaning Up

```bash
# Stop services
docker-compose stop

# Remove containers
docker-compose rm

# Remove containers and volumes
docker-compose down -v

# Remove everything including images
docker-compose down --rmi all -v

# Prune unused Docker resources
docker system prune -a
```

## Networking

### Service Communication

Services communicate using service names as hostnames:

- Backend → Database: `http://db:5432` (future PostgreSQL)
- Frontend → Backend: `http://backend:8000` (internal)
- Host → Frontend: `http://localhost:3001`
- Host → Backend: `http://localhost:8000`

The `sherpa-network` bridge network connects all services.

### Network Inspection

```bash
# Inspect network
docker network inspect sherpa_sherpa-network

# Test connectivity
docker-compose exec backend ping frontend
docker-compose exec frontend ping backend
```

## Volume Management

### Persistent Data

Data persists in these locations:

1. **Backend Data**: `./sherpa/data` (bind mount)
2. **Backend Logs**: `./sherpa/logs` (bind mount)
3. **Local Snippets**: `./sherpa/snippets.local` (bind mount)
4. **Database Volume**: `db-data` (named volume)

### Volume Commands

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect sherpa_db-data

# Backup database
docker run --rm -v sherpa_db-data:/data -v $(pwd):/backup alpine tar czf /backup/db-backup.tar.gz -C /data .

# Restore database
docker run --rm -v sherpa_db-data:/data -v $(pwd):/backup alpine tar xzf /backup/db-backup.tar.gz -C /data
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs backend

# Check container status
docker-compose ps

# Inspect container
docker inspect sherpa-backend

# Start in debug mode
docker-compose up --no-deps backend
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000
lsof -i :3001

# Stop conflicting service or change ports in docker-compose.yml
ports:
  - "8001:8000"  # Map to different host port
```

### Build Failures

```bash
# Clean build cache
docker-compose build --no-cache

# Check Dockerfile syntax
docker build -t test -f Dockerfile .

# Verify build context
docker-compose config
```

### Connectivity Issues

```bash
# Verify network exists
docker network ls

# Test DNS resolution
docker-compose exec backend ping frontend

# Check firewall rules
docker-compose exec backend wget http://frontend:3001

# Restart networking
docker-compose down
docker-compose up
```

### Health Check Failures

```bash
# Check health status
docker-compose ps

# View health check logs
docker inspect --format='{{json .State.Health}}' sherpa-backend | python -m json.tool

# Manually test health endpoint
docker-compose exec backend wget -O- http://localhost:8000/health
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Limit container resources
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

# Check disk space
docker system df
```

## Best Practices

### Development

1. Use bind mounts for code (enables live reload)
2. Set `SHERPA_ENV=development`
3. Keep logs visible with `docker-compose up` (no -d)
4. Use `--build` to ensure latest code

### Production

1. Use named volumes for data persistence
2. Set `SHERPA_ENV=production`
3. Run detached with `docker-compose up -d`
4. Configure resource limits
5. Set up log rotation
6. Use health checks for monitoring
7. Implement backup strategy
8. Use secrets management for API keys

### Security

1. **Never commit secrets** to docker-compose.yml
2. Use environment variables from `.env` file
3. Run containers as non-root users (already configured)
4. Keep images updated: `docker-compose pull && docker-compose up -d`
5. Scan images for vulnerabilities: `docker scan sherpa-backend`
6. Use private networks for service communication
7. Limit exposed ports to necessary ones only

### Maintenance

1. Regular updates: `docker-compose pull`
2. Clean unused resources: `docker system prune`
3. Monitor logs: `docker-compose logs -f`
4. Backup volumes regularly
5. Test disaster recovery procedures
6. Document custom configurations

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Docker Compose CI

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Start services
        run: docker-compose up -d
      - name: Wait for services
        run: sleep 10
      - name: Test backend
        run: curl http://localhost:8000/health
      - name: Test frontend
        run: curl http://localhost:3001
      - name: Cleanup
        run: docker-compose down -v
```

## Deployment Options

### Local Development
```bash
docker-compose up --build
```

### AWS ECS
Use `docker-compose` with ECS CLI or convert to CloudFormation.

### Kubernetes
Use `kompose` to convert docker-compose.yml to Kubernetes manifests:
```bash
kompose convert
kubectl apply -f .
```

### Docker Swarm
```bash
docker stack deploy -c docker-compose.yml sherpa
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [SHERPA Docker Guide](./DOCKER.md)
- [SHERPA README](./README.md)

## Support

For issues and questions:
1. Check logs: `docker-compose logs`
2. Review health checks: `docker-compose ps`
3. Inspect containers: `docker inspect`
4. Consult troubleshooting section above

---

**Last Updated**: December 2024
**Version**: 1.0.0
