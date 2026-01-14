#!/bin/bash
# Install Git hooks for this repository

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GIT_DIR="$(git rev-parse --git-dir)"

echo -e "${BLUE}📦 Installing Git hooks...${NC}\n"

# Install pre-commit hook
if [ -f "$SCRIPT_DIR/pre-commit" ]; then
    cp "$SCRIPT_DIR/pre-commit" "$GIT_DIR/hooks/pre-commit"
    chmod +x "$GIT_DIR/hooks/pre-commit"
    echo -e "${GREEN}✓ Installed pre-commit hook${NC}"
fi

# Install pre-push hook
if [ -f "$SCRIPT_DIR/pre-push" ]; then
    cp "$SCRIPT_DIR/pre-push" "$GIT_DIR/hooks/pre-push"
    chmod +x "$GIT_DIR/hooks/pre-push"
    echo -e "${GREEN}✓ Installed pre-push hook${NC}"
fi

echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Git hooks installed successfully!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Hooks installed:"
echo "  • pre-commit: Runs Ruff and Black on staged files"
echo "  • pre-push: Runs all tests before pushing"
echo ""
echo "To temporarily skip hooks, use:"
echo "  git commit --no-verify"
echo "  git push --no-verify"
echo ""