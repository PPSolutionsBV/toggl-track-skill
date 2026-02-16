"""
Toggl Track API Client - Complete Python client for Toggl Track API v9

A production-ready client with full API coverage, pagination support,
rate limiting awareness, and comprehensive error handling.

Example:
    from toggl_track import TogglClient
    
    client = TogglClient(api_token="your_token")
    
    # Get current user
    me = client.me.get()
    
    # Get time entries with auto-pagination
    entries = client.time_entries.list(start_date="2024-01-01", end_date="2024-01-31")
    
    # Start a timer
    timer = client.time_entries.start(
        workspace_id=123,
        description="Working on project"
    )
"""

from .client import TogglClient
from .exceptions import (
    TogglError,
    TogglAuthError,
    TogglRateLimitError,
    TogglQuotaError,
    TogglNotFoundError,
    TogglValidationError,
)
from .models import (
    User,
    TimeEntry,
    Project,
    Client,
    Tag,
    Workspace,
    Task,
    Group,
    Report,
)

__version__ = "1.0.0"
__all__ = [
    "TogglClient",
    "TogglError",
    "TogglAuthError", 
    "TogglRateLimitError",
    "TogglQuotaError",
    "TogglNotFoundError",
    "TogglValidationError",
    "User",
    "TimeEntry",
    "Project",
    "Client",
    "Tag",
    "Workspace",
    "Task",
    "Group",
    "Report",
]
