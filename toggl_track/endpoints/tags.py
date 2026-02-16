"""Tags endpoints."""

from typing import Optional, List
from .base import BaseEndpoint
from ..models import Tag
from ..utils import clean_params, validate_workspace_id


class TagsEndpoint(BaseEndpoint):
    """Endpoints for tag management."""
    
    def list(self, workspace_id: int) -> List[Tag]:
        """
        Get all tags in a workspace.
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            List of Tag models
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        data = self._get(f"/workspaces/{workspace_id}/tags")
        if isinstance(data, list):
            return [Tag.from_dict(item) for item in data]
        return []
    
    def get(self, workspace_id: int, tag_id: int) -> Optional[Tag]:
        """
        Get a specific tag.
        
        Args:
            workspace_id: Workspace ID
            tag_id: Tag ID
            
        Returns:
            Tag model or None if not found
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        try:
            data = self._get(f"/workspaces/{workspace_id}/tags/{tag_id}")
            return Tag.from_dict(data) if data else None
        except Exception:
            return None
    
    def create(self, workspace_id: int, name: str, **kwargs) -> Tag:
        """
        Create a new tag.
        
        Args:
            workspace_id: Workspace ID
            name: Tag name
            **kwargs: Additional fields
            
        Returns:
            Created Tag model
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        data = clean_params({"name": name, **kwargs})
        result = self._post(f"/workspaces/{workspace_id}/tags", data)
        return Tag.from_dict(result)
    
    def update(
        self,
        workspace_id: int,
        tag_id: int,
        **kwargs
    ) -> Tag:
        """
        Update a tag.
        
        Args:
            workspace_id: Workspace ID
            tag_id: Tag ID
            **kwargs: Fields to update
            
        Returns:
            Updated Tag model
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        result = self._put(f"/workspaces/{workspace_id}/tags/{tag_id}", kwargs)
        return Tag.from_dict(result)
    
    def delete(self, workspace_id: int, tag_id: int) -> bool:
        """
        Delete a tag.
        
        Args:
            workspace_id: Workspace ID
            tag_id: Tag ID
            
        Returns:
            True if deleted successfully
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        return self._delete(f"/workspaces/{workspace_id}/tags/{tag_id}")
