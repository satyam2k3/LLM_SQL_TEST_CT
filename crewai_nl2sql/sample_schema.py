"""
Sample HR/Financial Database Schema for NL2SQL Demo
"""

SAMPLE_SCHEMA = {
    "a_personnel_details": {
        "columns": {
            "employee_id": "INTEGER PRIMARY KEY",
            "department_id": "INTEGER",
            "location_id": "INTEGER", 
            "accounting_period": "VARCHAR(7)",  # YYYY-MM format
            "amount": "DECIMAL(15,2)",
            "currency_id": "VARCHAR(3)",
            "category": "VARCHAR(50)",  # salary, benefits, taxes, etc.
            "category_rollup": "VARCHAR(50)",
            "closed": "BOOLEAN",
            "plan_version_name": "VARCHAR(50)",  # actual, forecast, budget
            "aggregation_type": "VARCHAR(20)",
            "created_date": "DATE",
            "fiscal_year": "INTEGER"
        },
        "description": "Detailed personnel financial transactions"
    },
    
    "a_personnel_headcount": {
        "columns": {
            "employee_id": "INTEGER PRIMARY KEY",
            "department_id": "INTEGER",
            "location_id": "INTEGER",
            "accounting_period": "VARCHAR(7)",
            "headcount": "INTEGER",
            "movement_type": "VARCHAR(20)",  # hire, termination, transfer
            "effective_date": "DATE",
            "fiscal_year": "INTEGER"
        },
        "description": "Personnel headcount movements and snapshots"
    },
    
    "a_personnel_summary": {
        "columns": {
            "department_id": "INTEGER",
            "location_id": "INTEGER",
            "accounting_period": "VARCHAR(7)",
            "total_amount": "DECIMAL(15,2)",
            "currency_id": "VARCHAR(3)",
            "category_rollup": "VARCHAR(50)",
            "plan_version_name": "VARCHAR(50)",
            "headcount": "INTEGER",
            "fiscal_year": "INTEGER"
        },
        "description": "Aggregated personnel data for GL reconciliation"
    },
    
    "m_department": {
        "columns": {
            "department_id": "INTEGER PRIMARY KEY",
            "department_name": "VARCHAR(100)",
            "department_code": "VARCHAR(20)",
            "parent_department_id": "INTEGER",
            "is_active": "BOOLEAN"
        },
        "description": "Department master data"
    },
    
    "m_location": {
        "columns": {
            "location_id": "INTEGER PRIMARY KEY",
            "location_name": "VARCHAR(100)",
            "location_code": "VARCHAR(20)",
            "country": "VARCHAR(50)",
            "region": "VARCHAR(50)",
            "is_active": "BOOLEAN"
        },
        "description": "Location master data"
    },
    
    "m_accounting_period": {
        "columns": {
            "period_id": "INTEGER PRIMARY KEY",
            "name": "VARCHAR(7)",  # YYYY-MM format
            "fiscal_year": "INTEGER",
            "fiscal_quarter": "INTEGER",
            "fiscal_month": "INTEGER",
            "start_date": "DATE",
            "end_date": "DATE",
            "is_closed": "BOOLEAN"
        },
        "description": "Accounting period master"
    },
    
    "master_rollup_mapping_details": {
        "columns": {
            "category": "VARCHAR(50)",
            "category_rollup": "VARCHAR(50)",
            "rollup_level_1": "VARCHAR(50)",
            "rollup_level_2": "VARCHAR(50)",
            "is_compensation": "BOOLEAN",
            "requires_negation": "BOOLEAN"
        },
        "description": "Category rollup hierarchy and rules"
    },
    
    "currency_master": {
        "columns": {
            "currency_id": "VARCHAR(3) PRIMARY KEY",
            "currency_name": "VARCHAR(50)",
            "conversion_rate_to_usd": "DECIMAL(10,6)",
            "effective_date": "DATE"
        },
        "description": "Currency conversion rates"
    }
}

# Sample data dictionary rules
DATA_RULES = {
    "negation_rules": {
        "fully_loaded_cost": {
            "apply_negation": True,
            "categories": ["salary", "benefits", "taxes", "other_compensation"],
            "description": "Sum of all compensation categories with negation applied"
        },
        "benefits_ratio": {
            "apply_negation": False,
            "calculation": "benefits / salary",
            "description": "Ratio calculations don't apply negation"
        }
    },
    
    "scenario_filters": {
        "historical_actuals_only": {
            "filter": "plan_version_name = 'actual' AND closed = 1",
            "description": "Only closed actual periods"
        },
        "current_year_totals": {
            "filter": "fiscal_year = YEAR(CURRENT_DATE) AND plan_version_name IN ('actual', 'forecast')",
            "description": "Current fiscal year actuals and forecast"
        },
        "budget_vs_actual": {
            "filter": "plan_version_name IN ('actual', 'budget')",
            "description": "Compare budget to actuals"
        }
    },
    
    "currency_rules": {
        "multi_currency": "Always join currency_master when multiple currencies exist",
        "conversion": "amount * conversion_rate_to_usd for USD reporting"
    },
    
    "join_rules": [
        "Always join masters by ID fields only",
        "Map periods via a_personnel_details.accounting_period = m_accounting_period.name",
        "Include partition filters for large tables"
    ]
}

# Sample metric templates
METRIC_TEMPLATES = {
    "fully_loaded_cost_per_employee": """
        SELECT 
            d.department_name,
            l.location_name,
            SUM(CASE WHEN mrm.requires_negation = 1 THEN -pd.amount ELSE pd.amount END) / COUNT(DISTINCT pd.employee_id) as cost_per_employee
        FROM a_personnel_details pd
        JOIN m_department d ON pd.department_id = d.department_id
        JOIN m_location l ON pd.location_id = l.location_id
        JOIN m_accounting_period ap ON pd.accounting_period = ap.name
        JOIN master_rollup_mapping_details mrm ON pd.category = mrm.category
        WHERE {scenario_filter}
            AND mrm.is_compensation = 1
            AND pd.fiscal_year = {year}
        GROUP BY d.department_name, l.location_name
    """,
    
    "headcount_movement": """
        SELECT 
            ap.fiscal_quarter,
            ph.movement_type,
            COUNT(DISTINCT ph.employee_id) as employee_count
        FROM a_personnel_headcount ph
        JOIN m_accounting_period ap ON ph.accounting_period = ap.name
        WHERE ph.fiscal_year = {year}
            AND ph.movement_type IN ('hire', 'termination')
        GROUP BY ap.fiscal_quarter, ph.movement_type
        ORDER BY ap.fiscal_quarter
    """
}
