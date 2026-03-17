# DA-Agent Architecture

Technical overview of DA-Agent's design and implementation.

## System Overview

```
┌─────────────────────────────────────┐
│         User Input                  │
│    /da:analyze command              │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│   analyze-request Skill             │
│   - Structured dialog               │
│   - Security validation             │
│   - Complexity scoring              │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│   Python Library Backend            │
│   ├─ security_wrapper.py            │
│   ├─ complexity_scorer.py           │
│   └─ knowledge_store.py             │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│   Knowledge Base (SQLite)           │
│   ~/.da-agent/knowledge/kb.db       │
└─────────────────────────────────────┘
```

## Component Details

### 1. Skills Layer

**Location:** `skills/`

Claude Code skills that define the user-facing workflows.

**Phase 1 Skills:**
- `analyze-request`: Request understanding and routing

**Phase 2+ Skills (planned):**
- `execute-auto`: Automated execution
- `execute-collab`: Collaborative execution
- `execute-assist`: Advisory execution
- `knowledge-manager`: Knowledge base management

### 2. Commands Layer

**Location:** `commands/`

Slash commands that trigger skills.

**Phase 1 Commands:**
- `/da:analyze`: Start analysis session

### 3. Python Library

**Location:** `lib/`

Core business logic implemented in Python.

#### security_wrapper.py

Enforces security constraints:
- Workspace-scoped file access only
- Blocks sensitive files (.env, credentials, etc.)
- Path traversal protection

**Usage:**
```python
from lib.security_wrapper import SecureFileAccess

security = SecureFileAccess(os.getcwd())
safe_path = security.validate_path(user_path)
content = security.read_file(user_path)
```

#### complexity_scorer.py

Scores task complexity (1-10) and suggests execution mode.

**Scoring dimensions:**
- Data complexity (1-3 pts)
- Analytical method complexity (1-4 pts)
- Business logic complexity (1-3 pts)

**Strategy:**
- Primary: LLM-based scoring (Claude API)
- Fallback: Rule-based heuristics

**Usage:**
```python
from lib.complexity_scorer import ComplexityScorer

scorer = ComplexityScorer()
result = scorer.score(structured_req)
# result.score: 1-10
# result.mode: "auto" | "collab" | "assist"
# result.reasoning: explanation
```

#### knowledge_store.py

SQLite-based persistent storage.

**Tables:**
- `tasks`: Historical analysis tasks
- `code_templates`: Reusable code snippets
- `business_terms`: Business terminology with conflict detection

**Usage:**
```python
from lib.knowledge_store import KnowledgeStore

kb = KnowledgeStore(Path.home() / ".da-agent" / "knowledge")
task_id = kb.save_task(description, structured_req, score, mode)
similar = kb.search_similar_tasks("retention analysis")
```

### 4. Knowledge Base

**Location:** `~/.da-agent/knowledge/`

User-specific persistent storage.

**Structure:**
```
~/.da-agent/
└── knowledge/
    ├── kb.db              # SQLite database
    └── assets/            # (Phase 2+)
        ├── sql_templates/
        ├── python_snippets/
        └── reports/
```

## Data Flow

### Analysis Request Flow

1. **User invokes** `/da:analyze`
2. **Command triggers** `analyze-request` skill
3. **Skill conducts** structured dialog
4. **For each file path**, skill calls `SecureFileAccess.validate_path()`
5. **Once requirements gathered**, skill calls `ComplexityScorer.score()`
6. **Scorer tries** LLM first, falls back to rules if needed
7. **Result presented** to user for confirmation
8. **Task saved** to knowledge base via `KnowledgeStore.save_task()`
9. **Routing** (Phase 1: explains what would happen; Phase 2+: executes)

## Security Model

### Workspace Scoping

All file access is scoped to the current working directory.

**Why:** Prevents accidental access to system files or other projects.

**Implementation:** `SecureFileAccess` resolves paths and checks:
```python
path.relative_to(workspace_root)  # Raises ValueError if outside
```

### Forbidden Patterns

Certain file patterns are always blocked:
- `.env*`
- `credentials*`
- `.aws`, `.ssh`
- `id_rsa`, `.pem`

**Why:** Prevent exposure of secrets.

**Implementation:** String matching on resolved path.

### Path Traversal Protection

Paths are resolved to absolute form before validation.

**Why:** Prevents `../../../etc/passwd` style attacks.

**Implementation:** `Path.resolve()` before checking.

## Testing Strategy

### Unit Tests

Each module has comprehensive unit tests:
- `tests/test_security_wrapper.py`
- `tests/test_complexity_scorer.py`
- `tests/test_knowledge_store.py`

**Run:** `pytest tests/ -v`

### Integration Tests

(Phase 2+) End-to-end workflow tests.

### Test Fixtures

**Location:** `tests/fixtures/`

Sample data for tests:
- `sample_data.csv`: Simple CSV for testing
- `test_project/`: Full project structure for integration tests

## Extension Points

### Adding New Skills

1. Create `skills/your-skill/SKILL.md`
2. Add references in `skills/your-skill/references/`
3. Update `.claude-plugin/plugin.json`
4. Add tests

### Adding New Commands

1. Create `commands/your-command.md`
2. Update `.claude-plugin/plugin.json`

### Extending Python Library

1. Add module to `lib/`
2. Write unit tests
3. Import in skill SKILL.md files

## Performance Considerations

### LLM Scoring

- **Latency:** 1-3 seconds per request
- **Cost:** ~$0.01 per scoring
- **Mitigation:** Rule-based fallback for speed-critical scenarios

### Knowledge Base

- **SQLite performance:** Excellent for < 10k tasks
- **Search:** Simple keyword search in Phase 1; embeddings in Phase 2+
- **Scaling:** Phase 3+ will add archival and indexing

### File Access

- **Security overhead:** Minimal (~1ms per validation)
- **Trade-off:** Security > performance

## Phase 1 Limitations

What's NOT implemented yet:

- ❌ Actual code generation
- ❌ Data analysis execution
- ❌ Report generation
- ❌ Advanced template library
- ❌ Semantic search (embeddings)

Phase 1 focuses on:
- ✅ Foundation architecture
- ✅ Security model
- ✅ Request understanding
- ✅ Complexity scoring
- ✅ Knowledge base structure

## Future Phases

See design spec for:
- Phase 2: Execution modes
- Phase 3: Knowledge management
- Phase 4: Polish and integration
