#!/bin/bash
# Uninstall Git hooks for this repository

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

GIT_DIR="$(git rev-parse --git-dir)"

echo -e "${YELLOW}🗑️  Uninstalling Git hooks...${NC}\n"

# Remove pre-commit hook
if [ -f "$GIT_DIR/hooks/pre-commit" ]; then
    rm "$GIT_DIR/hooks/pre-commit"
    echo -e "${GREEN}✓ Removed pre-commit hook${NC}"
fi

# Remove pre-push hook
if [ -f "$GIT_DIR/hooks/pre-push" ]; then
    rm "$GIT_DIR/hooks/pre-push"
    echo -e "${GREEN}✓ Removed pre-push hook${NC}"
fi

echo -e "\n${GREEN}✓ Git hooks uninstalled successfully!${NC}\n"