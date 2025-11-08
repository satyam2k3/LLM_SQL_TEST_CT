"""
Tools for CrewAI NL2SQL Agents
"""
import json
import re
from typing import Dict, List, Any, Tuple
from crewai_tools import tool
from sample_schema import SAMPLE_SCHEMA, DATA_RULES, METRIC_TEMPLATES


@tool("Intent Classifier")
def classify_intent(question: str) -> Dict[str, Any]:
    """
    Classify user question into structured intent metadata
    
    Args:
        question: Natural language query
        
    Returns:
        Dict with metric_type, scenario, aggregation_level, time_window
    """
    intent = {
        "metric_type": None,
        "scenario": "historical_actuals_only",
        "aggregation_level": "company",
        "time_window": None,
        "requires_currency_conversion": False
    }
    
    question_lower = question.lower()
    
    # Detect metric type
    if "fully loaded cost" in question_lower or "total cost" in question_lower:
        intent["metric_type"] = "fully_loaded_cost"
    elif "benefits" in question_lower and "ratio" in question_lower:
        intent["metric_type"] = "benefits_ratio"
    elif "headcount" in question_lower or "movement" in question_lower:
        intent["metric_type"] = "headcount_movement"
    elif "salary" in question_lower:
        intent["metric_type"] = "salary"
    
    # Detect scenario
    if "current year" in question_lower or "to date" in question_lower:
        intent["scenario"] = "current_year_totals"
    elif "budget" in question_lower:
        intent["scenario"] = "budget_vs_actual"
    elif "forecast" in question_lower:
        intent["scenario"] = "current_year_totals"
        
    # Detect aggregation level
    if "per employee" in question_lower or "by employee" in question_lower:
        intent["aggregation_level"] = "employee_level"
    elif "department" in question_lower:
        intent["aggregation_level"] = "department"
    elif "location" in question_lower or "by location" in question_lower:
        intent["aggregation_level"] = "location"
        
    # Detect time window
    quarter_match = re.search(r'q([1-4])\s*(\d{4})?', question_lower)
    year_match = re.search(r'\b(20\d{2})\b', question_lower)
    
    if quarter_match:
        quarter = quarter_match.group(1)
        year = quarter_match.group(2) or (year_match.group(1) if year_match else "2025")
        intent["time_window"] = f"Q{quarter} {year}"
    elif year_match:
        intent["time_window"] = year_match.group(1)
    
    # Detect currency
    if "inr" in question_lower or "rupees" in question_lower:
        intent["requires_currency_conversion"] = True
        intent["target_currency"] = "INR"
    elif "usd" in question_lower or "dollars" in question_lower:
        intent["requires_currency_conversion"] = True
        intent["target_currency"] = "USD"
        
    return intent


@tool("Table Selector")
def select_tables(intent: Dict[str, Any]) -> List[str]:
    """
    Select appropriate tables based on intent
    
    Args:
        intent: Intent metadata from classifier
        
    Returns:
        List of table names needed for the query
    """
    tables = []
    
    # Core table selection based on metric
    if intent["metric_type"] in ["fully_loaded_cost", "salary", "benefits_ratio"]:
        tables.append("a_personnel_details")
    
    if intent["metric_type"] == "headcount_movement":
        tables.append("a_personnel_headcount")
        
    # Add GL summary if needed
    if intent.get("include_gl_reconciliation"):
        tables.append("a_personnel_summary")
        
    # Always add master tables
    tables.extend(["m_department", "m_location", "m_accounting_period"])
    
    # Add rollup mapping for cost categories
    if intent["metric_type"] in ["fully_loaded_cost", "benefits_ratio"]:
        tables.append("master_rollup_mapping_details")
        
    # Add currency master if conversion needed
    if intent.get("requires_currency_conversion"):
        tables.append("currency_master")
        
    return list(set(tables))  # Remove duplicates


@tool("Column Pruner")
def prune_columns(tables: List[str]) -> Dict[str, List[str]]:
    """
    Select only necessary columns from each table
    
    Args:
        tables: List of table names
        
    Returns:
        Dict mapping table names to list of columns to keep
    """
    pruned_schema = {}
    
    # Define columns to keep for each table
    column_rules = {
        "a_personnel_details": [
            "employee_id", "department_id", "location_id", 
            "accounting_period", "amount", "currency_id",
            "category", "category_rollup", "closed",
            "plan_version_name", "fiscal_year"
        ],
        "a_personnel_headcount": [
            "employee_id", "department_id", "location_id",
            "accounting_period", "headcount", "movement_type",
            "fiscal_year"
        ],
        "a_personnel_summary": [
            "department_id", "location_id", "accounting_period",
            "total_amount", "currency_id", "category_rollup",
            "plan_version_name", "headcount", "fiscal_year"
        ],
        "m_department": ["department_id", "department_name"],
        "m_location": ["location_id", "location_name", "country"],
        "m_accounting_period": [
            "period_id", "name", "fiscal_year", 
            "fiscal_quarter", "fiscal_month"
        ],
        "master_rollup_mapping_details": [
            "category", "category_rollup", "rollup_level_1",
            "is_compensation", "requires_negation"
        ],
        "currency_master": [
            "currency_id", "conversion_rate_to_usd"
        ]
    }
    
    for table in tables:
        if table in column_rules:
            pruned_schema[table] = column_rules[table]
            
    return pruned_schema


