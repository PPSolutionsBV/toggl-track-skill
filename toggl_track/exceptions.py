"""Custom exceptions for Toggl Track API."""


class TogglError(Exception):
    """Base exception for Toggl API errors."""
    
    def __init__(self, message: str, status_code: int = None, response_body: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body


class TogglAuthError(TogglError):
    """Authentication failed or invalid credentials."""
    pass


class TogglRateLimitError(TogglError):
    """Rate limit exceeded (429 Too Many Requests)."""
    
    def __init__(self, message: str, retry_after: int = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class TogglQuotaError(TogglError):
    """API quota exceeded (402 Payment Required)."""
    
    def __init__(self, message: str, quota_remaining: int = None, quota_resets_in: int = None, **kwargs):
        super().__init__(message, **kwargs)
        self.quota_remaining = quota_remaining
        self.quota_resets_in = quota_resets_in


class TogglNotFoundError(TogglError):
    """Resource not found (404)."""
    pass


class TogglValidationError(TogglError):
    """Invalid request data (400)."""
    pass


class TogglServerError(TogglError):
    """Server error (5xx)."""
    pass
