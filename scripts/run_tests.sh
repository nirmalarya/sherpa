#!/bin/bash
# SHERPA V1 Test Runner

set -e

echo "🧪 Running SHERPA V1 Test Suite"
echo "================================"
echo ""

# Activate virtual environment
if [ -d "venv-312" ]; then
    source venv-312/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found"
    exit 1
fi

# Run pytest with coverage
echo "📊 Running tests with coverage..."
pytest -v --cov=sherpa --cov-report=term-missing --cov-report=html

# Show coverage summary
echo ""
echo "✅ Tests complete!"
echo ""
echo "📈 Coverage report generated at: htmlcov/index.html"
echo ""

# Deactivate virtual environment
deactivate
