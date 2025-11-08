# NL2SQL CrewAI Pipeline

An agentic pipeline that converts natural language queries to SQL using CrewAI's multi-agent orchestration framework.

## 🏗️ Architecture

The pipeline consists of 5 specialized agents:

1. **Intent Agent** - Classifies user queries into structured metadata
2. **Table Agent** - Selects appropriate database tables
3. **Schema Agent** - Prunes columns to reduce token usage
4. **SQL Agent** - Generates optimized SQL queries
5. **Validation Agent** - Validates query correctness

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd crewai_nl2sql
pip install -r requirements.txt
```

### 2. Set up OpenAI API Key

Create a `.env` file with your OpenAI API key:

```
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Run the Demo

```bash
python demo.py
```

Choose from:
- Quick demo with predefined queries
- Interactive mode to enter your own queries

## 📊 Sample Queries

The system can handle queries like:

- "What is the fully loaded cost per employee by department for Q1 2025?"
- "Show me headcount movements by quarter for 2025"
- "Calculate the benefits ratio by location for current year"
- "What are the total salary costs by department in USD?"

## 🗄️ Sample Database Schema

The demo includes an in-memory SQLite database with:

- **Personnel Details** - Employee financial transactions
- **Personnel Headcount** - Headcount movements
- **Department/Location Masters** - Dimension tables
- **Accounting Periods** - Time dimension
- **Rollup Mappings** - Category hierarchies

## 🔧 Key Features

- **Multi-agent orchestration** using CrewAI
- **Intent classification** for query understanding
- **Smart table selection** based on metrics
- **Schema optimization** to reduce tokens
- **SQL validation** before execution
- **Business rule enforcement** (negation, scenarios, etc.)

## 📝 Business Rules

The system implements several financial data rules:

1. **Negation Logic** - Applies negative values for cost calculations
2. **Scenario Filters** - Handles actuals vs forecast vs budget
3. **Currency Conversion** - Multi-currency support
4. **Time Windows** - Fiscal period mapping
5. **Aggregation Levels** - Employee, department, location, company

## 🛠️ Customization

To adapt for your database:

1. Update `sample_schema.py` with your schema
2. Modify `DATA_RULES` for your business logic
3. Add new `METRIC_TEMPLATES` for common queries
4. Adjust agent prompts in `agents.py`

## 📊 Example Output

```
Query: "What is the fully loaded cost per employee by department for Q1 2025?"

Generated SQL:
SELECT 
    d.department_name,
    SUM(CASE WHEN mrm.requires_negation = 1 THEN -pd.amount ELSE pd.amount END) / 
    COUNT(DISTINCT pd.employee_id) as cost_per_employee
FROM a_personnel_details pd
JOIN m_department d ON pd.department_id = d.department_id
JOIN master_rollup_mapping_details mrm ON pd.category = mrm.category
WHERE pd.fiscal_year = 2025 
    AND pd.plan_version_name = 'actual'
    AND mrm.is_compensation = 1
GROUP BY d.department_name

Results:
+------------------+--------------------+
| department_name  | cost_per_employee  |
+==================+====================+
| Engineering      |        11,750.00   |
| Sales            |        14,500.00   |
+------------------+--------------------+
```

## 🚧 Production Considerations

For production use:

1. Replace SQLite with your actual database
2. Implement proper authentication
3. Add query result caching
4. Set up monitoring and logging
5. Create unit tests for agents
6. Add rate limiting for API calls
7. Implement user feedback collection

## 📚 Dependencies

- CrewAI - Multi-agent orchestration
- LangChain - LLM integration
- SQLAlchemy - Database abstraction
- OpenAI - Language model
- Pandas - Data manipulation
- Colorama - Terminal colors

## 🤝 Contributing

To extend the system:

1. Add new agents for specialized tasks
2. Create additional tools in `tools.py`
3. Implement new metric templates
4. Add support for more SQL dialects
5. Enhance validation rules

## 📄 License

MIT License - See LICENSE file for details
