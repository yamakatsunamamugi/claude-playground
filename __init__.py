"""
AI Chat Service Automation Package
fÒûvî„n×íÈ¿¤×ŸÅ

Version: 1.0.0
Author: AI Assistant
License: Educational Use Only

  Íjè‹:
- SnÄüëofÒûvî„ng(WfO`UD
- AIµüÓ¹n)(’uˆWfO`UD
- ìüÈ6P’ˆŠij“”g(WfO`UD
- ¢«¦óÈ\bnê¹¯LB‹Sh’ãWfO`UD
- F()(o¨hW~[“
"""

from .core.chatgpt_bot import ChatGPTBot
from .core.base_bot import BaseBot
from .core.exceptions import (
    AIServiceError,
    SelectorNotFoundError,
    RateLimitError,
    LoginRequiredError,
    ServiceUnavailableError,
    ResponseTimeoutError,
    ConfigurationError,
    DriverInitializationError
)

__version__ = "1.0.0"
__author__ = "AI Assistant"
__license__ = "Educational Use Only"

__all__ = [
    "ChatGPTBot",
    "BaseBot",
    "AIServiceError",
    "SelectorNotFoundError", 
    "RateLimitError",
    "LoginRequiredError",
    "ServiceUnavailableError",
    "ResponseTimeoutError",
    "ConfigurationError",
    "DriverInitializationError"
]

# (
nè’h:
def show_disclaimer():
    """(
nè’h:"""
    print("> AI Chat Service Automation")
    print(f"Version: {__version__}")
    print("")
    print("  IMPORTANT DISCLAIMERS:")
    print("- This tool is for educational and research purposes only")
    print("- Follow the terms of service of each AI service") 
    print("- Be aware of rate limits and potential account restrictions")
    print("- The tool may break due to UI changes")
    print("- Commercial use is not recommended")
    print("")