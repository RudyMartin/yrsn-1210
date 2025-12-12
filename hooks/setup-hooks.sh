#!/bin/bash
# Install git hooks for this repository
# Run this after cloning: ./hooks/setup-hooks.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "Installing git hooks..."

# Copy all hooks from hooks/ to .git/hooks/
for hook in "$SCRIPT_DIR"/*; do
    hook_name=$(basename "$hook")

    # Skip this setup script
    if [ "$hook_name" = "setup-hooks.sh" ]; then
        continue
    fi

    # Copy and make executable
    cp "$hook" "$HOOKS_DIR/$hook_name"
    chmod +x "$HOOKS_DIR/$hook_name"
    echo "  ✓ Installed $hook_name"
done

echo "Done! Git hooks installed."
