"""Projects endpoints."""

from typing import Optional, List, Dict, Any
from .base import BaseEndpoint
from ..models import Project, ProjectUser
from ..utils import clean_params, validate_workspace_id, validate_project_id, paginated_list


class ProjectsEndpoint(BaseEndpoint):
    """Endpoints for project management."""
    
    def list(
        self,
        workspace_id: int,
        active: Optional[bool] = None,
        since: Optional[int] = None,
        billable: Optional[bool] = None,
        user_ids: Optional[List[int]] = None,
        client_ids: Optional[List[int]] = None,
        group_ids: Optional[List[int]] = None,
        project_ids: Optional[List[int]] = None,
        statuses: Optional[List[str]] = None,
        name: Optional[str] = None,
        page: int = 1,
        per_page: int = 151,
        sort_field: Optional[str] = None,
        sort_order: Optional[str] = None,
        only_templates: Optional[bool] = None,
        only_me: Optional[bool] = None,
        only_editable: Optional[bool] = None,
        sort_pinned: Optional[bool] = None,
        search: Optional[str] = None,
        auto_paginate: bool = False,
        max_pages: Optional[int] = None,
    ) -> List[Project]:
        """
        Get projects for a workspace.
        
        Args:
            workspace_id: Workspace ID
            active: Filter by active status (True/False/None for all)
            since: Unix timestamp for projects modified since
            billable: Filter by billable status
            user_ids: Filter by user IDs
            client_ids: Filter by client IDs
            group_ids: Filter by group IDs
            project_ids: Filter by specific project IDs
            statuses: Filter by statuses
            name: Filter by name
            page: Page number
            per_page: Items per page (max 200)
            sort_field: Sort field
            sort_order: Sort order (asc/desc)
            only_templates: Only templates
            only_me: Only projects assigned to current user
            only_editable: Only projects user can edit
            sort_pinned: Place pinned projects at top
            search: Search query
            auto_paginate: Fetch all pages automatically
            max_pages: Max pages when auto_paginate=True
            
        Returns:
            List of Project models
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        params = clean_params({
            "active": "true" if active else "false" if active is False else None,
            "since": since,
            "billable": billable,
            "user_ids": ",".join(map(str, user_ids)) if user_ids else None,
            "client_ids": ",".join(map(str, client_ids)) if client_ids else None,
            "group_ids": ",".join(map(str, group_ids)) if group_ids else None,
            "project_ids": ",".join(map(str, project_ids)) if project_ids else None,
            "statuses": ",".join(statuses) if statuses else None,
            "name": name,
            "page": page,
            "per_page": min(per_page, 200),
            "sort_field": sort_field,
            "sort_order": sort_order,
            "only_templates": only_templates,
            "only_me": only_me,
            "only_editable": only_editable,
            "sort_pinned": sort_pinned,
            "search": search,
        })
        
        def fetch_page(p: int, pp: int):
            page_params = {**params, "page": p, "per_page": pp}
            return self._get(f"/workspaces/{workspace_id}/projects", page_params)
        
        if auto_paginate:
            result = paginated_list(fetch_page, page, per_page, True, max_pages)
            return [Project.from_dict(item) for item in result.items]
        else:
            data = fetch_page(page, per_page)
            items = data.get("items", [])
            return [Project.from_dict(item) for item in items]
    
    def get(self, workspace_id: int, project_id: int) -> Optional[Project]:
        """
        Get a specific project.
        
        Args:
            workspace_id: Workspace ID
            project_id: Project ID
            
        Returns:
            Project model or None if not found
        """
        workspace_id = validate_workspace_id(workspace_id)
        project_id = validate_project_id(project_id)
        
        try:
            data = self._get(f"/workspaces/{workspace_id}/projects/{project_id}")
            return Project.from_dict(data) if data else None
        except Exception:
            return None
    
    def create(
        self,
        workspace_id: int,
        name: str,
        client_id: Optional[int] = None,
        color: Optional[str] = None,
        is_private: bool = True,
        billable: Optional[bool] = None,
        rate: Optional[float] = None,
        estimated_hours: Optional[int] = None,
        **kwargs
    ) -> Project:
        """
        Create a new project.
        
        Args:
            workspace_id: Workspace ID
            name: Project name
            client_id: Client ID
            color: Project color
            is_private: Whether private
            billable: Whether billable (premium)
            rate: Hourly rate (premium)
            estimated_hours: Estimated hours (premium)
            **kwargs: Additional fields
            
        Returns:
            Created Project model
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        data = clean_params({
            "name": name,
            "client_id": client_id,
            "color": color,
            "is_private": is_private,
            "billable": billable,
            "rate": rate,
            "estimated_hours": estimated_hours,
            **kwargs
        })
        
        result = self._post(f"/workspaces/{workspace_id}/projects", data)
        return Project.from_dict(result)
    
    def update(
        self,
        workspace_id: int,
        project_id: int,
        **kwargs
    ) -> Project:
        """
        Update a project.
        
        Args:
            workspace_id: Workspace ID
            project_id: Project ID
            **kwargs: Fields to update
            
        Returns:
            Updated Project model
        """
        workspace_id = validate_workspace_id(workspace_id)
        project_id = validate_project_id(project_id)
        
        result = self._put(f"/workspaces/{workspace_id}/projects/{project_id}", kwargs)
        return Project.from_dict(result)
    
    def delete(self, workspace_id: int, project_id: int) -> bool:
        """
        Delete a project.
        
        Args:
            workspace_id: Workspace ID
            project_id: Project ID
            
        Returns:
            True if deleted successfully
        """
        workspace_id = validate_workspace_id(workspace_id)
        project_id = validate_project_id(project_id)
        
        return self._delete(f"/workspaces/{workspace_id}/projects/{project_id}")


