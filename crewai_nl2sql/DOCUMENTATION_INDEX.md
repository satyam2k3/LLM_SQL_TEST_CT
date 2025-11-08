# 📚 Documentation Index

Welcome! This is your guide to understanding the NL2SQL CrewAI pipeline implementation.

## Collector's Guide

Choose your learning path based on what you need to understand:

### 🚀 Quick Start (5 minutes)
**Start here if you want to run it NOW**
- [README.md](README.md) - Installation and quick start
- [FINAL_SUMMARY.md](FINAL_SUMMARY.md) - What was built and how to use it

### 🧠 Deep Understanding (30 minutes)
**Start here if you want to understand HOW it works**
- [DETAILED_DOCUMENTATION.md](DETAILED_DOCUMENTATION.md) - Comprehensive explanation bottom up
  - System overview
  - Agent responsibilities  
  - Data flow
  - Business logic
  - Code walkthrough

### 📊 Visual Learners (15 minutes)
**Start here if you prefer diagrams**
- [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md) - Visual architecture
  - System overview diagram
  - Agent interaction flow
  - Data transformation pipeline
  - State flow between agents
  - Component relationships

### 💻 Step-by-Step Walkthrough (20 minutes)
**Start here to see it in action**
- [EXECUTION_EXAMPLE.md](EXECUTION_EXAMPLE.md) - Complete example walkthrough
  - Exact step-by-step execution
  - What happens at each stage
  - Code snippets showing processing
  - Transformation of data
  - Final output

### 🛠️ Installation & Troubleshooting
**Start here for setup issues**
- [INSTALL_AND_RUN.md](INSTALL_AND_RUN.md) - Installation and running instructions
  - Dependency installation
  - Configuration
  - Troubleshooting

## Documentation Map

```
Documentation Structure:

README.md (Entry Point)
│
├─ FINAL_SUMMARY.md (What Was Built)
│
├─ DETAILED_DOCUMENTATION.md (How It Works)
│  ├─ System Overview
│  ├─ Architecture Deep Dive
│  ├─ Component Breakdown
│  │  ├─ 5 Agents (Intent, Table, Schema, SQL, Validation)
│  │  ├─ Tools for each agent
│  │  └─ Orchestration
│  ├─ Data Flow
│  ├─ Business Logic
│  │  ├─ Cost Negation
│  │  ├─ Scenario Filtering
│  │  ├─ Time Period Mapping
│  │  └─ Category Rollups
│  └─ Code Walkthrough
│
├─ ARCHITECTURE_DIAGRAM.md (Visual Understanding)
│  ├─ System Overview Diagram
│  ├─ Agent Interaction Flow
│  ├─ Data Transformation Pipeline
│  ├─ Agent Responsibilities
│  ├─ State Flow
│  └─ Component Relationships
│
├─ EXECUTION_EXAMPLE.md (See It Work)
│  ├─ The Question
│  ├─ Stage 1: Intent Classification
│  ├─ Stage 2: Table Selection
│  ├─ Stage 3: Schema Pruning
│  ├─ Stage 4: SQL Generation
│  ├─ Stage 5: SQL Validation
│  └─ Final Result
│
└─ INSTALL_AND_RUN.md (Getting Started)
   ├─ Installation Steps
   ├─ Running Options
   └─ Troubleshooting
```

## Key Concepts Explained

### Core Concepts
1. **Agent**: Specialized AI worker with a role, goal, backstory, and tools
2. **Tool**: Function that agents use to perform specific tasks
3. **Task**: Work item for an agent with description and expected output
4. **Crew**: CrewAI object that orchestrates multiple agents
5. **Orchestration**: Managing how agents work together

### The 5 Agents
1. **Intent Agent** - Understands what user wants
2. **Table Agent** - Picks right database tables
3. **Schema Agent** - Optimizes columns for efficiency
4. **SQL Agent** - Writes SQL code
5. **Validation Agent** - Checks correctness

### The Pipeline Flow
```
User Question
    ↓
Intent Classification
    ↓
Table Selection
    ↓
Schema Pruning
    ↓
SQL Generation
    ↓
Query Validation
    ↓
Executable SQL
    ↓
Query Results
```

## Recommended Reading Order

### For Understanding (Choose One Path)

**Path 1: Theoretical First**
1. DETAILED_DOCUMENTATION.md
2. ARCHITECTURE_DIAGRAM.md
3. EXECUTION_EXAMPLE.md

**Path 2: Practical First**
1. EXECUTION_EXAMPLE.md
2. ARCHITECTURE_DIAGRAM.md
3. DETAILED_DOCUMENTATION.md

**Path 3: Visual First**
1. ARCHITECTURE_DIAGRAM.md
2. EXECUTION_EXAMPLE.md
3. DETAILED_DOCUMENTATION.md

### For Implementing Changes

1. DETAILED_DOCUMENTATION.md (understand current design)
2. ARCHITECTURE_DIAGRAM.md (see relationships)
3. EXECUTION_EXAMPLE.md (see data flow)
4. Then modify code in these files:
   - agents.py (add/modify agents)
   - tools.py (add/modify tools)
   - crew.py (change orchestration)
   - sample_schema.py (add business rules)

## Code Files Reference

| File | Purpose | Key Concepts |
|------|---------|--------------|
| `agents.py` | Agent definitions | Agent class, roles, goals, tools |
| `tools.py` | Agent tools/functions | Tool decorator, function logic |
| `crew.py` | Pipeline orchestration | Crew, tasks, context |
| `sample_schema.py` | Data model & rules | Schema, business rules, templates |
| `main.py` | Application entry point | User interface, execution |
| `test_pipeline.py` | Demo without API | Mock responses, architecture show |

## Quick Answers

**Q: How do I run this?**
→ See INSTALL_AND_RUN.md

**Q: What is this system?**
→ See DETAILED_DOCUMENTATION.md "System Overview"

**Q: How does it work?**
→ See EXECUTION_EXAMPLE.md for step-by-step

**Q: What are the agents?**
→ See DETAILED_DOCUMENTATION.md "Component Breakdown"

**Q: How do agents work together?**
→ See ARCHITECTURE_DIAGRAM.md "Agent Interaction Flow"

**Q: What business rules are implemented?**
→ See DETAILED_DOCUMENTATION.md "Business Logic"

**Q: Where do I start modifying code?**
→ See recommended reading above

---

**Happy Learning! 🚀**
