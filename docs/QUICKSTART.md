# DA-Agent Quick Start

Get started with DA-Agent in 5 minutes.

## Installation

### 1. Install Dependencies

```bash
cd ~/da-agent
pip install -e .
```

### 2. Install as Claude Code Plugin

```bash
# In Claude Code
/plugin install da-agent@local:~/da-agent
```

### 3. Set Up Anthropic API Key

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

Or add to your shell profile (`~/.bashrc` or `~/.zshrc`):

```bash
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.zshrc
```

## Your First Analysis

### Example: Simple Aggregation

```bash
# 1. Prepare sample data
cat > ~/my_project/users.csv << EOF
user_id,name,revenue
1,Alice,100
2,Bob,150
3,Charlie,200
EOF

# 2. In Claude Code, navigate to your project
cd ~/my_project

# 3. Start analysis
/da:analyze
```

**Agent will ask:**
> What business question are you trying to answer?

**You respond:**
> Show me top users by revenue

**Agent continues:**
> Where is your data?

**You respond:**
> users.csv

**Agent scores the task:**
> Complexity: 2/10 (Auto Mode)
> This is a simple aggregation task.

## Phase 1 Capabilities

✅ What works now:
- Request understanding through structured dialog
- File path security validation
- Complexity scoring (LLM + rule-based fallback)
- Knowledge base storage

⏳ Coming in Phase 2:
- Auto execution mode
- Collaborative mode
- Advisory mode
- Report generation

## Security Notes

**Allowed:**
- Files in current working directory and subdirectories
- Standard data files (.csv, .xlsx, .parquet, etc.)

**Blocked:**
- Files outside working directory
- .env files
- Credential files
- .ssh directories

## Troubleshooting

### "Access denied: outside workspace"

You tried to access a file outside your current project directory.

**Solution:** Copy the file into your project, or navigate to the directory containing the file.

### "ModuleNotFoundError: anthropic"

Dependencies not installed.

**Solution:**
```bash
pip install -e .
```

### "API key not found"

Anthropic API key not set.

**Solution:**
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

## Next Steps

- Read [Architecture Overview](ARCHITECTURE.md)
- Check the [Design Spec](../../superpowers/specs/2026-03-17-da-agent-design.md)
- Explore example conversations in skill references
