#!/usr/bin/env python3
"""
Quick runner script for testing the ReAct Agent
"""

import sys
import json
from datetime import datetime
from react_agent import ReActAgent

def quick_test():
    """Quick test with sample queries"""
    print("Quick Test - ReAct AI Search Agent")
    print("=" * 50)
    
    # Sample test queries
    test_queries = [
        "Thời tiết Hà Nội hôm nay?",
        "Giá Bitcoin hiện tại?",
        "Tin tức AI mới nhất?"
    ]
    
    agent = ReActAgent()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: {query}")
        print("-" * 30)
        
        try:
            result = agent.react_agent(query)
            
            if result["success"]:
                print(f"SUCCESS ({result['execution_time']:.1f}s)")
                print(f"Answer: {result['final_answer'][:150]}...")
                print(f"Iterations: {result['total_iterations']}")
            else:
                print(f"FAILED: {result['error']}")
                
        except Exception as e:
            print(f"ERROR: {e}")

def single_test(query: str):
    """Test with a single query"""
    print(f"Testing: {query}")
    print("=" * 50)
    
    agent = ReActAgent()
    
    try:
        start_time = datetime.now()
        result = agent.react_agent(query)
        end_time = datetime.now()

        print(f"Total time: {(end_time - start_time).total_seconds():.2f}s")
        print(f"Iterations: {result['total_iterations']}")
        print(f"Status: {result['status']}")

        if result["success"]:
            print(f"\nFINAL ANSWER:")
            print(f"{result['final_answer']}")

            print(f"\nREASONING STEPS:")
            for i, step in enumerate(result['history'], 1):
                step_type = step['type'].upper()
                content = step['content'][:100] + "..." if len(step['content']) > 100 else step['content']
                print(f"  {i}. [{step_type}] {content}")
            
            # Save detailed results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_result_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
            print(f"\nDetailed results saved to: {filename}")

        else:
            print(f"\nERROR: {result['error']}")

    except Exception as e:
        print(f"EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

def interactive_simple():
    """Simple interactive mode"""
    print("ReAct Agent - Simple Interactive Mode")
    print("Type 'quit' to exit")
    print("=" * 50)
    
    agent = ReActAgent()
    
    while True:
        try:
            query = input("\nYour question: ").strip()
            
            if not query:
                continue
                
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            print("Processing...")
            result = agent.react_agent(query)
            
            if result["success"]:
                print(f"\nAnswer: {result['final_answer']}")
                print(f"Time: {result['execution_time']:.1f}s | Iterations: {result['total_iterations']}")
            else:
                print(f"\nError: {result['error']}")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")

def debug_mode():
    """Debug mode with verbose logging"""
    import logging
    
    # Set debug logging
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
    
    print("🐛 DEBUG MODE - Verbose logging enabled")
    print("=" * 50)
    
    query = input("Enter your test query: ").strip()
    if not query:
        query = "Thời tiết Hà Nội hôm nay?"
        print(f"Using default query: {query}")
    
    agent = ReActAgent()
    
    try:
        result = agent.react_agent(query)
        
        print("\n" + "="*50)
        print("DEBUG SUMMARY")
        print("="*50)
        
        print(f"Success: {result['success']}")
        print(f"Status: {result['status']}")
        print(f"Iterations: {result['total_iterations']}")
        print(f"Execution Time: {result['execution_time']:.2f}s")
        
        if result.get('error'):
            print(f"Error: {result['error']}")
        
        print(f"\nFinal Answer: {result.get('final_answer', 'No answer')}")
        
        # Show intermediate results
        if result.get('intermediate_results'):
            print(f"\nIntermediate Results:")
            for key, value in result['intermediate_results'].items():
                print(f"  - {key}: {type(value).__name__}")
                if isinstance(value, dict) and 'success' in value:
                    print(f"    Success: {value['success']}")
                    if not value['success'] and 'error' in value:
                        print(f"    Error: {value['error']}")
                        
    except Exception as e:
        print(f"\nEXCEPTION in debug mode: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main runner function"""
    if len(sys.argv) < 2:
        print("ReAct Agent Runner")
        print("\nUsage:")
        print("  python run_agent.py quick          # Quick test with sample queries")
        print("  python run_agent.py test 'query'   # Test single query")
        print("  python run_agent.py interactive    # Simple interactive mode")  
        print("  python run_agent.py debug          # Debug mode")
        print("\nExamples:")
        print("  python run_agent.py test 'Thời tiết Hà Nội?'")
        print("  python run_agent.py interactive")
        return
    
    command = sys.argv[1].lower()
    
    try:
        if command == "quick":
            quick_test()
        elif command == "test":
            if len(sys.argv) > 2:
                query = " ".join(sys.argv[2:])
                single_test(query)
            else:
                print("Please provide a query for testing")
                print("Example: python run_agent.py test 'Your question here'")
        elif command == "interactive" or command == "i":
            interactive_simple()
        elif command == "debug" or command == "d":
            debug_mode()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: quick, test, interactive, debug")
            
    except KeyboardInterrupt:
        print("\n Interrupted by user")
    except Exception as e:
        print(f"Runner error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()