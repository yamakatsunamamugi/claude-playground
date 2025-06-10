"""
AI Chat Service Automation - Custom Exceptions
"""

class AIServiceError(Exception):
    """Base exception class"""
    pass

class SelectorNotFoundError(AIServiceError):
    """Selector not found (UI change impact)"""
    def __init__(self, selectors_tried: list, service: str = "unknown"):
        self.selectors_tried = selectors_tried
        self.service = service
        super().__init__(f"None of the selectors found for {service}: {selectors_tried}")

class RateLimitError(AIServiceError):
    """Rate limit reached"""
    def __init__(self, service: str = "unknown", cooldown_seconds: int = None):
        self.service = service
        self.cooldown_seconds = cooldown_seconds
        message = f"Rate limit reached for {service}"
        if cooldown_seconds:
            message += f". Wait {cooldown_seconds} seconds."
        super().__init__(message)

class LoginRequiredError(AIServiceError):
    """Login required"""
    def __init__(self, service: str = "unknown"):
        self.service = service
        super().__init__(f"Login required for {service}")

class ServiceUnavailableError(AIServiceError):
    """Service unavailable"""
    def __init__(self, service: str = "unknown", status_code: int = None):
        self.service = service
        self.status_code = status_code
        message = f"Service {service} is unavailable"
        if status_code:
            message += f" (HTTP {status_code})"
        super().__init__(message)

class ResponseTimeoutError(AIServiceError):
    """Response timeout"""
    def __init__(self, service: str = "unknown", timeout_seconds: int = None):
        self.service = service
        self.timeout_seconds = timeout_seconds
        message = f"Response timeout for {service}"
        if timeout_seconds:
            message += f" (waited {timeout_seconds}s)"
        super().__init__(message)

class ConfigurationError(AIServiceError):
    """Configuration error"""
    def __init__(self, config_key: str, message: str = None):
        self.config_key = config_key
        full_message = f"Configuration error for '{config_key}'"
        if message:
            full_message += f": {message}"
        super().__init__(full_message)

class DriverInitializationError(AIServiceError):
    """Driver initialization error"""
    def __init__(self, driver_type: str = "unknown", original_error: Exception = None):
        self.driver_type = driver_type
        self.original_error = original_error
        message = f"Failed to initialize {driver_type} driver"
        if original_error:
            message += f": {str(original_error)}"
        super().__init__(message)