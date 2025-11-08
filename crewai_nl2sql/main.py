"""
Main NL2SQL Application
"""
import os
from dotenv import load_dotenv
from crew import NL2SQLCrew
import json
from datetime import datetime
import sqlite3
from tabulate import tabulate
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

# Load environment variables
load_dotenv()

class NL2SQLApp:
    """Main application for NL2SQL conversion"""
    
    def __init__(self):
        self.crew = NL2SQLCrew()
        self.setup_sample_database()
        
    def setup_sample_database(self):
        """Create sample database with test data"""
        self.conn = sqlite3.connect(':memory:')
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE m_department (
                department_id INTEGER PRIMARY KEY,
                department_name VARCHAR(100)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE m_location (
                location_id INTEGER PRIMARY KEY,
                location_name VARCHAR(100),
                country VARCHAR(50)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE m_accounting_period (
                period_id INTEGER PRIMARY KEY,
                name VARCHAR(7),
                fiscal_year INTEGER,
                fiscal_quarter INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE a_personnel_details (
                employee_id INTEGER,
                department_id INTEGER,
                location_id INTEGER,
                accounting_period VARCHAR(7),
                amount DECIMAL(15,2),
                currency_id VARCHAR(3),
                category VARCHAR(50),
                closed BOOLEAN,
                plan_version_name VARCHAR(50),
                fiscal_year INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE master_rollup_mapping_details (
                category VARCHAR(50),
                category_rollup VARCHAR(50),
                is_compensation BOOLEAN,
                requires_negation BOOLEAN
            )
        """)
        
        # Insert sample data
        departments = [(1, 'Engineering'), (2, 'Sales'), (3, 'HR')]
        locations = [(1, 'New York', 'USA'), (2, 'Mumbai', 'India'), (3, 'London', 'UK')]
        periods = [(1, '2025-01', 2025, 1), (2, '2025-02', 2025, 1), (3, '2025-03', 2025, 1)]
        
        cursor.executemany("INSERT INTO m_department VALUES (?, ?)", departments)
        cursor.executemany("INSERT INTO m_location VALUES (?, ?, ?)", locations)
        cursor.executemany("INSERT INTO m_accounting_period VALUES (?, ?, ?, ?)", periods)
        
        # Insert personnel details
        personnel_data = [
            (101, 1, 1, '2025-01', 10000, 'USD', 'salary', 1, 'actual', 2025),
            (101, 1, 1, '2025-01', 2000, 'USD', 'benefits', 1, 'actual', 2025),
            (101, 1, 1, '2025-01', 1500, 'USD', 'taxes', 1, 'actual', 2025),
            (102, 1, 2, '2025-01', 8000, 'INR', 'salary', 1, 'actual', 2025),
            (102, 1, 2, '2025-01', 1500, 'INR', 'benefits', 1, 'actual', 2025),
            (103, 2, 1, '2025-01', 12000, 'USD', 'salary', 1, 'actual', 2025),
            (103, 2, 1, '2025-01', 2500, 'USD', 'benefits', 1, 'actual', 2025),
        ]
        
        cursor.executemany("""
            INSERT INTO a_personnel_details VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, personnel_data)
        
        # Insert rollup mappings
        rollup_data = [
            ('salary', 'compensation', 1, 1),
            ('benefits', 'compensation', 1, 1),
            ('taxes', 'compensation', 1, 1),
        ]
        
        cursor.executemany("""
            INSERT INTO master_rollup_mapping_details VALUES (?, ?, ?, ?)
        """, rollup_data)
        
        self.conn.commit()
        
    def process_query(self, user_query: str):
        """Process a natural language query through the pipeline"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}Processing Natural Language Query")
        print(f"{Fore.CYAN}{'='*80}\n")
        
        # Run the crew
        results = self.crew.run(user_query)
        
        # Display results
        self._display_results(results)
        
        # Execute SQL if validation passed
        if results.get("final_sql") and "is_valid': true" in str(results.get("validation", "")):
            self._execute_sql(results["final_sql"])
            
        return results
        
    def _display_results(self, results):
        """Display pipeline results in a formatted way"""
        print(f"\n{Fore.GREEN}Pipeline Results:")
        print(f"{Fore.GREEN}{'-'*80}\n")
        
        # Display each stage output
        for stage, output in results.get("pipeline_output", {}).items():
            print(f"{Fore.YELLOW}📌 {stage.upper()}:")
            print(f"{Style.DIM}{output[:500]}...")  # Truncate long outputs
            print()
            
        # Display final SQL
        if results.get("final_sql"):
            print(f"\n{Fore.MAGENTA}🔍 GENERATED SQL:")
            print(f"{Fore.MAGENTA}{'-'*80}")
            print(f"{Fore.WHITE}{results['final_sql']}")
            print()
            
        # Display validation results
        if results.get("validation"):
            print(f"\n{Fore.CYAN}✅ VALIDATION:")
            print(f"{Fore.CYAN}{'-'*80}")
            print(results["validation"])
            
    def _execute_sql(self, sql):
        """Execute the generated SQL and display results"""
        try:
            print(f"\n{Fore.GREEN}📊 QUERY EXECUTION RESULTS:")
            print(f"{Fore.GREEN}{'-'*80}\n")
            
            cursor = self.conn.cursor()
            cursor.execute(sql)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch results
            rows = cursor.fetchall()
            
            if rows:
                # Display as table
                print(tabulate(rows, headers=columns, tablefmt="grid"))
                print(f"\n{Fore.GREEN}✓ Query returned {len(rows)} rows")
            else:
                print(f"{Fore.YELLOW}⚠ Query returned no results")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Query execution failed: {str(e)}")
            
    def run_demo(self):
        """Run demo with sample queries"""
        demo_queries = [
            "What is the fully loaded cost per employee by department for Q1 2025?",
            "Show me headcount movements by quarter for 2025",
            "Calculate the benefits ratio by location for current year",
            "What are the total salary costs by department in USD?",
            "Show me the average cost per employee in Engineering department"
        ]
        
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}NL2SQL Demo - Sample Queries")
        print(f"{Fore.CYAN}{'='*80}\n")
        
        for i, query in enumerate(demo_queries, 1):
            print(f"\n{Fore.YELLOW}Demo Query {i}: {query}")
            try:
                self.process_query(query)
            except Exception as e:
                print(f"{Fore.RED}Error processing query: {str(e)}")
            
            print(f"\n{Fore.CYAN}{'='*80}\n")
            
            # Pause between queries
            if i < len(demo_queries):
                input(f"{Fore.GREEN}Press Enter to continue to next query...")
                
    def interactive_mode(self):
        """Run in interactive mode"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}NL2SQL Interactive Mode")
        print(f"{Fore.CYAN}Type 'exit' to quit, 'demo' to run demo queries")
        print(f"{Fore.CYAN}{'='*80}\n")
        
        while True:
            query = input(f"\n{Fore.GREEN}Enter your query: {Fore.WHITE}")
            
            if query.lower() == 'exit':
                print(f"{Fore.YELLOW}Goodbye!")
                break
            elif query.lower() == 'demo':
                self.run_demo()
            elif query.strip():
                try:
                    self.process_query(query)
                except Exception as e:
                    print(f"{Fore.RED}Error: {str(e)}")
                    

if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print(f"{Fore.RED}Error: OPENAI_API_KEY not found in environment variables")
        print(f"{Fore.YELLOW}Please set your OpenAI API key in a .env file or environment variable")
        exit(1)
        
    app = NL2SQLApp()
    
    # Run in interactive mode
    app.interactive_mode()
