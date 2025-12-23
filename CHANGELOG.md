# Changelog

All notable changes to SHERPA V1 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-23

### Added
- Initial release of SHERPA V1 - Autonomous Coding Orchestrator
- FastAPI backend with async/await support on port 8001
- React + Vite frontend dashboard on port 3003
- SQLite database with aiosqlite for sessions, snippets, and work items
- AWS Bedrock Knowledge Base integration for semantic snippet search
- Built-in code snippets (7 patterns: security/auth, python/async, python/error-handling, react/hooks, testing/unit, api/rest, git/commits)
- Organizational snippets from S3 + Bedrock
- Project-specific snippets from ./sherpa/snippets/
- Local snippets from ./sherpa/snippets.local/
- Snippet hierarchy resolution (local > project > org > built-in)
- CLI with Click framework and Rich formatting
- CLI commands: init, generate, run, query, snippets, status, logs, serve
- Azure DevOps integration for work item management
- Git integration with GitPython for commit tracking
- File watching with watchdog for repository scanning
- Session management with pause/resume/stop controls
- Real-time progress updates via Server-Sent Events (SSE)
- Knowledge page for browsing and querying snippets
- Configuration management system
- Environment variable support
- CORS configuration for frontend-backend communication
- API versioning support
- Rate limiting for API endpoints
- Request validation with Pydantic models
- Error handling and recovery mechanisms
- Health check endpoints
- Metrics and monitoring
- Package structure with proper __init__.py files
- Requirements.txt with all dependencies
- Docker support with Dockerfile and docker-compose.yml
- CI/CD workflows documentation
- MIT License
- Comprehensive .gitignore

### Changed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- Secure credential storage
- Environment-based configuration
- Input validation and sanitization
- CORS properly configured

## [Unreleased]

### Planned
- WebSocket support for bidirectional real-time communication
- Unit tests with pytest
- Integration tests
- End-to-end tests with Playwright
- Code linting with ruff/black
- Type checking with pyright
- Pre-commit hooks
- Dark mode support for UI
- Tooltips and help text throughout UI
- Enhanced error recovery
- Concurrent session management improvements
