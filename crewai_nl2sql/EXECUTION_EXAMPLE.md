# 🎬 Step-by-Step Execution Example

This document walks through exactly what happens when you ask a question.

## The Question

```
What is the fully loaded cost per employee by department for Q1 2025?
```

---

## Stage 1: Intent Classification

### What the User Sees
Nothing yet - processing...

### What Happens Behind the Scenes

**Agent**: Intent Strategist  
**Tool**: `classify_intent()`

**Processing**:
```python
question = "What is the fully loaded cost per employee by department for Q1 2025?"

# Step 1: Normalize text
question_lower = "what is the fully loaded cost per employee by department for q1 2025?"

# Step 2: Detect metric type
if "fully loaded cost" in question_lower:
    intent["metric_type"] = "fully_loaded_cost"  # ✓ Matched!

# Step 3: Detect aggregation level
if "department" in question_lower:
    intent["aggregation_level"] = "department"  # ✓ Matched!

# Step 4: Detect time window
quarter_match = re.search(r'q([1-4])\s*(\d{4})?', question_lower)
# Finds: q1 2025
intent["time_window"] = "Q1 2025"  # ✓ Matched!

# Step 5: Check for negation requirement
# Since metric is "fully_loaded_cost", it needs negation logic
intent["requires_negation"] = True  # ✓ Set!

# Step 6: Detect scenario
if "current year" in question_lower or "to date" in question_lower:
    # Not found, use default
    intent["scenario"] = "historical_actuals_only"  # Default
```

**Output**:
```json
{
  "metric_type": "fully_loaded_cost",
  "scenario": "historical_actuals_only",
  "aggregation_level": "department",
  "time_window": "Q1 2025",
  "requires_currency_conversion": false,
  "requires_negation": true
}
```

---

## Stage 2: Table Selection

### What the User Sees
Still processing...

### What Happens Behind the Scenes

**Agent**: Table Curator  
**Tool**: `select_tables()`

**Input**: Intent metadata (from Stage 1)

**Processing**:
```python
tables = []

# Rule 1: Financial metrics need personnel details
if intent["metric_type"] in ["fully_loaded_cost", "salary", "benefits_ratio"]:
    tables.append("a_personnel_details")  # ✓ Added

# Rule 2: Always add master tables
tables.extend(["m_department", "m_location", "m_accounting_period"])
# ✓ Added: m_department, m_location, m_accounting_period

# Rule 3: Cost categories need rollup mapping
if intent["metric_type"] in ["fully_loaded_cost", "benefits_ratio"]:
    tables.append("master_rollup_mapping_details")  # ✓ Added

# Rule 4: Check currency requirement
if intent.get("requires_currency_conversion"):
    tables.append("currency_master")  # Not needed, skipped

# Remove duplicates
tables = list(set(tables))
```

**Output**:
```python
[
  "a_personnel_details",
  "m_department", 
  "m_location",
  "m_accounting_period",
  "master_rollup_mapping_details"
]
```

---

## Stage 3: Schema Pruning

### What the User Sees
Still processing...

### What Happens Behind the Scenes

**Agent**: Schema Trimmer  
**Tool**: `prune_columns()`

**Input**: List of tables from Stage 2

**Processing**:
```python
pruned_schema = {}

# For a_personnel_details
column_rules = {
    "a_personnel_details": [
        "employee_id",      # Keep - needed for counting employees
        "department_id",    # Keep - needed for grouping
        "amount",           # Keep - needed for calculation
        "category",         # Keep - needed for rollup
        "fiscal_year"       # Keep - needed for filtering
    ]
}

pruned_schema["a_personnel_details"] = [
    "employee_id",
    "department_id", 
    "accounting_period",
    "amount",
    "currency_id",
    "category",
    "category_rollup",
    "closed",
    "plan_version_name",
    "fiscal_year"
]

# For m_department
pruned_schema["m_department"] = [
    "department_id",        # Keep - needed for join
    "department_name"       # Keep - needed for display
]

# For master_rollup_mapping_details
pruned_schema["master_rollup_mapping_details"] = [
    "category",             # Keep - needed for join
    "category_rollup",      # Keep - for hierarchy
    "is_compensation",      # Keep - for filtering
    "requires_negation"     # Keep - for business logic
]
```

