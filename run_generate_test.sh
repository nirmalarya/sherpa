#!/bin/bash
# Test sherpa generate command

echo "🧪 Testing sherpa generate command"
echo ""

# Create test directory
TEST_DIR="/tmp/sherpa_generate_test_$(date +%s)"
mkdir -p "$TEST_DIR"
echo "Test directory: $TEST_DIR"
echo ""

# Change to test directory
cd "$TEST_DIR" || exit 1

# Run generate using Python module
echo "Step 1: Running sherpa generate..."
echo ""

PYTHONPATH="${BASH_SOURCE%/*}" "${BASH_SOURCE%/*}/venv-312/bin/python3" -m sherpa.cli.main generate

echo ""
echo "Step 2: Verifying created files..."
echo ""

# Check files
if [ -d ".cursor/rules" ]; then
    echo "✓ .cursor/rules/ directory created"
else
    echo "✗ .cursor/rules/ directory NOT created"
    exit 1
fi

if [ -f ".cursor/rules/00-sherpa-knowledge.md" ]; then
    echo "✓ .cursor/rules/00-sherpa-knowledge.md created"
else
    echo "✗ .cursor/rules/00-sherpa-knowledge.md NOT created"
    exit 1
fi

if [ -f "CLAUDE.md" ]; then
    echo "✓ CLAUDE.md created"
else
    echo "✗ CLAUDE.md NOT created"
    exit 1
fi

if [ -f "copilot-instructions.md" ]; then
    echo "✓ copilot-instructions.md created"
else
    echo "✗ copilot-instructions.md NOT created"
    exit 1
fi

echo ""
echo "Step 3: Saving results..."
RESULTS_DIR="${BASH_SOURCE%/*}/test_results_generate"
mkdir -p "$RESULTS_DIR"
cp .cursor/rules/00-sherpa-knowledge.md "$RESULTS_DIR/"
cp CLAUDE.md "$RESULTS_DIR/"
cp copilot-instructions.md "$RESULTS_DIR/"

echo "Results saved to: $RESULTS_DIR"
echo ""
echo "✓ All tests passed!"
