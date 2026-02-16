"""Main Toggl Track API Client."""

import os
import logging
from typing import Optional, Dict, Any

import requests

from .exceptions import (
    TogglError,
    TogglAuthError,
    TogglRateLimitError,
    TogglQuotaError,
    TogglNotFoundError,
    TogglValidationError,
    TogglServerError,
)
from .utils import RateLimiter, clean_params
from .endpoints import (
    MeEndpoint,
    TimeEntriesEndpoint,
    ProjectsEndpoint,
    ProjectUsersEndpoint,
    ClientsEndpoint,
    TagsEndpoint,
    WorkspacesEndpoint,
    WorkspaceUsersEndpoint,
    TasksEndpoint,
    ReportsEndpoint,
    GroupsEndpoint,
    OrganizationsEndpoint,
    WebhooksEndpoint,
    ExpensesEndpoint,
)

logger = logging.getLogger(__name__)


class TogglClient:
    """
    Complete Toggl Track API v9 Client.
    
    Features:
    - Full API coverage (Time Entries, Projects, Reports, etc.)
    - Automatic pagination support
    - Rate limiting and quota management
    - Type hints and data models
    - Comprehensive error handling
    
    Authentication:
        # Method 1: API Token (recommended)
        client = TogglClient(api_token="your_token")
        
        # Method 2: Email + Password
        client = TogglClient(email="user@example.com", password="secret")
        
        # Method 3: Environment variables
        export TOGGL_API_TOKEN=your_token
        client = TogglClient()
    
    Example:
        client = TogglClient(api_token="xxx")
        
        # Get current user
        me = client.me.get()
        
        # List time entries
        entries = client.time_entries.list(
            start_date="2024-01-01",
            end_date="2024-01-31"
        )
        
        # Start a timer
        timer = client.time_entries.start(
            workspace_id=123,
            description="Working on project"
        )
    """
    
    BASE_URL = "https://api.track.toggl.com/api/v9"
    
    def __init__(
        self,
        api_token: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        session_cookie: Optional[str] = None,
        rate_limit_requests_per_second: float = 1.0,
    ):
        """
        Initialize Toggl client.
        
        Args:
            api_token: Toggl API token (from https://track.toggl.com/profile)
            email: Toggl account email
            password: Toggl account password
            session_cookie: Session cookie for authentication
            rate_limit_requests_per_second: Rate limit for API requests
        """
        self.api_token = api_token or os.getenv("TOGGL_API_TOKEN")
        self.email = email or os.getenv("TOGGL_EMAIL")
        self.password = password or os.getenv("TOGGL_PASSWORD")
        self.session_cookie = session_cookie
        
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        
        # Setup authentication
        if self.api_token:
            self.session.auth = (self.api_token, "api_token")
        elif self.email and self.password:
            self.session.auth = (self.email, self.password)
        elif self.session_cookie:
            self.session.headers.update({
                "Cookie": f"__Secure-accounts-session={self.session_cookie}"
            })
        else:
            raise TogglAuthError(
                "Authentication required. Provide api_token, email+password, "
                "session_cookie, or set TOGGL_API_TOKEN environment variable. "
                "Get your token at: https://track.toggl.com/profile"
            )
        
        # Rate limiter
        self.rate_limiter = RateLimiter(rate_limit_requests_per_second)
        
        # Initialize endpoints
        self.me = MeEndpoint(self)
        self.time_entries = TimeEntriesEndpoint(self)
        self.projects = ProjectsEndpoint(self)
        self.project_users = ProjectUsersEndpoint(self)
        self.clients = ClientsEndpoint(self)
        self.tags = TagsEndpoint(self)
        self.workspaces = WorkspacesEndpoint(self)
        self.workspace_users = WorkspaceUsersEndpoint(self)
        self.tasks = TasksEndpoint(self)
        self.reports = ReportsEndpoint(self)
        self.groups = GroupsEndpoint(self)
        self.organizations = OrganizationsEndpoint(self)
        self.webhooks = WebhooksEndpoint(self)
        self.expenses = ExpensesEndpoint(self)
    
    def _handle_error(self, response: requests.Response):
        """Handle API errors and raise appropriate exceptions."""
        status_code = response.status_code
        
        try:
            body = response.json()
        except Exception:
            body = {"message": response.text}
        
        message = body.get("message", body.get("error", "Unknown error"))
        
        if status_code == 400:
            raise TogglValidationError(message, status_code, body)
        elif status_code == 401:
            raise TogglAuthError(message, status_code, body)
        elif status_code == 402:
            # Quota exceeded
            quota_remaining = response.headers.get("X-Toggl-Quota-Remaining")
            quota_resets = response.headers.get("X-Toggl-Quota-Resets-In")
            raise TogglQuotaError(
                message,
                quota_remaining=int(quota_remaining) if quota_remaining else None,
                quota_resets_in=int(quota_resets) if quota_resets else None,
                status_code=status_code,
                response_body=body
            )
        elif status_code == 403:
            raise TogglAuthError(message, status_code, body)
        elif status_code == 404:
            raise TogglNotFoundError(message, status_code, body)
        elif status_code == 429:
            # Rate limit
            retry_after = response.headers.get("Retry-After")
            raise TogglRateLimitError(
                message,
                retry_after=int(retry_after) if retry_after else None,
                status_code=status_code,
                response_body=body
            )
        elif status_code >= 500:
            raise TogglServerError(message, status_code, body)
        else:
            raise TogglError(message, status_code, body)
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> Any:
        """Make an API request with rate limiting and error handling."""
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()
        
        # Build URL
        url = endpoint if endpoint.startswith("http") else f"{self.BASE_URL}{endpoint}"
        
        # Clean params
        params = clean_params(params) if params else None
        data = clean_params(data) if data else None
        
        logger.debug(f"{method} {url} params={params} data={data}")
        
        # Make request
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=data,
        )
        
        # Update rate limit info from headers
        self.rate_limiter.update_from_headers(dict(response.headers))
        
        # Handle errors
        if not response.ok:
            self._handle_error(response)
        
        # Return JSON or None
        if response.content:
            return response.json()
        return None
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Make GET request."""
        return self._request("GET", endpoint, params)
    
    def _post(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Any:
        """Make POST request."""
        return self._request("POST", endpoint, params, data)
    
    def _put(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Any:
        """Make PUT request."""
        return self._request("PUT", endpoint, params, data)
    
    def _patch(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Any:
        """Make PATCH request."""
        return self._request("PATCH", endpoint, params, data)
    
    def _delete(self, endpoint: str, params: Optional[Dict] = None) -> bool:
        """Make DELETE request."""
        response = self._request("DELETE", endpoint, params)
        return True
    
    @staticmethod
    def create_session(email: str, password: str) -> str:
        """
        Create a session and return session cookie.
        
        Args:
            email: Toggl account email
            password: Toggl account password
            
        Returns:
            Session cookie value
        """
        url = "https://accounts.toggl.com/api/sessions"
        response = requests.post(
            url,
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        cookie = response.headers.get("Set-Cookie", "")
        if "__Secure-accounts-session=" in cookie:
            return cookie.split("__Secure-accounts-session=")[1].split(";")[0]
        raise TogglAuthError("Failed to get session cookie")
