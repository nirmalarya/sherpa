#!/bin/bash

# SHERPA V1 - Development Environment Setup Script
# This script sets up and runs the SHERPA autonomous coding orchestrator

set -e  # Exit on error

echo "🏔️  SHERPA V1 - Autonomous Coding Orchestrator"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "app_spec.txt" ]; then
    echo "❌ Error: app_spec.txt not found. Please run this script from the project root."
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "📋 Checking dependencies..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed."
    exit 1
fi

echo "✅ All required dependencies found"
echo ""

# Setup Python backend
echo "🐍 Setting up Python backend..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
elif [ -f "setup.py" ]; then
    pip install -q -e .
elif [ -f "pyproject.toml" ]; then
    pip install -q -e .
else
    echo "${YELLOW}⚠️  No requirements.txt, setup.py, or pyproject.toml found. Skipping Python dependencies.${NC}"
fi

echo "✅ Python backend setup complete"
echo ""

# Setup frontend
echo "⚛️  Setting up React frontend..."

if [ -d "sherpa/frontend" ]; then
    cd sherpa/frontend

    # Install npm dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        echo "Installing npm dependencies..."
        npm install
    else
        echo "npm dependencies already installed"
    fi

    cd ../..
    echo "✅ Frontend setup complete"
else
    echo "${YELLOW}⚠️  sherpa/frontend directory not found yet. Will be created during implementation.${NC}"
fi

echo ""

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p sherpa/data
mkdir -p sherpa/snippets
mkdir -p sherpa/snippets.local
mkdir -p sherpa/logs
mkdir -p .cursor/rules

echo "✅ Directory structure created"
echo ""

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    echo "🔧 Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
    echo ""
fi

# Display environment info
echo "================================================"
echo "✅ SHERPA V1 Setup Complete!"
echo "================================================"
echo ""
echo "📊 Environment Information:"
echo "   Python: $(python3 --version)"
echo "   Node: $(node --version)"
echo "   npm: $(npm --version)"
echo ""
echo "🚀 To run SHERPA:"
echo ""
echo "   ${GREEN}Option 1: Run full stack${NC}"
echo "   $ ./run.sh"
echo ""
echo "   ${GREEN}Option 2: Run backend only${NC}"
echo "   $ source venv/bin/activate"
echo "   $ uvicorn sherpa.api.main:app --reload --port 8000"
echo ""
echo "   ${GREEN}Option 3: Run frontend only${NC}"
echo "   $ cd sherpa/frontend"
echo "   $ npm run dev"
echo ""
echo "📝 Access points:"
echo "   Backend API: ${BLUE}http://localhost:8000${NC}"
echo "   Frontend UI: ${BLUE}http://localhost:3001${NC}"
echo "   API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo "📚 CLI Commands (after backend setup):"
echo "   $ sherpa init              # Initialize Bedrock KB"
echo "   $ sherpa generate          # Create instruction files"
echo "   $ sherpa run --spec FILE   # Run autonomous harness"
echo "   $ sherpa serve             # Start web dashboard"
echo "   $ sherpa status            # Show active sessions"
echo "   $ sherpa --help            # Show all commands"
echo ""
echo "================================================"
