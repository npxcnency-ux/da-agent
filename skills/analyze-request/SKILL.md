---
name: analyze-request
description: Understand user's analysis request through structured dialog, score complexity, and route to appropriate execution mode. Use when user wants to analyze data.
---

# Analyze Request Skill

> Request understanding and routing for DA-Agent

## Purpose

Transform vague business requests into structured analysis tasks, score complexity, and route to the appropriate execution mode.

## Security Constraints

CRITICAL: Before any file operation, validate paths:

```python
from lib.security_wrapper import SecureFileAccess

security = SecureFileAccess(os.getcwd())
safe_path = security.validate_path(user_provided_path)
```

Never access:
- Files outside current working directory
- .env files
- Credential files
- .ssh directories

If user provides forbidden path, respond:
"Sorry, for security reasons, I can only access files within the current project directory."

## Workflow

### Phase 1: Structured Dialog

Ask questions ONE AT A TIME to clarify the request. Use multiple choice when possible.

Use question templates from `references/question-templates.md`.

**Required information:**
1. Core question - What business question are we answering?
2. Data sources - Which files? (validate with security wrapper)
3. Time range - What period?
4. Dimensions - How to slice the data?
5. Analysis type - What kind of analysis?

### Phase 2: Complexity Scoring

Once you have structured requirements, score complexity:

```python
from lib.complexity_scorer import ComplexityScorer

scorer = ComplexityScorer()
result = scorer.score(structured_req)

print(f"Complexity Score: {result.score}/10")
print(f"Suggested Mode: {result.mode}")
print(f"Reasoning: {result.reasoning}")
```

See `references/complexity-scoring-rubric.md` for scoring criteria.

### Phase 3: User Confirmation

Present the scoring result and ask for confirmation:

**Example:**
> **Analysis Task Complexity**
>
> Score: 5/10
> Suggested Mode: **Collaborative**
> Reasoning: Multi-file JOIN (2pts) + Funnel analysis (2pts) + Business rules (1pt)
>
> In collaborative mode:
> - I'll generate code drafts for your review
> - You'll approve at key decision points
> - We'll work together on the analysis
>
> Proceed with this approach?

### Phase 4: Route to Execution

Based on confirmed mode:
- `auto` → Load execute-auto skill and hand off
- `collab` → (Phase 2: Coming soon)
- `assist` → (Phase 2: Coming soon)

For auto mode:

```python
# Hand off to execute-auto skill
print("Routing to auto-execution mode...")
# The execute-auto skill will take over from here
```

Then follow the execute-auto skill workflow.

### Phase 5: Knowledge Base Recording

Save the task to knowledge base:

```python
from lib.knowledge_store import KnowledgeStore
import os

kb = KnowledgeStore(Path.home() / ".da-agent" / "knowledge")
task_id = kb.save_task(
    description=original_request,
    structured_req=structured_req,
    complexity_score=result.score,
    execution_mode=result.mode
)
```

## Error Handling

- If security validation fails → Explain why and ask for different path
- If complexity scoring fails → Fall back to rule-based scoring
- If user provides incomplete info → Ask follow-up questions
- If task is too vague → Help decompose into specific questions

## Examples

See `references/question-templates.md` for conversation flow examples.
