#!/bin/bash

set -euo pipefail

# Get repo root directory
REPO=$(git rev-parse --show-toplevel)
cd "$REPO"

# Install Python code formatter
if ! pip install --quiet black; then
  echo "❌ Installation of Python code formatter (black) failed."
  exit 1
fi

# Install Jinja2/HTML code formatter
if ! npm install --save-dev prettier prettier-plugin-jinja-template prettier-plugin-organize-attributes; then
  echo "❌ Installation of Jinja2 code formatter (prettier) failed."
  exit 1
fi

# Format all Python files
echo "✅ Formatting Python files..."
black .

# Format all HTML files recursively
echo "✅ Formatting HTML files..."
npx prettier "**/*.html" --write

echo "✅ Code formatting complete."
