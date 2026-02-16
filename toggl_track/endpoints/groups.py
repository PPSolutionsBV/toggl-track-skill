"""Groups endpoints."""

from typing import Optional, List
from .base import BaseEndpoint
from ..models import Group
from ..utils import clean_params, validate_workspace_id


class GroupsEndpoint(BaseEndpoint):
    """Endpoints for group management."""
    
    def list(
        self,
        workspace_id: int,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Group]:
        """
        Get all groups in a workspace.
        
        Args:
            workspace_id: Workspace ID
            page: Page number
            per_page: Items per page
            
        Returns:
            List of Group models
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        params = clean_params({
            "page": page,
            "per_page": per_page,
        })
        
        data = self._get(f"/workspaces/{workspace_id}/groups", params)
        if isinstance(data, list):
            return [Group.from_dict(item) for item in data]
        return []
    
    def get(self, workspace_id: int, group_id: int) -> Optional[Group]:
        """
        Get a specific group.
        
        Args:
            workspace_id: Workspace ID
            group_id: Group ID
            
        Returns:
            Group model or None if not found
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        try:
            data = self._get(f"/workspaces/{workspace_id}/groups/{group_id}")
            return Group.from_dict(data) if data else None
        except Exception:
            return None
    
    def create(
        self,
        workspace_id: int,
        name: str,
        user_ids: Optional[List[int]] = None,
        **kwargs
    ) -> Group:
        """
        Create a new group.
        
        Args:
            workspace_id: Workspace ID
            name: Group name
            user_ids: List of user IDs to add
            **kwargs: Additional fields
            
        Returns:
            Created Group model
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        data = clean_params({
            "name": name,
            "user_ids": user_ids,
            **kwargs
        })
        
        result = self._post(f"/workspaces/{workspace_id}/groups", data)
        return Group.from_dict(result)
    
    def update(
        self,
        workspace_id: int,
        group_id: int,
        **kwargs
    ) -> Group:
        """
        Update a group.
        
        Args:
            workspace_id: Workspace ID
            group_id: Group ID
            **kwargs: Fields to update
            
        Returns:
            Updated Group model
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        result = self._put(f"/workspaces/{workspace_id}/groups/{group_id}", kwargs)
        return Group.from_dict(result)
    
    def delete(self, workspace_id: int, group_id: int) -> bool:
        """
        Delete a group.
        
        Args:
            workspace_id: Workspace ID
            group_id: Group ID
            
        Returns:
            True if deleted successfully
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        return self._delete(f"/workspaces/{workspace_id}/groups/{group_id}")
