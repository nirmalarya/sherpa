# 🏔️ SHERPA V1 - Autonomous Coding Orchestrator

SHERPA is an orchestration platform that enhances autonomous coding agents with organizational knowledge. It operates in two modes:

1. **Generate Mode**: Create instruction files for interactive agents (Cursor, Claude, Copilot)
2. **Run Mode**: Execute autonomous coding harness with knowledge injection

## 🎯 Features

- **Knowledge Layer**: AWS Bedrock Knowledge Base integration for semantic code snippet search
- **Snippet Hierarchy**: Local > Project > Org > Built-in snippet resolution
- **Azure DevOps Integration**: Bidirectional sync with work items
- **Autonomous Harness**: Multi-agent system with fresh context windows
- **Real-time Dashboard**: React + Vite frontend with live progress tracking
- **CLI Tools**: Rich terminal interface for all operations

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm 9+
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd sherpa
```

2. Run setup script:
```bash
./init.sh
```

3. Configure AWS credentials (for Bedrock):
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

4. Initialize SHERPA:
```bash
source venv/bin/activate
sherpa init
```

### Running SHERPA

**Option 1: Full Stack (Backend + Frontend)**
```bash
./run.sh
```

**Option 2: Backend Only**
```bash
source venv/bin/activate
uvicorn sherpa.api.main:app --reload --port 8000
```

**Option 3: Frontend Only**
```bash
cd sherpa/frontend
npm run dev
```

**Access Points:**
- Backend API: http://localhost:8000
- Frontend UI: http://localhost:3001
- API Documentation: http://localhost:8000/docs

## 📚 CLI Commands

```bash
# Initialize Bedrock Knowledge Base
sherpa init

# Generate instruction files for interactive agents
sherpa generate

# Run autonomous harness with spec file
sherpa run --spec app_spec.txt

# Run with Azure DevOps work items
sherpa run --source azure-devops

# Query knowledge base
sherpa query "authentication patterns"

# List all snippets
sherpa snippets list

# Show active sessions
sherpa status

# View session logs
sherpa logs <session-id>

# Start web dashboard
sherpa serve
```

## 🏗️ Architecture

### Technology Stack

**Backend (Python)**
- FastAPI (async/await)
- SQLite with aiosqlite
- AWS Bedrock Knowledge Base
- Azure DevOps Python SDK
- GitPython

**Frontend (React)**
- React 18.3.1
- Vite 5.0.0
- Tailwind CSS 3.4.0
- React Router 6.20.0
- Recharts 2.10.0
- EventSource (SSE)

### Project Structure

```
sherpa/                      # Repository root
├── sherpa/                  # Python package (source code)
│   ├── api/                # FastAPI backend
│   │   ├── main.py        # API entry point
│   │   ├── routes/        # API endpoints
│   │   └── models/        # Database models
│   ├── cli/               # Click CLI commands
│   │   ├── main.py        # CLI entry point
│   │   └── commands/      # Command implementations
│   ├── core/              # Core business logic
│   │   ├── bedrock_client.py    # Bedrock KB client
│   │   ├── snippet_manager.py   # Snippet management
│   │   ├── db.py          # Database layer
│   │   ├── harness/       # Autonomous agent orchestration
│   │   └── integrations/  # Azure DevOps, Git
│   ├── frontend/          # React + Vite UI
│   │   ├── src/
│   │   │   ├── pages/     # Route components
│   │   │   ├── components/# Shared components
│   │   │   ├── lib/       # API client
│   │   │   └── styles/    # Tailwind CSS
│   │   └── package.json
│   ├── snippets/          # Built-in code snippets
│   ├── snippets.local/    # Local snippets (gitignored)
│   ├── data/              # SQLite database (gitignored)
│   └── logs/              # Application logs (gitignored)
│
├── tests/                  # Test suite
│   ├── test_config_manager.py
│   ├── test_database.py
│   └── ...
│
├── scripts/                # Utility scripts
│   ├── tests/             # Test verification scripts
│   ├── debug/             # Debug utilities
│   └── verify/            # Verification scripts
│
├── docs/                   # Documentation
│   ├── CICD.md
│   ├── DOCKER.md
│   └── ...
│
└── Configuration files:
    ├── README.md          # This file
    ├── requirements.txt   # Python dependencies
    ├── package.json       # Project metadata
    ├── init.sh            # Setup script
    ├── docker-compose.yml # Docker configuration
    ├── Dockerfile         # Container definition
    ├── pyproject.toml     # Python project config
    ├── pytest.ini         # Test configuration
    ├── CHANGELOG.md       # Version history
    ├── LICENSE            # MIT License
    └── .gitignore         # Git exclusions
