---
name: analyze
description: Start a data analysis session
---

# /da:analyze Command

Start a new data analysis session.

## Usage

```
/da:analyze
```

## What It Does

Launches the `analyze-request` skill to:
1. Understand your analysis request through structured questions
2. Validate data file paths (security check)
3. Score task complexity
4. Route to appropriate execution mode

## Example

```
User: /da:analyze

Agent: Let's start your analysis. What business question are you trying to answer?

User: Why did user retention drop last week?

Agent: When specifically?
A) Last Monday-Sunday
B) Last 7 days rolling
...
```

## Phase 1 Note

In Phase 1, the command will score your task but won't execute it (execution modes coming in Phase 2). You'll learn what approach would be taken.

## Security

- Only files within current working directory are accessible
- .env and credential files are blocked
- See skill documentation for details
