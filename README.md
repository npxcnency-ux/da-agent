# DA-Agent: Data Analysis Agent with Layered Intelligent Routing

Intelligent data analysis assistant for data analysts working with local files.
Automatically adapts behavior based on task complexity: Auto, Collaborative, or Advisory mode.

## Quick Start

```bash
# Install
pip install -e .

# In Claude Code
/plugin install da-agent@local:~/da-agent

# Use
/da:analyze
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
