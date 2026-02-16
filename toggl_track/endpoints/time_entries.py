"""Time entries endpoints."""

from typing import Optional, List, Dict, Any, Iterator
from datetime import datetime, timezone
from .base import BaseEndpoint
from ..models import TimeEntry
from ..utils import clean_params, validate_time_entry_id, auto_paginate


class TimeEntriesEndpoint(BaseEndpoint):
    """Endpoints for time entry management."""
    
    def list(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        since: Optional[int] = None,
        before: Optional[str] = None,
        meta: Optional[bool] = None,
        include_sharing: Optional[bool] = None,
    ) -> List[TimeEntry]:
        """
        Get time entries for current user.
        
        Note: This endpoint returns all matching entries (no pagination).
        For large date ranges, consider using reports API.
        
        Args:
            start_date: Start date (YYYY-MM-DD or RFC3339)
            end_date: End date (YYYY-MM-DD or RFC3339)
            since: Unix timestamp to get entries modified since
            before: Get entries before this date
            meta: Include meta entity data (client_name, project_name, etc.)
            include_sharing: Include sharing details
            
        Returns:
            List of TimeEntry models
        """
        params = clean_params({
            "start_date": start_date,
            "end_date": end_date,
            "since": since,
            "before": before,
            "meta": "true" if meta else None,
            "include_sharing": "true" if include_sharing else None,
        })
        
        data = self._get("/me/time_entries", params)
        
        if isinstance(data, list):
            return [TimeEntry.from_dict(item) for item in data]
        elif isinstance(data, dict) and "items" in data:
            return [TimeEntry.from_dict(item) for item in data["items"]]
        return []
    
    def get(
        self,
        time_entry_id: int,
        meta: Optional[bool] = None,
        include_sharing: Optional[bool] = None
    ) -> Optional[TimeEntry]:
        """
        Get a specific time entry by ID.
        
        Args:
            time_entry_id: The time entry ID
            meta: Include meta entity data
            include_sharing: Include sharing details
            
        Returns:
            TimeEntry model or None if not found
        """
        time_entry_id = validate_time_entry_id(time_entry_id)
        
        params = clean_params({
            "meta": "true" if meta else None,
            "include_sharing": "true" if include_sharing else None,
        })
        
        try:
            data = self._get(f"/me/time_entries/{time_entry_id}", params)
            return TimeEntry.from_dict(data) if data else None
        except Exception:
            return None
    
    def current(
        self,
        meta: Optional[bool] = None,
        include_sharing: Optional[bool] = None
    ) -> Optional[TimeEntry]:
        """
        Get currently running time entry.
        
        Args:
            meta: Include meta entity data
            include_sharing: Include sharing details
            
        Returns:
            TimeEntry model or None if no timer running
        """
        params = clean_params({
            "meta": "true" if meta else None,
            "include_sharing": "true" if include_sharing else None,
        })
        
        data = self._get("/me/time_entries/current", params)
        return TimeEntry.from_dict(data) if data else None
    
    def create(
        self,
        workspace_id: int,
        description: str,
        duration: int,
        start: str,
        project_id: Optional[int] = None,
        task_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        tag_ids: Optional[List[int]] = None,
        billable: bool = False,
        stop: Optional[str] = None,
        created_with: str = "toggl-track-skill",
        meta: Optional[bool] = None,
    ) -> TimeEntry:
        """
        Create a new time entry.
        
        Args:
            workspace_id: Workspace ID (required)
            description: Time entry description
            duration: Duration in seconds. For running entries, use -1 * (Unix start time)
            start: Start time (ISO 8601)
            project_id: Project ID
            task_id: Task ID
            tags: List of tag names
            tag_ids: List of tag IDs
            billable: Whether billable
            stop: Stop time (ISO 8601), omit for running entries
            created_with: Client identifier
            meta: Include meta entity data in response
            
        Returns:
            Created TimeEntry model
        """
        data = clean_params({
            "workspace_id": workspace_id,
            "description": description,
            "duration": duration,
            "start": start,
            "project_id": project_id,
            "task_id": task_id,
            "tags": tags,
            "tag_ids": tag_ids,
            "billable": billable,
            "stop": stop,
            "created_with": created_with,
        })
        
        params = clean_params({"meta": "true" if meta else None})
        
        result = self._post(f"/workspaces/{workspace_id}/time_entries", data, params)
        return TimeEntry.from_dict(result)
    
    def start(
        self,
        workspace_id: int,
        description: str,
        project_id: Optional[int] = None,
        task_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        billable: bool = False,
        created_with: str = "toggl-track-skill",
    ) -> TimeEntry:
        """
        Start a new running timer.
        
        Args:
            workspace_id: Workspace ID
            description: Time entry description
            project_id: Project ID
            task_id: Task ID
            tags: List of tag names
            billable: Whether billable
            created_with: Client identifier
            
        Returns:
            Created TimeEntry model (running)
        """
        start_time = datetime.now(timezone.utc)
        start_iso = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        # For running entries: duration = -1 * Unix timestamp
        duration = int(-1 * start_time.timestamp())
        
        return self.create(
            workspace_id=workspace_id,
            description=description,
            duration=duration,
            start=start_iso,
            project_id=project_id,
            task_id=task_id,
            tags=tags,
            billable=billable,
            created_with=created_with,
        )
    
    def update(
        self,
        workspace_id: int,
        time_entry_id: int,
        **kwargs
    ) -> TimeEntry:
        """
        Update a time entry.
        
        Args:
            workspace_id: Workspace ID
            time_entry_id: Time entry ID
            **kwargs: Fields to update (description, project_id, tags, etc.)
            
        Returns:
            Updated TimeEntry model
        """
        time_entry_id = validate_time_entry_id(time_entry_id)
        
        result = self._put(
            f"/workspaces/{workspace_id}/time_entries/{time_entry_id}",
            kwargs
        )
        return TimeEntry.from_dict(result)
    
    def patch(
        self,
        workspace_id: int,
        time_entry_ids: List[int],
        operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Bulk patch multiple time entries (RFC 6902 JSON Patch).
        
        Args:
            workspace_id: Workspace ID
            time_entry_ids: List of time entry IDs (max 100)
            operations: List of patch operations
                [{"op": "replace", "path": "/description", "value": "new"}]
                
        Returns:
            Dict with 'success' and 'failure' keys
        """
        if len(time_entry_ids) > 100:
            raise ValueError("Maximum 100 time entries per patch request")
        
        ids_str = ",".join(map(str, time_entry_ids))
        return self._patch(
            f"/workspaces/{workspace_id}/time_entries/{ids_str}",
            operations
        )
    
    def stop(
        self,
        workspace_id: int,
        time_entry_id: int
    ) -> TimeEntry:
        """
        Stop a running time entry.
        
        Args:
            workspace_id: Workspace ID
            time_entry_id: Time entry ID
            
        Returns:
            Updated TimeEntry model (stopped)
        """
        stop_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return self.update(workspace_id, time_entry_id, stop=stop_time)
    
    def delete(self, workspace_id: int, time_entry_id: int) -> bool:
        """
        Delete a time entry.
        
        Args:
            workspace_id: Workspace ID
            time_entry_id: Time entry ID
            
        Returns:
            True if deleted successfully
        """
        time_entry_id = validate_time_entry_id(time_entry_id)
        return self._delete(f"/workspaces/{workspace_id}/time_entries/{time_entry_id}")
