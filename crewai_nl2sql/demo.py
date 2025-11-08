"""
Demo script for NL2SQL CrewAI Pipeline
"""
from main import NL2SQLApp
from colorama import init, Fore, Style
import os

# Initialize colorama
init(autoreset=True)

def run_quick_demo():
    """Run a quick demo with predefined queries"""
    
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}🚀 NL2SQL CrewAI Pipeline - Quick Demo")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    # Create app instance
    app = NL2SQLApp()
    
    # Demo queries with expected outcomes
    demo_scenarios = [
        {
            "query": "What is the fully loaded cost per employee by department for Q1 2025?",
            "description": "Tests cost aggregation with negation logic and department grouping",
            "expected": "Should calculate total compensation costs (salary + benefits + taxes) per employee by department"
        },
        {
            "query": "Show me the total salary costs for Engineering department in 2025",
            "description": "Tests simple filtering and aggregation",
            "expected": "Should sum salary amounts for Engineering department only"
        },
        {
            "query": "Calculate the average cost per employee by location for current year actuals",
            "description": "Tests location-based grouping and average calculations", 
            "expected": "Should group by location and calculate average costs"
        }
    ]
    
    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"\n{Fore.YELLOW}{'*'*80}")
        print(f"{Fore.YELLOW}DEMO SCENARIO {i}")
        print(f"{Fore.YELLOW}{'*'*80}\n")
        
        print(f"{Fore.GREEN}Query: {scenario['query']}")
        print(f"{Fore.BLUE}Purpose: {scenario['description']}")
        print(f"{Fore.MAGENTA}Expected: {scenario['expected']}\n")
        
        try:
            # Process the query
            results = app.process_query(scenario['query'])
            
            # Show success status
            if results['status'] == 'success':
                print(f"\n{Fore.GREEN}✅ Query processed successfully!")
            else:
                print(f"\n{Fore.RED}❌ Query processing failed")
                
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error: {str(e)}")
            
        # Pause between scenarios
        if i < len(demo_scenarios):
            input(f"\n{Fore.CYAN}Press Enter to continue to next scenario...")
            
    print(f"\n{Fore.GREEN}{'='*80}")
    print(f"{Fore.GREEN}Demo completed! 🎉")
    print(f"{Fore.GREEN}{'='*80}\n")
    

def show_pipeline_architecture():
    """Display the pipeline architecture"""
    
    architecture = """
    🏗️  NL2SQL PIPELINE ARCHITECTURE
    ================================
    
    User Query
        ↓
    📋 Intent Agent
        - Classifies metric type
        - Identifies scenario & time window
        - Detects aggregation level
        ↓
    🗂️  Table Agent  
        - Selects relevant tables
        - Adds necessary joins
        ↓
    ✂️  Schema Agent
        - Prunes unnecessary columns
        - Reduces token usage
        ↓
    💻 SQL Agent
        - Generates SQL query
        - Applies business logic
        - Documents decisions
        ↓
    ✅ Validation Agent
        - Checks query correctness
        - Validates joins & filters
        ↓
    📊 Query Execution
        - Runs on sample database
        - Returns formatted results
    """
    
    print(f"{Fore.CYAN}{architecture}")
    

if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print(f"{Fore.RED}⚠️  Warning: OPENAI_API_KEY not found!")
        print(f"{Fore.YELLOW}Please set your OpenAI API key to run this demo:")
        print(f"{Fore.YELLOW}export OPENAI_API_KEY='your-api-key-here'")
        print(f"{Fore.YELLOW}Or create a .env file with: OPENAI_API_KEY=your-api-key-here\n")
        
        # For demo purposes, show the architecture anyway
        show_pipeline_architecture()
        exit(1)
    
    # Show architecture
    show_pipeline_architecture()
    
    # Ask user what to do
    print(f"\n{Fore.GREEN}What would you like to do?")
    print(f"{Fore.CYAN}1. Run quick demo (3 predefined queries)")
    print(f"{Fore.CYAN}2. Enter interactive mode")
    print(f"{Fore.CYAN}3. Exit\n")
    
    choice = input(f"{Fore.GREEN}Enter your choice (1-3): {Fore.WHITE}")
    
    if choice == '1':
        run_quick_demo()
    elif choice == '2':
        app = NL2SQLApp()
        app.interactive_mode()
    else:
        print(f"{Fore.YELLOW}Goodbye!")
