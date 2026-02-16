"""User (/me) endpoints."""

from typing import Optional, Dict, Any
from .base import BaseEndpoint
from ..models import User


class MeEndpoint(BaseEndpoint):
    """Endpoints for current user management."""
    
    def get(self, with_related_data: bool = False) -> User:
        """
        Get current user details.
        
        Args:
            with_related_data: Include clients, projects, tasks, tags, workspaces, time_entries
            
        Returns:
            User model with user details
        """
        params = {}
        if with_related_data:
            params["with_related_data"] = "true"
        
        data = self._get("/me", params)
        return User.from_dict(data)
    
    def update(self, **kwargs) -> User:
        """
        Update current user.
        
        Args:
            fullname: User's full name
            email: User's email
            timezone: User's timezone
            beginning_of_week: First day of week (0=Sunday, 1=Monday)
            
        Returns:
            Updated User model
        """
        data = self._put("/me", kwargs)
        return User.from_dict(data)
    
    def check_logged_in(self) -> bool:
        """Check if authentication is working."""
        try:
            self._get("/me/logged")
            return True
        except Exception:
            return False
    
    def reset_api_token(self) -> str:
        """
        Reset API token and return new token.
        
        Returns:
            New API token string
        """
        result = self._post("/me/reset_token")
        return result.get("api_token", "")
