#!/bin/bash

# Run integration tests for SHERPA V1
echo "Running integration tests..."

# Activate virtual environment
source ./venv-312/bin/activate

# Run pytest with integration marker
pytest tests/test_integration_api.py -v -m integration

# Store exit code
EXIT_CODE=$?

# Deactivate virtual environment
deactivate

# Exit with pytest's exit code
exit $EXIT_CODE
