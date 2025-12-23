#!/bin/bash

# SHERPA V1 - E2E Test Runner
# This script runs Playwright E2E tests for the SHERPA frontend

set -e

echo "🎭 SHERPA V1 - E2E Test Runner"
echo "=============================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if backend is running
echo "📡 Checking if backend is running..."
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is running on port 8001${NC}"
else
    echo -e "${RED}❌ Backend is not running on port 8001${NC}"
    echo "Please start the backend with:"
    echo "  source venv-312/bin/activate"
    echo "  uvicorn sherpa.api.main:app --reload --port 8001 --host 0.0.0.0"
    exit 1
fi

# Navigate to frontend directory
cd sherpa/frontend

# Install Playwright browsers if needed
if [ ! -d "$HOME/.cache/ms-playwright" ] && [ ! -d "$HOME/Library/Caches/ms-playwright" ]; then
    echo ""
    echo "📦 Installing Playwright browsers..."
    ./node_modules/.bin/playwright install chromium
fi

# Run Playwright tests
echo ""
echo "🎭 Running Playwright E2E tests..."
echo ""

npm run test:e2e

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ All E2E tests passed!${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Some E2E tests failed${NC}"
    echo ""
    exit 1
fi
