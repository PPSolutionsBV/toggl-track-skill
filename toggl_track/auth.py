"""Authentication handling for Toggl Track API."""

import base64
from typing import Optional, Tuple


class TogglAuth:
    """Handles authentication for Toggl Track API."""
    
    def __init__(
        self,
        api_token: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None
    ):
        """Initialize authentication.
        
        Args:
            api_token: Toggl API token (preferred method)
            email: User email (alternative auth)
            password: User password (alternative auth)
            
        Raises:
            ValueError: If no valid credentials provided
        """
        self.api_token = api_token
        self.email = email
        self.password = password
        
        if api_token:
            self._auth_header = self._make_auth_header(api_token, "api_token")
        elif email and password:
            self._auth_header = self._make_auth_header(email, password)
        else:
            raise ValueError(
                "Authentication required: provide either api_token or email/password"
            )
    
    def _make_auth_header(self, username: str, password: str) -> str:
        """Create Basic Auth header."""
        credentials = f"{username}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    @property
    def auth_header(self) -> str:
        """Get the Authorization header value."""
        return self._auth_header
    
    @property
    def headers(self) -> dict:
        """Get all required headers for authentication."""
        return {
            "Authorization": self.auth_header,
            "Content-Type": "application/json",
        }
