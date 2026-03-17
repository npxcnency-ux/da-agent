# Question Templates for Structured Dialog

## Template 1: Core Question

**Ask:**
> What business question are you trying to answer?

**Good answers:**
- "Why did user retention drop last week?"
- "Which marketing channel has the best ROI?"
- "Are there any anomalies in daily revenue?"

**Bad answers (too vague):**
- "Show me the data"
- "Analyze everything"

**Follow-up if vague:**
> Let's make it more specific. Are you trying to:
> A) Understand a metric's trend over time
> B) Compare different segments
> C) Find root cause of a change
> D) Predict future behavior

## Template 2: Data Sources

**Ask:**
> Where is your data? Please provide file path(s).

**Validation:**
```python
from lib.security_wrapper import SecureFileAccess

security = SecureFileAccess(os.getcwd())
try:
    safe_path = security.validate_path(user_provided_path)
    # Proceed
except SecurityError as e:
    print(f"Cannot access that file: {e}")
    # Ask for different path
```

**If multiple files:**
> Do these files need to be joined together?
> A) Yes, they share a common key (e.g., user_id)
> B) No, analyze them separately

## Template 3: Time Range

**Ask:**
> What time period should I analyze?

**Options:**
> A) Last week (Monday-Sunday)
> B) Last 7 days (rolling)
> C) Last month
> D) Year-over-year comparison
> E) Custom range (please specify)

## Template 4: Dimensions

**Ask:**
> How should I slice the data?

**Options:**
> A) Overall (no grouping)
> B) By time (daily/weekly/monthly)
> C) By category (channel, region, product, etc.)
> D) By user segment
> E) Multiple dimensions (specify)

## Template 5: Analysis Type

**Ask based on context:**

**For trend questions:**
> What kind of trend analysis?
> A) Simple line chart over time
> B) Growth rate calculation
> C) Anomaly detection
> D) Seasonality analysis

**For comparison questions:**
> How should I compare?
> A) Side-by-side bar chart
> B) Percentage difference
> C) Statistical significance test

**For root cause questions:**
> What type of analysis?
> A) Segment breakdown (which segment changed)
> B) Cohort analysis (when did it start)
> C) Correlation analysis (what's related)

## Example Conversation Flow

**User:** "Help me analyze user retention"

**Agent:** "What business question are you trying to answer?

A) Why did retention drop?
B) Which cohorts have best retention?
C) How does retention compare to last month?
D) Other (please describe)"

**User:** "A - why did it drop"

**Agent:** "When did you notice the drop?

A) Last week
B) Last month
C) I'm not sure, help me find it"

**User:** "A"

**Agent:** "Where is your data? Please provide file path(s)."

**User:** "~/data/events.csv"

**Agent:** [Validates path with security wrapper]

"Got it. Do you have user information in a separate file, or is everything in events.csv?

A) All in events.csv
B) Need to join with users.csv
C) Need multiple files"

**User:** "B - users.csv is also in ~/data/"

**Agent:** [Validates second path]

"Perfect. How should I break down the analysis?

A) Overall retention drop
B) By user acquisition channel
C) By user segment
D) Multiple dimensions"

**User:** "B"

**Agent:** [Scores complexity]

"Analysis Task Complexity

Score: 5/10
Suggested Mode: Collaborative
Reasoning: Multi-file JOIN (2pts) + Retention analysis (2pts) + Business rules (1pt)

In collaborative mode, I'll generate code drafts for your review and we'll work together. Proceed?"

**User:** "Yes"

**Agent:** [Routes to execution - Phase 1: tells user execution coming in Phase 2]
