#!/bin/bash

# Install Playwright browsers
# This script installs the Chromium browser needed for E2E tests

echo "Installing Playwright browsers..."

# Navigate to frontend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install chromium browser for Playwright
node_modules/.bin/playwright install chromium

echo "Playwright installation complete!"
