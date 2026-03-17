# DA-Agent: Data Analysis Agent with Layered Intelligent Routing

Intelligent data analysis assistant for data analysts working with local files.
Automatically adapts behavior based on task complexity: Auto, Collaborative, or Advisory mode.

## Installation & Quick Start

### One-Command Install (Recommended)

```bash
cd ~/da-agent
./install-local.sh
```

Then **restart Claude Code** and use: `/da:analyze`

### Manual Installation

```bash
# 1. Install Python package
pip install -e .

# 2. Create symlink for Claude Code
ln -s ~/da-agent ~/.claude/plugins/cache/da-agent-local

# 3. Register in ~/.claude/plugins/installed_plugins.json
# (See install-local.sh for the JSON entry format)

# 4. Restart Claude Code

# 5. Use the plugin
/da:analyze
```

### Test Without Claude Code

```bash
# Run the demo script
python tests/demo_phase1.py

# Or use Python directly
python -c "
from lib.security_wrapper import SecureFileAccess
from lib.complexity_scorer import ComplexityScorer
print('✓ All modules working')
"
```

## Features

- 🤖 **Auto Mode**: Fully automated for simple tasks
- 🤝 **Collaborative Mode**: Human-in-the-loop for medium complexity
- 🧠 **Advisory Mode**: Expert guidance for complex analysis
- 🔒 **Security**: Workspace-scoped file access only
- 📚 **Knowledge Base**: Continuous learning from past analyses

## Documentation

- [Quick Start](docs/QUICKSTART.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Design Spec](../docs/superpowers/specs/2026-03-17-da-agent-design.md)

## Phase 1 Status

✅ **Completed:**
- Project scaffolding
- Security wrapper with workspace scoping
- SQLite knowledge base
- LLM + rule-based complexity scorer
- analyze-request skill
- execute-auto skill (simple aggregations)
- /da:analyze command
- End-to-end execution for simple queries ✨
- Comprehensive test coverage

**Deliverable:** Can handle "show me top 10 users by revenue" end-to-end ✅

⏳ **Next (Phase 2):**
- Collaborative mode with checkpoints
- Advisory mode with guidance
- Extended code template library
- Rich report generation with charts

## License

MIT