@tool("SQL Generator")
def generate_sql(intent: Dict[str, Any], tables: List[str], 
                pruned_schema: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Generate SQL query based on intent and schema
    
    Args:
        intent: Intent metadata
        tables: Selected tables
        pruned_schema: Pruned column schema
        
    Returns:
        Dict with SQL query and reasoning
    """
    # Check if we have a template
    if intent["metric_type"] in ["fully_loaded_cost", "headcount_movement"]:
        template_key = f"{intent['metric_type']}_per_employee" if intent["aggregation_level"] == "employee_level" else intent["metric_type"]
        
        if template_key in METRIC_TEMPLATES:
            sql_template = METRIC_TEMPLATES[template_key]
            
            # Apply scenario filter
            scenario_filter = DATA_RULES["scenario_filters"].get(
                intent["scenario"], 
                DATA_RULES["scenario_filters"]["historical_actuals_only"]
            )["filter"]
            
            # Extract year from time window
            year = "2025"  # Default
            if intent.get("time_window"):
                year_match = re.search(r'20\d{2}', intent["time_window"])
                if year_match:
                    year = year_match.group()
            
            sql = sql_template.format(
                scenario_filter=scenario_filter,
                year=year
            )
            
            return {
                "sql": sql.strip(),
                "decisions": {
                    "negation": "applied" if intent["metric_type"] == "fully_loaded_cost" else "not_applied",
                    "scenario": intent["scenario"],
                    "currency": "no_conversion",
                    "rollups": ["salary", "benefits", "taxes"] if "fully_loaded" in intent["metric_type"] else []
                },
                "notes": f"Generated from template for {intent['metric_type']}"
            }
    
    # If no template, build basic query
    return build_custom_sql(intent, tables, pruned_schema)


def build_custom_sql(intent: Dict[str, Any], tables: List[str], 
                    pruned_schema: Dict[str, List[str]]) -> Dict[str, Any]:
    """Build custom SQL when no template exists"""
    
    # Start with basic SELECT
    main_table = "a_personnel_details" if "a_personnel_details" in tables else tables[0]
    
    sql_parts = {
        "select": [],
        "from": main_table,
        "joins": [],
        "where": [],
        "group_by": [],
        "order_by": []
    }
    
    # Build SELECT clause based on aggregation
    if intent["aggregation_level"] == "department":
        sql_parts["select"].append("d.department_name")
        sql_parts["group_by"].append("d.department_name")
    elif intent["aggregation_level"] == "location":
        sql_parts["select"].append("l.location_name")
        sql_parts["group_by"].append("l.location_name")
        
    # Add metric calculation
    if intent["metric_type"] == "fully_loaded_cost":
        sql_parts["select"].append(
            "SUM(CASE WHEN mrm.requires_negation = 1 THEN -pd.amount ELSE pd.amount END) as total_cost"
        )
    else:
        sql_parts["select"].append("SUM(pd.amount) as total_amount")
    
    # Build JOINs
    if "m_department" in tables:
        sql_parts["joins"].append(
            f"JOIN m_department d ON {main_table}.department_id = d.department_id"
        )
    if "m_location" in tables:
        sql_parts["joins"].append(
            f"JOIN m_location l ON {main_table}.location_id = l.location_id"
        )
    if "m_accounting_period" in tables:
        sql_parts["joins"].append(
            f"JOIN m_accounting_period ap ON {main_table}.accounting_period = ap.name"
        )
        
    # Build WHERE clause
    scenario_filter = DATA_RULES["scenario_filters"].get(
        intent["scenario"], 
        DATA_RULES["scenario_filters"]["historical_actuals_only"]
    )["filter"]
    sql_parts["where"].append(scenario_filter)
    
    # Construct final SQL
    sql = f"""
SELECT {', '.join(sql_parts['select'])}
FROM {sql_parts['from']} {main_table[0:2]}
{' '.join(sql_parts['joins'])}
WHERE {' AND '.join(sql_parts['where'])}
{f"GROUP BY {', '.join(sql_parts['group_by'])}" if sql_parts['group_by'] else ""}
    """.strip()
    
    return {
        "sql": sql,
        "decisions": {
            "negation": "applied" if intent["metric_type"] == "fully_loaded_cost" else "not_applied",
            "scenario": intent["scenario"],
            "currency": "no_conversion",
            "rollups": []
        },
        "notes": "Custom query built from components"
    }


@tool("SQL Validator")
def validate_sql(sql: str, tables: List[str], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate generated SQL for correctness
    
    Args:
        sql: SQL query to validate
        tables: Expected tables
        schema: Full schema definition
        
    Returns:
        Dict with validation status and issues
    """
    issues = []
    sql_lower = sql.lower()
    
    # Check 1: All expected tables are referenced
    for table in tables:
        if table.lower() not in sql_lower:
            issues.append(f"Expected table '{table}' not found in query")
            
    # Check 2: Join conditions exist
    if "join" in sql_lower:
        # Check for proper join conditions
        if ".department_id = " not in sql_lower and "m_department" in tables:
            issues.append("Missing proper join condition for department")
        if ".location_id = " not in sql_lower and "m_location" in tables:
            issues.append("Missing proper join condition for location")
            
    # Check 3: Period mapping
    if "m_accounting_period" in tables:
        if ".accounting_period = " not in sql_lower or ".name" not in sql_lower:
            issues.append("Incorrect period mapping - should join on accounting_period = name")
            
    # Check 4: Scenario filter
    if "where" not in sql_lower:
        issues.append("Missing WHERE clause for scenario filter")
        
    # Check 5: Negation logic
    if "fully_loaded_cost" in str(tables) and "case when" not in sql_lower:
        issues.append("Missing negation logic for fully loaded cost calculation")
        
    # Check 6: No varchar to integer casts
    if "cast(" in sql_lower and "as integer" in sql_lower:
        issues.append("Avoid casting varchar to integer on name fields")
        
    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "recommendations": [
            "Add missing join conditions" if "join" in i for i in issues
        ]
    }
