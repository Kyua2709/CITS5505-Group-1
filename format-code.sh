#!/bin/bash

set -euo pipefail

# Constants for line lengths
LINE_LENGTH_CODE=120
LINE_LENGTH_TEMPLATE=180

# Get repository root and change to it
REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

# Install Python code formatter (black)
echo "🔧 Installing Python formatter (black)..."
if ! pip install --quiet black; then
  echo "❌ Failed to install black."
  exit 1
fi

# Install Prettier and its plugins for formatting HTML, Jinja2, etc.
echo "🔧 Installing Prettier and plugins..."
if ! npm install --save-dev prettier prettier-plugin-jinja-template prettier-plugin-organize-attributes; then
  echo "❌ Failed to install Prettier or plugins."
  exit 1
fi

# Format Python files
echo "✨ Formatting Python files..."
black --line-length "$LINE_LENGTH_CODE" .

# Format HTML files using Prettier with custom config
echo "✨ Formatting HTML files..."
PRETTIER_CONFIG_HTML=".prettierrc-html.json"
cat << EOF > "$PRETTIER_CONFIG_HTML"
{
  "plugins": ["prettier-plugin-jinja-template", "prettier-plugin-organize-attributes"],
  "printWidth": $LINE_LENGTH_TEMPLATE,
  "htmlWhitespaceSensitivity": "ignore",
  "attributeGroups": ["^id$", "^class$", "\$DEFAULT"],
  "attributeSort": "ASC",
  "overrides": [
    {
      "files": ["*.html"],
      "options": {
        "parser": "jinja-template"
      }
    }
  ]
}
EOF
npx prettier "**/*.html" --write --config "$PRETTIER_CONFIG_HTML"
rm "$PRETTIER_CONFIG_HTML"

# Format JS and CSS files with basic Prettier config
echo "✨ Formatting JS and CSS files..."
PRETTIER_CONFIG_BASIC=".prettierrc-basic.json"
cat << EOF > "$PRETTIER_CONFIG_BASIC"
{
  "printWidth": $LINE_LENGTH_CODE
}
EOF
npx prettier "**/*.js" --write --config "$PRETTIER_CONFIG_BASIC"
npx prettier "**/*.css" --write --config "$PRETTIER_CONFIG_BASIC"
rm "$PRETTIER_CONFIG_BASIC"

echo "✅ Code formatting complete."
