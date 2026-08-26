"""
isbrokersafe.exceptions
~~~~~~~~~~~~~~~~~~~~~~~
Custom exceptions for IsBrokerSafe SDK.
"""

class IsBrokerSafeError(Exception):
    """Base exception for all IsBrokerSafe errors."""
    pass

class AuthenticationError(IsBrokerSafeError):
    """Raised when the API key is missing or invalid (HTTP 401)."""
    pass

class QuotaExceededError(IsBrokerSafeError):
    """Raised when monthly API quota is exceeded (HTTP 429/403)."""
    pass

class RateLimitError(IsBrokerSafeError):
    """Raised when requests exceed rate limits."""
    pass

class APIResponseError(IsBrokerSafeError):
    """Raised when the API returns an unexpected error status code."""
    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
