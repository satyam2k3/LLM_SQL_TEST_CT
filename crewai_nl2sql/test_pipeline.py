"""
Test script to demonstrate NL2SQL pipeline structure
This can run without an OpenAI API key to show the system design
"""
import json
from colorama import init, Fore, Style
from sample_schema import SAMPLE_SCHEMA, DATA_RULES, METRIC_TEMPLATES

# Initialize colorama
init(autoreset=True)

def demonstrate_pipeline():
    """Demonstrate the pipeline flow with mock responses"""
    
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}🎯 NL2SQL Pipeline Demonstration (No API Key Required)")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    # Sample query
    query = "What is the fully loaded cost per employee by department for Q1 2025?"
    print(f"{Fore.GREEN}User Query: {query}\n")
    
    # Stage 1: Intent Classification
    print(f"{Fore.YELLOW}📋 Stage 1: Intent Classification")
    print(f"{Fore.YELLOW}{'-'*50}")
    mock_intent = {
        "metric_type": "fully_loaded_cost",
        "scenario": "historical_actuals_only",
        "aggregation_level": "department",
        "time_window": "Q1 2025",
        "requires_currency_conversion": False
    }
    print(f"Output: {json.dumps(mock_intent, indent=2)}\n")
    
    # Stage 2: Table Selection
    print(f"{Fore.YELLOW}🗂️  Stage 2: Table Selection")
    print(f"{Fore.YELLOW}{'-'*50}")
    selected_tables = [
        "a_personnel_details",
        "m_department",
        "m_location", 
        "m_accounting_period",
        "master_rollup_mapping_details"
    ]
    print(f"Selected Tables: {selected_tables}\n")
    
    # Stage 3: Schema Pruning
    print(f"{Fore.YELLOW}✂️  Stage 3: Schema Pruning")
    print(f"{Fore.YELLOW}{'-'*50}")
    pruned_columns = {
        "a_personnel_details": ["employee_id", "department_id", "amount", "category", "fiscal_year"],
        "m_department": ["department_id", "department_name"],
        "master_rollup_mapping_details": ["category", "requires_negation", "is_compensation"]
    }
    print("Pruned Schema (showing key tables):")
    for table, cols in list(pruned_columns.items())[:2]:
        print(f"  {table}: {cols}")
    print()
    
    # Stage 4: SQL Generation
    print(f"{Fore.YELLOW}💻 Stage 4: SQL Generation")
    print(f"{Fore.YELLOW}{'-'*50}")
    generated_sql = """SELECT 
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
GROUP BY d.department_name"""
    
    print(f"{Fore.WHITE}{generated_sql}\n")
    
    # Stage 5: Validation
    print(f"{Fore.YELLOW}✅ Stage 5: SQL Validation")
    print(f"{Fore.YELLOW}{'-'*50}")
    validation_result = {
        "is_valid": True,
        "checks_passed": [
            "✓ All tables properly joined",
            "✓ Period mapping correct (accounting_period = name)",
            "✓ Scenario filter applied",
            "✓ Negation logic present for costs",
            "✓ Appropriate GROUP BY clause"
        ],
        "issues": []
    }
    for check in validation_result["checks_passed"]:
        print(f"{Fore.GREEN}{check}")
    print()
    
    # Show sample results
    print(f"{Fore.CYAN}📊 Sample Results:")
    print(f"{Fore.CYAN}{'-'*50}")
    print("""
+------------------+--------------------+
| department_name  | cost_per_employee  |
+==================+====================+
| Engineering      |       -13,500.00   |
| Sales            |       -14,500.00   |
| HR               |       -11,000.00   |
+------------------+--------------------+
    """)
    
    print(f"{Fore.GREEN}✓ Pipeline demonstration complete!\n")


def show_available_metrics():
    """Show available metric templates"""
    print(f"\n{Fore.CYAN}📊 Available Metric Templates:")
    print(f"{Fore.CYAN}{'-'*50}\n")
    
    for metric_name, template in METRIC_TEMPLATES.items():
        print(f"{Fore.YELLOW}{metric_name}:")
        # Clean up template for display
        clean_template = ' '.join(template.split())[:100] + "..."
        print(f"{Style.DIM}{clean_template}\n")


def show_business_rules():
    """Display business rules"""
    print(f"\n{Fore.CYAN}📋 Business Rules:")
    print(f"{Fore.CYAN}{'-'*50}\n")
    
    # Negation rules
    print(f"{Fore.YELLOW}Negation Rules:")
    for metric, rules in DATA_RULES["negation_rules"].items():
        print(f"  • {metric}: {rules['description']}")
    print()
    
    # Scenario filters  
    print(f"{Fore.YELLOW}Scenario Filters:")
    for scenario, filter_def in DATA_RULES["scenario_filters"].items():
        print(f"  • {scenario}: {filter_def['description']}")
    print()


def show_schema_overview():
    """Display schema overview"""
    print(f"\n{Fore.CYAN}🗄️ Database Schema Overview:")
    print(f"{Fore.CYAN}{'-'*50}\n")
    
    for table_name, table_info in SAMPLE_SCHEMA.items():
        print(f"{Fore.YELLOW}{table_name}:")
        print(f"{Style.DIM}  {table_info['description']}")
        print(f"{Style.DIM}  Columns: {len(table_info['columns'])}")
        # Show first 3 columns
        cols = list(table_info['columns'].keys())[:3]
        print(f"{Style.DIM}  Sample: {', '.join(cols)}...")
        print()


if __name__ == "__main__":
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}NL2SQL CrewAI Pipeline - Architecture Demo")
    print(f"{Fore.CYAN}{'='*80}")
    
    # Show menu
    while True:
        print(f"\n{Fore.GREEN}Choose an option:")
        print(f"{Fore.CYAN}1. Demonstrate full pipeline flow")
        print(f"{Fore.CYAN}2. Show database schema")
        print(f"{Fore.CYAN}3. Show business rules")
        print(f"{Fore.CYAN}4. Show available metrics")
        print(f"{Fore.CYAN}5. Exit\n")
        
        choice = input(f"{Fore.GREEN}Enter your choice (1-5): {Fore.WHITE}")
        
        if choice == '1':
            demonstrate_pipeline()
        elif choice == '2':
            show_schema_overview()
        elif choice == '3':
            show_business_rules()
        elif choice == '4':
            show_available_metrics()
        elif choice == '5':
            print(f"{Fore.YELLOW}Goodbye!")
            break
        else:
            print(f"{Fore.RED}Invalid choice. Please try again.")