class ProjectUsersEndpoint(BaseEndpoint):
    """Endpoints for project user management."""
    
    def list(
        self,
        workspace_id: int,
        project_ids: Optional[List[int]] = None,
        user_id: Optional[int] = None,
        with_group_members: Optional[bool] = None,
    ) -> List[ProjectUser]:
        """
        Get project users for a workspace.
        
        Args:
            workspace_id: Workspace ID
            project_ids: Filter by project IDs (max 200)
            user_id: Filter by user ID
            with_group_members: Include group members
            
        Returns:
            List of ProjectUser models
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        if project_ids and len(project_ids) > 200:
            raise ValueError("Maximum 200 project IDs allowed")
        
        params = clean_params({
            "project_ids": ",".join(map(str, project_ids)) if project_ids else None,
            "user_id": user_id,
            "with_group_members": with_group_members,
        })
        
        data = self._get(f"/workspaces/{workspace_id}/project_users", params)
        items = data.get("items", []) if isinstance(data, dict) else data
        return [ProjectUser.from_dict(item) for item in items]
    
    def add(
        self,
        workspace_id: int,
        project_id: int,
        user_id: int,
        manager: bool = False,
        rate: Optional[float] = None,
        labor_cost: Optional[float] = None,
        rate_change_mode: Optional[str] = None,
        labor_cost_change_mode: Optional[str] = None,
    ) -> ProjectUser:
        """
        Add a user to a project.
        
        Args:
            workspace_id: Workspace ID
            project_id: Project ID
            user_id: User ID
            manager: Whether user is manager
            rate: Hourly rate
            labor_cost: Labor cost
            rate_change_mode: "start-today", "override-current", "override-all"
            labor_cost_change_mode: "start-today", "override-current", "override-all"
            
        Returns:
            Created ProjectUser model
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        data = clean_params({
            "project_id": project_id,
            "user_id": user_id,
            "manager": manager,
            "rate": rate,
            "labor_cost": labor_cost,
            "rate_change_mode": rate_change_mode,
            "labor_cost_change_mode": labor_cost_change_mode,
        })
        
        result = self._post(f"/workspaces/{workspace_id}/project_users", data)
        return ProjectUser.from_dict(result)
    
    def update(
        self,
        workspace_id: int,
        project_user_id: int,
        **kwargs
    ) -> ProjectUser:
        """
        Update a project user.
        
        Args:
            workspace_id: Workspace ID
            project_user_id: Project user ID
            **kwargs: Fields to update
            
        Returns:
            Updated ProjectUser model
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        result = self._put(
            f"/workspaces/{workspace_id}/project_users/{project_user_id}",
            kwargs
        )
        return ProjectUser.from_dict(result)
    
    def patch(
        self,
        workspace_id: int,
        project_user_ids: List[int],
        operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Bulk patch project users.
        
        Args:
            workspace_id: Workspace ID
            project_user_ids: List of project user IDs
            operations: Patch operations
            
        Returns:
            Dict with success/failure info
        """
        workspace_id = validate_workspace_id(workspace_id)
        ids_str = ",".join(map(str, project_user_ids))
        
        return self._patch(
            f"/workspaces/{workspace_id}/project_users/{ids_str}",
            operations
        )
    
    def delete(self, workspace_id: int, project_user_id: int) -> bool:
        """
        Remove a user from a project.
        
        Args:
            workspace_id: Workspace ID
            project_user_id: Project user ID
            
        Returns:
            True if removed successfully
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        return self._delete(f"/workspaces/{workspace_id}/project_users/{project_user_id}")
