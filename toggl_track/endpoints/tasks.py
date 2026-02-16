"""Tasks endpoints."""

from typing import Optional, List
from .base import BaseEndpoint
from ..models import Task
from ..utils import clean_params, validate_workspace_id, validate_project_id


class TasksEndpoint(BaseEndpoint):
    """Endpoints for task management."""
    
    def list(
        self,
        workspace_id: int,
        project_id: Optional[int] = None,
        active: Optional[bool] = None,
    ) -> List[Task]:
        """
        Get tasks for a workspace.
        
        Args:
            workspace_id: Workspace ID
            project_id: Filter by project ID
            active: Filter by active status
            
        Returns:
            List of Task models
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        params = clean_params({
            "project_id": project_id,
            "active": active,
        })
        
        data = self._get(f"/workspaces/{workspace_id}/tasks", params)
        if isinstance(data, list):
            return [Task.from_dict(item) for item in data]
        return []
    
    def get(self, workspace_id: int, task_id: int) -> Optional[Task]:
        """
        Get a specific task.
        
        Args:
            workspace_id: Workspace ID
            task_id: Task ID
            
        Returns:
            Task model or None if not found
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        try:
            data = self._get(f"/workspaces/{workspace_id}/tasks/{task_id}")
            return Task.from_dict(data) if data else None
        except Exception:
            return None
    
    def create(
        self,
        workspace_id: int,
        project_id: int,
        name: str,
        active: bool = True,
        estimated_seconds: Optional[int] = None,
        **kwargs
    ) -> Task:
        """
        Create a new task.
        
        Args:
            workspace_id: Workspace ID
            project_id: Project ID
            name: Task name
            active: Whether active
            estimated_seconds: Estimated time in seconds
            **kwargs: Additional fields
            
        Returns:
            Created Task model
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        data = clean_params({
            "project_id": project_id,
            "name": name,
            "active": active,
            "estimated_seconds": estimated_seconds,
            **kwargs
        })
        
        result = self._post(f"/workspaces/{workspace_id}/tasks", data)
        return Task.from_dict(result)
    
    def update(
        self,
        workspace_id: int,
        task_id: int,
        **kwargs
    ) -> Task:
        """
        Update a task.
        
        Args:
            workspace_id: Workspace ID
            task_id: Task ID
            **kwargs: Fields to update
            
        Returns:
            Updated Task model
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        result = self._put(f"/workspaces/{workspace_id}/tasks/{task_id}", kwargs)
        return Task.from_dict(result)
    
    def delete(self, workspace_id: int, task_id: int) -> bool:
        """
        Delete a task.
        
        Args:
            workspace_id: Workspace ID
            task_id: Task ID
            
        Returns:
            True if deleted successfully
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        return self._delete(f"/workspaces/{workspace_id}/tasks/{task_id}")
