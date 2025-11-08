"""
CrewAI Crew and Tasks for NL2SQL Pipeline
"""
from crewai import Crew, Task
from agents import NL2SQLAgents
import json


class NL2SQLCrew:
    """Orchestrates the NL2SQL pipeline using CrewAI"""
    
    def __init__(self):
        # Initialize all agents
        self.agents = NL2SQLAgents()
        self.intent_agent = self.agents.intent_agent()
        self.table_agent = self.agents.table_agent()
        self.schema_agent = self.agents.schema_agent()
        self.sql_agent = self.agents.sql_agent()
        self.validation_agent = self.agents.validation_agent()
        
    def create_tasks(self, user_query: str):
        """Create tasks for the NL2SQL pipeline"""
        
        # Task 1: Intent Classification
        intent_task = Task(
            description=f"""
            Analyze this user query and classify the intent:
            '{user_query}'
            
            Extract:
            - Metric type (fully_loaded_cost, benefits_ratio, headcount_movement, etc.)
            - Scenario (historical_actuals_only, current_year_totals, budget_vs_actual)
            - Aggregation level (employee_level, department, location, company)
            - Time window (specific quarters, years, or date ranges)
            - Currency requirements if mentioned
            
            Return a structured JSON with these fields.
            """,
            agent=self.intent_agent,
            expected_output="JSON object with intent classification"
        )
        
        # Task 2: Table Selection
        table_task = Task(
            description="""
            Based on the classified intent from the previous task, select the appropriate database tables.
            
            Consider:
            - Core fact tables for the metric type
            - Required dimension tables for joins
            - Special tables for currency conversion or category rollups
            - Whether GL reconciliation tables are needed
            
            Return a list of table names.
            """,
            agent=self.table_agent,
            expected_output="List of required table names",
            context=[intent_task]
        )
        
        # Task 3: Schema Pruning
        schema_task = Task(
            description="""
            Given the selected tables, identify which columns are necessary for the query.
            
            Keep:
            - All join keys (IDs)
            - Measure columns (amount, headcount)
            - Business attributes (category, currency_id, plan_version_name)
            - Time-related columns
            
            Remove:
            - Denormalized text fields
            - Audit columns
            - Unused attributes
            
            Return a mapping of table names to required columns.
            """,
            agent=self.schema_agent,
            expected_output="Dictionary mapping tables to column lists",
            context=[table_task]
        )
        
        # Task 4: SQL Generation
        sql_task = Task(
            description="""
            Generate the SQL query using:
            - The classified intent
            - Selected tables
            - Pruned schema
            
            Ensure:
            - Proper joins between all tables
            - Correct scenario filters applied
            - Appropriate aggregations and groupings
            - Negation logic for cost calculations if needed
            - Currency conversion if required
            
            Document your decisions about negation, scenario, currency, and rollups.
            """,
            agent=self.sql_agent,
            expected_output="JSON with SQL query and reasoning",
            context=[intent_task, table_task, schema_task]
        )
        
        # Task 5: SQL Validation
        validation_task = Task(
            description="""
            Validate the generated SQL query for:
            - All required tables are properly joined
            - Join conditions are correct (especially period mapping)
            - Scenario filters are applied
            - Negation logic is correct for the metric type
            - No invalid casts or operations
            - Query will execute without errors
            
            If issues are found, provide specific feedback for correction.
            """,
            agent=self.validation_agent,
            expected_output="Validation report with any issues and recommendations",
            context=[sql_task, table_task]
        )
        
        return [intent_task, table_task, schema_task, sql_task, validation_task]
    
    def run(self, user_query: str):
        """Execute the NL2SQL pipeline"""
        print(f"\n🚀 Processing query: '{user_query}'\n")
        
        # Create tasks
        tasks = self.create_tasks(user_query)
        
        # Create and run crew
        crew = Crew(
            agents=[
                self.intent_agent,
                self.table_agent,
                self.schema_agent,
                self.sql_agent,
                self.validation_agent
            ],
            tasks=tasks,
            verbose=True
        )
        
        # Execute the crew
        result = crew.kickoff()
        
        return self._format_results(result, tasks)
    
    def _format_results(self, crew_output, tasks):
        """Format the pipeline results"""
        results = {
            "status": "success",
            "pipeline_output": {},
            "final_sql": None,
            "validation": None
        }
        
        try:
            # Extract outputs from each task
            for i, task in enumerate(tasks):
                task_name = ["intent", "tables", "schema", "sql_generation", "validation"][i]
                if hasattr(task, 'output') and task.output:
                    results["pipeline_output"][task_name] = task.output.raw_output
                    
                    # Extract final SQL if available
                    if task_name == "sql_generation":
                        try:
                            sql_output = json.loads(task.output.raw_output)
                            results["final_sql"] = sql_output.get("sql")
                        except:
                            # If not JSON, try to extract SQL from text
                            if "SELECT" in task.output.raw_output:
                                results["final_sql"] = task.output.raw_output
                                
                    elif task_name == "validation":
                        results["validation"] = task.output.raw_output
                        
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            
        return results
