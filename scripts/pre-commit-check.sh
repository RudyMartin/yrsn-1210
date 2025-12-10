#!/bin/bash
# Pre-commit hook to check for exposed API keys and secrets

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Checking for exposed secrets..."

# Patterns to check for
PATTERNS=(
    "sk-[a-zA-Z0-9]{20,}"  # OpenAI API keys
    "sk-proj-[a-zA-Z0-9]{20,}"  # OpenAI project keys
    "ghp_[a-zA-Z0-9]{36,}"  # GitHub personal access tokens
    "xoxb-[0-9]{11}-[0-9]{11}-[a-zA-Z0-9]{24,}"  # Slack bot tokens
    "AKIA[0-9A-Z]{16}"  # AWS access keys
    "-----BEGIN PRIVATE KEY-----"  # Private keys
    "-----BEGIN RSA PRIVATE KEY-----"  # RSA private keys
)

# Files to check (staged files)
FILES=$(git diff --cached --name-only --diff-filter=ACM)

FOUND_SECRETS=0

for file in $FILES; do
    # Skip binary files
    if git diff --cached "$file" | grep -q "^Binary files"; then
        continue
    fi
    
    # Check each pattern
    for pattern in "${PATTERNS[@]}"; do
        if git diff --cached "$file" | grep -qiE "$pattern"; then
            echo -e "${RED}⚠️  WARNING: Potential secret found in $file${NC}"
            echo -e "${YELLOW}   Pattern: $pattern${NC}"
            FOUND_SECRETS=1
        fi
    done
done

if [ $FOUND_SECRETS -eq 1 ]; then
    echo -e "${RED}❌ Commit blocked: Potential secrets detected!${NC}"
    echo -e "${YELLOW}Please remove secrets from files before committing.${NC}"
    echo -e "${YELLOW}Use placeholders like 'sk-ENTER-YOUR-KEY-HERE' instead.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ No secrets detected${NC}"
    exit 0
fi

