# Complexity Scoring Rubric

Score analysis tasks on a scale of 1-10.

## Scoring Dimensions

### 1. Data Complexity (1-3 points)

- **1 point**: Single file, no joins
  - Example: "Show me top 10 customers by revenue" from `customers.csv`

- **2 points**: Multiple files requiring JOIN
  - Example: "User retention by channel" needs `users.csv` + `events.csv`

- **3 points**: Complex data cleaning or transformation
  - Example: "Parse JSON logs, deduplicate, then analyze"

### 2. Analytical Method Complexity (1-4 points)

- **1 point**: Simple aggregation/sorting/filtering
  - Example: `df.groupby('category').sum()`

- **2 points**: Multi-dimensional slicing/pivoting
  - Example: Cohort analysis, retention heatmap, pivot tables

- **3 points**: Statistical tests/correlation analysis
  - Example: t-test, chi-square, correlation matrix

- **4 points**: Advanced modeling
  - Example: Regression, classification, time series forecasting

### 3. Business Logic Complexity (1-3 points)

- **1 point**: Standard metrics (DAU, revenue, etc.)
  - Clear definition, no ambiguity

- **2 points**: Requires understanding business rules
  - Example: "Active user" definition varies by context

- **3 points**: Cross-department alignment needed
  - Example: Sales and Marketing define "conversion" differently

## Score to Mode Mapping

- **Score < 3**: Auto Mode - Fully automated
- **Score 3-7**: Collaborative Mode - Human checkpoints
- **Score > 7**: Advisory Mode - Agent provides guidance

## Examples

### Example 1: Auto Mode (Score = 2)

**Request**: "Show me top 10 users by total revenue"

**Breakdown**:
- Data: Single file `users.csv` (1pt)
- Method: Simple aggregation (1pt)
- Business: Standard metric (0pt, already counted in method)

**Total**: 2 points → **Auto Mode**

### Example 2: Collaborative Mode (Score = 5)

**Request**: "Analyze why retention dropped last week by channel"

**Breakdown**:
- Data: Need `users.csv` + `events.csv` with JOIN (2pt)
- Method: Retention cohort analysis (2pt)
- Business: "Retention" definition may vary (1pt)

**Total**: 5 points → **Collaborative Mode**

### Example 3: Advisory Mode (Score = 9)

**Request**: "Build a churn prediction model with 85% accuracy"

**Breakdown**:
- Data: Multiple sources, feature engineering (3pt)
- Method: Classification model + cross-validation (4pt)
- Business: "Churn" definition needs alignment (2pt)

**Total**: 9 points → **Advisory Mode**
