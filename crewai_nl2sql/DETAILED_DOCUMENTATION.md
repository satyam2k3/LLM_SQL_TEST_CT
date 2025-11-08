# 📚 NL2SQL CrewAI Pipeline - Detailed Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Deep Dive](#architecture-deep-dive)
3. [Component Breakdown](#component-breakdown)
4. [Data Flow](#data-flow)
5. [Business Logic](#business-logic)
6. [Code Walkthrough](#code-walkthrough)
7. [How It Works](#how-it-works)

---

## System Overview

### What Is This?

An **agentic pipeline** that automatically converts plain English questions into executable SQL queries for HR and financial data analysis.

### The Problem It Solves

Business analysts and executives often need to query financial and HR data but don't know SQL. This system:

- **Takes** natural language questions like "What's the fully loaded cost per employee by department?"
- **Understands** the business context (cost calculations, aggregation levels, time periods)
- **Generates** complex SQL with proper joins, filters, and business rules
- **Validates** the query before execution to ensure correctness

### The Solution: Multi-Agent System

Instead of one big AI trying to do everything, we use **5 specialized agents**, each expert in one task:

1. **Intent Agent** - Understands what the user wants
2. **Table Agent** - Picks the right database tables
3. **Schema Agent** - Reduces complexity by selecting only needed columns
4. **SQL Agent** - Writes the actual SQL code
5. **Validation Agent** - Checks for errors

---

## Architecture Deep Dive

### Technology Stack

```
User Query
    ↓
┌─────────────────────────────────────────────────────────┐
│                 CrewAI Framework                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │  Agent 1 │→ │  Agent 2 │→ │  Agent 3 │→ │ Agent 4 │ │
│  │  Intent  │  │  Tables  │  │  Schema  │  │   SQL   │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
│                       ↓                                    │
│                 ┌──────────┐                              │
│                 │  Agent 5 │                              │
│                 │  Validate│                              │
│                 └──────────┘                              │
└─────────────────────────────────────────────────────────┘
    ↓
Executable SQL Query
    ↓
Database Execution
    ↓
Formatted Results
```

### Key Technologies

1. **CrewAI** - Orchestrates multi-agent workflows
2. **LangChain** - Connects to language models
3. **SQLite** - In-memory demo database
4. **Python** - Implementation language

---

## Component Breakdown

### 1. Agents (agents.py)

Agents are specialized AI workers with defined roles, goals, and tools.

#### Intent Strategist Agent

**Purpose**: Understand user intent

**What it does**:
- Analyzes the natural language query
- Identifies the business metric being requested
- Determines the time period and scenario
- Detects aggregation level (company, department, employee)

**Example Input**:
```
"What is the fully loaded cost per employee by department for Q1 2025?"
```

**Example Output**:
```json
{
  "metric_type": "fully_loaded_cost",
  "scenario": "historical_actuals_only",
  "aggregation_level": "department",
  "time_window": "Q1 2025",
  "requires_currency_conversion": false
}
```

**Tools**: `classify_intent()`

#### Table Curator Agent

**Purpose**: Select relevant database tables

**What it does**:
- Chooses the core fact table (where actual data lives)
- Adds dimension tables (department, location, time)
- Includes special tables for currency or category rollups if needed

**Example Output**:
```python
[
  "a_personnel_details",      # Main employee cost data
  "m_department",             # Department lookups
  "m_location",               # Location lookups
  "m_accounting_period",      # Time period lookups
  "master_rollup_mapping_details"  # Category hierarchy
]
```

**Tools**: `select_tables()`

#### Schema Trimmer Agent

**Purpose**: Reduce token usage by keeping only necessary columns

**Why it's important**:
- Large schemas can confuse AI models
- Too many irrelevant columns waste tokens and money
- Focus on essential data improves accuracy

**What it does**:
- For each table, keeps only:
  - Join keys (IDs)
  - Measure columns (amounts, counts)
  - Business attributes (categories, plan versions)
  - Time fields

**Example Output**:
```json
{
  "a_personnel_details": ["employee_id", "department_id", "amount", "category", "fiscal_year"],
  "m_department": ["department_id", "department_name"],
  "master_rollup_mapping_details": ["category", "requires_negation", "is_compensation"]
}
```

**Tools**: `prune_columns()`

#### SQL Composer Agent

**Purpose**: Generate the actual SQL query

**What it does**:
- Writes SELECT statements with proper columns
- Adds necessary JOINs between tables
- Implements WHERE filters for scenarios
- Applies business rules (negation, aggregations)
- Documents decisions

**Example Output**:
```sql
SELECT 
    d.department_name,
    SUM(CASE WHEN mrm.requires_due to character limit, I'll continue in the next part.

negation = 1 THEN -pd.amount ELSE pd.amount END) / 
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
```

**Key Decisions**:
- Applied negation logic for costs
- Filtered to actuals only
- Grouped by department
- Calculated per-employee average

**Tools**: `generate_sql()`

#### Query Auditor Agent

**Purpose**: Validate SQL correctness

**What it checks**:
- All tables properly joined
- Period mapping is correct
- Scenario filters applied
- Business rules implemented correctly
- Query will execute without errors

**Example Output**:
```json
{
  "is_valid": true,
  "issues": [],
  "checks_passed": [
    "✓ All tables properly joined",
    "✓ Period mapping correct",
    "✓ Scenario filter applied",
    "✓ Negation logic present"
  ]
}
```

**Tools**: `validate_sql()`

---

## Data Flow

Let's trace a complete example:

### User Input
```
"What is the fully loaded cost per employee by department for Q1 2025?"
```

### Stage 1: Intent Classification

**Agent**: Intent Strategist
**Input**: Raw question
**Processing**: Pattern matching and semantic analysis
**Output**:
```json
{
  "metric_type": "fully_loaded_cost",
  "aggregation_level": "department",
  "time_window": "Q1 2025"
}
```

### Stage 2: Table Selection

**Agent**: Table Curator  
**Input**: Intent metadata
**Processing**: Rules-based selection
- Financial metric → needs `a_personnel_details`
- Department grouping → needs `m_department`
- Q1 2025 → needs `m_accounting_period`
- Cost categories → needs `master_rollup_mapping_details`

**Output**: List of 4 tables

### Stage 3: Schema Pruning

**Agent**: Schema Trimmer
**Input**: Table list
**Processing**: Keep only essential columns
- IDs for joining
- Amount for calculation
- Names for display
- Categories for filtering

**Output**: Reduced schema dictionary

### Stage 4: SQL Generation

**Agent**: SQL Composer
**Input**: Intent + Tables + Schema
**Processing**:
1. Write SELECT with department name
2. Calculate total cost (sum with negation)
3. Divide by employee count
4. Add JOINs to connect tables
5. Add WHERE filters for Q1 2025
6. Add GROUP BY for department

**Output**: Complete SQL query

### Stage 5: Validation

**Agent**: Query Auditor
**Input**: Generated SQL
**Processing**: Check:
- Syntax is valid
- All joins present
- Correct business logic
- No illegal operations

**Output**: Validation report

### Final Output: Executable SQL

```sql
SELECT 
    d.department_name,
    SUM(CASE WHEN mrm.requires_negation = 1 THEN -pd.amount ELSE pd.amount END) / 
    COUNT(DISTINCT pd.employee_id) as cost_per_employee
FROM a_personnel_details pd
JOIN m_department trollup_table
- **Benefits**: Reduced token usage, clearer output

### Agent Orchestration (crew.py)

**Purpose**: Manage the pipeline flow

**Key Concepts**:

1. **Task Creation**: Each agent gets a task with:
   - Description of what to do
   - Expected output format
   - Input from previous tasks

2. **Agent Assignment**: Link tasks to agents

3. **Dependency Management**: Define task order

4. **Execution**: CrewAI runs agents in sequence

**Example Task Definition**:

```python
intent_task = Task(
    description="Analyze user query something about what's going on is working now...understand...",
    agent=intent_agent,
    expected_output="JSON with intent classification"
)

sql_task = Task(
    description="Generate SQL query based on intent and tables",
    agent=sql_agent,
    expected_output="JSON with SQL and reasoning",
    context=[intent_task, table_task]  # Depends on previous tasks
)
```

---

## Business Logic

### What Makes This Different from Generic SQL Generators?

This system understands **financial and HR data semantics**.

### Key Business Rules

#### 1. Cost Negation

**Problem**: In accounting, different cost categories have different signs
- Salary: positive
- Benefits: positive  
- Taxes: positive
- But for "fully loaded cost", some need negation

**Solution**: Use mapping table
```sql
CASE WHEN mrm.requires_negation = 1 
  THEN -pd.amount 
  ELSE pd.amount 
END
```

#### 2. Scenario Filtering

**Problem**: Financial data has different scenarios
- Actuals (what happened)
- Forecasts (what might happen)
- Budgets (what was planned)

**Solution**: Filter by `plan_version_name`
```sql
WHERE pd.plan_version_name IN ('actual', 'forecast')
```

#### 3. Time Period Mapping

**Problem**: Dates need to map to fiscal periods
- User says "Q1 2025"
- Database has "2025-01", "2025-02", "2025-03"
- Need to map periods to quarters

**Solution**: Join through `m_accounting_period`
```sql
JOIN m_accounting_period ap 
  ON pd.accounting_period = ap.name
WHERE ap.fiscal_quarter = 1 AND ap.fiscal_year = 2025
```

#### 4. Category Rollups

**Problem**: Costs are broken into details but need aggregation
- Detail: salary, bonus, benefits, taxes
- Rollup: total compensation

**Solution**: Use `master_rollup_mapping_details` to map
```sql
JOIN master_rollup_mapping_details mrm 
  ON pd.category = mrm.category
WHERE mrm.is_compensation = 1
```

---

## Code Walkthrough

Let's examine key files:

### File Structure

```
crewai_nl2sql/
├── agents.py          # Agent definitions
├── tools.py           # Agent tools (functions)
├── crew.py            # Orchestration
├── sample_schema.py   # Data model & rules
├── main.py            # Application entry
└── test_pipeline.py   # Demo mode
```

### agents.py - Agent Definitions

Each agent is created using CrewAI's Agent class:

```python
def intent_agent():
    return Agent(
        role="Intent Strategist",
        goal="Analyze queries and extract intent metadata",
        backstory="You are an expert at understanding business questions...",
        tools=[classify_intent],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
```

**Key Parameters**:
- `role`: The agent's professional identity
- `goal`: What it's trying to accomplish
- `backstory`: Context to guide behavior
- `tools`: Functions it can use
- `llm`: Language model to use
- `verbose`: Show detailed output
- `allow_delegation`: Can it delegate to other agents?

### tools.py - Agent Tools

Tools are functions that agents call to perform actions:

```python
@tool("Intent Classifier")
def classify_intent(question: str) -> Dict[str, Any]:
    """
    Classify user question into structured metadata
    """
    intent = {
        "metric_type": None,
        "scenario": "historical_actuals_only",
        "aggregation_level": "company",
        "time_window": None
    }
    
    # Pattern matching logic
    question_lower = question.lower()
    
    if "fully loaded cost" in question_lower:
        intent["metric_type"] = "fully_loaded_cost"
    
    if "department" in question_lower:
        intent["aggregation_level"] = "department"
    
    return intent
```

**How it works**:
1. Agent gets a tool
2. Agent calls the tool with input
3. Tool performs processing
4. Returns structured output
5. Agent uses output in next step

### crew.py - Orchestration

The Crew ties everything together:

```python
class NL2SQLCrew:
    def create_tasks(self, user_query: str):
        # Create task for each agent
        intent_task = Task(
            description=f"Analyze this query: '{user_query}'",
            agent=self.intent_agent,
            expected_output="JSON with intent"
        )
        
        table_task = Task(
            description="Select tables based on intent",
            agent=self.table_agent,
            expected_output="List of tables",
            context=[intent_task]  # Uses output from intent
        )
        
        # ... more tasks
        
        return [intent_task, table_task, ...]
    
    def run(self, user_query: str):
        tasks = self.create_tasks(user_query)
        crew = Crew(agents=[...], tasks=tasks)
        result = crew.kickoff()
        return result
```

### sample_schema.py - Data Model

Defines the database structure:

```python
SAMPLE_SCHEMA = {
    "a_personnel_details": {
        "columns": {
            "employee_id": "INTEGER",
            "amount": "DECIMAL(15,2)",
            ...
        },
        "description": "Detailed personnel financial transactions"
    },
    ...
}

DATA_RULES = {
    "negation_rules": {
        "fully_loaded_cost": {
            "apply_negation": True,
            "description": "Sum of all compensation"
        }
    },
    "scenario_filters": {
        "historical_actuals_only": {
            "filter": "plan_version_name = 'actual' AND closed = 1"
        }
    }
}
```

---

## How It Works

### Complete Example Walkthrough

**Step 1: User Asks Question**
```
User: "What is the fully loaded cost per employee by department for Q1 2025?"
```

**Step 2: Intent Agent Analyzes**
- Extracts keywords: "fully loaded cost", "per employee", "department", "Q1 2025"
- Classifies as financial metric with department aggregation
- Outputs structured intent

**Step 3: Table Agent Selects**
- Knows cost data is in `a_personnel_details`
- Adds dimension tables for department and time
- Includes rollup mapping for categories

**Step 4: Schema Agent Prunes**
- Removes unnecessary columns
- Keeps IDs, amounts, categories
- Reduces from 50+ columns to ~10

**Step 5: SQL Agent Writes**
- Looks up template for explanating it fully
- Applies business rules
- Generates complete SQL with joins and filters

**Step 6: Validation Agent Checks**
- Verifies joins are correct
- Confirms business logic
- Ensures query will run

**Step 7: Query Executes**
```
Results:
+------------------+--------------------+
| department_name  | cost_per_employee  |
+------------------+--------------------+
| Engineering      |     13,500.00     |
| Sales            |     14,500.00     |
+------------------+--------------------+
```

### Why Multi-Agent Approach?

**Traditional Approach** (Single Agent):
```
User Query → Big AI → SQL (often wrong)
```

Problems:
- AI gets confused with too much to do
- Hard to debug when it fails
- Can't specialize in different skills

**Our Approach** (Multi-Agent):
```
User Query 
  → Agent 1 (Intent) → understands what user wants
  → Agent 2 (Tables) → knows which tables to use
  → Agent 3 (Schema) → optimizes the data
  → Agent 4 (SQL) → writes the code
  → Agent 5 (Validate) → checks correctness
  → SQL
```

Benefits:
- Each agent is expert in one thing
- Easy to debug (know which stage failed)
- Can improve agents independently
- Clear separation of concerns

---

## Key Insights

### 1. Agents Are Like Team Members

Each agent has:
- **Role**: What they do (Intent Analyst)
- **Goal**: What they're trying to achieve
- **Backstory**: Their experience and expertise
- **Tools**: Specialized functions they can use

### 2. Tasks Are Like Fresh handoffs

- Each task specifies what needs to be done
- Tasks depend on other tasks' outputs
- CrewAI ensures proper order of execution

### 3. Tools Are Like Specialized Equipment

- Each tool does one specific thing
- Tools return structured data
- Agents decide when to use tools

### 4. Business Rules Enable Accuracy

- Generic SQL generators miss industry-specific logic
- Our system understands:
  - Financial accounting rules
  - HR data structures
  - Scenario filtering
  - Cost calculations

---

## Summary

This system demonstrates:

✅ **Multi-agent coordination** - 5 specialized agents working together  
✅ **Clear data flow** - Intent → Tables → Schema → SQL → Validation  
✅ **Business logic** - Understands financial/HR semantics  
✅ **Production-ready patterns** - Separated concerns, modular design  
✅ **Practical demo** - Runs without API keys  

The architecture is **scalable**, **maintainable**, and **extensible** - exactly what you need for a production NL2SQL system!
