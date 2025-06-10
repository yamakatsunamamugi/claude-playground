#!/usr/bin/env python3
"""
AI Chat Service Automation - Simple Demo
"""

import sys
import argparse
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.chatgpt_bot import ChatGPTBot
from core.exceptions import AIServiceError


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Chat Automation Demo")
    parser.add_argument("--message", type=str, help="Message to send")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    if not args.message and not args.interactive:
        args.interactive = True
    
    print("🤖 AI Chat Service Automation - Demo Version")
    print("⚠️  This is a simplified demo version")
    print("-" * 50)
    
    bot = ChatGPTBot()
    
    try:
        # Launch and login
        if not bot.launch_browser():
            print("❌ Failed to launch browser")
            return 1
        
        if not bot.wait_for_manual_login():
            print("❌ Login failed")
            return 1
        
        if args.interactive:
            print("✅ Ready for conversation!")
            print("Type 'quit' to exit")
            
            while True:
                try:
                    user_input = input("\n👤 You: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        break
                    
                    if not user_input:
                        continue
                    
                    response = bot.send_message(user_input)
                    print(f"🤖 AI: {response}")
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
        else:
            # Single message
            response = bot.send_message(args.message)
            print(f"🤖 Response: {response}")
        
        # Show stats
        stats = bot.get_chatgpt_stats()
        print(f"\n📊 Stats: {stats['messages_sent']} messages sent")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        bot.cleanup()


if __name__ == "__main__":
    sys.exit(main())