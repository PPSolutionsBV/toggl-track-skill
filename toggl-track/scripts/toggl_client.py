"""
Toggl Track API Client - Complete Python client for Toggl Track API v9

Usage:
    from toggl_client import TogglClient
    
    client = TogglClient(api_token="your_token_here")
    
    # Get current user with all related data
    me = client.get_me(with_related_data=True)
    
    # Get time entries (returns dict with 'items' key)
    result = client.get_time_entries(start_date="2024-01-01", end_date="2024-01-31")
    entries = result['items']
    
    # Get running timer
    current = client.get_current_time_entry()
"""

import os
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Union
import requests


class TogglClient:
    """Complete Toggl Track API v9 client
    
    Authentication methods:
    1. API Token: TogglClient(api_token="your_token")
    2. Email/Password: TogglClient(email="user@example.com", password="secret")
    3. Session Cookie: TogglClient(session_cookie="cookie_value")
    """
    
    BASE_URL = "https://api.track.toggl.com/api/v9"
    REPORTS_URL = "https://api.track.toggl.com/reports/api/v3"
    ACCOUNTS_URL = "https://accounts.toggl.com/api"
    
    def __init__(
        self,
        api_token: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        session_cookie: Optional[str] = None
    ):
        """
        Initialize Toggl client
        
        Args:
            api_token: Toggl Track API token (from https://track.toggl.com/profile)
            email: Toggl account email (alternative to api_token)
            password: Toggl account password (alternative to api_token)
            session_cookie: Session cookie from accounts.toggl.com (alternative auth)
        """
        self.api_token = api_token or os.getenv("TOGGL_API_TOKEN")
        self.email = email or os.getenv("TOGGL_EMAIL")
        self.password = password or os.getenv("TOGGL_PASSWORD")
        self.session_cookie = session_cookie
        
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })
        
        # Determine authentication method
        if self.api_token:
            # Method 1: API Token (recommended for scripts)
            self.session.auth = (self.api_token, "api_token")
        elif self.email and self.password:
            # Method 2: Email/Password Basic Auth
            self.session.auth = (self.email, self.password)
        elif self.session_cookie:
            # Method 3: Session Cookie
            self.session.headers.update({
                "Cookie": f"__Secure-accounts-session={self.session_cookie}"
            })
        else:
            raise ValueError(
                "Authentication required. Provide one of:\n"
                "  - api_token (or TOGGL_API_TOKEN env var)\n"
                "  - email + password (or TOGGL_EMAIL + TOGGL_PASSWORD env vars)\n"
                "  - session_cookie\n\n"
                "Get your API token at: https://track.toggl.com/profile"
            )
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Make GET request to Toggl API"""
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json() if response.content else None
    
    def _post(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        """Make POST request to Toggl API"""
        url = f"{self.BASE_URL}{endpoint}" if not endpoint.startswith("http") else endpoint
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json() if response.content else None
    
    def _put(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        """Make PUT request to Toggl API"""
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.put(url, json=data)
        response.raise_for_status()
        return response.json() if response.content else None
    
    def _patch(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        """Make PATCH request to Toggl API"""
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.patch(url, json=data)
        response.raise_for_status()
        return response.json() if response.content else None
    
    def _delete(self, endpoint: str) -> bool:
        """Make DELETE request to Toggl API"""
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.delete(url)
        response.raise_for_status()
        return response.status_code == 200
    
    # ==================== Authentication Methods ====================
    
    @staticmethod
    def create_session(email: str, password: str) -> str:
        """
        Create a session and return the session cookie.
        
        Args:
            email: Toggl account email
            password: Toggl account password
            
        Returns:
            Session cookie value for use with TogglClient(session_cookie=...)
        """
        url = "https://accounts.toggl.com/api/sessions"
        response = requests.post(
            url,
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        # Extract cookie from response
        cookie = response.headers.get("Set-Cookie", "")
        if "__Secure-accounts-session=" in cookie:
            return cookie.split("__Secure-accounts-session=")[1].split(";")[0]
        raise ValueError("Failed to get session cookie")
    
    def destroy_session(self) -> bool:
        """Destroy the current session (if using session cookie auth)"""
        url = f"{self.ACCOUNTS_URL}/sessions"
        response = self.session.delete(url)
        return response.status_code == 200
    
    def reset_api_token(self) -> str:
        """Reset API token and return new token"""
        result = self._post("/me/reset_token")
        return result.get("api_token")
    
    # ==================== User & Session ====================
    
    def get_me(self, with_related_data: bool = False) -> Dict[str, Any]:
        """
        Get current user details.
        
        Args:
            with_related_data: If True, includes clients, projects, tasks, tags, 
                              workspaces, and time_entries in the response
        
        Returns:
            User details dict. Related data fields are null if with_related_data=False
        """
        params = {}
        if with_related_data:
            params["with_related_data"] = "true"
        return self._get("/me", params)
    
    def check_logged_in(self) -> bool:
        """Check if authentication is working"""
        try:
            self._get("/me/logged")
            return True
        except requests.HTTPError:
            return False
    
    # ==================== Workspaces ====================
    
    def get_workspaces(self) -> List[Dict[str, Any]]:
        """Get all workspaces for current user"""
        return self._get("/workspaces") or []
    
    def get_workspace(self, workspace_id: int) -> Dict[str, Any]:
        """Get specific workspace details"""
        return self._get(f"/workspaces/{workspace_id}")
    
    def get_workspace_users(self, workspace_id: int) -> List[Dict[str, Any]]:
        """Get all users in a workspace (legacy endpoint)"""
        return self._get(f"/workspaces/{workspace_id}/users") or []
    
    def get_workspace_groups(self, workspace_id: int) -> List[Dict[str, Any]]:
        """Get all groups in a workspace"""
        return self._get(f"/workspaces/{workspace_id}/groups") or []
    
    def get_workspace_tasks(self, workspace_id: int) -> List[Dict[str, Any]]:
        """Get all tasks in a workspace"""
        return self._get(f"/workspaces/{workspace_id}/tasks") or []
    
    # ==================== Projects ====================
    
    def get_projects(
        self, 
        workspace_id: int, 
        active: Optional[bool] = None,
        since: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all projects in a workspace
        
        Args:
            workspace_id: The workspace ID
            active: Filter by active status (True/False/None for all)
            since: Unix timestamp to get projects modified since
        """
        params = {}
        if active is not None:
            params["active"] = "true" if active else "false"
        if since is not None:
            params["since"] = since
        return self._get(f"/workspaces/{workspace_id}/projects", params) or []
    
    def get_project(self, workspace_id: int, project_id: int) -> Dict[str, Any]:
        """Get specific project details"""
        return self._get(f"/workspaces/{workspace_id}/projects/{project_id}")
    
    def create_project(self, workspace_id: int, name: str, **kwargs) -> Dict[str, Any]:
        """Create a new project"""
        data = {"name": name, **kwargs}
        return self._post(f"/workspaces/{workspace_id}/projects", data)
    
    def update_project(self, workspace_id: int, project_id: int, **kwargs) -> Dict[str, Any]:
        """Update a project"""
        return self._put(f"/workspaces/{workspace_id}/projects/{project_id}", kwargs)
    
    def delete_project(self, workspace_id: int, project_id: int) -> bool:
        """Delete a project"""
        return self._delete(f"/workspaces/{workspace_id}/projects/{project_id}")
    
    # ==================== Project Users ====================
    
    def get_project_users(
        self,
        workspace_id: int,
        project_ids: Optional[List[int]] = None,
        user_id: Optional[int] = None,
        with_group_members: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Get project users for a workspace
        
        Args:
            workspace_id: The workspace ID
            project_ids: Filter by specific project IDs (comma-separated)
            user_id: Filter by specific user
            with_group_members: Include group members
            
        Returns:
            Dict with 'items' key containing list of project users
        """
        params = {}
        if project_ids:
            params["project_ids"] = ",".join(map(str, project_ids))
        if user_id:
            params["user_id"] = user_id
        if with_group_members is not None:
            params["with_group_members"] = "true" if with_group_members else "false"
        return self._get(f"/workspaces/{workspace_id}/project_users", params) or {"items": []}
    
    # ==================== Clients ====================
    
    def get_clients(self, workspace_id: int) -> List[Dict[str, Any]]:
        """Get all clients in a workspace"""
        return self._get(f"/workspaces/{workspace_id}/clients") or []
    
    def get_client(self, workspace_id: int, client_id: int) -> Dict[str, Any]:
        """Get specific client details"""
        return self._get(f"/workspaces/{workspace_id}/clients/{client_id}")
    
    def create_client(self, workspace_id: int, name: str, **kwargs) -> Dict[str, Any]:
        """Create a new client"""
        data = {"name": name, **kwargs}
        return self._post(f"/workspaces/{workspace_id}/clients", data)
    
    # ==================== Tags ====================
    
    def get_tags(self, workspace_id: int) -> List[Dict[str, Any]]:
        """Get all tags in a workspace"""
        return self._get(f"/workspaces/{workspace_id}/tags") or []
    
    def create_tag(self, workspace_id: int, name: str) -> Dict[str, Any]:
        """Create a new tag"""
        return self._post(f"/workspaces/{workspace_id}/tags", {"name": name})
    
    # ==================== Time Entries ====================
    
    def get_time_entries(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        since: Optional[int] = None,
        before: Optional[str] = None,
        meta: Optional[bool] = None,
        include_sharing: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Get time entries for current user
        
        IMPORTANT: Returns a dict with 'items' key, not a direct list!
        
        Args:
            start_date: Start date (YYYY-MM-DD or RFC3339)
            end_date: End date (YYYY-MM-DD or RFC3339)
            since: Unix timestamp to get entries modified since (includes deleted)
            before: Get entries before this date
            meta: Include meta entity data (client_name, project_name, etc.)
            include_sharing: Include sharing details
            
        Returns:
            Dict with 'items' key containing list of time entries
        """
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if since:
            params["since"] = since
        if before:
            params["before"] = before
        if meta is not None:
            params["meta"] = "true" if meta else "false"
        if include_sharing is not None:
            params["include_sharing"] = "true" if include_sharing else "false"
        
        return self._get("/me/time_entries", params) or {"items": []}
    
    def get_time_entry_by_id(
        self,
        time_entry_id: int,
        meta: Optional[bool] = None,
        include_sharing: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Get a specific time entry by ID
        
        Args:
            time_entry_id: The time entry ID
            meta: Include meta entity data
            include_sharing: Include sharing details
        """
        params = {}
        if meta is not None:
            params["meta"] = "true" if meta else "false"
        if include_sharing is not None:
            params["include_sharing"] = "true" if include_sharing else "false"
        return self._get(f"/me/time_entries/{time_entry_id}", params)
    
    def get_current_time_entry(self) -> Optional[Dict[str, Any]]:
        """Get currently running time entry (timer)"""
        return self._get("/me/time_entries/current")
    
    def create_time_entry(
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
        duronly: bool = False,
        created_with: str = "toggl-track-skill"
    ) -> Dict[str, Any]:
        """
        Create a new time entry
        
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
            duronly: Create with duration but without stop time (deprecated)
            created_with: Client identifier
        """
        data = {
            "workspace_id": workspace_id,
            "description": description,
            "duration": duration,
            "start": start,
            "billable": billable,
            "duronly": duronly,
            "created_with": created_with
        }
        
        if project_id:
            data["project_id"] = project_id
        if task_id:
            data["task_id"] = task_id
        if tags:
            data["tags"] = tags
        if tag_ids:
            data["tag_ids"] = tag_ids
        if stop:
            data["stop"] = stop
            
        return self._post(f"/workspaces/{workspace_id}/time_entries", data)
    
    def start_time_entry(
        self,
        workspace_id: int,
        description: str,
        project_id: Optional[int] = None,
        task_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        billable: bool = False,
        created_with: str = "toggl-track-skill"
    ) -> Dict[str, Any]:
        """
        Start a new running timer
        
        For running entries, duration should be -1 * (Unix timestamp of start time)
        """
        start_time = datetime.now(timezone.utc)
        start_iso = start_time.isoformat()
        # For running entries: duration = -1 * Unix timestamp
        duration = int(-1 * start_time.timestamp())
        
        return self.create_time_entry(
            workspace_id=workspace_id,
            description=description,
            duration=duration,
            start=start_iso,
            project_id=project_id,
            task_id=task_id,
            tags=tags,
            billable=billable,
            created_with=created_with
        )
    
    def update_time_entry(
        self,
        workspace_id: int,
        time_entry_id: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Update a time entry"""
        return self._put(f"/workspaces/{workspace_id}/time_entries/{time_entry_id}", kwargs)
    
    def patch_time_entries(
        self,
        workspace_id: int,
        time_entry_ids: List[int],
        operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Bulk patch multiple time entries (RFC 6902 JSON Patch)
        
        Args:
            workspace_id: Workspace ID
            time_entry_ids: List of time entry IDs to patch
            operations: List of patch operations [{"op": "replace", "path": "/description", "value": "new"}]
            
        Returns:
            Dict with 'success' and 'failure' keys
        """
        ids_str = ",".join(map(str, time_entry_ids))
        return self._patch(f"/workspaces/{workspace_id}/time_entries/{ids_str}", operations)
    
    def stop_time_entry(self, workspace_id: int, time_entry_id: int) -> Dict[str, Any]:
        """
        Stop a running time entry
        
        Note: The stop endpoint may vary by API version. This uses PUT to update stop time.
        """
        stop_time = datetime.now(timezone.utc).isoformat()
        return self.update_time_entry(workspace_id, time_entry_id, stop=stop_time)
    
    def delete_time_entry(self, workspace_id: int, time_entry_id: int) -> bool:
        """Delete a time entry"""
        return self._delete(f"/workspaces/{workspace_id}/time_entries/{time_entry_id}")
    
    # ==================== Reports ====================
    
    def get_summary_report(
        self,
        workspace_id: int,
        start_date: str,
        end_date: str,
        description: Optional[str] = None,
        project_ids: Optional[List[int]] = None,
        client_ids: Optional[List[int]] = None,
        tag_ids: Optional[List[int]] = None,
        user_ids: Optional[List[int]] = None,
        billable: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Get summary report for workspace
        
        Args:
            workspace_id: The workspace ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            description: Filter by description
            project_ids: Filter by projects
            client_ids: Filter by clients
            tag_ids: Filter by tags
            user_ids: Filter by users
            billable: Filter by billable status
        """
        url = f"{self.REPORTS_URL}/workspace/{workspace_id}/summary/time_entries"
        data = {
            "start_date": start_date,
            "end_date": end_date
        }
        if description:
            data["description"] = description
        if project_ids:
            data["project_ids"] = project_ids
        if client_ids:
            data["client_ids"] = client_ids
        if tag_ids:
            data["tag_ids"] = tag_ids
        if user_ids:
            data["user_ids"] = user_ids
        if billable is not None:
            data["billable"] = billable
        
        return self._post(url, data)
    
    def get_detailed_report(
        self,
        workspace_id: int,
        start_date: str,
        end_date: str,
        description: Optional[str] = None,
        project_ids: Optional[List[int]] = None,
        client_ids: Optional[List[int]] = None,
        tag_ids: Optional[List[int]] = None,
        user_ids: Optional[List[int]] = None,
        billable: Optional[bool] = None,
        page: int = 1,
        per_page: int = 50
    ) -> Dict[str, Any]:
        """Get detailed report with pagination"""
        url = f"{self.REPORTS_URL}/workspace/{workspace_id}/details/time_entries"
        data = {
            "start_date": start_date,
            "end_date": end_date,
            "page": page,
            "per_page": per_page
        }
        if description:
            data["description"] = description
        if project_ids:
            data["project_ids"] = project_ids
        if client_ids:
            data["client_ids"] = client_ids
        if tag_ids:
            data["tag_ids"] = tag_ids
        if user_ids:
            data["user_ids"] = user_ids
        if billable is not None:
            data["billable"] = billable
        
        return self._post(url, data)
    
    def get_weekly_report(
        self,
        workspace_id: int,
        start_date: str,
        end_date: str,
        description: Optional[str] = None,
        project_ids: Optional[List[int]] = None,
        client_ids: Optional[List[int]] = None,
        tag_ids: Optional[List[int]] = None,
        user_ids: Optional[List[int]] = None,
        billable: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Get weekly report grouped by day"""
        url = f"{self.REPORTS_URL}/workspace/{workspace_id}/weekly/time_entries"
        data = {
            "start_date": start_date,
            "end_date": end_date
        }
        if description:
            data["description"] = description
        if project_ids:
            data["project_ids"] = project_ids
        if client_ids:
            data["client_ids"] = client_ids
        if tag_ids:
            data["tag_ids"] = tag_ids
        if user_ids:
            data["user_ids"] = user_ids
        if billable is not None:
            data["billable"] = billable
        
        return self._post(url, data)
    
    # ==================== Utility Methods ====================
    
    def get_all_data(self, days: int = 30) -> Dict[str, Any]:
        """
        Fetch all relevant data for the user using with_related_data parameter
        
        This is more efficient than making separate calls.
        
        Args:
            days: Number of days of time entries to fetch (if not using with_related_data)
            
        Returns:
            Dict with user data including related entities
        """
        # Get user with all related data
        return self.get_me(with_related_data=True)


if __name__ == "__main__":
    # Example usage
    import json
    
    token = os.getenv("TOGGL_API_TOKEN")
    if not token:
        print("Please set TOGGL_API_TOKEN environment variable")
        print("Or use TOGGL_EMAIL and TOGGL_PASSWORD")
        print("Get your token at: https://track.toggl.com/profile")
        exit(1)
    
    client = TogglClient(api_token=token)
    
    # Test authentication
    print("Testing authentication...")
    if client.check_logged_in():
        print("✓ Authentication successful")
    else:
        print("✗ Authentication failed")
        exit(1)
    
    # Get user info with related data
    print("\nFetching user data with related entities...")
    me = client.get_me(with_related_data=True)
    print(f"User: {me.get('fullname', 'Unknown')} ({me.get('email', 'No email')})")
    print(f"Workspaces: {len(me.get('workspaces') or [])}")
    print(f"Projects: {len(me.get('projects') or [])}")
    print(f"Clients: {len(me.get('clients') or [])}")
    print(f"Tags: {len(me.get('tags') or [])}")
    print(f"Time entries: {len(me.get('time_entries') or [])}")
    
    # Get time entries with proper response format
    print("\nFetching time entries...")
    result = client.get_time_entries(meta=True)
    entries = result.get('items', [])
    print(f"Found {len(entries)} time entries")
    
    # Get current timer
    current = client.get_current_time_entry()
    if current:
        print(f"\n⏱️  Currently tracking: {current.get('description', 'No description')}")
    else:
        print("\nNo timer running")
