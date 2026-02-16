"""Organizations endpoints."""

from typing import Optional, List, Dict, Any
from .base import BaseEndpoint
from ..utils import clean_params


class OrganizationsEndpoint(BaseEndpoint):
    """Endpoints for organization management."""
    
    def get(self, organization_id: int) -> Dict[str, Any]:
        """
        Get organization details.
        
        Args:
            organization_id: Organization ID
            
        Returns:
            Organization data dict
        """
        return self._get(f"/organizations/{organization_id}")
    
    def update(self, organization_id: int, **kwargs) -> Dict[str, Any]:
        """
        Update organization settings.
        
        Args:
            organization_id: Organization ID
            **kwargs: Fields to update
            
        Returns:
            Updated organization data
        """
        return self._put(f"/organizations/{organization_id}", kwargs)
    
    def list_users(
        self,
        organization_id: int,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        List users in organization.
        
        Args:
            organization_id: Organization ID
            page: Page number
            per_page: Items per page
            
        Returns:
            List of organization user dicts
        """
        params = clean_params({
            "page": page,
            "per_page": per_page,
        })
        
        data = self._get(f"/organizations/{organization_id}/users", params)
        if isinstance(data, list):
            return data
        return data.get("items", []) if data else []
    
    def invite_user(
        self,
        organization_id: int,
        email: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Invite a user to the organization.
        
        Args:
            organization_id: Organization ID
            email: User email address
            **kwargs: Additional fields
            
        Returns:
            Invitation result
        """
        data = clean_params({
            "email": email,
            **kwargs
        })
        
        return self._post(f"/organizations/{organization_id}/invitations", data)
