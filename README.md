# DA-Agent: Data Analysis Agent with Layered Intelligent Routing

Intelligent data analysis assistant for data analysts working with local files.
Automatically adapts behavior based on task complexity: Auto, Collaborative, or Advisory mode.

## Installation & Quick Start

### Method 1: Python CLI (Works Anywhere)

```bash
cd ~/da-agent
pip install -e .
python cli.py analyze
```

This interactive CLI provides the full DA-Agent workflow without requiring Claude Code.

### Method 2: Claude Code Integration

```bash
cd ~/da-agent
./install-local.sh
```

Then **restart Claude Code** and use the Skill tool to invoke `da:analyze-request` or `da:execute-auto`.

**Note:** Claude Code v2.1.77+ uses skills (invoked via the Skill tool), not slash commands. The `/da:analyze` command syntax is not supported.

### Test the Installation

```bash
# Run the demo script
python tests/demo_phase1.py

# Or test Python modules directly
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
- Python CLI for interactive analysis
- End-to-end execution for simple queries ✨
- Comprehensive test coverage (96 tests, 95% coverage)

**Deliverable:** Can handle "show me top 10 users by revenue" end-to-end ✅

⏳ **Next (Phase 2):**
- Collaborative mode with checkpoints
- Advisory mode with guidance
- Extended code template library
- Rich report generation with charts

## License

MIT
