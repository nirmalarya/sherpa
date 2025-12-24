#!/bin/bash
# Fix backend by installing missing dependencies and restarting

set -e

echo "🔧 Fixing SHERPA backend..."

# Install missing dependencies
echo "📦 Installing missing Python packages..."
venv-312/bin/pip install cryptography==42.0.0 watchdog==4.0.0

# Kill old backend process (if running)
echo "🛑 Stopping old backend process..."
pkill -f "uvicorn sherpa.api.main:app" || true

# Wait a moment
sleep 2

# Start new backend
echo "🚀 Starting backend on port 8001..."
venv-312/bin/uvicorn sherpa.api.main:app --reload --port 8001 --host 0.0.0.0 >> logs/backend.log 2>&1 &

# Wait for startup
sleep 3

# Test connection
echo "🧪 Testing backend connection..."
venv-312/bin/python test_backend_connection.py

echo "✅ Backend fix complete!"
