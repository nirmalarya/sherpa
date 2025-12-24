# SHERPA V1 - CI/CD Pipeline Documentation

## Overview

This document describes the CI/CD pipeline for SHERPA V1, implemented using GitHub Actions. The pipeline automates testing, building, security scanning, and deployment of the application.

## Workflow File

- **Location**: `.github/workflows/ci.yml`
- **Triggers**: Push to main/master/develop, Pull Requests, Manual dispatch
- **Status**: ✅ Fully configured and tested

## Pipeline Jobs

### 1. Backend Tests (`backend-tests`)

**Purpose**: Test and lint Python backend code

**Steps**:
- Checkout code
- Set up Python 3.12 with pip caching
- Install dependencies (FastAPI, uvicorn, aiosqlite, pytest, etc.)
- Lint with flake8 (syntax errors and code quality)
- Check code formatting with black
- Check import sorting with isort
- Run pytest with coverage reporting
- Upload coverage reports to Codecov

**Environment Variables**:
- `SHERPA_ENV=testing`
- `DATABASE_URL=sqlite:///./sherpa/data/test.db`

**Outputs**:
- Coverage reports (XML, HTML, terminal)
- Test results

### 2. Frontend Tests (`frontend-tests`)

**Purpose**: Test, lint, and build React frontend

**Steps**:
- Checkout code
- Set up Node.js 20 with npm caching
- Install dependencies with `npm ci`
- Lint frontend code (ESLint)
- Type check (if TypeScript configured)
- Run frontend tests (if configured)
- Build production bundle
- Upload build artifacts

**Artifacts**:
- Frontend build output (`sherpa/frontend/dist`)
- Retention: 7 days

### 3. Docker Build (`docker-build`)

**Purpose**: Build and test Docker images

**Dependencies**: Requires `backend-tests` and `frontend-tests` to pass

**Steps**:
- Checkout code
- Set up Docker Buildx
- Build backend Docker image (with layer caching)
- Build frontend Docker image (with layer caching)
- Start services with Docker Compose
- Verify backend health endpoint
- Verify frontend accessibility
- Cleanup containers

**Caching**: Uses GitHub Actions cache for Docker layers

### 4. Integration Tests (`integration-tests`)

**Purpose**: Test API endpoints end-to-end

**Dependencies**: Requires `backend-tests` and `frontend-tests` to pass

**Steps**:
- Checkout code
- Set up Python 3.12
- Install dependencies
- Start backend server on port 8001
- Test health endpoint
- Test sessions API endpoint
- Test snippets API endpoint

**Test Commands**:
```python
# Health check
httpx.get('http://localhost:8001/health')

# Sessions endpoint
httpx.get('http://localhost:8001/api/sessions')

# Snippets endpoint
httpx.get('http://localhost:8001/api/snippets')
```

### 5. Security Scan (`security-scan`)

**Purpose**: Scan for vulnerabilities

**Steps**:
- Checkout code
- Run Trivy vulnerability scanner
- Generate SARIF report
- Upload results to GitHub Security tab

**Note**: Continues on error to not block the pipeline

### 6. Code Quality (`code-quality`)

**Purpose**: Static analysis with CodeQL

**Steps**:
- Checkout code
- Initialize CodeQL for Python and JavaScript
- Perform automated security analysis
- Report findings to GitHub Security

**Note**: Continues on error to not block the pipeline

### 7. Deploy (`deploy`)

**Purpose**: Deployment to production (placeholder)

**Conditions**:
- Only runs on `main` branch
- Only runs on push events (not PRs)
- Requires all previous jobs to succeed

**Steps**:
- Checkout code
- Create deployment summary
- Placeholder for actual deployment logic

**Current Status**: Configured as placeholder - customize for your deployment target

## Trigger Conditions

### Push Events
```yaml
on:
  push:
    branches: [main, master, develop]
```

Triggers on pushes to main, master, or develop branches.

### Pull Request Events
```yaml
on:
  pull_request:
    branches: [main, master, develop]
```

Triggers on PRs targeting main, master, or develop branches.

### Manual Dispatch
```yaml
on:
  workflow_dispatch:
```

Can be triggered manually from the GitHub Actions tab.

## Environment Variables

### Global
- `PYTHON_VERSION: '3.12'` - Python version for all jobs
- `NODE_VERSION: '20'` - Node.js version for frontend jobs

### Backend Tests
- `SHERPA_ENV: testing` - Set environment to testing mode
- `DATABASE_URL: sqlite:///./sherpa/data/test.db` - Test database path

## Caching Strategy

### Python Dependencies
```yaml
uses: actions/setup-python@v5
with:
  cache: 'pip'
```

Caches pip dependencies based on `requirements.txt`.

### Node.js Dependencies
```yaml
uses: actions/setup-node@v4
with:
  cache: 'npm'
  cache-dependency-path: sherpa/frontend/package-lock.json
```

Caches npm dependencies based on `package-lock.json`.

### Docker Layers
```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

Caches Docker build layers in GitHub Actions cache.

## Artifacts

### Frontend Build
- **Name**: `frontend-build`
- **Path**: `sherpa/frontend/dist`
- **Retention**: 7 days
- **Use Case**: Download production build for manual inspection or deployment

## Security Features

### 1. Vulnerability Scanning
- Tool: Trivy
- Scope: Filesystem scan
- Output: SARIF format for GitHub Security

### 2. Code Analysis
- Tool: CodeQL
- Languages: Python, JavaScript
- Scope: Static security analysis

### 3. Dependency Scanning
- Automatic: GitHub Dependabot (if enabled in repo settings)
- Manual: `npm audit`, `pip-audit`

## Deployment Options

### Option 1: AWS ECS (Elastic Container Service)
```yaml
- name: Deploy to AWS ECS
  run: |
    # Configure AWS credentials
    # Push images to ECR
    # Update ECS service