**Output**:
```json
{
  "a_personnel_details": [
    "employee_id", "department_id", "accounting_period", 
    "amount", "category", "closed", "plan_version_name", "fiscal_year"
  ],
  "m_department": ["department_id", "department_name"],
  "m_accounting_period": ["period_id", "name", "fiscal_quarter", "fiscal_year"],
  "master_rollup_mapping_details": [
    "category", "is_compensation", "requires_negation"
  ]
}
```

---

## Stage 4: SQL Generation

### What the User Sees
Still processing...

### What Happens Behind the Scenes

**Agent**: SQL Composer  
**Tool**: `generate_sql()`

**Input**: 
- Intent (from Stage 1)
- Tables (from Stage 2)
- Pruned schema (from Stage 3)

**Processing**:
```python
# Step 1: Check if template exists
if intent["metric_type"] == "fully_loaded_cost":
    template_key = "fully_loaded_cost_per_employee"
    
    # Load template
    template = """
        SELECT 
            d.department_name,
            SUM(CASE WHEN mrm.requires_negation = 1 THEN -pd.amount ELSE pd.amount END) / 
            COUNT(DISTINCT pd.employee_id) as cost_per_employee
        FROM a_personnel_details pd
        JOIN m_department d ON pd.department_id = d.department_id
        JOIN m_accounting_period ap ON pd.accounting_period = ap.name
        JOIN master_rollup_mapping_details mrm ON pd.category = mrm.category
        WHERE {scenario_filter}
            AND mrm.is_compensation = 1
            AND pd.fiscal_year = {year}
        GROUP BY d.department_name
    """
    
    # Step 2: Get scenario filter
    scenario_filter = DATA_RULES["scenario_filters"]["historical_actuals_only"]["filter"]
    # Result: "pd.plan_version_name = 'actual' AND pd.closed = 1"
    
    # Step 3: Extract year
    year = "2025"  # From intent["time_window"]
    
    # Step 4: Format template
    sql = template.format(
        scenario_filter=scenario_filter,
        year=year
    )
```

**Output**:
```json
{
  "sql": "SELECT \n    d.department_name,\n    SUM(CASE WHEN mrm.requires_negation = 1 THEN -pd.amount ELSE pd.amount END) / \n    COUNT(DISTINCT pd.employee_id) as cost_per_employee\nFROM a_personnel_details pd\nJOIN m_department d ON pd.department_id = d.department_id\nJOIN m_accounting_period ap ON pd.accounting_period = ap.name\nJOIN master_rollup_mapping_details mrm ON pd.category = mrm.category\nWHERE pd.plan_version_name = 'actual' \n    AND pd.closed = 1\n    AND mrm.is_compensation = 1\n    AND pd.fiscal_year = 2025\nGROUP BY d.department_name",
  "decisions": {
    "negation": "applied",
    "scenario": "historical_actuals_only",
    "currency": "no_conversion",
    "rollups": ["salary", "benefits", "taxes"]
  },
  "notes": "Generated from template for fully_loaded_cost"
}
```

---

## Stage 5: SQL Validation

### What the User Sees
Still processing...

### What Happens Behind the Scenes

**Agent**: Query Auditor  
**Tool**: `validate_sql()`

**Input**: Generated SQL from Stage 4

**Processing**:
```python
sql_lower = sql.lower()
issues = []

# Check 1: All tables are referenced
expected_tables = ["a_personnel_details", "m_department", "m_accounting_period", 
                   "master_rollup_mapping_details"]

for table in expected_tables:
    if table.lower() not in sql_lower:
        issues.append(f"Missing table: {table}")
    else:
        # ✓ All tables present

# Check 2: Join conditions exist
if ".department_id = " in sql_lower:
    # ✓ Department join present
    
if "accounting_period = " in sql_lower and ".name" in sql_lower:
    # ✓ Period mapping correct

# Check 3: Scenario filter
if "where" in sql_lower:
    # ✓ WHERE clause present
    if "plan_version_name" in sql_lower:
        # ✓ Scenario filter applied

# Check 4: Negation logic
if "case when" in sql_lower and "requires_negation" in sql_lower:
    # ✓ Negation logic present

# Check 5: No illegal casts
if "cast(" in sql_lower:
    if "as integer" in sql_lower:
        # Check if casting names (bad) or numbers (ok)
        if "department_name" not in sql_lower or "location_name" not in sql_lower:
            # ✓ No illegal casts
    else:
        # ✓ No illegal casts
```

