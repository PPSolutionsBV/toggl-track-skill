"""
Toggl Track API Client - Complete Python client for Toggl Track API v9

Usage:
    from toggl_client import TogglClient
    
    client = TogglClient(api_token="your_token_here")
    
    # Get current user
    me = client.get_me()
    
    # Get time entries
    entries = client.get_time_entries(start_date="2024-01-01", end_date="2024-01-31")
    
    # Get running timer
    current = client.get_current_time_entry()
"""

import os
import base64
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
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
    
    def _delete(self, endpoint: str) -> bool:
        """Make DELETE request to Toggl API"""
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.delete(url)
        response.raise_for_status()
        return response.status_code == 200
    
    # ==================== User & Session ====================
    
    def get_me(self) -> Dict[str, Any]:
        """Get current user details including workspaces"""
        return self._get("/me")
    
    def check_logged_in(self) -> bool:
        """Check if authentication is working"""
        try:
            self._get("/me/logged")
            return True
        except requests.HTTPError:
            return False
    
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
    
    # ==================== Workspaces ====================
    
    def get_workspaces(self) -> List[Dict[str, Any]]:
        """Get all workspaces for current user"""
        return self._get("/workspaces") or []
    
    def get_workspace(self, workspace_id: int) -> Dict[str, Any]:
        """Get specific workspace details"""
        return self._get(f"/workspaces/{workspace_id}")
    
    def get_workspace_users(self, workspace_id: int) -> List[Dict[str, Any]]:
        """Get all users in a workspace"""
        return self._get(f"/workspaces/{workspace_id}/users") or []
    
    def get_workspace_groups(self, workspace_id: int) -> List[Dict[str, Any]]:
        """Get all groups in a workspace"""
        return self._get(f"/workspaces/{workspace_id}/groups") or []
    
    def get_workspace_tasks(self, workspace_id: int) -> List[Dict[str, Any]]:
        """Get all tasks in a workspace"""
        return self._get(f"/workspaces/{workspace_id}/tasks") or []
    
    # ==================== Projects ====================
    
    def get_projects(self, workspace_id: int, active: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Get all projects in a workspace
        
        Args:
            workspace_id: The workspace ID
            active: Filter by active status (True/False/None for all)
        """
        params = {}
        if active is not None:
            params["active"] = "true" if active else "false"
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
        description: Optional[str] = None,
        project_ids: Optional[List[int]] = None,
        client_ids: Optional[List[int]] = None,
        tag_ids: Optional[List[int]] = None,
        billable: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Get time entries for current user
        
        Args:
            start_date: Start date in ISO 8601 format (e.g., "2024-01-01T00:00:00Z")
            end_date: End date in ISO 8601 format
            description: Filter by description text
            project_ids: Filter by project IDs
            client_ids: Filter by client IDs
            tag_ids: Filter by tag IDs
            billable: Filter by billable status
        """
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if description:
            params["description"] = description
        if project_ids:
            params["project_ids"] = ",".join(map(str, project_ids))
        if client_ids:
            params["client_ids"] = ",".join(map(str, client_ids))
        if tag_ids:
            params["tag_ids"] = ",".join(map(str, tag_ids))
        if billable is not None:
            params["billable"] = "true" if billable else "false"
        
        return self._get("/me/time_entries", params) or []
    
    def get_current_time_entry(self) -> Optional[Dict[str, Any]]:
        """Get currently running time entry (timer)"""
        return self._get("/me/time_entries/current")
    
    def get_workspace_time_entries(
        self,
        workspace_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        user_ids: Optional[List[int]] = None,
        description: Optional[str] = None,
        project_ids: Optional[List[int]] = None,
        client_ids: Optional[List[int]] = None,
        tag_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """Get time entries for a workspace (admin access required)"""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if user_ids:
            params["user_ids"] = ",".join(map(str, user_ids))
        if description:
            params["description"] = description
        if project_ids:
            params["project_ids"] = ",".join(map(str, project_ids))
        if client_ids:
            params["client_ids"] = ",".join(map(str, client_ids))
        if tag_ids:
            params["tag_ids"] = ",".join(map(str, tag_ids))
        
        return self._get(f"/workspaces/{workspace_id}/time_entries", params) or []
    
    def get_time_entry(self, workspace_id: int, entry_id: int) -> Dict[str, Any]:
        """Get specific time entry"""
        return self._get(f"/workspaces/{workspace_id}/time_entries/{entry_id}")
    
    def start_time_entry(
        self,
        workspace_id: int,
        description: str,
        project_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        billable: bool = False,
        start_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start a new time entry (timer)"""
        data = {
            "workspace_id": workspace_id,
            "description": description,
            "billable": billable,
            "created_with": "toggl-track-skill"
        }
        if project_id:
            data["project_id"] = project_id
        if tags:
            data["tags"] = tags
        if start_date:
            data["start"] = start_date
        else:
            data["start"] = datetime.now(timezone.utc).isoformat()
        
        return self._post(f"/workspaces/{workspace_id}/time_entries", data)
    
    def stop_time_entry(self, workspace_id: int, entry_id: int) -> Dict[str, Any]:
        """Stop a running time entry"""
        url = f"{self.BASE_URL}/workspaces/{workspace_id}/time_entries/{entry_id}/stop"
        response = self.session.patch(url)
        response.raise_for_status()
        return response.json() if response.content else {}
    
    def update_time_entry(self, workspace_id: int, entry_id: int, **kwargs) -> Dict[str, Any]:
        """Update a time entry"""
        return self._put(f"/workspaces/{workspace_id}/time_entries/{entry_id}", kwargs)
    
    def delete_time_entry(self, workspace_id: int, entry_id: int) -> bool:
        """Delete a time entry"""
        return self._delete(f"/workspaces/{workspace_id}/time_entries/{entry_id}")
    
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
    
    def get_all_data(self) -> Dict[str, Any]:
        """
        Fetch all relevant data for the user:
        - User profile
        - Workspaces
        - Projects per workspace
        - Clients per workspace
        - Tags per workspace
        - Recent time entries (last 30 days)
        """
        from datetime import datetime, timedelta
        
        result = {
            "user": self.get_me(),
            "workspaces": [],
            "time_entries": []
        }
        
        workspaces = self.get_workspaces()
        
        for ws in workspaces:
            ws_id = ws["id"]
            ws_data = {
                **ws,
                "projects": self.get_projects(ws_id),
                "clients": self.get_clients(ws_id),
                "tags": self.get_tags(ws_id)
            }
            result["workspaces"].append(ws_data)
        
        # Get time entries for last 30 days
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=30)
        result["time_entries"] = self.get_time_entries(
            start_date=start.isoformat(),
            end_date=end.isoformat()
        )
        
        return result


if __name__ == "__main__":
    # Example usage with different authentication methods
    import json
    
    # Method 1: API Token (recommended)
    # Get your token at: https://track.toggl.com/profile
    token = os.getenv("TOGGL_API_TOKEN")
    
    # Method 2: Email/Password
    # email = os.getenv("TOGGL_EMAIL")
    # password = os.getenv("TOGGL_PASSWORD")
    
    # Method 3: Create session from email/password
    # session_cookie = TogglClient.create_session("user@example.com", "password")
    # client = TogglClient(session_cookie=session_cookie)
    
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
    
    # Get user info
    me = client.get_me()
    print(f"\nUser: {me.get('fullname', 'Unknown')} ({me.get('email', 'No email')})")
    
    # Get workspaces
    workspaces = client.get_workspaces()
    print(f"\nWorkspaces ({len(workspaces)}):")
    for ws in workspaces:
        print(f"  - {ws.get('name')} (ID: {ws.get('id')})")
    
    # Get current timer
    current = client.get_current_time_entry()
    if current:
        print(f"\n⏱️  Currently tracking: {current.get('description', 'No description')}")
    else:
        print("\nNo timer running")
