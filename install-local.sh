#!/bin/bash
# DA-Agent Local Plugin Installer for Claude Code

set -e

echo "🚀 Installing DA-Agent as local Claude Code plugin..."

# 1. Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -e . > /dev/null 2>&1
echo "✓ Python package installed"

# 2. Create symlink in Claude plugins cache
PLUGIN_CACHE="$HOME/.claude/plugins/cache"
SYMLINK_PATH="$PLUGIN_CACHE/da-agent-local"

if [ -L "$SYMLINK_PATH" ]; then
    echo "✓ Symlink already exists: $SYMLINK_PATH"
else
    echo "🔗 Creating symlink..."
    ln -s "$(pwd)" "$SYMLINK_PATH"
    echo "✓ Symlink created: $SYMLINK_PATH"
fi

# 3. Register in installed_plugins.json
INSTALLED_PLUGINS="$HOME/.claude/plugins/installed_plugins.json"

if grep -q '"da-agent@local"' "$INSTALLED_PLUGINS"; then
    echo "✓ Plugin already registered in Claude Code"
else
    echo "📝 Registering plugin in Claude Code..."
    # Backup original file
    cp "$INSTALLED_PLUGINS" "${INSTALLED_PLUGINS}.backup"

    # Add plugin entry (simple approach - adds before closing brace)
    python3 << 'EOF'
import json
import sys
from pathlib import Path

plugins_file = Path.home() / ".claude/plugins/installed_plugins.json"
with open(plugins_file) as f:
    data = json.load(f)

if "da-agent@local" not in data["plugins"]:
    data["plugins"]["da-agent@local"] = [{
        "scope": "user",
        "installPath": str(Path.home() / ".claude/plugins/cache/da-agent-local"),
        "version": "0.1.0",
        "installedAt": "2026-03-17T08:54:00.000Z",
        "lastUpdated": "2026-03-17T08:54:00.000Z",
        "gitCommitSha": "local-dev"
    }]

    with open(plugins_file, 'w') as f:
        json.dump(data, f, indent=2)
    print("✓ Plugin registered")
else:
    print("✓ Plugin already registered")
EOF
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "📖 Next steps:"
echo "   1. Restart Claude Code to load the plugin"
echo "   2. Navigate to this directory: cd $(pwd)"
echo "   3. Use the command: /da:analyze"
echo ""
echo "🧪 Or run the demo: python tests/demo_phase1.py"
echo ""
