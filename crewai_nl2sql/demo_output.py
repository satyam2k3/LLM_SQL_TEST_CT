"""
Script to automatically demonstrate the pipeline output
"""
from test_pipeline import demonstrate_pipeline, show_schema_overview, show_business_rules
from colorama import init, Fore

# Initialize colorama
init(autoreset=True)

if __name__ == "__main__":
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}🚀 NL2SQL CrewAI Pipeline - Automated Demo")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    # Run the full pipeline demonstration
    demonstrate_pipeline()
    
    print(f"\n{Fore.YELLOW}Press Enter to see the database schema...")
    input()
    
    # Show schema
    show_schema_overview()
    
    print(f"\n{Fore.YELLOW}Press Enter to see the business rules...")
    input()
    
    # Show business rules
    show_business_rules()
    
    print(f"\n{Fore.GREEN}Demo complete! 🎉")
    print(f"{Fore.GREEN}This demonstrates how the NL2SQL pipeline works without requiring any API keys.")
    print(f"\n{Fore.CYAN}To run with real LLMs:")
    print(f"{Fore.WHITE}1. Set OPENAI_API_KEY in a .env file")
    print(f"{Fore.WHITE}2. Run: python main.py")