```

## 📦 Snippet System

Snippets are resolved in this priority order:

1. **Local** (`./sherpa/snippets.local/`) - Your personal snippets (gitignored)
2. **Project** (`./sherpa/snippets/`) - Team/project snippets
3. **Org** (S3 + Bedrock) - Organization-wide snippets
4. **Built-in** - 7 default snippets included:
   - security/auth
   - python/error-handling
   - python/async
   - react/hooks
   - testing/unit
   - api/rest
   - git/commits

## 🔧 Configuration

Configuration is stored in `./sherpa/config.json`:

```json
{
  "bedrock_kb_id": "your-kb-id",
  "aws_region": "us-east-1",
  "azure_devops": {
    "organization": "your-org",
    "project": "your-project"
  }
}
```

## 🧪 Development

### Running Tests

```bash
# Backend tests
source venv/bin/activate
pytest

# Frontend tests
cd sherpa/frontend
npm test

# E2E tests
npm run test:e2e
```

### Code Quality

```bash
# Python linting
flake8 sherpa/
black sherpa/

# TypeScript linting
cd sherpa/frontend
npm run lint
```

## 📊 Dashboard Features

### HomePage
- Active sessions with progress bars
- Quick actions (New session, Generate files)
- Recent activity feed

### SessionsPage
- List all sessions with filtering
- Search by name/description
- Sort by date, status, progress

### SessionDetailPage
- Real-time progress (SSE)
- Feature checklist
- Live log streaming
- Git commit history
- Session controls (stop/pause/resume)

### KnowledgePage
- Search code snippets
- Browse by category
- Preview snippet content
- Add to project snippets

### SourcesPage
- Azure DevOps connector
- Connection testing
- Sync status monitoring

## 🔐 Security

- Credentials stored encrypted
- Sensitive data redacted from logs
- AWS credentials from environment variables
- .env files gitignored

## 📖 API Documentation

The full API documentation is available when running the backend server:

- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Main API Endpoints

- `GET /health` - Health check endpoint
- `GET /api/sessions` - List all sessions
- `POST /api/sessions` - Create new session
- `GET /api/sessions/{id}` - Get session details
- `GET /api/sessions/{id}/progress` - SSE stream for real-time progress
- `GET /api/snippets` - List all code snippets
- `POST /api/snippets/query` - Search snippets with semantic search
- `GET /api/azure-devops/work-items` - Fetch Azure DevOps work items
- `POST /api/azure-devops/sync` - Sync with Azure DevOps

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 SHERPA V1 Contributors

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/sherpa.git
   cd sherpa
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Workflow

1. **Set up development environment**:
   ```bash
   ./init.sh
   source venv/bin/activate
   ```

2. **Make your changes** following the code style guidelines
   - Backend: Follow PEP 8, use type hints
   - Frontend: Follow ESLint rules, use TypeScript

3. **Test your changes**:
   ```bash
   # Run backend tests
   pytest

   # Run frontend tests
   cd sherpa/frontend && npm test

   # Run E2E tests
   npm run test:e2e
   ```

4. **Lint your code**:
   ```bash
   # Python
   black sherpa/
   flake8 sherpa/

   # TypeScript
   cd sherpa/frontend && npm run lint
   ```

5. **Commit your changes** using conventional commits:
   ```bash
   git commit -m "feat: add new feature"
   git commit -m "fix: resolve bug in feature"
   git commit -m "docs: update README"
   ```

6. **Push to your fork** and **create a Pull Request**

### Contribution Guidelines

- **Write tests** for new features
- **Update documentation** for API changes
- **Keep commits atomic** and well-described
- **Follow existing code patterns** and architecture
- **Add changelog entry** in CHANGELOG.md for user-facing changes
- **Ensure all tests pass** before submitting PR

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on collaboration and learning

## 📞 Support

### Documentation

- **README**: This file for getting started
- **API Docs**: http://localhost:8000/docs (when server running)
- **CHANGELOG**: See [CHANGELOG.md](CHANGELOG.md) for version history

### Getting Help

- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions and share ideas

### Reporting Issues

When reporting a bug, please include:
- SHERPA version (`sherpa --version` or check setup.py)
- Operating system and version
- Python version
- Node.js version
- Steps to reproduce
- Expected vs actual behavior
- Error messages and logs (from `sherpa/logs/`)

### Feature Requests

We welcome feature requests! Please:
- Check existing issues first
- Describe the use case
- Explain how it benefits users
- Provide examples if possible

---

Built with ❤️ for autonomous coding excellence
