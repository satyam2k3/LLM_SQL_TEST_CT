#!/usr/bin/env python
"""
Simple script to run the NL2SQL system
"""
import os
import sys
from colorama import init, Fore

# Initialize colorama
init(autoreset=True)

def main():
    """Main entry point"""
    
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}🚀 NL2SQL CrewAI Pipeline Runner")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print(f"{Fore.YELLOW}⚠️  No OpenAI API key found!\n")
        print(f"{Fore.GREEN}You have two options:\n")
        print(f"{Fore.CYAN}1. Run the demo without API key (shows pipeline architecture)")
        print(f"{Fore.CYAN}2. Set your OpenAI API key and run the full system\n")
        
        choice = input(f"{Fore.GREEN}Enter your choice (1 or 2): {Fore.WHITE}")
        
        if choice == '1':
            # Run test pipeline
            os.system(f"{sys.executable} test_pipeline.py")
        else:
            print(f"\n{Fore.YELLOW}To set your API key:")
            print(f"{Fore.WHITE}1. Create a .env file in this directory")
            print(f"{Fore.WHITE}2. Add: OPENAI_API_KEY=your-key-here")
            print(f"{Fore.WHITE}3. Run this script again\n")
    else:
        # API key found, run full system
        print(f"{Fore.GREEN}✓ OpenAI API key found!\n")
        print(f"{Fore.CYAN}What would you like to do?")
        print(f"{Fore.CYAN}1. Run demo with sample queries")
        print(f"{Fore.CYAN}2. Interactive mode (enter your own queries)")
        print(f"{Fore.CYAN}3. Test pipeline (no API calls)\n")
        
        choice = input(f"{Fore.GREEN}Enter your choice (1-3): {Fore.WHITE}")
        
        if choice == '1':
            os.system(f"{sys.executable} demo.py")
        elif choice == '2':
            os.system(f"{sys.executable} main.py")
        else:
            os.system(f"{sys.executable} test_pipeline.py")


if __name__ == "__main__":
    main()
