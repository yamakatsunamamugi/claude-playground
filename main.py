#!/usr/bin/env python3
"""
AI Chat Service Automation - Main Application
Main Application

Usage Examples:
    python main.py
    python main.py --service chatgpt --message "Hello, how are you?"
    python main.py --interactive
"""

import sys
import argparse
import time
from pathlib import Path
from typing import Optional

# Add package root
sys.path.insert(0, str(Path(__file__).parent))

from core.chatgpt_bot import ChatGPTBot
from core.exceptions import (
    AIServiceError, LoginRequiredError, RateLimitError,
    SelectorNotFoundError, ResponseTimeoutError
)


class ChatAutomationApp:
    """
    Main class for chat automation application
    """
    
    def __init__(self):
        self.bot: Optional[ChatGPTBot] = None
        self.running = False
    
    def run_single_message(self, message: str, service: str = "chatgpt") -> bool:
        """
        Execute single message sending
        
        Args:
            message: Message to send
            service: Service name
            
        Returns:
            bool: Execution success flag
        """
        print(f"🤖 AI Chat Automation - Single Message Mode")
        print(f"Service: {service}")
        print(f"Message: {message}")
        print("-" * 50)
        
        try:
            # Bot initialization
            if service == "chatgpt":
                self.bot = ChatGPTBot()
            else:
                print(f"❌ Service '{service}' is not supported yet.")
                return False
            
            # Launch browser
            print("🚀 Launching browser...")
            if not self.bot.launch_browser():
                print("❌ Failed to launch browser")
                return False
            
            # Wait for login
            print("⏳ Waiting for manual login...")
            if not self.bot.wait_for_manual_login(timeout=300):
                print("❌ Login failed or timed out")
                return False
            
            # Send message
            print("📤 Sending message...")
            response = self.bot.send_message(message)
            
            if response:
                print("✅ Response received!")
                print("-" * 50)
                print("🤖 AI Response:")
                print(response)
                print("-" * 50)
                
                # Show stats
                stats = self.bot.get_chatgpt_stats()
                print(f"📊 Stats: {stats['messages_sent']} messages sent, {stats['responses_received']} responses received")
                
                # Auto save
                if self.bot.save_conversation():
                    print("💾 Conversation saved automatically")
                
                return True
            else:
                print("❌ No response received")
                return False
                
        except LoginRequiredError:
            print("❌ Login required. Please ensure you're logged in to the service.")
            return False
        except RateLimitError as e:
            print(f"⚠️ Rate limit reached: {e}")
            print("Please wait and try again later.")
            return False
        except SelectorNotFoundError as e:
            print(f"❌ UI element not found: {e}")
            print("The service UI may have changed. Please check for updates.")
            return False
        except ResponseTimeoutError:
            print("⏰ Response timeout. The AI might be taking longer than usual.")
            return False
        except AIServiceError as e:
            print(f"❌ Service error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
        finally:
            if self.bot:
                self.bot.cleanup()
    
    def run_interactive_mode(self, service: str = "chatgpt") -> bool:
        """
        Execute interactive mode
        
        Args:
            service: Service name
            
        Returns:
            bool: Execution success flag
        """
        print(f"🤖 AI Chat Automation - Interactive Mode")
        print(f"Service: {service}")
        print("Type 'quit', 'exit', or 'q' to stop")
        print("Type 'help' for available commands")
        print("-" * 50)
        
        try:
            # Bot initialization
            if service == "chatgpt":
                self.bot = ChatGPTBot()
            else:
                print(f"❌ Service '{service}' is not supported yet.")
                return False
            
            # Launch browser
            print("🚀 Launching browser...")
            if not self.bot.launch_browser():
                print("❌ Failed to launch browser")
                return False
            
            # Wait for login
            print("⏳ Waiting for manual login...")
            if not self.bot.wait_for_manual_login(timeout=300):
                print("❌ Login failed or timed out")
                return False
            
            print("✅ Ready for conversation!")
            print("💡 Tip: The bot will simulate human-like typing for natural interaction.")
            
            self.running = True
            message_count = 0
            
            while self.running:
                try:
                    # User input
                    user_input = input("\\n👤 You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Command processing
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        break
                    elif user_input.lower() == 'help':
                        self._show_help()
                        continue
                    elif user_input.lower() == 'stats':
                        self._show_stats()
                        continue
                    elif user_input.lower() == 'save':
                        if self.bot.save_conversation():
                            print("💾 Conversation saved successfully")
                        else:
                            print("❌ Failed to save conversation")
                        continue
                    elif user_input.lower() == 'reset':
                        if self.bot.reset_conversation():
                            print("🔄 Conversation reset")
                            message_count = 0
                        else:
                            print("❌ Failed to reset conversation")
                        continue
                    
                    # Send message
                    print("📤 Sending message...")
                    response = self.bot.send_message(user_input)
                    
                    if response:
                        message_count += 1
                        print(f"🤖 AI: {response}")
                        
                        # Periodic stats display
                        if message_count % 5 == 0:
                            print(f"\\n📊 Messages exchanged: {message_count}")
                    else:
                        print("❌ No response received")
                
                except KeyboardInterrupt:
                    print("\\n🛑 Interrupted by user")
                    break
                except RateLimitError as e:
                    print(f"\\n⚠️ Rate limit: {e}")
                    print("Waiting before continuing...")
                    time.sleep(10)
                    continue
                except Exception as e:
                    print(f"\\n❌ Error: {e}")
                    print("Continuing...")
                    continue
            
            # End processing
            print("\\n👋 Conversation ended")
            
            # Final stats
            self._show_stats()
            
            # Auto save
            if message_count > 0 and self.bot.save_conversation():
                print("💾 Final conversation saved automatically")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start interactive mode: {e}")
            return False
        finally:
            if self.bot:
                self.bot.cleanup()
    
    def _show_help(self):
        """Show help"""
        print("\\n📚 Available Commands:")
        print("  help    - Show this help message")
        print("  stats   - Show conversation statistics")
        print("  save    - Save current conversation")
        print("  reset   - Start a new conversation")
        print("  quit    - Exit the application")
        print("\\n💡 Tips:")
        print("  - The bot simulates human-like typing patterns")
        print("  - Rate limits are automatically managed")
        print("  - Conversations are auto-saved when you exit")
    
    def _show_stats(self):
        """Show statistics"""
        if self.bot:
            stats = self.bot.get_chatgpt_stats()
            print("\\n📊 Session Statistics:")
            print(f"  Messages sent: {stats['messages_sent']}")
            print(f"  Responses received: {stats['responses_received']}")
            print(f"  Errors: {stats['errors_count']}")
            print(f"  Model: {stats['model_name']}")
            if stats.get('session_duration_seconds'):
                print(f"  Session duration: {stats['session_duration_seconds']:.1f}s")
            if stats.get('conversation_url'):
                print(f"  Conversation URL: {stats['conversation_url']}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="AI Chat Service Automation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --interactive                    # Start interactive mode
  %(prog)s --message "Hello!"               # Send single message
  %(prog)s --service chatgpt --message "Hi" # Specify service

Supported Services:
  - chatgpt (ChatGPT - most stable)
  - gemini (Google Gemini - experimental)
  - claude (Claude - experimental)

Note: This tool is for educational and research purposes only.
      Please follow the terms of service of each AI service.
        """
    )
    
    parser.add_argument(
        "--service",
        choices=["chatgpt", "gemini", "claude"],
        default="chatgpt",
        help="AI service to use (default: chatgpt)"
    )
    
    parser.add_argument(
        "--message",
        type=str,
        help="Single message to send"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Start in interactive mode"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to config file"
    )
    
    args = parser.parse_args()
    
    # Argument validation
    if not args.message and not args.interactive:
        # Default to interactive mode
        args.interactive = True
    
    if args.message and args.interactive:
        print("❌ Cannot use --message and --interactive together")
        return 1
    
    # Show warnings
    print("⚠️  IMPORTANT DISCLAIMERS:")
    print("   - This tool is for educational and research purposes only")
    print("   - Follow the terms of service of each AI service")
    print("   - Be aware of rate limits and potential account restrictions")
    print("   - The tool may break due to UI changes")
    print("")
    
    # Application execution
    app = ChatAutomationApp()
    
    try:
        if args.interactive:
            success = app.run_interactive_mode(args.service)
        else:
            success = app.run_single_message(args.message, args.service)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\\n🛑 Interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())