#!/bin/bash

# SHERPA V1 - Run Script
# Starts both backend and frontend services

set -e

echo "🏔️  Starting SHERPA V1..."
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Please run ./init.sh first."
    exit 1
fi

# Check if backend files exist
if [ ! -d "sherpa" ]; then
    echo "❌ sherpa/ directory not found. Implementation not yet complete."
    exit 1
fi

# Function to kill background processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping SHERPA services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup EXIT INT TERM

# Start backend
echo "🐍 Starting backend on http://localhost:8000..."
if [ -f "sherpa/api/main.py" ]; then
    uvicorn sherpa.api.main:app --reload --port 8000 > sherpa/logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "✅ Backend started (PID: $BACKEND_PID)"
else
    echo "⚠️  Backend not yet implemented"
fi

# Start frontend
echo "⚛️  Starting frontend on http://localhost:3001..."
if [ -d "sherpa/frontend" ]; then
    cd sherpa/frontend
    npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ../..
    echo "✅ Frontend started (PID: $FRONTEND_PID)"
else
    echo "⚠️  Frontend not yet implemented"
fi

echo ""
echo "================================================"
echo "✅ SHERPA V1 is running!"
echo "================================================"
echo ""
echo "📍 Access points:"
echo "   Backend API: http://localhost:8000"
echo "   Frontend UI: http://localhost:3001"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📊 Logs:"
echo "   Backend: sherpa/logs/backend.log"
echo "   Frontend: sherpa/logs/frontend.log"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes
wait
