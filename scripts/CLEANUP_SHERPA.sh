#!/bin/bash
# Clean up SHERPA file organization

set -e

echo "🧹 Cleaning up SHERPA file organization..."

# Create directories
mkdir -p .sessions
mkdir -p scripts/tests
mkdir -p scripts/debug
mkdir -p scripts/verify
mkdir -p docs

# Move session summaries
echo "Moving session files..."
mv SESSION_*.md .sessions/ 2>/dev/null || true
mv NEXT_SESSION_*.md .sessions/ 2>/dev/null || true
mv session_*.txt .sessions/ 2>/dev/null || true
mv session_*.html .sessions/ 2>/dev/null || true

# Move test files
echo "Moving test files..."
mv test_*.html scripts/tests/ 2>/dev/null || true
mv test_*.py scripts/tests/ 2>/dev/null || true
mv test_*.js scripts/tests/ 2>/dev/null || true
mv test_*.sh scripts/tests/ 2>/dev/null || true
mv test_spec.txt scripts/tests/ 2>/dev/null || true

# Move debug scripts
echo "Moving debug scripts..."
mv debug_*.js scripts/debug/ 2>/dev/null || true
mv debug_*.py scripts/debug/ 2>/dev/null || true

# Move verification scripts
echo "Moving verification scripts..."
mv verify_*.html scripts/verify/ 2>/dev/null || true
mv verify_*.js scripts/verify/ 2>/dev/null || true
mv verify_*.sh scripts/verify/ 2>/dev/null || true
mv verification_*.html scripts/verify/ 2>/dev/null || true

# Move check/analyze scripts
echo "Moving utility scripts..."
mv check_*.py scripts/ 2>/dev/null || true
mv analyze_*.js scripts/ 2>/dev/null || true
mv count_*.py scripts/ 2>/dev/null || true
mv find_*.py scripts/ 2>/dev/null || true
mv list_*.py scripts/ 2>/dev/null || true
mv get_*.py scripts/ 2>/dev/null || true

# Move add/clear/install scripts
mv add_*.py scripts/ 2>/dev/null || true
mv add_*.html scripts/ 2>/dev/null || true
mv clear_*.py scripts/ 2>/dev/null || true
mv install_*.py scripts/ 2>/dev/null || true
mv install_*.sh scripts/ 2>/dev/null || true
mv load_*.py scripts/ 2>/dev/null || true
mv migrate_*.py scripts/ 2>/dev/null || true

# Move documentation
echo "Moving documentation..."
mv CICD.md docs/ 2>/dev/null || true
mv DOCKER*.md docs/ 2>/dev/null || true
mv GIT_HOOKS.md docs/ 2>/dev/null || true
mv TYPE_CHECKING.md docs/ 2>/dev/null || true
mv CLI_*.md docs/ 2>/dev/null || true
mv *_VERIFICATION*.md docs/ 2>/dev/null || true
mv CORS_*.md docs/ 2>/dev/null || true
mv GENERATE_*.md docs/ 2>/dev/null || true
mv HUMAN_ACTION_REQUIRED.md docs/ 2>/dev/null || true
mv README_PLEASE_FIX_BACKEND.md docs/ 2>/dev/null || true
mv START_HERE_HUMAN.md docs/ 2>/dev/null || true
mv STOP_READ_THIS_FIRST.md docs/ 2>/dev/null || true
mv URGENT_FIX_REQUIRED.txt docs/ 2>/dev/null || true

# Keep in root (essential files only)
echo "
Root files remaining:
"
ls -1

echo "
✅ Cleanup complete!

Structure now:
├── sherpa/          (source code)
├── tests/           (test suite)
├── .sessions/       (session summaries)
├── scripts/         (utility scripts)
├── docs/            (documentation)
└── (10-15 files in root - clean!)
"

