"""Workspaces endpoints."""

from typing import Optional, List, Dict, Any
from .base import BaseEndpoint
from ..models import Workspace, WorkspaceUser, Group
from ..utils import clean_params, validate_workspace_id, paginated_list


class WorkspacesEndpoint(BaseEndpoint):
    """Endpoints for workspace management."""
    
    def list(self) -> List[Workspace]:
        """
        Get all workspaces for current user.
        
        Returns:
            List of Workspace models
        """
        data = self._get("/workspaces")
        if isinstance(data, list):
            return [Workspace.from_dict(item) for item in data]
        return []
    
    def get(self, workspace_id: int) -> Optional[Workspace]:
        """
        Get a specific workspace.
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            Workspace model or None if not found
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        try:
            data = self._get(f"/workspaces/{workspace_id}")
            return Workspace.from_dict(data) if data else None
        except Exception:
            return None
    
    def create(
        self,
        organization_id: int,
        name: str,
        **kwargs
    ) -> Workspace:
        """
        Create a new workspace in an organization.
        
        Args:
            organization_id: Organization ID
            name: Workspace name
            **kwargs: Additional fields (admins, default_currency, etc.)
            
        Returns:
            Created Workspace model
        """
        data = clean_params({"name": name, **kwargs})
        result = self._post(f"/organizations/{organization_id}/workspaces", data)
        return Workspace.from_dict(result)
    
    def update(self, workspace_id: int, **kwargs) -> Workspace:
        """
        Update a workspace.
        
        Args:
            workspace_id: Workspace ID
            **kwargs: Fields to update
            
        Returns:
            Updated Workspace model
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        result = self._put(f"/workspaces/{workspace_id}", kwargs)
        return Workspace.from_dict(result)
    
    def groups(self, workspace_id: int) -> List[Group]:
        """
        Get all groups in a workspace.
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            List of Group models
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        data = self._get(f"/workspaces/{workspace_id}/groups")
        if isinstance(data, list):
            return [Group.from_dict(item) for item in data]
        return []


class WorkspaceUsersEndpoint(BaseEndpoint):
    """Endpoints for workspace user management."""
    
    def list(
        self,
        organization_id: int,
        workspace_id: int,
        page: int = 1,
        per_page: int = 50,
        custom_rates: Optional[bool] = None,
        active: Optional[bool] = None,
        name: Optional[str] = None,
        search: Optional[str] = None,
        auto_paginate: bool = False,
        max_pages: Optional[int] = None,
    ) -> List[WorkspaceUser]:
        """
        Get all users in a workspace.
        
        Args:
            organization_id: Organization ID
            workspace_id: Workspace ID
            page: Page number
            per_page: Items per page
            custom_rates: Filter by custom rates
            active: Filter by active status
            name: Filter by name
            search: Search by name or email
            auto_paginate: Fetch all pages automatically
            max_pages: Max pages when auto_paginate=True
            
        Returns:
            List of WorkspaceUser models
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        params = clean_params({
            "page": page,
            "per_page": per_page,
            "custom_rates": custom_rates,
            "active": active,
            "name": name,
            "search": search,
        })
        
        def fetch_page(p: int, pp: int):
            page_params = {**params, "page": p, "per_page": pp}
            return self._get(
                f"/organizations/{organization_id}/workspaces/{workspace_id}/workspace_users",
                page_params
            )
        
        if auto_paginate:
            result = paginated_list(fetch_page, page, per_page, True, max_pages)
            return [WorkspaceUser.from_dict(item) for item in result.items]
        else:
            data = fetch_page(page, per_page)
            items = data.get("items", [])
            return [WorkspaceUser.from_dict(item) for item in items]
    
    def patch(
        self,
        organization_id: int,
        workspace_id: int,
        delete: List[int]
    ) -> bool:
        """
        Remove users from workspace (bulk delete).
        
        Args:
            organization_id: Organization ID
            workspace_id: Workspace ID
            delete: List of workspace user IDs to delete
            
        Returns:
            True if successful
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        data = {"delete": delete}
        self._patch(
            f"/organizations/{organization_id}/workspaces/{workspace_id}/workspace_users",
            data
        )
        return True
