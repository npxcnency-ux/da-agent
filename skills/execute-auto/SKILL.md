---
name: execute-auto
description: Automatically execute simple aggregation tasks end-to-end. Use for complexity score < 3.
---

# Execute Auto Skill

> Fully automated execution for simple tasks

## Purpose

Execute simple aggregation tasks end-to-end without human intervention.

**Trigger:** Complexity score < 3

**Supported Tasks:**
- Top N queries ("show me top 10 users by revenue")
- Group-by aggregations ("total sales by region")

## Workflow

### Phase 1: Generate Code

Use CodeGenerator to create Python code from template:

```python
from lib.code_generator import CodeGenerator
from pathlib import Path

templates_dir = Path(__file__).parent.parent / "assets" / "sql_templates"
generator = CodeGenerator(templates_dir)

task = {
    "analysis_type": "aggregation",
    "operation": "top_n",
    "data_source": structured_req["data_sources"][0],
    "sort_by": structured_req["sort_by"],
    "limit": structured_req.get("limit", 10)
}

code = generator.generate(task)
```

### Phase 2: Show Code to User

Before execution, show the generated code:

```
Generated code:

[paste code here]

This will:
1. Read data from [file]
2. Sort by [column]
3. Return top [N] results
4. Save to outputs/result.csv

Execute? (y/n)
```

### Phase 3: Execute Code

If user approves:

```python
from lib.executor import Executor
import os

executor = Executor(Path(os.getcwd()))

try:
    output = executor.execute(code, timeout=30)
    print(output)
except ExecutionError as e:
    print(f"Execution failed: {e}")
    print("Please check your data file and try again.")
```

### Phase 4: Present Results

```
✓ Analysis complete!

Results saved to: outputs/result.csv

[Show preview of results]

Would you like me to:
A) Generate a summary report
B) Save this to knowledge base
C) Done
```

### Phase 5: Save to Knowledge Base

```python
from lib.knowledge_store import KnowledgeStore
from pathlib import Path

kb_dir = Path.home() / ".da-agent" / "knowledge"
kb_dir.mkdir(parents=True, exist_ok=True)
kb = KnowledgeStore(str(kb_dir / "kb.db"))

task_id = kb.save_task(
    description=original_request,
    structured_req=structured_req,
    complexity_score=score,
    execution_mode="auto"
)
```

## Error Handling

**File not found:**
```
Error: Cannot find data file 'users.csv'
Please check:
- File exists in current directory
- Filename is correct
- You have read permissions
```

**Invalid column:**
```
Error: Column 'revenue' not found in data
Available columns: [list columns]
```

**Security error:**
```
Error: Cannot access file outside workspace
Please copy the file to current directory
```

## Phase 1 Limitations

- Only simple aggregations (top N, groupby)
- Single file only (no joins)
- No charts/visualizations
- Basic text output only

Phase 2+ will add:
- Multi-file joins
- Charts and visualizations
- Rich HTML reports
- More analysis types
