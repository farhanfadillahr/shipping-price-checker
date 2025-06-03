#!/usr/bin/env python3
"""
Command-line interface for the Indonesian Shipping Price Checker
Run this for a simple terminal-based chat interface
"""

import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shipping_assistant import create_shipping_assistant

def main():
    """Main CLI interface"""
    print("🚚 Indonesian Shipping Price Checker - CLI Version")
    print("=" * 60)
    print("Welcome! I can help you check shipping costs across Indonesia.")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.\n")
    
    # Initialize assistant
    print("Initializing AI assistant...")
    try:
        assistant = create_shipping_assistant()
        print("✅ Assistant ready!\n")
    except Exception as e:
        print(f"❌ Error initializing assistant: {e}")
        sys.exit(1)
    
    # Chat loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                print("\n👋 Thank you for using the shipping price checker!")
                break
            
            if not user_input:
                continue
            
            # Get assistant response
            print("\n🤖 Assistant is thinking...")
            response = assistant.chat(user_input)
            print(f"\n🤖 Assistant: {response}\n")
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again with a different query.\n")

if __name__ == "__main__":
    main()
