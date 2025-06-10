"""
AI Chat Service Automation Package
f��v�n��ȿ�ן�

Version: 1.0.0
Author: AI Assistant
License: Educational Use Only

� ́j��:
- Sn���of��v�ng(WfO`UD
- AI��ӹn)(��u�WfO`UD
- ���6P���ij��g(WfO`UD
- �����\bn깯LB�Sh��WfO`UD
- F()(o�hW~[�
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
n��h:
def show_disclaimer():
    """(
n��h:"""
    print("> AI Chat Service Automation")
    print(f"Version: {__version__}")
    print("")
    print("� IMPORTANT DISCLAIMERS:")
    print("- This tool is for educational and research purposes only")
    print("- Follow the terms of service of each AI service") 
    print("- Be aware of rate limits and potential account restrictions")
    print("- The tool may break due to UI changes")
    print("- Commercial use is not recommended")
    print("")