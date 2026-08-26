"""
verifydating.exceptions
~~~~~~~~~~~~~~~~~~~~~~~
Custom exceptions raised by the VerifyDating API client.
"""

class VerifyDatingError(Exception):
    """Base exception for all VerifyDating SDK errors."""
    pass

class AuthenticationError(VerifyDatingError):
    """Raised when API Key authentication fails."""
    pass

class QuotaExceededError(VerifyDatingError):
    """Raised when monthly API quota is exceeded."""
    pass

class RateLimitError(VerifyDatingError):
    """Raised when rate limits are exceeded."""
    pass

class APIResponseError(VerifyDatingError):
    """Raised when API returns an unhandled HTTP error code."""
    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
