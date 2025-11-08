# NL2SQL CrewAI Pipeline

A production-ready multi-agent system that converts natural language queries to SQL using CrewAI's orchestration framework. This system is designed for HR and Financial data analysis, with specialized agents handling intent classification, table selection, schema optimization, SQL generation, and validation.

## 🎯 Features

- **Multi-Agent Architecture**: 5 specialized agents working in sequence
- **Intent Classification**: Understands user queries and extracts structured metadata
- **Smart Table Selection**: Automatically selects appropriate database tables
- **Schema Optimization**: Prunes unnecessary columns to reduce token usage
- **SQL Generation**: Creates optimized SQL queries with business rules
- **Query Validation**: Validates SQL correctness before execution
- **Sample Database**: Includes in-memory SQLite database for demonstration
- **Multiple Run Modes**: Test mode (no API), demo mode, and interactive mode

## 🏗️ Architecture

The pipeline consists of 5 specialized agents:

1. **Intent Agent** - Classifies user queries into structured metadata
2. **Table Agent** - Selects appropriate database tables based on metrics
3. **Schema Agent** - Prunes columns to reduce token usage
4. **SQL Agent** - Generates optimized SQL queries with business rules
5. **Validation Agent** - Validates query correctness before execution

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (optional for test mode)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd llm_sql_test_CT
```

2. Install dependencies:
```bash
cd crewai_nl2sql
pip install -r requirements.txt
```

3. Set up environment variables (optional):
```bash
# Create a .env file in the crewai_nl2sql directory
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### Running the System

#### Test Mode (No API Key Required)
Demonstrates the pipeline architecture without making API calls:
```bash
cd crewai_nl2sql
python test_pipeline.py
```

#### Demo Mode (Requires API Key)
Runs predefined queries:
```bash
cd crewai_nl2sql
python demo.py
```

#### Interactive Mode (Requires API Key)
Enter your own queries:
```bash
cd crewai_nl2sql
python run.py
```

## 📊 Sample Queries

The system can handle queries like:

- "What is the fully loaded cost per employee by department for Q1 2025?"
- "Show me headcount movements by quarter for 2025"
- "Calculate the benefits ratio by location for current year"
- "What are the total salary costs by department in USD?"

## 🗄️ Database Schema

The demo includes an in-memory SQLite database with:

- **Personnel Details** - Employee financial transactions
- **Personnel Headcount** - Headcount movements
- **Department/Location Masters** - Dimension tables
- **Accounting Periods** - Time dimension
- **Rollup Mappings** - Category hierarchies

## 🔧 Business Rules

The system implements several financial data rules:

1. **Negation Logic** - Applies negative values for cost calculations
2. **Scenario Filters** - Handles actuals vs forecast vs budget
3. **Currency Conversion** - Multi-currency support
4. **Time Windows** - Fiscal period mapping
5. **Aggregation Levels** - Employee, department, location, company

## 📁 Project Structure

```
.
├── crewai_nl2sql/          # Main application directory
│   ├── agents.py          # Agent definitions
│   ├── crew.py            # CrewAI orchestration
│   ├── tools.py            # Agent tools
│   ├── sample_schema.py   # Sample database schema
│   ├── demo.py            # Demo script
│   ├── run.py             # Interactive runner
│   ├── test_pipeline.py   # Test mode (no API)
│   ├── main.py            # Main application
│   └── requirements.txt   # Python dependencies
├── README.md              # This file
└── .gitignore             # Git ignore rules
```

## 🛠️ Customization

To adapt for your database:

1. Update `crewai_nl2sql/sample_schema.py` with your schema
2. Modify `DATA_RULES` for your business logic
3. Add new `METRIC_TEMPLATES` for common queries
4. Adjust agent prompts in `crewai_nl2sql/agents.py`

## 📚 Documentation

Comprehensive documentation is available in the `crewai_nl2sql/` directory:

- `README.md` - Quick start guide
- `DETAILED_DOCUMENTATION.md` - In-depth explanation
- `ARCHITECTURE_DIAGRAM.md` - Visual diagrams
- `EXECUTION_EXAMPLE.md` - Step-by-step walkthrough
- `INSTALL_AND_RUN.md` - Setup instructions

## 🚧 Production Considerations

For production use:

1. Replace SQLite with your actual database
2. Implement proper authentication
3. Add query result caching
4. Set up monitoring and logging
5. Create unit tests for agents
6. Add rate limiting for API calls
7. Implement user feedback collection

## 📦 Dependencies

- **CrewAI** - Multi-agent orchestration
- **LangChain** - LLM integration
- **SQLAlchemy** - Database abstraction
- **OpenAI** - Language model
- **Pandas** - Data manipulation
- **Colorama** - Terminal colors

See `crewai_nl2sql/requirements.txt` for complete list.

## 🤝 Contributing

To extend the system:

1. Add new agents for specialized tasks
2. Create additional tools in `tools.py`
3. Implement new metric templates
4. Add support for more SQL dialects
5. Enhance validation rules

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built with [CrewAI](https://github.com/joaomdmoura/crewAI) - A framework for orchestrating role-playing, autonomous AI agents.