**Output**:
```json
{
  "is_valid": true,
  "issues": [],
  "checks_passed": [
    "✓ All tables properly joined",
    "✓ Period mapping correct (accounting_period = name)",
    "✓ Scenario filter applied",
    "✓ Negation logic present for costs",
    "✓ Appropriate GROUP BY clause"
  ],
  "recommendations": []
}
```

---

## Final Result

### What the User Sees

```
🚀 Processing query: 'What is the fully loaded cost per employee by department for Q1 2025?'

─────────────────────────────────────────────────────────────────────────────
Pipeline Results:
─────────────────────────────────────────────────────────────────────────────

📌 INTENT:
{
  "metric_type": "fully_loaded_cost",
  "scenario": "historical_actuals_only",
  "aggregation_level": "department",
  "time_window": "Q1 2025"
}

📌 TABLES:
["a_personnel_details", "m_department", "m_accounting_period", 
 "master_rollup_mapping_details"]

📌 SCHEMA:
{"a_personnel_details": ["employee_id", "department_id", "amount", ...]}

📌 SQL_GENERATION:
{"sql": "SELECT d.department_name, ...", "decisions": {...}}

🔍 GENERATED SQL:
─────────────────────────────────────────────────────────────────────────────
SELECT 
    d.department_name,
    SUM(CASE WHEN mrm.requires_negation = 1 THEN -pd.amount ELSE pd.amount END) / 
    COUNT(DISTINCT pd.employee_id) as cost_per_employee
FROM a_personnel_details pd
JOIN m_department d ON pd.department_id = d.department_id
JOIN m_accounting_period ap ON pd.accounting_period = ap.name
JOIN master_rollup_mapping_details mrm ON pd.category = mrm.category
WHERE pd.plan_version_name = 'actual' 
    AND pd.closed = 1
    AND ap.fiscal_quarter = 1
    AND ap.fiscal_year = 2025
    AND mrm.is_compensation = 1
GROUP BY d.department_name

✅ VALIDATION:
─────────────────────────────────────────────────────────────────────────────
✓ All tables properly joined
✓ Period mapping correct (accounting_period = name)
✓ Scenario filter applied
✓ Negation logic present for costs
✓ Appropriate GROUP BY clause

📊 QUERY EXECUTION RESULTS:
─────────────────────────────────────────────────────────────────────────────

+------------------+--------------------+
| department_name  | cost_per_employee  |
+==================+====================+
| Engineering      |        13,500.00   |
| Sales            |        14,500.00   |
| HR               |        11,000.00   |
+------------------+--------------------+

✓ Query returned 3 rows
```

---

## Key Insights from This Example

### 1. Each Stage Transforms Data

- **Stage 1**: Free text → Structured metadata
- **Stage 2**: Metadata → Table list
- **Stage 3**: Table list → Optimized schema
- **Stage 4**: Schema + Intent → SQL code
- **Stage 5 stadium → Validation → Success/Failure

### 2. Business Rules Are Applied

- **Negation Rule**: Applied because metric is "fully_loaded_cost"
- **Scenario Filter**: Applied because scenario is "historical_actuals_only"
- **Time Window**: Applied from "Q1 2025" to fiscal_year = 2025

### 3. Validation Catches Errors

- Checks that all necessary tables are joined
- Verifies business logic is correctly implemented
- Ensures SQL will execute without errors

### 4. Modular Design Works

Each agent:
- Receives specific input
- Does one focused task
- Produces structured output
- Passes results to next agent

This makes the system:
- **Debuggable**: Know exactly which stage failed
- **Maintainable**: Update one agent independently
- **Scalable**: Add new agents or features easily