```

### Option 2: Azure Container Apps
```yaml
- name: Deploy to Azure Container Apps
  run: |
    # Login to Azure
    # Push images to ACR
    # Update Container App
```

### Option 3: Google Cloud Run
```yaml
- name: Deploy to Cloud Run
  run: |
    # Authenticate with GCP
    # Push images to GCR
    # Deploy to Cloud Run
```

### Option 4: Docker Swarm / Kubernetes
```yaml
- name: Deploy to Kubernetes
  run: |
    # Configure kubectl
    # Apply manifests
    # Rollout deployment
```

## Customization Guide

### Adding New Tests

1. **Backend Tests**:
   - Add test files to `sherpa/tests/`
   - Tests will be automatically discovered by pytest

2. **Frontend Tests**:
   - Add test files to `sherpa/frontend/src/**/*.test.js`
   - Configure test script in `package.json`

3. **Integration Tests**:
   - Add test commands to `integration-tests` job
   - Use httpx for API testing

### Modifying Build Steps

1. **Backend Build**:
   - Edit `Dockerfile` in project root
   - Update `docker-build` job if needed

2. **Frontend Build**:
   - Edit `sherpa/frontend/Dockerfile`
   - Update `frontend-tests` build step

### Configuring Deployment

1. Choose deployment target (AWS, Azure, GCP, etc.)
2. Add secrets to GitHub repository settings:
   - Go to Settings → Secrets → Actions
   - Add required credentials (API keys, tokens, etc.)
3. Update `deploy` job in workflow:
   - Replace placeholder with actual deployment commands
   - Reference secrets using `${{ secrets.SECRET_NAME }}`

## GitHub Secrets Required

### For Deployment (Optional)
- `AWS_ACCESS_KEY_ID` - AWS credentials
- `AWS_SECRET_ACCESS_KEY` - AWS credentials
- `AZURE_CREDENTIALS` - Azure service principal
- `GCP_SA_KEY` - Google Cloud service account key

### For External Services (Optional)
- `CODECOV_TOKEN` - Codecov upload token
- `SLACK_WEBHOOK` - Notifications
- `DISCORD_WEBHOOK` - Notifications

## Monitoring and Notifications

### GitHub Actions UI
- Navigate to repository → Actions tab
- View workflow runs, logs, and artifacts
- Download build artifacts if needed

### Status Badges
Add to README.md:
```markdown
![CI/CD Pipeline](https://github.com/YOUR_USERNAME/sherpa/actions/workflows/ci.yml/badge.svg)
```

### Notifications
Configure in GitHub repository settings:
- Settings → Notifications
- Choose email/Slack/Discord integrations

## Troubleshooting

### Job Fails on Backend Tests
1. Check Python version compatibility
2. Verify all dependencies in `requirements.txt`
3. Review test logs in Actions tab
4. Run tests locally: `pytest sherpa/tests -v`

### Job Fails on Frontend Tests
1. Check Node.js version compatibility
2. Verify `package-lock.json` is committed
3. Review build logs in Actions tab
4. Run locally: `cd sherpa/frontend && npm ci && npm run build`

### Docker Build Fails
1. Check Dockerfile syntax
2. Verify base images are accessible
3. Review Docker build logs
4. Test locally: `docker build . -t sherpa-backend:test`

### Integration Tests Fail
1. Verify backend starts correctly
2. Check port availability (8001)
3. Review server logs
4. Test locally: `python -m uvicorn sherpa.api.main:app --port 8001`

## Performance Optimization

### Caching
- ✅ Python dependencies cached
- ✅ Node.js dependencies cached
- ✅ Docker layers cached
- Estimated time savings: 50-70% on subsequent runs

### Parallelization
- ✅ Backend and frontend tests run in parallel
- ✅ Security scanning runs independently
- ✅ Code quality checks run independently

### Job Dependencies
```
backend-tests ─┐
                ├──> docker-build ──> deploy
frontend-tests ┘     └──> integration-tests
```

## Best Practices

### 1. Always Run Tests Locally First
```bash
# Backend tests
pytest sherpa/tests -v

# Frontend tests
cd sherpa/frontend && npm test

# Linting
flake8 sherpa
black --check sherpa
cd sherpa/frontend && npm run lint
```

### 2. Commit Message Format
```
feat: Add user authentication endpoint

- Implemented JWT-based auth
- Added tests for auth flow
- Updated API documentation

Closes #123
```

### 3. Pull Request Workflow
1. Create feature branch
2. Implement changes with tests
3. Push to GitHub
4. CI/CD runs automatically
5. Review results in Actions tab
6. Request code review
7. Merge when all checks pass

### 4. Monitoring
- Check Actions tab regularly
- Fix failing tests immediately
- Keep dependencies updated
- Review security scan results

## Maintenance

### Regular Updates
- **Monthly**: Update GitHub Actions versions
- **Monthly**: Update base images (Python, Node.js)
- **Weekly**: Review security scan results
- **Weekly**: Update dependencies if needed

### Dependency Updates
```bash
# Backend
pip list --outdated
pip install -U package-name

# Frontend
npm outdated
npm update package-name
```

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Action](https://github.com/marketplace/actions/build-and-push-docker-images)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [Trivy Security Scanner](https://github.com/aquasecurity/trivy)

## Support

For issues with the CI/CD pipeline:
1. Check workflow logs in GitHub Actions tab
2. Review this documentation
3. Run tests locally to reproduce issues
4. Consult team lead or DevOps engineer

---

**Last Updated**: December 23, 2025
**Version**: 1.0.0
**Status**: ✅ Production Ready
