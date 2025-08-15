#!/usr/bin/env python3
"""
Main entry point for ReAct AI Search Agent
"""

import json
import logging
from datetime import datetime
from react_agent import ReActAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def print_separator():
    """Print a separator line"""
    print("=" * 80)

def print_agent_result(result: dict):
    """Pretty print agent result"""
    print_separator()
    print("REACT AI SEARCH AGENT RESULT")
    print_separator()
    
    if result["success"]:
        print(f"Status: {result['status'].upper()}")
        print(f"Execution Time: {result['execution_time']:.2f}s")
        print(f"Total Iterations: {result['total_iterations']}")
        print()
        
        print("USER INPUT:")
        print(f"   {result['user_input']}")
        print()
        
        print("FINAL ANSWER:")
        print(f"   {result['final_answer']}")
        print()
        
        if result.get('history'):
            print("REASONING PROCESS:")
            for i, step in enumerate(result['history'][-6:], 1):  # Show last 6 steps
                step_type = step['type'].upper()
                content = step['content'][:150] + "..." if len(step['content']) > 150 else step['content']
                print(f"   {i}. [{step_type}] {content}")
            print()
        
        if result.get('intermediate_results'):
            print("TOOLS USED:")
            for key, value in result['intermediate_results'].items():
                if isinstance(value, dict) and 'success' in value:
                    status = "✅" if value['success'] else "❌"
                    print(f"   {status} {key}")
            print()
            
    else:
        print(f"Status: ERROR")
        print(f"Error: {result['error']}")
        print(f"Execution Time: {result['execution_time']:.2f}s")
        print()

def interactive_mode():
    """Run agent in interactive mode"""
    print_separator()
    print("REACT AI SEARCH AGENT - INTERACTIVE MODE")
    print_separator()
    print("Enter your questions (type 'quit' to exit, 'help' for commands)")
    print()
    
    agent = ReActAgent()
    
    while True:
        try:
            user_input = input("Your question: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
                
            if user_input.lower() == 'help':
                print("\nAvailable commands:")
                print("  - Type any question to search and get answers")
                print("  - 'quit' or 'exit' to leave")
                print("  - 'help' to show this message")
                print("\nExample questions:")
                print("  - Thời tiết Hà Nội hôm nay như thế nào?")
                print("  - Tìm kiếm thông tin về trí tuệ nhân tạo")
                print("  - Bitcoin giá bao nhiều?")
                print()
                continue
            
            print(f"\nProcessing: {user_input}")
            print("Please wait...")
            
            # Run the agent
            start_time = datetime.now()
            result = agent.react_agent(user_input)
            end_time = datetime.now()
            
            # Print results
            print_agent_result(result)
            
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            print("Goodbye!")
            break
            
        except Exception as e:
            logger.error(f"Interactive mode error: {e}")
            print(f"\nError: {e}")
            print("Please try again with a different question.\n")

def single_query_mode(query: str):
    """Run agent for a single query"""
    print_separator()
    print("REACT AI SEARCH AGENT - SINGLE QUERY MODE")
    print_separator()
    
    agent = ReActAgent()

    print(f"Processing query: {query}")
    print("Please wait...")
    
    try:
        result = agent.react_agent(query)
        print_agent_result(result)
        
        # Save detailed results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"agent_result_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"Detailed results saved to: {filename}")
        
    except Exception as e:
        logger.error(f"Single query error: {e}")
        print(f"Error: {e}")

def test_mode():
    """Run agent in test mode with predefined queries"""
    print_separator()
    print("REACT AI SEARCH AGENT - TEST MODE")
    print_separator()
    
    test_queries = [
        "Thời tiết Hà Nội hôm nay như thế nào?",
        "Giá Bitcoin hiện tại là bao nhiều?",
        "Tìm kiếm thông tin về ChatGPT mới nhất",
        "Tóm tắt tin tức công nghệ hôm nay"
    ]
    
    agent = ReActAgent()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}/{len(test_queries)}: {query}")
        print("Processing...")
        
        try:
            result = agent.react_agent(query)
            
            # Print summary
            status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
            print(f"   Result: {status}")
            print(f"   Time: {result['execution_time']:.2f}s")
            print(f"   Iterations: {result['total_iterations']}")
            
            if result["success"]:
                answer = result['final_answer'][:100] + "..." if len(result['final_answer']) > 100 else result['final_answer']
                print(f"   Answer: {answer}")
            else:
                print(f"   Error: {result['error']}")
                
        except Exception as e:
            print(f"   Exception: {e}")
        
        print("-" * 50)

    print("\nTest mode completed!")

def main():
    """Main function"""
    import sys
    
    print("ReAct AI Search Agent")
    print("Powered by Gemini 2.0 + SerpAPI + Open Source Models")
    
    try:
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == "interactive" or command == "i":
                interactive_mode()
            elif command == "test" or command == "t":
                test_mode()
            elif command == "query" or command == "q":
                if len(sys.argv) > 2:
                    query = " ".join(sys.argv[2:])
                    single_query_mode(query)
                else:
                    print("Please provide a query after 'query' command")
                    print("Example: python main.py query 'What is the weather in Hanoi?'")
            else:
                print(f"Unknown command: {command}")
                print("Available commands:")
                print("  interactive (i) - Interactive question-answer mode")
                print("  test (t)        - Run predefined test queries")
                print("  query (q) <text> - Single query mode")
        else:
            # Default to interactive mode
            interactive_mode()
            
    except Exception as e:
        logger.error(f"Main error: {e}")
        print(f"Application error: {e}")

if __name__ == "__main__":
    main()