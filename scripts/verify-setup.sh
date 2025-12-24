#!/bin/bash

# SHERPA V1 - Setup Verification Script
# Verifies that the initial setup was completed correctly

echo "🏔️  SHERPA V1 - Setup Verification"
echo "===================================="
echo ""

ERRORS=0

# Check critical files
echo "📋 Checking critical files..."

FILES=(
    "feature_list.json"
    "app_spec.txt"
    "README.md"
    "init.sh"
    "run.sh"
    "requirements.txt"
    "setup.py"
    ".gitignore"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (MISSING!)"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "📁 Checking directory structure..."

DIRS=(
    "sherpa"
    "sherpa/api"
    "sherpa/cli"
    "sherpa/core"
    "sherpa/frontend"
    "sherpa/data"
    "sherpa/snippets"
)

for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir/"
    else
        echo "  ❌ $dir/ (MISSING!)"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "📦 Checking Python package structure..."

PY_FILES=(
    "sherpa/__init__.py"
    "sherpa/api/__init__.py"
    "sherpa/cli/__init__.py"
    "sherpa/core/__init__.py"
)

for file in "${PY_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (MISSING!)"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "⚛️  Checking frontend structure..."

FE_FILES=(
    "sherpa/frontend/package.json"
    "sherpa/frontend/vite.config.js"
    "sherpa/frontend/index.html"
    "sherpa/frontend/src/main.jsx"
    "sherpa/frontend/src/App.jsx"
)

for file in "${FE_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (MISSING!)"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "🔍 Checking feature_list.json format..."

if command -v python3 &> /dev/null; then
    FEATURE_COUNT=$(python3 -c "import json; data=json.load(open('feature_list.json')); print(len(data))" 2>/dev/null || echo "ERROR")
    if [ "$FEATURE_COUNT" != "ERROR" ]; then
        echo "  ✅ feature_list.json is valid JSON"
        echo "  ✅ Contains $FEATURE_COUNT features"
    else
        echo "  ❌ feature_list.json has invalid format"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "  ⚠️  Python3 not available, skipping JSON validation"
fi

echo ""
echo "📊 Git repository status..."

if [ -d ".git" ]; then
    echo "  ✅ Git repository initialized"
    COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo "0")
    echo "  ✅ $COMMIT_COUNT commits made"
else
    echo "  ❌ Git repository not initialized"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "===================================="

if [ $ERRORS -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED!"
    echo ""
    echo "Setup is complete and ready for implementation."
    echo "Next agent can proceed with backend/frontend development."
    exit 0
else
    echo "❌ $ERRORS ERRORS FOUND!"
    echo ""
    echo "Some files or directories are missing."
    echo "Please review the setup process."
    exit 1
fi
