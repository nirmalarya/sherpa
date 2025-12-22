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
sherpa/
├── api/                    # FastAPI backend
│   ├── main.py            # API entry point
│   ├── routes/            # API endpoints
│   └── models/            # Database models
├── cli/                   # Click CLI commands
│   └── commands/          # Command implementations
├── core/                  # Core business logic
│   ├── knowledge/         # Bedrock KB client
│   ├── harness/          # Autonomous agent orchestration
│   └── integrations/     # Azure DevOps, Git
├── frontend/             # React + Vite UI
│   ├── src/
│   │   ├── pages/        # Route components
│   │   ├── components/   # Shared components
│   │   ├── lib/          # API client
│   │   └── styles/       # Tailwind CSS
│   └── package.json
├── snippets/             # Project-level code snippets
├── snippets.local/       # Local code snippets (gitignored)
├── data/                 # SQLite database
└── logs/                 # Application logs
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

## 📝 License

[License information to be added]

## 🤝 Contributing

[Contributing guidelines to be added]

## 📞 Support

[Support information to be added]

---

Built with ❤️ for autonomous coding excellence
