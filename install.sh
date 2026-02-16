#!/bin/bash
# Install toggl-track skill from GitHub

set -e

REPO_URL="${1:-https://github.com/YOUR_USERNAME/toggl-track-skill}"
INSTALL_DIR="${HOME}/.openclaw/skills"
TEMP_DIR=$(mktemp -d)

echo "Installing toggl-track skill..."
echo "From: $REPO_URL"

# Clone repo
git clone "$REPO_URL" "$TEMP_DIR/repo"

# Install skill
mkdir -p "$INSTALL_DIR"
cp -r "$TEMP_DIR/repo/toggl-track" "$INSTALL_DIR/"

# Cleanup
rm -rf "$TEMP_DIR"

echo "✓ toggl-track skill installed to $INSTALL_DIR/toggl-track"
echo ""
echo "Next steps:"
echo "  1. Get your API token: https://track.toggl.com/profile"
echo "  2. Set environment variable: export TOGGL_API_TOKEN=your_token"
echo "  3. Run: python3 $INSTALL_DIR/toggl-track/scripts/fetch_all.py"
