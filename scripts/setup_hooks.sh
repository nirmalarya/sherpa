#!/bin/bash

# SHERPA V1 - Git Hooks Setup Script
# Installs and configures pre-commit hooks

set -e

echo "🪝 SHERPA V1 - Git Hooks Setup"
echo "==============================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if git repository exists
if [ ! -d ".git" ]; then
    echo "${RED}❌ Not a git repository. Please run 'git init' first.${NC}"
    exit 1
fi

# Determine which virtual environment to use
VENV_PATH=""
if [ -d "venv-312" ]; then
    VENV_PATH="venv-312"
elif [ -d "venv" ]; then
    VENV_PATH="venv"
else
    echo "${RED}❌ Virtual environment not found. Please create venv or venv-312.${NC}"
    exit 1
fi

echo "${BLUE}📦 Using virtual environment: ${VENV_PATH}${NC}"
echo ""

# Install pre-commit if not already installed
if [ ! -f "${VENV_PATH}/bin/pre-commit" ]; then
    echo "${YELLOW}⚠️  Installing pre-commit...${NC}"
    ${VENV_PATH}/bin/pip install -q pre-commit detect-secrets
    echo "${GREEN}✅ pre-commit installed${NC}"
else
    echo "${GREEN}✅ pre-commit already installed${NC}"
fi

echo ""

# Check if .pre-commit-config.yaml exists
if [ ! -f ".pre-commit-config.yaml" ]; then
    echo "${RED}❌ .pre-commit-config.yaml not found${NC}"
    exit 1
fi

echo "${BLUE}🔧 Installing Git hooks...${NC}"

# Install the git hook scripts
if ${VENV_PATH}/bin/pre-commit install; then
    echo "${GREEN}✅ Git hooks installed successfully${NC}"
else
    echo "${RED}❌ Failed to install git hooks${NC}"
    exit 1
fi

echo ""

# Install pre-commit hook dependencies
echo "${BLUE}📥 Installing hook dependencies...${NC}"
if ${VENV_PATH}/bin/pre-commit install-hooks; then
    echo "${GREEN}✅ Hook dependencies installed${NC}"
else
    echo "${YELLOW}⚠️  Some hook dependencies may not have installed. This is usually OK.${NC}"
fi

echo ""

# Optional: Run hooks on all files to verify setup
echo "${BLUE}🧪 Testing hooks (optional - can skip with Ctrl+C)...${NC}"
echo "${YELLOW}This may take a minute...${NC}"
echo ""

if ${VENV_PATH}/bin/pre-commit run --all-files; then
    echo ""
    echo "${GREEN}✅ All hooks passed!${NC}"
else
    echo ""
    echo "${YELLOW}⚠️  Some hooks failed. This is normal if there are existing issues.${NC}"
    echo "${YELLOW}   Fix the issues and try again.${NC}"
fi

echo ""
echo "==============================="
echo "${GREEN}✅ Git Hooks Setup Complete!${NC}"
echo "==============================="
echo ""
echo "${BLUE}Hooks configured:${NC}"
echo "  - ESLint (Frontend linting)"
echo "  - flake8 (Backend linting)"
echo "  - black (Backend formatting)"
echo "  - mypy (Type checking)"
echo "  - Trailing whitespace check"
echo "  - End-of-file fixer"
echo "  - YAML/JSON validation"
echo "  - Large file detection"
echo "  - Merge conflict detection"
echo "  - Private key detection"
echo "  - Secret detection"
echo ""
echo "${BLUE}Usage:${NC}"
echo "  - Hooks run automatically on 'git commit'"
echo "  - Run manually: ${GREEN}pre-commit run --all-files${NC}"
echo "  - Skip hooks (not recommended): ${YELLOW}git commit --no-verify${NC}"
echo "  - Update hooks: ${GREEN}pre-commit autoupdate${NC}"
echo ""
echo "🎉 Happy coding with automatic quality checks!"
