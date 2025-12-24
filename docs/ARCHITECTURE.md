# SHERPA Architecture

## Vision

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SHERPA - Autonomous Coding Engine                │
│                   "Agents that ship - your way"                     │
└─────────────────────────────────────────────────────────────────────┘

INPUT LAYER
┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│ Spec Files   │ File Loader  │ Azure DevOps │ Jira Tickets │ GitHub Issues│
│              │              │ Work Items   │   (future)   │   (future)   │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
                                    ↓
                        ┌──────────────────────┐
                        │  Spec Normalizer     │
                        │  (unified format)    │
                        └──────────────────────┘
                                    ↓
KNOWLEDGE LAYER
┌─────────────────────────────────────────────────────────────────────┐
│  Knowledge Resolver (hierarchy + semantic search)                   │
│  ┌──────────┬──────────┬──────────┬──────────┐                     │
│  │  LOCAL   │ PROJECT  │   ORG    │ BUILT-IN │                     │
│  │ snippets │ snippets │ (S3+KB)  │ snippets │                     │
│  └──────────┴──────────┴──────────┴──────────┘                     │
│  Priority: LOCAL > PROJECT > ORG > BUILT-IN                         │
│                                                                      │
│  ┌────────────────────────────────┐                                │
│  │   Brownfield Scanner           │                                │
│  │   (existing repo analysis)     │                                │
│  │   - README, docs, code         │                                │
│  │   - Tech stack detection       │                                │
│  │   - Pattern extraction         │                                │
│  └────────────────────────────────┘                                │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
                        ┌──────────────────────┐
                        │ Spec + Knowledge +   │
                        │   Repo Context       │
                        └──────────────────────┘
                                    ↓
SHERPA CORE
┌─────────────────────────────────────────────────────────────────────┐
│  GENERATE MODE                    │  RUN MODE                        │
│  ┌─────────────────────────┐      │  ┌──────────────────────────┐  │
│  │ Creates instruction files│      │  │  Autonomous Harness      │  │
│  │ • .cursor/rules/        │      │  │  ┌────────────────────┐  │  │
│  │ • CLAUDE.md             │      │  │  │ Initializer Agent  │  │  │
│  │ • copilot-instructions  │      │  │  │ • Read spec        │  │  │
│  │ • GEMINI.md (future)    │      │  │  │ • Generate features│  │  │
│  └─────────────────────────┘      │  │  └────────────────────┘  │  │
│                                    │  │           ↓              │  │
│                                    │  │  ┌────────────────────┐  │  │
│                                    │  │  │  Coding Agent      │  │  │
│                                    │  │  │ • Get next feature │  │  │
│                                    │  │  │ • Implement        │  │  │
│                                    │  │  │ • Test             │  │  │
│                                    │  │  │ • Mark passing     │  │  │
│                                    │  │  └────────────────────┘  │  │
│                                    │  │           ↓              │  │
│                                    │  │  Auto-continue loop      │  │
│                                    │  │  until all features done │  │
│                                    │  │                          │  │
│                                    │  │  Knowledge injected at   │  │
│                                    │  │  EVERY session:          │  │
│                                    │  │  • Relevant snippets     │  │
│                                    │  │  • Security checklists   │  │
│                                    │  │  • Best practices        │  │
│                                    │  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
OUTPUT LAYER
┌─────────────────────────────────────────────────────────────────────┐
│  GENERATE MODE                    │  RUN MODE                        │
│  • .cursor/rules/security.mdc     │  • Complete Application          │
│  • .cursor/rules/...              │  • CODING_STANDARDS.md           │
│  • CLAUDE.md                      │  • Relevant snippets             │
│  • copilot-instructions.md        │  • Git commits                   │
│  • GEMINI.md (future)             │  • Tests passing                 │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
PROGRESS TRACKING
┌─────────────────────────────────────────────────────────────────────┐
│  Local JSON          │  Jira Transitions  │  Azure DevOps           │
│  (feature_list.json) │  (ticket→done)     │  (Work item state +     │
│                      │  (future)          │   PR creation)          │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
                        Bi-directional: Read tickets IN, update progress OUT

SECURITY
┌─────────────────────────────────────────────────────────────────────┐
│  • Bash command allowlist                                           │
│  • Filesystem sandboxing                                            │
│  • MCP permissions                                                  │
│  • Credential management (PAT, API keys encrypted)                  │
└─────────────────────────────────────────────────────────────────────┘

USAGE
┌─────────────────────────────────────────────────────────────────────┐
│  sherpa init                     │  sherpa init generate (--agent X)│
│  sherpa generate (--spec <path>) │  sherpa run --source azure       │
│  sherpa scan                     │  query, status                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Current Implementation Status (v1.0)

### ✅ Fully Implemented

- **Knowledge Layer:** LOCAL > PROJECT > ORG > BUILT-IN hierarchy
- **Generate Mode:** .cursor/rules/, CLAUDE.md, copilot-instructions.md
- **Run Mode:** Autonomous harness with auto-continue
- **Azure DevOps:** Fetch work items, update progress, bidirectional sync
- **Security:** All 4 layers (bash, filesystem, MCP, credentials)
- **Progress Tracking:** Local JSON + Azure DevOps sync
- **CLI:** init, generate, run, query, status, logs, serve

### ⚠️ Partially Implemented

- **Spec Normalizer:** Basic support (needs enhancement)
- **PR Creation:** Git integration (not Azure DevOps PR API)
- **Org Snippets:** S3 client exists (needs testing with real bucket)

### ❌ Not Yet Implemented (Roadmap)

**v1.1 (Next Release - High Priority):**
- **Brownfield Scanner:** Analyze existing repos for context extraction
- **Enhancement Mode:** Improve existing projects (not just build new)
- **AGENT.md Generator:** For agent-based development workflows

**v2.0 (Future):**
- **GitHub Issues Integration:** Personal project management
- **Linear Integration:** Team collaboration and visibility
- **GEMINI.md Generator:** Google Gemini Code Assist support
- **Additional Integrations:** Extensible plugin system for other trackers

---

## Technology Stack

**Backend:**
- Python 3.9+ with FastAPI (async/await)
- SQLite with aiosqlite (async operations)
- AWS Bedrock Knowledge Base (semantic search)
- Azure DevOps Python SDK
- Click + Rich (beautiful CLI)

**Frontend:**
- React 18.3.1 with Vite 5.0.0
- Tailwind CSS 3.4.0
- React Router 6.20.0
- Recharts 2.10.0 (progress visualization)
- EventSource (SSE for real-time updates)

**Integrations:**
- AWS S3 (org snippets)
- AWS Bedrock KB (vector search)
- Azure DevOps (work items, repos)
- Git (commit tracking)

---

## Design Principles

1. **Knowledge-First:** Everything enhanced with organizational knowledge
2. **Hierarchy:** Local overrides project overrides org overrides built-in
3. **Two Modes:** Generate (interactive) + Run (autonomous)
4. **Autonomous:** Self-sufficient agent loops until completion
5. **Secure:** Multi-layer defense-in-depth
6. **Observable:** Real-time progress tracking
7. **Extensible:** Plugin architecture for new sources/trackers

